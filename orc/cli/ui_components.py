"""
ORC UI Components Module

Premium UI components for CLI with syntax highlighting and code display.

Author: ORC Team
Date: 2026-01-14
"""

import re
from typing import Optional

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import TerminalFormatter, Terminal256Formatter
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


class UIComponents:
    """Premium UI components for CLI interface."""
    
    def __init__(self, use_color: bool = True):
        """
        Initialize UI components.
        
        Args:
            use_color: Enable color output
        """
        self.use_color = use_color and PYGMENTS_AVAILABLE
    
    def display_user_message(self, message: str) -> None:
        """
        Display user message with clean borders.
        
        Args:
            message: User's message
        """
        print()
        print(f"You: {message}")
        print()
    
    def display_ai_message(self, message: str) -> None:
        """
        Display AI response with syntax highlighting for code blocks.
        
        Args:
            message: AI's response message
        """
        print()
        print("ORC: ", end="")
        
        # Check for markdown code blocks
        if "```" in message:
            parts = self._split_code_blocks(message)
            for part in parts:
                if part['type'] == 'code':
                    print()  # Newline before code
                    self.display_code_block(part['content'], part.get('language', ''))
                    print()  # Newline after code
                else:
                    print(part['content'], end="")
        else:
            print(message)
        
        print()
    
    def display_code_block(self, code: str, language: str = '') -> None:
        """
        Display syntax-highlighted code block.
        
        Args:
            code: Code to display
            language: Programming language (auto-detect if empty)
        """
        if not language:
            language = self.auto_detect_language(code)
        
        highlighted = self.highlight_code(code, language)
        
        # Print with border
        print("─" * 60)
        print(highlighted)
        print("─" * 60)
    
    def highlight_code(self, code: str, language: str = 'python') -> str:
        """
        Apply syntax highlighting to code.
        
        Args:
            code: Code to highlight
            language: Programming language
        
        Returns:
            str: Highlighted code or plain code if pygments unavailable
        """
        if not self.use_color or not PYGMENTS_AVAILABLE:
            return code
        
        try:
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = Terminal256Formatter(style='monokai')
            return highlight(code, lexer, formatter).rstrip()
        except ClassNotFound:
            # Language not recognized, try to guess
            try:
                lexer = guess_lexer(code)
                formatter = Terminal256Formatter(style='monokai')
                return highlight(code, lexer, formatter).rstrip()
            except:
                return code
        except Exception:
            return code
    
    def auto_detect_language(self, code: str) -> str:
        """
        Auto-detect programming language from code.
        
        Args:
            code: Code snippet
        
        Returns:
            str: Detected language name
        """
        code_lower = code.lower().strip()
        
        # Python indicators
        if any(keyword in code for keyword in ['def ', 'import ', 'class ', 'self.', 'print(']):
            return 'python'
        
        # JavaScript indicators
        if any(keyword in code for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
            return 'javascript'
        
        # TypeScript indicators
        if any(keyword in code for keyword in ['interface ', ': string', ': number', ': boolean']):
            return 'typescript'
        
        # SQL indicators
        if any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert into', 'create table']):
            return 'sql'
        
        # JSON indicators
        if code.strip().startswith('{') and code.strip().endswith('}'):
            return 'json'
        
        # YAML indicators
        if ':' in code and code.startswith((' ', '-')):
            return 'yaml'
        
        # HTML/XML indicators
        if code.strip().startswith('<') and '>' in code:
            return 'html'
        
        # Default to text
        return 'text'
    
    def display_status_bar(self, model: str, tokens_used: int, cost: float) -> None:
        """
        Display status bar with model info and token usage.
        
        Args:
            model: AI model name
            tokens_used: Number of tokens used
            cost: Estimated cost
        """
        status = f"Model: {model} | Tokens: {tokens_used:,} | Cost: ${cost:.4f}"
        print()
        print("─" * 60)
        print(status)
        print("─" * 60)
        print()
    
    def _split_code_blocks(self, text: str) -> list:
        """
        Split text into code blocks and regular text.
        
        Args:
            text: Text with potential code blocks
        
        Returns:
            list: List of dicts with 'type', 'content', and optional 'language'
        """
        parts = []
        pattern = r'```(\w+)?\n(.*?)```'
        last_end = 0
        
        for match in re.finditer(pattern, text, re.DOTALL):
            # Add text before code block
            if match.start() > last_end:
                parts.append({
                    'type': 'text',
                    'content': text[last_end:match.start()]
                })
            
            # Add code block
            language = match.group(1) or ''
            code = match.group(2)
            parts.append({
                'type': 'code',
                'content': code,
                'language': language
            })
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            parts.append({
                'type': 'text',
                'content': text[last_end:]
            })
        
        return parts if parts else [{'type': 'text', 'content': text}]
    
    def print_table(self, headers: list, rows: list) -> None:
        """
        Print formatted table.
        
        Args:
            headers: List of column headers
            rows: List of row data (list of lists)
        """
        if not rows:
            return
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print(header_line)
        print("-" * len(header_line))
        
        # Print rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
            print(row_line)
    
    def print_tree(self, data: dict, prefix: str = "", is_last: bool = True) -> None:
        """
        Print tree structure.
        
        Args:
            data: Dictionary with nested structure
            prefix: Current line prefix
            is_last: Is this the last item at this level
        """
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            
            # Print current item
            connector = "└── " if is_last_item else "├── "
            print(f"{prefix}{connector}{key}")
            
            # Recurse if value is dict
            if isinstance(value, dict):
                extension = "    " if is_last_item else "│   "
                self.print_tree(value, prefix + extension, is_last_item)


# Global instance for convenience
ui = UIComponents()
