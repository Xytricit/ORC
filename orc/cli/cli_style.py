"""
ORC CLI Output Styling Module

Professional styling system for CLI output with semantic colors,
clean symbols, and fallback for non-color terminals.

Author: ORC Team
Date: 2026-01-14
"""

import sys
from typing import Optional


class CLIOutput:
    """Professional styling system for CLI output."""
    
    # Color codes (ANSI)
    COLORS = {
        'accent': '\033[96m',      # Cyan
        'success': '\033[92m',     # Green
        'warning': '\033[93m',     # Yellow
        'error': '\033[91m',       # Red
        'dim': '\033[90m',         # Gray
        'bold': '\033[1m',
        'reset': '\033[0m',
    }
    
    # Symbols with fallbacks
    SYMBOLS = {
        'chevron': '>',
        'check': '[OK]',
        'cross': '[ERR]',
        'bullet': '-',
        'warning': '[WARN]',
    }
    
    FALLBACK_SYMBOLS = {
        'check': '[OK]',
        'cross': '[ERR]',
        'warning': '[WARN]',
        'bullet': '',
    }
    
    def __init__(self, use_color: Optional[bool] = None):
        """
        Initialize CLI output handler.
        
        Args:
            use_color: Force color on/off. If None, auto-detect terminal support.
        """
        if use_color is None:
            # Auto-detect color support
            self.use_color = self._supports_color()
        else:
            self.use_color = use_color
    
    def _supports_color(self) -> bool:
        """
        Check if terminal supports color output.
        
        Returns:
            bool: True if color is supported
        """
        # Check if stdout is a TTY
        if not hasattr(sys.stdout, 'isatty'):
            return False
        if not sys.stdout.isatty():
            return False
        
        # Check for CI/CD environments
        import os
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            return False
        
        # Windows color support
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        
        return True
    
    def _colorize(self, text: str, color: str) -> str:
        """
        Apply color to text if color is enabled.
        
        Args:
            text: Text to colorize
            color: Color name from COLORS dict
        
        Returns:
            str: Colored text or plain text
        """
        if not self.use_color:
            return text
        
        color_code = self.COLORS.get(color, '')
        reset = self.COLORS['reset']
        return f"{color_code}{text}{reset}"
    
    def _get_symbol(self, symbol_name: str, fallback: bool = False) -> str:
        """
        Get symbol with optional fallback.
        
        Args:
            symbol_name: Name of symbol
            fallback: Use fallback symbol if True
        
        Returns:
            str: Symbol character or fallback text
        """
        if fallback or not self.use_color:
            return self.FALLBACK_SYMBOLS.get(symbol_name, self.SYMBOLS.get(symbol_name, ''))
        return self.SYMBOLS.get(symbol_name, '')
    
    def start_phase(self, title: str) -> None:
        """
        Print phase header with chevron symbol.
        
        Args:
            title: Phase title
        """
        chevron = self.SYMBOLS['chevron']
        colored_title = self._colorize(title, 'accent')
        print(f"{chevron} {colored_title}")
    
    def success(self, message: str, indent: int = 2) -> None:
        """
        Print success message with check symbol.
        
        Args:
            message: Success message
            indent: Number of spaces to indent
        """
        if self.use_color:
            symbol = self._colorize(self.SYMBOLS['check'], 'success')
        else:
            symbol = self._get_symbol('check', fallback=True)
        
        spaces = ' ' * indent
        print(f"{spaces}{symbol} {message}")
    
    def warning(self, message: str, indent: int = 2) -> None:
        """
        Print warning message with warning symbol.
        
        Args:
            message: Warning message
            indent: Number of spaces to indent
        """
        if self.use_color:
            symbol = self._colorize(self.SYMBOLS['warning'], 'warning')
        else:
            symbol = self._get_symbol('warning', fallback=True)
        
        spaces = ' ' * indent
        print(f"{spaces}{symbol} {message}")
    
    def error(self, message: str, indent: int = 2) -> None:
        """
        Print error message with cross symbol.
        
        Args:
            message: Error message
            indent: Number of spaces to indent
        """
        if self.use_color:
            symbol = self._colorize(self.SYMBOLS['cross'], 'error')
        else:
            symbol = self._get_symbol('cross', fallback=True)
        
        spaces = ' ' * indent
        print(f"{spaces}{symbol} {message}", file=sys.stderr)
    
    def info(self, message: str, indent: int = 2) -> None:
        """
        Print info message with bullet symbol.
        
        Args:
            message: Info message
            indent: Number of spaces to indent
        """
        symbol = self.SYMBOLS['bullet'] if self.use_color else ''
        spaces = ' ' * indent
        colored_message = self._colorize(message, 'dim')
        
        if symbol:
            print(f"{spaces}{symbol} {colored_message}")
        else:
            print(f"{spaces}{message}")
    
    def print(self, message: str, color: Optional[str] = None) -> None:
        """
        Print message with optional color.
        
        Args:
            message: Message to print
            color: Optional color name
        """
        if color:
            message = self._colorize(message, color)
        print(message)
    
    def dim(self, text: str) -> str:
        """
        Return dimmed text.
        
        Args:
            text: Text to dim
        
        Returns:
            str: Dimmed text
        """
        return self._colorize(text, 'dim')
    
    def bold(self, text: str) -> str:
        """
        Return bold text.
        
        Args:
            text: Text to make bold
        
        Returns:
            str: Bold text
        """
        return self._colorize(text, 'bold')


# Global instance for convenience
output = CLIOutput()
