"""
ORC UI Components - Beautiful, Professional CLI Interface
Inspired by modern CLI design patterns
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED, DOUBLE, HEAVY, SIMPLE
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from typing import List, Dict, Optional
import time

console = Console()


def show_logo():
    """Display ORC ASCII logo"""
    logo = """
    [bold cyan]
     ██████╗ ██████╗  ██████╗
    ██╔═══██╗██╔══██╗██╔════╝
    ██║   ██║██████╔╝██║     
    ██║   ██║██╔══██╗██║     
    ╚██████╔╝██║  ██║╚██████╗
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝
    [/bold cyan]
    """
    console.print(logo)


def show_tagline(version: str, lines: int, languages: int):
    """Display tagline box"""
    tagline = Panel(
        f"[bold]AI-Powered Codebase Intelligence[/bold]\n"
        f"v{version} | {lines:,} lines | {languages} languages",
        box=ROUNDED,
        padding=(0, 3),
        border_style="cyan"
    )
    console.print(tagline)


def show_status_bar(provider: str, model: str, context: str, status: str):
    """Display status bar"""
    status_text = (
        f"[cyan]●[/cyan] Connected: {provider} ({model})    "
        f"[cyan]●[/cyan] Context: {context}    "
        f"[green]●[/green] Status: {status}"
    )
    status_panel = Panel(
        status_text,
        box=SIMPLE,
        padding=(0, 2),
        border_style="dim"
    )
    console.print(status_panel)


def show_help_hint():
    """Display help hint"""
    console.print("\n[dim]Type /help for commands or /exit to quit[/dim]\n")
    console.print("─" * 70)


def show_analysis_steps(steps: List[str]):
    """Show multi-step analysis with spinners"""
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for step in steps:
            task = progress.add_task(f"[cyan]{step}[/cyan]", total=None)
            time.sleep(0.6)  # Simulate work
            progress.update(task, completed=True)
            progress.remove_task(task)
            console.print(f"[green]✓[/green] {step}")


def show_results_table(results: Dict[str, tuple]):
    """Display analysis results in a table
    
    Args:
        results: Dict of {metric: (value, status)}
    """
    console.print("\n" + "─" * 70)
    console.print("\n  [bold]ANALYSIS RESULTS[/bold]\n")
    
    table = Table(
        show_header=True,
        header_style="bold",
        border_style="dim",
        box=ROUNDED,
        padding=(0, 2)
    )
    
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="white", width=20)
    table.add_column("Status", style="green", width=25)
    
    for metric, (value, status) in results.items():
        # Add status icon
        if "Excellent" in status or "Good" in status or "Clean" in status:
            status_display = f"[green]✓[/green] {status}"
        elif "Outdated" in status or "Medium" in status:
            status_display = f"[yellow]●[/yellow] {status}"
        else:
            status_display = f"[cyan]●[/cyan] {status}"
        
        table.add_row(metric, value, status_display)
    
    console.print(table)
    console.print("\n" + "─" * 70 + "\n")


def show_insights(insights: List[str]):
    """Display key insights"""
    console.print("  [bold]KEY INSIGHTS[/bold]\n")
    
    for insight in insights:
        console.print(f"  [cyan]●[/cyan] {insight}")
    
    console.print("\n" + "─" * 70 + "\n")


def show_recommendations(recommendations: List[Dict[str, str]]):
    """Display actionable recommendations
    
    Args:
        recommendations: List of {title, command, description}
    """
    content = "[bold]RECOMMENDED ACTIONS[/bold]\n\n"
    
    for idx, rec in enumerate(recommendations, 1):
        content += f"  [cyan]{idx}.[/cyan] {rec['title']}\n"
        content += f"     [dim]{rec['description']}[/dim]\n"
        if rec.get('command'):
            content += f"     [yellow]{rec['command']}[/yellow]\n"
        content += "\n"
    
    panel = Panel(
        content.rstrip(),
        title="[bold]Next Steps[/bold]",
        title_align="center",
        box=ROUNDED,
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()


def show_quick_actions():
    """Display quick action buttons"""
    actions = [
        ("/analyze", "Deep codebase analysis"),
        ("/search", "Find code patterns"),
        ("/deps", "Check dependencies"),
        ("/quality", "Code quality audit"),
        ("/help", "View all commands")
    ]
    
    content = "[bold]QUICK ACTIONS[/bold]\n\n"
    for cmd, desc in actions:
        content += f"  [cyan]{cmd:15}[/cyan] {desc}\n"
    
    panel = Panel(
        content.rstrip(),
        title="[bold]Get Started[/bold]",
        title_align="center",
        box=SIMPLE,
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()


def show_commands_table():
    """Display available commands in a clean table"""
    console.print("\n" + "─" * 70)
    console.print("\n  [bold]AVAILABLE COMMANDS[/bold]\n")
    console.print("─" * 70 + "\n")
    
    commands = [
        ("/analyze", "Run complete codebase analysis"),
        ("/search <query>", "Semantic code search across files"),
        ("/explain <file>", "Get detailed AI explanation of file"),
        ("/refactor <file>", "Receive smart refactoring suggestions"),
        ("/docs <file>", "Auto-generate comprehensive docs"),
        ("/test <file>", "Generate unit tests for code"),
        ("/deps", "Analyze dependencies and security"),
        ("/quality", "Run code quality checks"),
        ("/providers", "Switch AI provider (Groq/OpenAI/Claude)"),
        ("/settings", "Configure ORC preferences"),
        ("/history", "View command history"),
        ("/clear", "Clear the terminal screen"),
        ("/exit", "Exit ORC")
    ]
    
    for cmd, desc in commands:
        console.print(f"  [cyan]{cmd:24}[/cyan]  {desc}")
    
    console.print("\n" + "─" * 70 + "\n")


def show_error(title: str, message: str, suggestions: Optional[List[str]] = None):
    """Display error message"""
    content = f"[bold red]ERROR[/bold red]\n\n{message}\n"
    
    if suggestions:
        content += "\n[bold]SUGGESTIONS:[/bold]\n"
        for suggestion in suggestions:
            content += f"  [cyan]●[/cyan] {suggestion}\n"
    
    panel = Panel(
        content.rstrip(),
        title=f"[bold red]✗[/bold red] {title}",
        title_align="center",
        box=DOUBLE,
        border_style="red",
        padding=(1, 2)
    )
    
    console.print("\n" + "─" * 70 + "\n")
    console.print(panel)
    console.print("\n" + "─" * 70 + "\n")


def show_success(message: str, title: str = "Success"):
    """Display success message"""
    panel = Panel(
        f"[green]{message}[/green]",
        title=f"[bold green]✓[/bold green] {title}",
        title_align="center",
        box=ROUNDED,
        border_style="green",
        padding=(0, 2)
    )
    
    console.print("\n" + panel)
    console.print()


def show_thinking_step(step: str):
    """Show what AI is currently thinking"""
    console.print(f"  [dim]│[/dim]  [cyan]💭[/cyan] [dim]{step}[/dim]")


def show_tool_execution(tool_name: str, status: str = "running", args: Optional[Dict] = None, summary: Optional[str] = None):
    """Show tool execution with beautiful formatting"""
    # Format tool name
    tool_display = tool_name.replace("_", " ").title()
    
    if status == "running":
        # Show what the tool is doing
        arg_display = ""
        if args:
            key_args = []
            if 'pattern' in args:
                key_args.append(f"'{args['pattern']}'")
            elif 'file_path' in args:
                from pathlib import Path
                key_args.append(f"{Path(args['file_path']).name}")
            elif 'limit' in args:
                key_args.append(f"limit={args['limit']}")
            
            if key_args:
                arg_display = f" [dim]({', '.join(key_args)})[/dim]"
        
        console.print(f"  [dim]│[/dim]  [cyan]⚙[/cyan] [cyan]{tool_display}[/cyan]{arg_display}")
    
    elif status == "done":
        console.print(f"  [dim]│[/dim]  [green]✓[/green] [green]{tool_display}[/green] [dim]complete[/dim]")
        if summary:
            console.print(f"  [dim]│[/dim]    [dim]{summary}[/dim]")
    
    elif status == "error":
        console.print(f"  [dim]│[/dim]  [red]✗[/red] [red]{tool_display}[/red] [dim]failed[/dim]")


def show_ai_plan(plan: str):
    """Show AI's execution plan"""
    console.print(f"  [dim]│[/dim]  [cyan]💭[/cyan] [dim]Plan: {plan}[/dim]")


def show_section_header(title: str, iteration: Optional[tuple] = None):
    """Show section header with optional iteration counter"""
    if iteration:
        current, total = iteration
        title_text = f"{title} (Iteration {current}/{total})"
    else:
        title_text = title
    
    console.print(f"  [bold cyan]┌─ {title_text}[/bold cyan]")


def show_section_footer(status: str = "Complete"):
    """Show section footer"""
    if status == "Complete":
        console.print(f"  [bold cyan]└─[/bold cyan] [green]✓[/green] [green]{status}[/green]")
    elif status == "Ready":
        console.print(f"  [bold cyan]└─[/bold cyan] [green]✓[/green] [green]{status}[/green]")
    else:
        console.print(f"  [bold cyan]└─[/bold cyan] [cyan]{status}[/cyan]")


def show_task_list(tasks: List[Dict[str, str]]):
    """Show AI's task list with progress"""
    console.print()
    console.print("  [bold cyan]┌─ Analysis Plan[/bold cyan]")
    
    for idx, task in enumerate(tasks, 1):
        status = task.get("status", "pending")
        name = task.get("name", "Task")
        
        if status == "done":
            console.print(f"  [dim]│[/dim]  [green]✓[/green] [strike dim]{idx}. {name}[/strike dim]")
        elif status == "running":
            console.print(f"  [dim]│[/dim]  [cyan]▶[/cyan] [bold white]{idx}. {name}[/bold white]")
        else:
            console.print(f"  [dim]│[/dim]  [dim]◯[/dim] [dim]{idx}. {name}[/dim]")
    
    console.print("  [bold cyan]└─[/bold cyan]")


# Legacy compatibility functions
def show_tool_log(tool_name: str, status: str = "running", args: Optional[Dict] = None):
    """Legacy function - redirects to show_tool_execution"""
    show_tool_execution(tool_name, status, args)


def show_ai_todo(tasks: List[Dict]):
    """Legacy function - redirects to show_task_list"""
    show_task_list(tasks)
