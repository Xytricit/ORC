"""
Professional CLI Output Style System
Generic, phase-based output structure that prevents AI overfitting
"""

from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

console = Console()


# ============================================================================
# SYMBOL WHITELIST (STRICT)
# ============================================================================
SYMBOLS = {
    "phase": "▸",      # Phase indicator
    "success": "+",    # Success indicator
    "warning": "!",    # Warning indicator
    "error": "×",      # Error indicator
    "item": "•",       # List item
}


# ============================================================================
# COLOR ROLES (semantic, not prescriptive)
# ============================================================================
COLORS = {
    "accent": "cyan",       # Primary accent color
    "success": "green",     # Success states
    "warning": "yellow",    # Warning states
    "error": "red",         # Error states
    "dim": "bright_black",  # Secondary details
    "normal": "white",      # Default text
}


# ============================================================================
# PHASE-BASED OUTPUT SYSTEM
# ============================================================================

class CLIOutput:
    """
    Phase-based CLI output system
    Prevents wall-of-text syndrome with clear visual hierarchy
    """
    
    def __init__(self, use_color: bool = True):
        """
        Initialize CLI output system
        
        Args:
            use_color: Whether to use colors (falls back to symbols if False)
        """
        self.use_color = use_color
        self.console = Console()
    
    def command_start(self, command_name: str, description: Optional[str] = None):
        """
        Display command invocation
        
        Args:
            command_name: Name of the command
            description: Optional description
        """
        if self.use_color:
            self.console.print(f"\n[{COLORS['accent']}]{command_name}[/{COLORS['accent']}]", end="")
        else:
            self.console.print(f"\n{command_name}", end="")
        
        if description:
            self.console.print(f" {SYMBOLS['phase']} {description}")
        else:
            self.console.print()
    
    def phase(self, phase_name: str, context: Optional[List[str]] = None):
        """
        Display a phase with optional context
        
        Args:
            phase_name: Name of the phase/action
            context: List of context details (indented)
        """
        self.console.print()  # One blank line between phases
        
        if self.use_color:
            self.console.print(f" [{COLORS['normal']}]{SYMBOLS['phase']} {phase_name}[/{COLORS['normal']}]")
        else:
            self.console.print(f" {SYMBOLS['phase']} {phase_name}")
        
        if context:
            for detail in context:
                if self.use_color:
                    self.console.print(f"   [{COLORS['dim']}]{detail}[/{COLORS['dim']}]")
                else:
                    self.console.print(f"   {detail}")
    
    def result(self, status: str, message: str, items: Optional[List[str]] = None):
        """
        Display phase result
        
        Args:
            status: 'success', 'warning', or 'error'
            message: Result message
            items: Optional list of items/paths with IDs
        """
        symbol = SYMBOLS.get(status, SYMBOLS["item"])
        color = COLORS.get(status, COLORS["normal"])
        
        if self.use_color:
            self.console.print(f" [{color}]{symbol} {message}[/{color}]")
        else:
            status_label = f"[{status.upper()}]"
            self.console.print(f" {status_label} {message}")
        
        if items:
            for idx, item in enumerate(items, 1):
                if self.use_color:
                    self.console.print(f"   [{COLORS['dim']}][{idx:02d}][/{COLORS['dim']}] {item}")
                else:
                    self.console.print(f"   [{idx:02d}] {item}")
    
    def final_status(self, status: str, message: str):
        """
        Display final command status
        
        Args:
            status: 'success', 'warning', or 'error'
            message: Final status message
        """
        symbol = SYMBOLS.get(status, SYMBOLS["item"])
        color = COLORS.get(status, COLORS["normal"])
        
        self.console.print()  # Blank line before final status
        
        if self.use_color:
            self.console.print(f" [{color}]{symbol} {message}[/{color}]")
        else:
            status_label = f"[{status.upper()}]"
            self.console.print(f" {status_label} {message}")
        
        self.console.print()  # Blank line after
    
    def table(self, title: str, headers: List[str], rows: List[List[str]]):
        """
        Display a clean table
        
        Args:
            title: Table title
            headers: Column headers
            rows: Table rows
        """
        table = Table(title=title, show_header=True, header_style=f"bold {COLORS['accent']}")
        
        for header in headers:
            table.add_column(header)
        
        for row in rows:
            table.add_row(*row)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def suggestion(self, message: str):
        """
        Display a suggestion/hint
        
        Args:
            message: Suggestion text
        """
        if self.use_color:
            self.console.print(f" [{COLORS['dim']}]{SYMBOLS['phase']} {message}[/{COLORS['dim']}]")
        else:
            self.console.print(f" {SYMBOLS['phase']} {message}")


# ============================================================================
# STARTUP BANNER (clean, professional)
# ============================================================================

def display_startup_banner(version: str = "2.0"):
    """
    Display clean startup banner
    
    Args:
        version: Version string
    """
    console.print()
    console.print(f"[{COLORS['accent']}]ORC[/{COLORS['accent']}] v{version} {SYMBOLS['phase']} Optimization & Refactoring Catalyst")
    console.print(f"[{COLORS['dim']}]Type /help for commands or ask something directly[/{COLORS['dim']}]")
    console.print()
    
    # Getting started (compact, scannable)
    console.print(f"[{COLORS['dim']}]Getting started:[/{COLORS['dim']}]")
    console.print(f"[{COLORS['dim']}]1. Analyse a folder or module: [/{COLORS['dim']}][{COLORS['normal']}]analyse src/utils/[/{COLORS['normal']}]")
    console.print(f"[{COLORS['dim']}]2. Check unused code safely: [/{COLORS['dim']}][{COLORS['normal']}]remove unused code[/{COLORS['normal']}]")
    console.print(f"[{COLORS['dim']}]3. Explore database or API layers: [/{COLORS['dim']}][{COLORS['normal']}]review database schema[/{COLORS['normal']}]")
    console.print(f"[{COLORS['dim']}]4. Ask for insights: [/{COLORS['dim']}][{COLORS['normal']}]Which functions are unused?[/{COLORS['normal']}]")
    console.print()


# ============================================================================
# SESSION STATS DISPLAY (compact table)
# ============================================================================

def display_session_stats(model: str, tokens: int, time_active: str, 
                         files: int, lines: int, languages: List[str]):
    """
    Display session and project stats in compact format
    
    Args:
        model: AI model being used
        tokens: Tokens used
        time_active: Time active string
        files: Number of files
        lines: Number of lines
        languages: List of languages
    """
    output = CLIOutput()
    
    output.phase("Session Stats", [
        f"Model: {model}",
        f"Tokens used: {tokens:,}",
        f"Time active: {time_active}"
    ])
    
    output.phase("Project Stats", [
        f"Files: {files:,}",
        f"Lines: {lines:,}",
        f"Languages: {', '.join(languages)}"
    ])
    
    console.print()


# ============================================================================
# AI RESPONSE FORMATTING (natural + structured)
# ============================================================================

def display_ai_analysis(query: str, scanning_target: str, 
                       results: List[Dict[str, str]], 
                       suggestions: Optional[List[str]] = None):
    """
    Display AI analysis results in phase-based format
    
    Args:
        query: User's query
        scanning_target: What's being scanned
        results: List of result dicts with 'type' and 'name' keys
        suggestions: Optional list of suggestions
    """
    output = CLIOutput()
    
    # Phase 1: Scanning
    output.phase(f"Scanning {scanning_target}...", [
        "Parsing files",
        "Mapping dependencies"
    ])
    
    # Phase 2: Results
    if results:
        result_items = [f"{r['type']}: {r['name']}" for r in results]
        output.result("warning", f"{len(results)} items detected:", result_items)
    else:
        output.result("success", "No issues found")
    
    # Phase 3: Suggestions
    if suggestions:
        console.print()
        for suggestion in suggestions:
            output.suggestion(suggestion)
    
    output.final_status("success", "Analysis complete")


# ============================================================================
# CONFIRMATION PROMPT (destructive actions)
# ============================================================================

def confirm_destructive_action(action: str, items: List[str]) -> bool:
    """
    Prompt for confirmation before destructive action
    
    Args:
        action: Action description
        items: List of items to be affected
    
    Returns:
        True if confirmed, False otherwise
    """
    console.print()
    console.print(f"[{COLORS['warning']}]{SYMBOLS['warning']} {action}:[/{COLORS['warning']}]")
    
    for idx, item in enumerate(items, 1):
        console.print(f"   [{COLORS['dim']}][{idx:02d}][/{COLORS['dim']}] {item}")
    
    console.print()
    console.print(f"[{COLORS['dim']}]Type 'yes' to confirm or anything else to cancel[/{COLORS['dim']}]")
    
    response = console.input(f"[{COLORS['accent']}] [/{COLORS['accent']}] ").strip().lower()
    
    return response == "yes"
