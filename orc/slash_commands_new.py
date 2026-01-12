"""
New slash command handlers for session management
To be integrated into cli_loop.py
"""

def handle_save_command(session, args):
    """Handle /save command"""
    from rich.console import Console
    console = Console()
    
    name = args if args else f"session_{session.project_name}"
    
    # Get metadata
    metadata = {
        "project": session.project_name,
        "message_count": len(session.conversation_history),
        "tools_used": session.tools_used_this_session,
        "cost": session.token_tracker.get_stats()["total_cost"]
    }
    
    # Save session
    success = session.session_manager.save_session(name, session.conversation_history, metadata)
    
    if success:
        console.print(f"\n[green]+ Saved conversation as '{name}'[/green]")
        console.print(f"[dim]  Messages: {len(session.conversation_history)} | Location: .orc/sessions/{name}.json[/dim]\n")
    else:
        console.print(f"\n[red]Failed to save session[/red]\n")


def handle_load_command(session, args):
    """Handle /load command"""
    from rich.console import Console
    console = Console()
    
    if not args:
        console.print("\n[yellow]Usage: /load <session_name>[/yellow]\n")
        return
    
    # Load session
    session_data = session.session_manager.load_session(args)
    
    if session_data:
        session.conversation_history = session_data.get("conversation", [])
        console.print(f"\n[green]+ Loaded conversation '{args}'[/green]")
        console.print(f"[dim]  Messages: {len(session.conversation_history)} | Saved: {session_data.get('saved_at', 'Unknown')}[/dim]\n")
    else:
        console.print(f"\n[red]Session '{args}' not found[/red]")
        console.print("[dim]Use /sessions to list available sessions[/dim]\n")


def handle_sessions_command(session):
    """Handle /sessions command"""
    from rich.console import Console
    from rich.table import Table
    console = Console()
    
    sessions = session.session_manager.list_sessions()
    
    if not sessions:
        console.print("\n[dim]No saved sessions found[/dim]\n")
        return
    
    table = Table(title="Saved Sessions", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Saved", style="dim")
    table.add_column("Messages", justify="right")
    table.add_column("Cost", justify="right")
    
    for sess in sessions:
        name = sess["name"]
        saved_at = sess["saved_at"].split("T")[0] if "T" in sess["saved_at"] else sess["saved_at"]
        msg_count = str(sess["message_count"])
        cost = f"${sess.get('metadata', {}).get('cost', 0):.4f}"
        
        table.add_row(name, saved_at, msg_count, cost)
    
    console.print()
    console.print(table)
    console.print(f"\n[dim]Load with: /load <name>[/dim]\n")


def handle_export_command(session, args):
    """Handle /export command"""
    from rich.console import Console
    from pathlib import Path
    console = Console()
    
    format_type = args.lower() if args else "md"
    
    if format_type not in ["md", "json", "markdown"]:
        console.print("\n[yellow]Usage: /export [md|json][/yellow]")
        console.print("[dim]Default: md[/dim]\n")
        return
    
    # Normalize format
    if format_type == "markdown":
        format_type = "md"
    
    # Generate filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"orc_export_{timestamp}.{format_type}"
    output_file = Path(filename)
    
    # Export
    if format_type == "md":
        result = session.session_manager.export_to_markdown(session.conversation_history, output_file)
    else:
        metadata = {
            "project": session.project_name,
            "tools_used": session.tools_used_this_session,
            "stats": session.token_tracker.get_stats()
        }
        result = session.session_manager.export_to_json(session.conversation_history, output_file, metadata)
    
    if result:
        console.print(f"\n[green]+ Exported conversation to {filename}[/green]")
        console.print(f"[dim]  Messages: {len(session.conversation_history)} | Format: {format_type.upper()}[/dim]\n")
    else:
        console.print(f"\n[red]Failed to export conversation[/red]\n")


def handle_copy_command(session):
    """Handle /copy command"""
    from rich.console import Console
    console = Console()
    
    code_block = session.session_manager.get_last_code_block()
    
    if not code_block:
        console.print("\n[yellow]No code blocks found in recent messages[/yellow]\n")
        return
    
    # Try to copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(code_block)
        console.print("\n[green]+ Copied last code block to clipboard[/green]")
        console.print(f"[dim]  {len(code_block)} characters[/dim]\n")
    except ImportError:
        # Fallback: show the code
        console.print("\n[yellow]Clipboard not available (install pyperclip)[/yellow]")
        console.print("[dim]Here's the code:[/dim]\n")
        from orc.ui_components import display_code_block
        display_code_block(code_block, "python")
        console.print()


def handle_tokens_command(session):
    """Handle /tokens command"""
    from rich.console import Console
    from rich.table import Table
    console = Console()
    
    stats = session.token_tracker.get_stats()
    
    table = Table(title="Token Usage", show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Input Tokens", f"{stats['total_input_tokens']:,}")
    table.add_row("Output Tokens", f"{stats['total_output_tokens']:,}")
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    table.add_row("Requests", str(stats['request_count']))
    table.add_row("Avg per Request", f"{stats['avg_tokens_per_request']:.0f}")
    
    console.print()
    console.print(table)
    console.print()


def handle_cost_command(session):
    """Handle /cost command"""
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    stats = session.token_tracker.get_stats()
    cost = stats['total_cost']
    
    if cost == 0:
        message = "[green]$0.00[/green]\n\n[dim]You're using a free provider (Groq/Ollama)[/dim]"
    else:
        message = f"[cyan]${cost:.4f}[/cyan]\n\n"
        message += f"[dim]Input: ${(stats['total_input_tokens'] / 1_000_000) * 0.5:.4f} | "
        message += f"Output: ${(stats['total_output_tokens'] / 1_000_000) * 1.5:.4f}[/dim]"
    
    panel = Panel(
        message,
        title="[bold]Session Cost[/bold]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print()
    console.print(panel)
    console.print()


def handle_context_command(session):
    """Handle /context command"""
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    
    # Get current model
    model = session.ai_client.get_status().split(": ")[1] if ":" in session.ai_client.get_status() else "unknown"
    
    # Estimate context usage
    context_info = session.token_tracker.estimate_context_usage(session.conversation_history, model)
    
    tokens_used = context_info['tokens_used']
    tokens_total = context_info['tokens_total']
    percentage = context_info['percentage']
    remaining = context_info['remaining']
    
    # Build progress bar
    filled = int(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    # Determine color
    if percentage > 90:
        color = "red"
        status = "Critical"
    elif percentage > 75:
        color = "yellow"
        status = "High"
    elif percentage > 50:
        color = "cyan"
        status = "Moderate"
    else:
        color = "green"
        status = "Good"
    
    message = f"[{color}]{bar}[/{color}] [{color}]{percentage:.1f}%[/{color}]\n\n"
    message += f"[dim]Used: {tokens_used:,} / {tokens_total:,} tokens[/dim]\n"
    message += f"[dim]Remaining: {remaining:,} tokens[/dim]\n"
    message += f"[dim]Status: [{color}]{status}[/{color}][/dim]"
    
    panel = Panel(
        message,
        title=f"[bold]Context Window ({model})[/bold]",
        border_style=color,
        padding=(1, 2)
    )
    
    console.print()
    console.print(panel)
    console.print()
