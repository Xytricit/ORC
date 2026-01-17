def get_orc_banner():
    """Get the ORC ASCII art banner"""
    banner = """[green]
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║     ██████╗ ██████╗  ██████╗                  ║
    ║    ██╔═══██╗██╔══██╗██╔════╝                  ║
    ║    ██║   ██║██████╔╝██║                       ║
    ║    ██║   ██║██╔══██╗██║                       ║
    ║    ╚██████╔╝██║  ██║╚██████╗                  ║
    ║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝                  ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝[/green]
    [bold]Optimization & Refactoring Catalyst[/bold] [dim]v2.0[/dim]
    [dim]AI-Powered Codebase Intelligence Platform[/dim]
"""
    return banner


def get_orc_banner_plain():
    """Get the ORC ASCII art banner without Rich markup"""
    banner = """
     ██████╗ ██████╗  ██████╗
    ██╔═══██╗██╔══██╗██╔════╝
    ██║   ██║██████╔╝██║     
    ██║   ██║██╔══██╗██║     
    ╚██████╔╝██║  ██║╚██████╗
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝

    Optimization & Refactoring Catalyst v2.0
"""
    return banner


def print_startup_info(project_name, loc, languages):
    """Get the startup info line"""
    lang_str = ", ".join(languages) if languages else "Unknown"
    return f"""
    [dim]Project:[/dim]    [cyan]{project_name}[/cyan]
    [dim]Lines:[/dim]      [cyan]{loc:,}[/cyan]
    [dim]Languages:[/dim]  [cyan]{lang_str}[/cyan]
    [dim]Status:[/dim]     [green]Ready[/green]

    [dim]Type a message or /help for commands[/dim]
"""


def print_startup_info_plain(project_name, loc, languages):
    """Get the startup info line without Rich markup"""
    lang_str = ", ".join(languages) if languages else "Unknown"
    return f"""
    Indexed: {project_name} | {loc:,} LOC | {lang_str}
    Status: Ready

─────────────────────────────────────────────────────
"""