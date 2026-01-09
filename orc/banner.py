def get_orc_banner():
    """Get the ORC ASCII art banner in green"""
    banner = """
[green]
     ██████╗ ██████╗  ██████╗
    ██╔═══██╗██╔══██╗██╔════╝
    ██║   ██║██████╔╝██║     
    ██║   ██║██╔══██╗██║     
    ╚██████╔╝██║  ██║╚██████╗
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝
[/green]
[dim]    Optimization & Refactoring Catalyst v2.0[/dim]
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
[dim]    Indexed:[/dim] [cyan]{project_name}[/cyan] [dim]|[/dim] [cyan]{loc:,} LOC[/cyan] [dim]|[/dim] [cyan]{lang_str}[/cyan]
[dim]    Status:[/dim] [green]Ready[/green]

[dim]─────────────────────────────────────────────────────[/dim]
"""


def print_startup_info_plain(project_name, loc, languages):
    """Get the startup info line without Rich markup"""
    lang_str = ", ".join(languages) if languages else "Unknown"
    return f"""
    Indexed: {project_name} | {loc:,} LOC | {lang_str}
    Status: Ready

─────────────────────────────────────────────────────
"""