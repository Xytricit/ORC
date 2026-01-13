"""
ORC CLI - Main command-line interface
"""
import click
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from orc.cli_auth import get_api_config

console = Console()

# Import version from package
try:
    from orc import __version__
except ImportError:
    __version__ = "1.0.0"


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    """ORC - Optimization & Refactoring Catalyst
    
    Codebase intelligence and analysis tool.
    """
    # If no subcommand, launch interactive ORC
    if ctx.invoked_subcommand is None:
        # Launch interactive ORC (no auth required)
        from orc.cli_loop import run_cli_session
        run_cli_session()


@main.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', default='.orc/index.db', help='Output database path')
@click.option('--force', is_flag=True, help='Force re-indexing')
def index(path, output, force):
    """Index a codebase for analysis.
    
    Creates a searchable database of functions, classes, and dependencies.
    """
    # No auth required for basic indexing
    from orc.core.parallel_indexer import index_directory_parallel
    from orc.storage.graph_db import GraphStorage
    
    path = Path(path).resolve()
    output = Path(output)
    
    # Create .orc directory if needed
    output.parent.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[cyan]Indexing:[/cyan] {path}")
    console.print(f"[cyan]Database:[/cyan] {output}")
    
    # Check if database exists and not forcing
    if output.exists() and not force:
        console.print("\n[yellow]Database already exists.[/yellow]")
        console.print("Use --force to re-index, or use 'orc stats' to view existing index.")
        return
    
    console.print("\n[yellow]Indexing files...[/yellow]")
    
    try:
        # Use parallel indexer (no progress bar, just show message)
        result = index_directory_parallel(path)
        
        # Save to database
        console.print("[yellow]Saving to database...[/yellow]")
        db = GraphStorage(output)
        
        # Store files using upsert_file_index
        for file_path, file_info in result.get('files', {}).items():
            db.upsert_file_index(
                path=str(file_path),
                language=file_info.get('language', 'unknown'),
                framework=file_info.get('framework', ''),
                loc=file_info.get('loc', 0),
                last_modified=0.0,  # Will be updated by incremental indexing
                hash_value='',
                metadata=file_info
            )
        
        # Store functions using bulk_upsert_functions
        functions_dict = result.get('functions', {})
        if functions_dict:
            db.bulk_upsert_functions(functions_dict)
        
        # Store classes using bulk_upsert_classes
        classes_dict = result.get('classes', {})
        if classes_dict:
            db.bulk_upsert_classes(classes_dict)
        
        # Store resolved file dependencies (NEW)
        file_deps_resolved = result.get('file_dependencies_resolved', [])
        if file_deps_resolved:
            console.print("[yellow]Storing file dependencies...[/yellow]")
            db.store_file_dependencies(file_deps_resolved)
        
        # Store resolved function calls (NEW)
        function_calls_resolved = result.get('function_calls_resolved', [])
        if function_calls_resolved:
            console.print("[yellow]Storing function calls...[/yellow]")
            db.store_resolved_function_calls(function_calls_resolved)
        
        # Store entry points (NEW)
        entry_points = result.get('entry_points', [])
        if entry_points:
            console.print("[yellow]Storing entry points...[/yellow]")
            db.store_entry_points(entry_points)
        
        # Store AI summaries (NEW)
        summaries = result.get('summaries', {})
        if summaries:
            console.print("[yellow]Storing AI summaries...[/yellow]")
            for target_id, summary in summaries.items():
                # Determine target type from ID
                if target_id.startswith('file:'):
                    target_type = 'file'
                    target_id = target_id[5:]  # Remove 'file:' prefix
                elif '::' in target_id:
                    # Could be function or class
                    if any(c in target_id for c in ['__init__', 'def ', 'async def']):
                        target_type = 'function'
                    else:
                        target_type = 'class'
                else:
                    target_type = 'function'
                
                db.store_summary(target_type, target_id, summary)
        
        console.print("\n[bold green]+ Indexing complete![/bold green]")
        console.print(f"  Files: {len(result.get('files', {}))}")
        console.print(f"  Functions: {len(result.get('functions', {}))}")
        console.print(f"  Classes: {len(result.get('classes', {}))}")
        console.print(f"  File Dependencies: {len(result.get('file_dependencies_resolved', []))}")
        console.print(f"  Function Calls: {len(result.get('function_calls_resolved', []))}")
        console.print(f"  Entry Points: {len(result.get('entry_points', []))}")
        
        circular = result.get('circular_dependencies', [])
        if circular:
            console.print(f"  [yellow]Circular Dependencies: {len(circular)}[/yellow]")
        
        summaries = result.get('summaries', {})
        if summaries:
            console.print(f"  AI Summaries: {len(summaries)}")
        
        console.print(f"\nRun 'orc stats' to see detailed statistics.")
        console.print("Run 'orc' to chat with AI about your code!")
        
    except Exception as e:
        console.print(f"[red]Error during indexing:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def stats(db, json_output):
    """Show codebase statistics.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc report[/cyan] for richer statistics and visualizations.
    
    Displays file counts, function counts, language breakdown, and complexity metrics.
    """
    from orc.ai_tools import ORCTools
    from rich.table import Table
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc scan[/cyan] first to create the database.")
        sys.exit(1)
    
    tools = ORCTools(db_path=str(db_path))
    result = tools.get_codebase_stats()
    
    if 'error' in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)
    
    if json_output:
        print(json.dumps(result, indent=2))
        return
    
    # Pretty print with better formatting
    console.print("\n[bold cyan]Codebase Statistics[/bold cyan]")
    console.print(f"  Files: [yellow]{result.get('total_files', 0)}[/yellow]")
    console.print(f"  Functions: [yellow]{result.get('total_functions', 0)}[/yellow]")
    console.print(f"  Classes: [yellow]{result.get('total_classes', 0)}[/yellow]")
    console.print(f"  Average Complexity: [yellow]{result.get('average_complexity', 0):.2f}[/yellow]")
    console.print(f"  Max Complexity: [yellow]{result.get('max_complexity', 0)}[/yellow]")
    
    if result.get('files_by_language'):
        console.print("\n[bold cyan]Files by Language:[/bold cyan]")
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        for lang, count in sorted(result['files_by_language'].items(), key=lambda x: x[1], reverse=True):
            table.add_row(f"[cyan]{lang}[/cyan]", f"[yellow]{count}[/yellow]")
        
        console.print(table)
    
    console.print("\n[dim]Tip: For detailed analysis, run [cyan]orc report[/cyan][/dim]\n")


@main.command()
@click.argument('what', required=True)
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--limit', default=20, help='Maximum results')
@click.option('--min-confidence', default=0.7, type=float, help='Minimum confidence for dead code')
def find(what, db, limit, min_confidence):
    """Smart search for code issues and patterns.
    
    Find various code issues with natural language:
      • dead, unused - Find dead/unused code
      • complex, complexity - Find complex functions
      • large, big - Find large files
      • duplicate, duplicates - Find potential duplicates
      • <pattern> - Search for functions/classes by name
    
    Examples:
      orc find dead              # Find dead code
      orc find complex           # Find complex functions
      orc find large             # Find large files
      orc find auth              # Search for "auth" functions
      orc find UserController    # Find specific class/function
    """
    from orc.ai_tools import ORCTools
    from orc.tools.codebase_mapper import CodebaseMapper
    from rich.panel import Panel
    from rich.table import Table
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc scan[/cyan] first to index your codebase.")
        sys.exit(1)
    
    tools = ORCTools(db_path=str(db_path))
    mapper = CodebaseMapper(db_path)
    
    what_lower = what.lower()
    
    # Dead code detection
    if what_lower in ['dead', 'unused', 'deadcode']:
        console.print(Panel(
            "[bold cyan]Searching for Dead Code[/bold cyan]\n\n"
            f"Confidence threshold: {min_confidence}",
            border_style="cyan"
        ))
        console.print("\n[yellow]Analyzing function usage...[/yellow]\n")
        
        result = tools.get_dead_code(confidence_threshold=min_confidence, limit=limit)
        
        if 'error' in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            sys.exit(1)
        
        summary = result.get('summary', {})
        safe = result.get('safe_to_delete', [])
        review = result.get('review_needed', [])
        
        console.print(f"[dim]Analyzed {summary.get('total_functions_analyzed', 0)} functions[/dim]")
        console.print(f"[dim]Found {summary.get('total_potentially_unused', 0)} potentially unused[/dim]\n")
        
        if safe:
            console.print(Panel(
                f"[bold red]High Confidence ({len(safe)} items)[/bold red]\n"
                "[dim]These are very likely safe to remove[/dim]",
                border_style="red"
            ))
            
            table = Table(show_header=True, box=None)
            table.add_column("Function", style="red")
            table.add_column("File", style="dim")
            table.add_column("Confidence", justify="right", style="yellow")
            
            for item in safe[:limit]:
                table.add_row(
                    f"{item['name']}()",
                    Path(item['file_path']).name,
                    f"{item['confidence']:.0%}"
                )
            
            console.print(table)
            console.print()
        
        if review:
            console.print(Panel(
                f"[bold yellow]Review Needed ({len(review)} items)[/bold yellow]\n"
                "[dim]Manual review recommended[/dim]",
                border_style="yellow"
            ))
            
            for i, item in enumerate(review[:5], 1):
                console.print(f"  {i}. [yellow]{item['name']}()[/yellow]")
                console.print(f"     File: [dim]{Path(item['file_path']).name}[/dim]")
                console.print(f"     Confidence: {item['confidence']:.0%}")
        
        if not safe and not review:
            console.print("[green]+ No dead code found! Your codebase is clean.[/green]\n")
        
        console.print()
        console.print("[dim]Tip: Use [cyan]orc[/cyan] to chat with AI about specific functions[/dim]")
    
    # Complex functions
    elif what_lower in ['complex', 'complexity', 'complicated']:
        console.print(Panel(
            "[bold cyan]Finding Complex Functions[/bold cyan]\n\n"
            "Looking for functions with high cyclomatic complexity",
            border_style="cyan"
        ))
        console.print()
        
        result = tools.get_complexity_report(min_complexity=10, limit=limit)
        
        if 'error' in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            sys.exit(1)
        
        summary = result.get('summary', {})
        high_complexity = result.get('high_complexity_functions', [])
        
        console.print(f"[bold]Summary[/bold]")
        console.print(f"   Total Functions: {summary.get('total_functions', 0)}")
        console.print(f"   Average Complexity: {summary.get('average_complexity', 0):.2f}")
        console.print(f"   Critical (20+): [red]{summary.get('critical_count', 0)}[/red]")
        console.print(f"   High (10-19): [yellow]{summary.get('high_count', 0)}[/yellow]\n")
        
        if high_complexity:
            table = Table(show_header=True, box=None)
            table.add_column("Function", style="red")
            table.add_column("Complexity", justify="right", style="yellow")
            table.add_column("File", style="dim")
            table.add_column("Lines", style="cyan")
            
            for item in high_complexity[:limit]:
                table.add_row(
                    f"{item['name']}()",
                    str(item['complexity']),
                    Path(item['file_path']).name,
                    f"{item['start_line']}-{item['end_line']}"
                )
            
            console.print(table)
            console.print()
            console.print("[dim]Tip: Consider refactoring functions with complexity > 20[/dim]")
        else:
            console.print("[green]+ All functions have acceptable complexity![/green]\n")
    
    # Large files
    elif what_lower in ['large', 'big', 'huge', 'files']:
        console.print(Panel(
            "[bold cyan]Finding Large Files[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        hotspots = mapper.get_hotspots(limit=limit)
        large_files = hotspots.get('large_files', [])
        
        if large_files:
            table = Table(show_header=True, box=None)
            table.add_column("File", style="cyan")
            table.add_column("Lines", justify="right", style="yellow")
            table.add_column("Language", style="dim")
            
            for item in large_files[:limit]:
                table.add_row(
                    Path(item.get('path', '')).name,
                    f"{item.get('loc', 0):,}",
                    item.get('language', 'unknown')
                )
            
            console.print(table)
            console.print()
            console.print("[dim]Tip: Consider splitting files larger than 500 lines[/dim]")
        else:
            console.print("[green]+ All files are reasonably sized![/green]\n")
    
    # Search by pattern (default behavior)
    else:
        console.print(Panel(
            f"[bold cyan]Searching for: '{what}'[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        # Try functions first
        result = tools.query_functions(pattern=what, limit=limit)
        functions = result.get('functions', [])
        
        # Try classes
        class_result = tools.query_classes(pattern=what, limit=limit)
        classes = class_result.get('classes', [])
        
        if functions:
            console.print(f"[bold green]Functions ({len(functions)} found)[/bold green]")
            table = Table(show_header=True, box=None)
            table.add_column("Function", style="green")
            table.add_column("File", style="dim")
            table.add_column("Complexity", justify="right", style="yellow")
            
            for item in functions[:limit]:
                table.add_row(
                    f"{item['name']}()",
                    Path(item['file_path']).name,
                    str(item['complexity'])
                )
            
            console.print(table)
            console.print()
        
        if classes:
            console.print(f"[bold green]Classes ({len(classes)} found)[/bold green]")
            for item in classes[:10]:
                console.print(f"  - [green]{item['name']}[/green]")
                console.print(f"    File: [dim]{Path(item['file_path']).name}[/dim]")
                console.print(f"    Language: [dim]{item['language']}[/dim]")
            console.print()
        
        if not functions and not classes:
            console.print(f"[yellow]No functions or classes found matching:[/yellow] {what}")
            console.print("\n[dim]Try:[/dim]")
            console.print("   [cyan]orc find dead[/cyan] - Find dead code")
            console.print("   [cyan]orc find complex[/cyan] - Find complex functions")
            console.print("   [cyan]orc[/cyan] - Chat with AI to search your code")
            console.print()


@main.command()
@click.argument('pattern')
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--type', 'search_type', type=click.Choice(['functions', 'classes', 'files']), default='functions')
@click.option('--limit', default=20, help='Maximum results')
def query(pattern, db, search_type, limit):
    """Search for functions, classes, or files.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc find <pattern>[/cyan] instead for a better experience.
    
    Examples:
      orc find auth          # Instead of: orc query auth
      orc find User          # Instead of: orc query User --type classes
    """
    console.print("\n[yellow]This command is deprecated.[/yellow]")
    console.print(f"Please use [cyan]orc find {pattern}[/cyan] instead.\n")
    
    # Call find instead
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(find, [pattern, '--db', db, '--limit', str(limit)])


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--limit', default=10, help='Results per category')
def hotspots(db, limit):
    """Find complexity and size hotspots.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc report[/cyan] for a better experience with more insights.
    
    Shows the most complex functions, largest files, and highly coupled modules.
    """
    console.print("\n[yellow]This command is deprecated.[/yellow]")
    console.print("Please use [cyan]orc report[/cyan] for comprehensive hotspot analysis.\n")
    
    # Still provide basic functionality
    from orc.tools.codebase_mapper import CodebaseMapper
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc scan[/cyan] first.")
        sys.exit(1)
    
    mapper = CodebaseMapper(db_path)
    result = mapper.get_hotspots(limit=limit)
    
    # Complexity hotspots
    console.print("[bold red]Complexity Hotspots:[/bold red]")
    for item in result.get('complexity_hotspots', [])[:limit]:
        console.print(f"[yellow]{item.get('name', 'unknown')}()[/yellow]")
        console.print(f"  Complexity: {item.get('complexity', 0)}")
        console.print(f"  File: {Path(item.get('file_path', '')).name}")
    
    # Large files
    console.print("\n[bold yellow]Large Files:[/bold yellow]")
    for item in result.get('large_files', [])[:limit]:
        console.print(f"[cyan]{Path(item.get('path', '')).name}[/cyan]")
        console.print(f"  Lines: {item.get('loc', 0)}")
        console.print(f"  Language: {item.get('language', 'unknown')}")
    
    console.print("\n[dim]Tip: For more insights, run [cyan]orc report[/cyan][/dim]\n")


@main.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', default='.orc/index.db', help='Output database path')
@click.option('--quick', is_flag=True, help='Quick scan (skip detailed analysis)')
def scan(path, output, quick):
    """Smart scan: Index and analyze in one go.
    
    This is the recommended way to get started. It will:
      1. Index your codebase (parse all files)
      2. Run comprehensive analysis
      3. Show you a beautiful report
    
    Example:
      orc scan                  # Scan current directory
      orc scan ./my-project     # Scan specific directory
      orc scan --quick          # Fast scan without deep analysis
    """
    from orc.core.parallel_indexer import index_directory_parallel
    from orc.storage.graph_db import GraphStorage
    from orc.tools.codebase_mapper import CodebaseMapper
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    path = Path(path).resolve()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    console.print(Panel(
        f"[bold cyan]ORC Smart Scan[/bold cyan]\n\n"
        f"Path: [yellow]{path}[/yellow]\n"
        f"Database: [yellow]{output}[/yellow]\n"
        f"Mode: [yellow]{'Quick' if quick else 'Full'}[/yellow]",
        border_style="cyan"
    ))
    
    # Step 1: Index
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Indexing files...", total=None)
        
        result = index_directory_parallel(path)
        
        progress.update(task, description="[cyan]Saving to database...")
        
        db = GraphStorage(output)
        
        # Store files
        for file_path, file_info in result.get('files', {}).items():
            db.upsert_file_index(
                path=str(file_path),
                language=file_info.get('language', 'unknown'),
                framework=file_info.get('framework', ''),
                loc=file_info.get('loc', 0),
                last_modified=0.0,
                hash_value='',
                metadata=file_info
            )
        
        # Store functions
        functions_dict = result.get('functions', {})
        if functions_dict:
            db.bulk_upsert_functions(functions_dict)
        
        # Store classes
        classes_dict = result.get('classes', {})
        if classes_dict:
            db.bulk_upsert_classes(classes_dict)
        
        progress.update(task, description="[green]Indexing complete!")
    
    console.print(f"\n[green]+[/green] Indexed {len(result.get('files', {}))} files")
    console.print(f"[green]+[/green] Found {len(result.get('functions', {}))} functions")
    console.print(f"[green]+[/green] Found {len(result.get('classes', {}))} classes\n")
    
    # Step 2: Analyze (unless quick mode)
    if not quick:
        console.print("[cyan]Running analysis...[/cyan]\n")
        
        mapper = CodebaseMapper(output)
        stats = mapper.get_statistics()
        hotspots = mapper.get_hotspots(limit=5)
        
        # Show quick summary
        console.print(Panel(
            f"[bold green]Scan Complete![/bold green]\n\n"
            f"[cyan]Statistics:[/cyan]\n"
            f"   - Files: {stats.get('total_files', 0)}\n"
            f"   - Functions: {stats.get('total_functions', 0)}\n"
            f"   - Classes: {stats.get('total_classes', 0)}\n"
            f"   - Total LOC: {stats.get('total_loc', 0):,}\n\n"
            f"[yellow]Top Complexity:[/yellow] {stats.get('max_complexity', 0)}\n"
            f"[yellow]Average Complexity:[/yellow] {stats.get('average_complexity', 0):.2f}",
            border_style="green"
        ))
        
        console.print("\n[dim]Tip: Run [cyan]orc report[/cyan] for detailed analysis[/dim]")
        console.print("[dim]Tip: Run [cyan]orc find dead[/cyan] to find unused code[/dim]")
        console.print("[dim]Tip: Run [cyan]orc[/cyan] to chat with AI about your code[/dim]\n")
    else:
        console.print(Panel(
            "[bold green]Quick Scan Complete![/bold green]\n\n"
            f"+ Indexed {len(result.get('files', {}))} files\n"
            "+ Database ready for analysis\n\n"
            "[dim]Run [cyan]orc report[/cyan] for detailed analysis[/dim]",
            border_style="green"
        ))


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--format', 'output_format', type=click.Choice(['full', 'summary', 'json']), default='full', help='Report format')
@click.option('--save', type=click.Path(), help='Save report to file')
def report(db, output_format, save):
    """Generate a beautiful comprehensive report.
    
    Shows complete analysis including:
      • Codebase statistics and metrics
      • Complexity hotspots
      • Large files and coupling issues
      • Language distribution
      • Health score
    
    Examples:
      orc report                    # Full interactive report
      orc report --format summary   # Quick summary
      orc report --save report.txt  # Save to file
    """
    from orc.tools.codebase_mapper import CodebaseMapper
    from orc.ai_tools import ORCTools
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.table import Table
    import json as json_lib
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc scan[/cyan] first to index your codebase.")
        sys.exit(1)
    
    mapper = CodebaseMapper(db_path)
    tools = ORCTools(db_path=str(db_path))
    
    # Gather data
    stats = mapper.get_statistics()
    hotspots = mapper.get_hotspots(limit=10)
    codebase_stats = tools.get_codebase_stats()
    
    # JSON output
    if output_format == 'json':
        report_data = {
            'statistics': stats,
            'hotspots': hotspots,
            'codebase': codebase_stats
        }
        output_text = json_lib.dumps(report_data, indent=2)
        
        if save:
            Path(save).write_text(output_text)
            console.print(f"[green]+[/green] Report saved to {save}")
        else:
            print(output_text)
        return
    
    # Calculate health score
    avg_complexity = stats.get('average_complexity', 0)
    max_complexity = stats.get('max_complexity', 0)
    total_functions = stats.get('total_functions', 1)
    
    health_score = 100
    if avg_complexity > 10:
        health_score -= (avg_complexity - 10) * 2
    if max_complexity > 20:
        health_score -= (max_complexity - 20)
    health_score = max(0, min(100, health_score))
    
    health_color = "green" if health_score >= 80 else "yellow" if health_score >= 60 else "red"
    
    # Header
    console.print("\n")
    console.print(Panel(
        f"[bold cyan]ORC Codebase Report[/bold cyan]\n\n"
        f"Health Score: [{health_color}]{health_score:.0f}/100[/{health_color}]",
        border_style="cyan"
    ))
    
    # Summary mode - just show key metrics
    if output_format == 'summary':
        console.print(f"\n[bold]Quick Summary[/bold]")
        console.print(f"   Files: {stats.get('total_files', 0)}")
        console.print(f"   Functions: {total_functions}")
        console.print(f"   Avg Complexity: {avg_complexity:.2f}")
        console.print(f"   Max Complexity: {max_complexity}")
        console.print()
        return
    
    # Full report
    # Statistics panel
    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_row("Total Files", f"[cyan]{stats.get('total_files', 0)}[/cyan]")
    stats_table.add_row("Functions", f"[cyan]{total_functions}[/cyan]")
    stats_table.add_row("Classes", f"[cyan]{stats.get('total_classes', 0)}[/cyan]")
    stats_table.add_row("Total LOC", f"[cyan]{stats.get('total_loc', 0):,}[/cyan]")
    stats_table.add_row("Avg Complexity", f"[yellow]{avg_complexity:.2f}[/yellow]")
    stats_table.add_row("Max Complexity", f"[red]{max_complexity}[/red]")
    
    console.print("\n")
    console.print(Panel(stats_table, title="[bold]Statistics[/bold]", border_style="blue"))
    
    # Language distribution
    if codebase_stats.get('files_by_language'):
        lang_table = Table(show_header=True, box=None)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Files", style="yellow", justify="right")
        
        for lang, count in sorted(
            codebase_stats['files_by_language'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:
            lang_table.add_row(lang, str(count))
        
        console.print("\n")
        console.print(Panel(lang_table, title="[bold]Language Distribution[/bold]", border_style="blue"))
    
    # Complexity hotspots
    if hotspots.get('complexity_hotspots'):
        console.print("\n")
        console.print("[bold red]Complexity Hotspots[/bold red]")
        for i, item in enumerate(hotspots['complexity_hotspots'][:5], 1):
            console.print(f"  {i}. [yellow]{item.get('name', 'unknown')}()[/yellow]")
            console.print(f"     Complexity: [red]{item.get('complexity', 0)}[/red]")
            console.print(f"     File: [dim]{Path(item.get('file_path', '')).name}[/dim]")
    
    # Large files
    if hotspots.get('large_files'):
        console.print("\n")
        console.print("[bold yellow]Largest Files[/bold yellow]")
        for i, item in enumerate(hotspots['large_files'][:5], 1):
            console.print(f"  {i}. [cyan]{Path(item.get('path', '')).name}[/cyan]")
            console.print(f"     Lines: [yellow]{item.get('loc', 0):,}[/yellow]")
            console.print(f"     Language: [dim]{item.get('language', 'unknown')}[/dim]")
    
    # Coupling hotspots
    if hotspots.get('coupling_hotspots'):
        console.print("\n")
        console.print("[bold magenta]Highly Coupled Modules[/bold magenta]")
        for i, item in enumerate(hotspots['coupling_hotspots'][:5], 1):
            console.print(f"  {i}. [magenta]{item.get('module_name', 'unknown')}[/magenta]")
            console.print(f"     Imported by: [yellow]{item.get('imported_by_count', 0)}[/yellow] files")
    
    # Footer with suggestions
    console.print("\n")
    console.print(Panel(
        "[bold]Next Steps[/bold]\n\n"
        "[cyan]orc find dead[/cyan] - Find unused code\n"
        "[cyan]orc find complex[/cyan] - Find complex functions\n"
        "[cyan]orc[/cyan] - Chat with AI about your code\n"
        "[cyan]orc check[/cyan] - Quick health check",
        border_style="green"
    ))
    console.print()
    
    # Save to file if requested
    if save:
        # Capture output to file (simplified version)
        with open(save, 'w') as f:
            f.write(f"ORC Codebase Report\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Health Score: {health_score:.0f}/100\n\n")
            f.write(f"Statistics:\n")
            f.write(f"  Files: {stats.get('total_files', 0)}\n")
            f.write(f"  Functions: {total_functions}\n")
            f.write(f"  Classes: {stats.get('total_classes', 0)}\n")
            f.write(f"  Total LOC: {stats.get('total_loc', 0):,}\n")
            f.write(f"  Average Complexity: {avg_complexity:.2f}\n")
            f.write(f"  Max Complexity: {max_complexity}\n")
        console.print(f"[green]+[/green] Report saved to {save}")


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
def analyze(db):
    """Analyze codebase for issues.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc report[/cyan] instead for a better experience.
    """
    console.print("\n[yellow]This command is deprecated.[/yellow]")
    console.print("Please use [cyan]orc report[/cyan] for comprehensive analysis.\n")
    
    # Call report instead
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(report, ['--db', db])


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--confidence', default=0.7, type=float, help='Confidence threshold (0.0-1.0)')
@click.option('--limit', default=30, help='Maximum results')
@click.option('--timeout', default=30, type=int, help='Timeout in seconds')
def dead(db, confidence, limit, timeout):
    """Find potentially unused/dead code.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc find dead[/cyan] for better formatting and insights.
    
    Scans for functions that appear to have no callers.
    """
    console.print("\n[yellow]This command is deprecated.[/yellow]")
    console.print("Please use [cyan]orc find dead[/cyan] for a better experience.\n")
    
    # Call find dead instead
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(find, ['dead', '--db', db, '--limit', str(limit), '--min-confidence', str(confidence)])


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--threshold', default=10, type=int, help='Complexity threshold')
@click.option('--limit', default=20, help='Maximum results')
def complexity(db, threshold, limit):
    """Show complexity metrics and analysis.
    
    [bold yellow]⚠️  DEPRECATED[/bold yellow]
    Use [cyan]orc find complex[/cyan] for better visualization and insights.
    
    Displays functions with high cyclomatic complexity.
    """
    console.print("\n[yellow]This command is deprecated.[/yellow]")
    console.print("Please use [cyan]orc find complex[/cyan] for a better experience.\n")
    
    # Call find complex instead
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(find, ['complex', '--db', db, '--limit', str(limit)])


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--quick', is_flag=True, help='Skip detailed checks')
def check(db, quick):
    """Quick health check of your codebase.
    
    Provides a fast overview of code quality metrics:
      • Health score (0-100)
      • Critical issues count
      • Quick statistics
      • Actionable recommendations
    
    Perfect for CI/CD pipelines or quick status checks.
    
    Examples:
      orc check              # Full health check
      orc check --quick      # Super fast check
    """
    from orc.tools.codebase_mapper import CodebaseMapper
    from orc.ai_tools import ORCTools
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc scan[/cyan] first to index your codebase.")
        sys.exit(1)
    
    console.print()
    console.print("[cyan]Running health check...[/cyan]")
    
    mapper = CodebaseMapper(db_path)
    tools = ORCTools(db_path=str(db_path))
    
    # Get basic stats
    stats = mapper.get_statistics()
    
    # Get complexity analysis
    complexity_result = tools.get_complexity_report(min_complexity=10, limit=5)
    
    # Get dead code analysis (unless quick mode)
    dead_code_count = 0
    if not quick:
        dead_result = tools.get_dead_code(confidence_threshold=0.8, limit=10)
        dead_code_count = len(dead_result.get('safe_to_delete', []))
    
    # Calculate health score
    avg_complexity = stats.get('average_complexity', 0)
    max_complexity = stats.get('max_complexity', 0)
    total_functions = stats.get('total_functions', 1)
    
    critical_count = complexity_result.get('summary', {}).get('critical_count', 0)
    high_count = complexity_result.get('summary', {}).get('high_count', 0)
    
    health_score = 100
    
    # Deduct points for complexity issues
    if avg_complexity > 10:
        health_score -= min(20, (avg_complexity - 10) * 2)
    if max_complexity > 30:
        health_score -= min(20, (max_complexity - 30))
    if critical_count > 0:
        health_score -= min(20, critical_count * 5)
    
    # Deduct points for dead code
    if dead_code_count > 0:
        health_score -= min(10, dead_code_count * 2)
    
    health_score = max(0, min(100, health_score))
    
    # Determine status
    if health_score >= 90:
        status_text = "EXCELLENT"
        status_color = "green"
        border_color = "green"
    elif health_score >= 75:
        status_text = "GOOD"
        status_color = "green"
        border_color = "green"
    elif health_score >= 60:
        status_text = "FAIR"
        status_color = "yellow"
        border_color = "yellow"
    elif health_score >= 40:
        status_text = "NEEDS WORK"
        status_color = "yellow"
        border_color = "yellow"
    else:
        status_text = "CRITICAL"
        status_color = "red"
        border_color = "red"
    
    # Display results
    console.print()
    console.print(Panel(
        f"[bold {status_color}]{status_text}[/bold {status_color}]\n\n"
        f"Health Score: [{status_color}]{health_score:.0f}/100[/{status_color}]",
        title="[bold]Codebase Health Check[/bold]",
        border_style=border_color
    ))
    
    console.print()
    console.print("[bold]Quick Stats[/bold]")
    console.print(f"   Files: [cyan]{stats.get('total_files', 0)}[/cyan]")
    console.print(f"   Functions: [cyan]{total_functions}[/cyan]")
    console.print(f"   Average Complexity: [yellow]{avg_complexity:.2f}[/yellow]")
    
    # Issues
    console.print()
    console.print("[bold]Issues Found[/bold]")
    
    issues = []
    if critical_count > 0:
        issues.append(f"   - [red]{critical_count}[/red] critical complexity functions (20+)")
    if high_count > 0:
        issues.append(f"   - [yellow]{high_count}[/yellow] high complexity functions (10-19)")
    if dead_code_count > 0:
        issues.append(f"   - [yellow]{dead_code_count}[/yellow] potentially unused functions")
    
    if issues:
        for issue in issues:
            console.print(issue)
    else:
        console.print("   [green]+ No major issues detected![/green]")
    
    # Recommendations
    console.print()
    console.print("[bold]Recommendations[/bold]")
    
    if health_score < 60:
        console.print("   1. [cyan]orc find complex[/cyan] - Review and refactor complex functions")
        if dead_code_count > 0:
            console.print("   2. [cyan]orc find dead[/cyan] - Remove unused code")
        console.print("   3. [cyan]orc report[/cyan] - Get detailed analysis")
    elif health_score < 80:
        if critical_count > 0:
            console.print("   [cyan]orc find complex[/cyan] - Address critical complexity")
        if dead_code_count > 0:
            console.print("   [cyan]orc find dead[/cyan] - Clean up unused code")
        console.print("   [cyan]orc report[/cyan] - Review full report")
    else:
        console.print("   [green]+ Your codebase is in great shape![/green]")
        console.print("   Run [cyan]orc[/cyan] to chat with AI about your code")
        console.print("   Use [cyan]orc report[/cyan] for detailed insights")
    
    console.print()
    
    # Exit with appropriate code for CI/CD
    if health_score < 50:
        sys.exit(1)  # Fail in CI/CD if health is critical


@main.command()
def init():
    """Initialize ORC in the current directory.
    
    Creates .orc directory, .orcrc config file, and .orcignore file.
    """
    import yaml
    
    # Create .orc directory
    orc_dir = Path('.orc')
    orc_dir.mkdir(exist_ok=True)
    console.print("[green]+[/green] Created .orc/ directory")
    
    # Create .orcrc config file
    orcrc_path = Path('.orcrc')
    if orcrc_path.exists():
        console.print("[yellow]![/yellow] .orcrc already exists, skipping")
    else:
        config = {
            'version': '1.0.0',
            'ignore': [
                'node_modules/',
                '__pycache__/',
                '.git/',
                '.venv/',
                'venv/',
                'dist/',
                'build/'
            ],
            'dynamic_patterns': [
                'getattr',
                'eval',
                '__import__',
                'exec'
            ],
            'complexity_threshold': 10,
            'confidence_threshold': 0.7
        }
        with open(orcrc_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print("[green]+[/green] Created .orcrc config file")
    
    # Create .orcignore file
    orcignore_path = Path('.orcignore')
    if orcignore_path.exists():
        console.print("[yellow]![/yellow] .orcignore already exists, skipping")
    else:
        ignore_patterns = [
            '# ORC Ignore Patterns',
            '# Files and directories to exclude from analysis',
            '',
            'node_modules/',
            '__pycache__/',
            '*.pyc',
            '.git/',
            '.venv/',
            'venv/',
            'dist/',
            'build/',
            '*.min.js',
            '*.bundle.js',
            'coverage/',
            '.pytest_cache/',
            '.mypy_cache/'
        ]
        with open(orcignore_path, 'w') as f:
            f.write('\n'.join(ignore_patterns))
        console.print("[green]+[/green] Created .orcignore file")
    
    console.print("\n[bold green]ORC initialized successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Run [cyan]orc index[/cyan] to index your codebase")
    console.print("  2. Run [cyan]orc analyze[/cyan] to get analysis results")
    console.print("  3. Edit .orcignore to customize ignored patterns")


@main.group()
def config():
    """Manage ORC configuration."""
    pass


@config.command('show')
def config_show():
    """Show current configuration."""
    import yaml
    
    orcrc_path = Path('.orcrc')
    
    if not orcrc_path.exists():
        console.print("[red]Error:[/red] No .orcrc found.")
        console.print("Run [cyan]orc init[/cyan] first to initialize ORC.")
        sys.exit(1)
    
    with open(orcrc_path) as f:
        config_data = yaml.safe_load(f)
    
    console.print("\n[bold cyan]ORC Configuration[/bold cyan]\n")
    console.print(yaml.dump(config_data, default_flow_style=False))


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value."""
    import yaml
    
    orcrc_path = Path('.orcrc')
    
    if not orcrc_path.exists():
        console.print("[red]Error:[/red] No .orcrc found.")
        console.print("Run [cyan]orc init[/cyan] first.")
        sys.exit(1)
    
    with open(orcrc_path) as f:
        config_data = yaml.safe_load(f)
    
    # Parse value (try to convert to appropriate type)
    try:
        # Try int
        parsed_value = int(value)
    except ValueError:
        try:
            # Try float
            parsed_value = float(value)
        except ValueError:
            # Try boolean
            if value.lower() in ('true', 'yes', 'on'):
                parsed_value = True
            elif value.lower() in ('false', 'no', 'off'):
                parsed_value = False
            else:
                parsed_value = value
    
    config_data[key] = parsed_value
    
    with open(orcrc_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    console.print(f"[green]+[/green] Set {key} = {parsed_value}")


@config.command('add-ignore')
@click.argument('pattern')
def config_add_ignore(pattern):
    """Add a pattern to the ignore list."""
    import yaml
    
    orcrc_path = Path('.orcrc')
    
    if not orcrc_path.exists():
        console.print("[red]Error:[/red] No .orcrc found.")
        console.print("Run [cyan]orc init[/cyan] first.")
        sys.exit(1)
    
    with open(orcrc_path) as f:
        config_data = yaml.safe_load(f)
    
    if 'ignore' not in config_data:
        config_data['ignore'] = []
    
    if pattern not in config_data['ignore']:
        config_data['ignore'].append(pattern)
        
        with open(orcrc_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        console.print(f"[green]+[/green] Added '{pattern}' to ignore list")
    else:
        console.print(f"[yellow]![/yellow] Pattern '{pattern}' already in ignore list")


@main.command()
@click.argument('pattern')
def ignore(pattern):
    """Add a pattern to .orcignore file.
    
    Examples:
      orc ignore "test_*.py"
      orc ignore "legacy/"
    """
    orcignore_path = Path('.orcignore')
    
    # Create .orcignore if it doesn't exist
    if not orcignore_path.exists():
        console.print("[yellow]No .orcignore found, creating one...[/yellow]")
        with open(orcignore_path, 'w') as f:
            f.write('# ORC Ignore Patterns\n\n')
    
    # Check if pattern already exists
    with open(orcignore_path) as f:
        existing_lines = f.read().splitlines()
    
    if pattern in existing_lines:
        console.print(f"[yellow]Pattern '{pattern}' already in .orcignore[/yellow]")
        return
    
    # Add pattern
    with open(orcignore_path, 'a') as f:
        f.write(f'{pattern}\n')
    
    console.print(f"[green]+[/green] Added '{pattern}' to .orcignore")


@main.command()
@click.argument('finding_id')
def explain(finding_id):
    """Explain a finding in detail.
    
    Example:
      orc explain D-12
    """
    console.print(f"[yellow]Explaining finding:[/yellow] {finding_id}")
    console.print("\n[bold]Note:[/bold] This feature requires storing findings with IDs.")
    console.print("Currently findings are displayed directly without persistent IDs.")
    console.print("\nTo implement this feature:")
    console.print("  1. Store analysis results with unique IDs")
    console.print("  2. Add retrieval by ID")
    console.print("  3. Add detailed context and suggestions")


@main.command()
@click.argument('target', required=False)
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--finding-id', help='Delete specific finding by ID')
@click.option('--yes', is_flag=True, help='Skip confirmation')
@click.option('--backup/--no-backup', default=True, help='Create backup before deletion')
def delete(target, db, finding_id, yes, backup):
    """Delete dead code safely (with backup).
    
    Examples:
      orc delete path/to/file.py --yes
      orc delete --finding-id D-12
    """
    console.print("[bold red]WARNING: Code Deletion[/bold red]")
    console.print("\nThis feature will:")
    console.print("  1. Create a backup in .orc/backups/")
    console.print("  2. Remove the specified code")
    console.print("  3. Update the index")
    console.print("\n[yellow]Note:[/yellow] Full implementation requires:")
    console.print("  - Safe AST-based code removal")
    console.print("  - Backup management system")
    console.print("  - Undo capability")
    console.print("\nFor now, please manually review and delete code after running 'orc dead'")


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--limit', default=10, help='Maximum suggestions')
def optimize(db, limit):
    """Get optimization suggestions.
    
    Analyzes code for performance improvements.
    """
    console.print("[bold cyan]Optimization Analysis[/bold cyan]\n")
    console.print("[yellow]Note:[/yellow] Advanced optimization detection is in development.")
    console.print("\nCurrent capabilities via other commands:")
    console.print("  - [cyan]orc complexity[/cyan] - Find complex functions")
    console.print("  - [cyan]orc hotspots[/cyan] - Find large files and coupling")
    console.print("  - [cyan]orc dead[/cyan] - Find unused code")
    console.print("\nPlanned features:")
    console.print("  - Detect O(n²) algorithms")
    console.print("  - Suggest better data structures")
    console.print("  - Find redundant computations")
    console.print("  - Recommend caching opportunities")







if __name__ == '__main__':
    main()






