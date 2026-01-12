"""
Premium UI Components for ORC Chat Interface

Inspired by Claude CLI, Gemini CLI, and Qwen CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table
from rich import box
import re
from typing import Optional, List, Dict

console = Console()


def display_user_message(message: str):
    """Display user message with clean formatting"""
    console.print()
    console.print("┌─ [bold cyan]You[/bold cyan]")
    
    # Handle multi-line messages
    lines = message.split('\n')
    for line in lines:
        console.print(f"│ {line}")
    
    console.print("└─")
    console.print()


def display_ai_message(message: str, metadata: Optional[Dict] = None):
    """
    Display AI message with syntax highlighting and metadata
    
    Args:
        message: AI response text (may contain code blocks)
        metadata: Optional dict with tokens, time, cost info
    """
    console.print()
    console.print("┌─ [bold green]ORC[/bold green]")
    
    # Parse and display message with code highlighting
    parts = parse_message_with_code(message)
    
    for part in parts:
        if part['type'] == 'text':
            # Regular text
            lines = part['content'].split('\n')
            for line in lines:
                if line.strip():  # Skip empty lines
                    console.print(f"│ {line}")
        
        elif part['type'] == 'code':
            # Code block with syntax highlighting
            console.print("│")
            display_code_block(part['content'], part.get('language', 'python'), prefix="│ ")
            console.print("│")
    
    # Footer with metadata
    if metadata:
        footer_parts = []
        if 'tokens' in metadata:
            footer_parts.append(f"tokens: {metadata['tokens']}")
        if 'time' in metadata:
            footer_parts.append(f"time: {metadata['time']:.1f}s")
        if 'cost' in metadata:
            footer_parts.append(f"cost: ${metadata['cost']:.4f}")
        
        if footer_parts:
            console.print(f"└─ [dim]{' | '.join(footer_parts)}[/dim]")
        else:
            console.print("└─")
    else:
        console.print("└─")
    
    console.print()


def parse_message_with_code(message: str) -> List[Dict]:
    """
    Parse message to separate text and code blocks
    
    Returns:
        List of dicts with 'type' ('text' or 'code'), 'content', and optional 'language'
    """
    parts = []
    
    # Regex to find code blocks: ```language\ncode\n```
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    last_end = 0
    for match in re.finditer(code_block_pattern, message, re.DOTALL):
        # Add text before code block
        if match.start() > last_end:
            text = message[last_end:match.start()].strip()
            if text:
                parts.append({
                    'type': 'text',
                    'content': text
                })
        
        # Add code block
        language = match.group(1) or 'python'
        code = match.group(2).strip()
        parts.append({
            'type': 'code',
            'language': language,
            'content': code
        })
        
        last_end = match.end()
    
    # Add remaining text
    if last_end < len(message):
        text = message[last_end:].strip()
        if text:
            parts.append({
                'type': 'text',
                'content': text
            })
    
    # If no code blocks found, return as single text part
    if not parts:
        parts.append({
            'type': 'text',
            'content': message.strip()
        })
    
    return parts


def display_code_block(code: str, language: str = "python", prefix: str = ""):
    """
    Display syntax-highlighted code block
    
    Args:
        code: Code to display
        language: Programming language for syntax highlighting
        prefix: Prefix for each line (e.g., "│ ")
    """
    syntax = Syntax(
        code,
        language,
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
        background_color="default"
    )
    
    # If prefix specified, render and add prefix to each line
    if prefix:
        # Render syntax to string
        from io import StringIO
        from rich.console import Console as TempConsole
        
        string_buffer = StringIO()
        temp_console = TempConsole(file=string_buffer, force_terminal=True, width=console.width - len(prefix) - 2)
        temp_console.print(syntax)
        output = string_buffer.getvalue()
        
        for line in output.rstrip('\n').split('\n'):
            console.print(f"{prefix}{line}")
    else:
        console.print(syntax)


def display_tool_execution(tool_name: str, result: str):
    """Display tool execution result with clean formatting"""
    console.print()
    console.print(f"┌─ [bold yellow]Tool: {tool_name}[/bold yellow]")
    
    lines = result.split('\n')
    for line in lines:
        console.print(f"│ {line}")
    
    console.print("└─")
    console.print()


def display_error(title: str, message: str, suggestion: Optional[str] = None):
    """Display error with helpful formatting"""
    content = f"[red]{message}[/red]"
    
    if suggestion:
        content += f"\n\n[dim]Suggestion: {suggestion}[/dim]"
    
    panel = Panel(
        content,
        title=f"[red]✗ {title}[/red]",
        border_style="red",
        padding=(1, 2)
    )
    
    console.print()
    console.print(panel)
    console.print()


def display_success(message: str):
    """Display success message"""
    console.print(f"[green]+ {message}[/green]")


def display_info(message: str):
    """Display info message"""
    console.print(f"[cyan]i {message}[/cyan]")


def display_warning(message: str):
    """Display warning message"""
    console.print(f"[yellow]! {message}[/yellow]")


def display_status_bar(model: str, context_used: int, context_total: int, 
                       message_count: int, cost: float = 0.0):
    """
    Display status bar at top of chat
    
    Args:
        model: Current model (e.g., "groq/llama-3.1-70b")
        context_used: Tokens used in context
        context_total: Total context window size
        message_count: Number of messages in conversation
        cost: Estimated cost
    """
    status_parts = [
        f"[cyan]Model:[/cyan] {model}",
        f"[cyan]Context:[/cyan] {context_used:,}/{context_total:,}",
        f"[cyan]Messages:[/cyan] {message_count}",
    ]
    
    if cost > 0:
        status_parts.append(f"[cyan]Cost:[/cyan] ${cost:.4f}")
    
    status_text = " | ".join(status_parts)
    
    console.print(f"[dim]{status_text}[/dim]")
    console.print("─" * console.width)
    console.print()


def display_help():
    """Display enhanced help menu"""
    help_table = Table(show_header=False, box=None, padding=(0, 2))
    
    help_table.add_row(
        "[bold cyan]Conversation[/bold cyan]",
        ""
    )
    help_table.add_row("  /save [name]", "Save this conversation")
    help_table.add_row("  /load [name]", "Load a saved conversation")
    help_table.add_row("  /export [fmt]", "Export conversation (md/json)")
    help_table.add_row("  /reset", "Start new conversation")
    help_table.add_row("  /clear", "Clear screen")
    help_table.add_row("  /history", "Show message history")
    
    help_table.add_row("", "")
    help_table.add_row(
        "[bold cyan]Configuration[/bold cyan]",
        ""
    )
    help_table.add_row("  /provider <name>", "Switch AI provider")
    help_table.add_row("  /model <name>", "Switch model")
    help_table.add_row("  /summarizer", "Configure code summarizer")
    help_table.add_row("  /compact", "Toggle compact mode")
    
    help_table.add_row("", "")
    help_table.add_row(
        "[bold cyan]Code Tools[/bold cyan]",
        ""
    )
    help_table.add_row("  /copy", "Copy last code block")
    help_table.add_row("  /tokens", "Show token usage")
    help_table.add_row("  /cost", "Show estimated cost")
    help_table.add_row("  /context", "Show context window")
    
    help_table.add_row("", "")
    help_table.add_row(
        "[bold cyan]Help[/bold cyan]",
        ""
    )
    help_table.add_row("  /help", "Show this help")
    help_table.add_row("  /models", "List available models")
    help_table.add_row("  /exit", "Exit ORC")
    
    console.print()
    console.print(Panel(
        help_table,
        title="[bold]ORC Commands[/bold]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    console.print("[dim]Tip: Press Escape twice to navigate message history[/dim]")
    console.print()
