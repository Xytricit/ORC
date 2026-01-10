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
from orc.cli_auth import require_auth, is_authenticated, login_flow, logout, get_api_config

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
        # Check authentication first
        if not is_authenticated():
            require_auth()
        
        # Launch interactive ORC
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
    from orc.storage.graph_db import GraphDatabase
    
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
        # Use parallel indexer
        with Progress() as progress:
            task = progress.add_task("[cyan]Indexing...", total=None)
            result = index_directory_parallel(path)
            progress.update(task, completed=100)
        
        # Save to database
        console.print("[yellow]Saving to database...[/yellow]")
        db = GraphDatabase(str(output))
        
        # Store files
        for file_path, file_info in result.get('files', {}).items():
            db.add_file(
                file_path=file_path,
                language=file_info.get('language', 'unknown'),
                size=file_info.get('loc', 0)
            )
        
        # Store functions
        for func_name, func_info in result.get('functions', {}).items():
            db.add_function(
                name=func_name,
                file_path=func_info.get('file_path', ''),
                start_line=func_info.get('start_line', 0),
                end_line=func_info.get('end_line', 0),
                complexity=func_info.get('complexity', 1),
                params=func_info.get('params', [])
            )
        
        # Store classes
        for class_name, class_info in result.get('classes', {}).items():
            db.add_class(
                name=class_name,
                file_path=class_info.get('file_path', ''),
                start_line=class_info.get('start_line', 0),
                end_line=class_info.get('end_line', 0),
                methods=class_info.get('methods', [])
            )
        
        db.connection.commit()
        
        console.print("\n[bold green]✓ Indexing complete![/bold green]")
        console.print(f"  Files: {len(result.get('files', {}))}")
        console.print(f"  Functions: {len(result.get('functions', {}))}")
        console.print(f"  Classes: {len(result.get('classes', {}))}")
        console.print(f"\nRun 'orc stats' to see detailed statistics.")
        
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
    
    Displays file counts, function counts, language breakdown, and complexity metrics.
    """
    from orc.ai_tools import ORCTools
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first to create the database.")
        sys.exit(1)
    
    tools = ORCTools(db_path=str(db_path))
    result = tools.get_codebase_stats()
    
    if 'error' in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)
    
    if json_output:
        print(json.dumps(result, indent=2))
        return
    
    # Pretty print
    console.print("\n[bold cyan]Codebase Statistics[/bold cyan]")
    console.print(f"Total Files: {result.get('total_files', 0)}")
    console.print(f"Total Functions: {result.get('total_functions', 0)}")
    console.print(f"Total Classes: {result.get('total_classes', 0)}")
    console.print(f"Average Complexity: {result.get('average_complexity', 0):.2f}")
    console.print(f"Max Complexity: {result.get('max_complexity', 0)}")
    
    if result.get('files_by_language'):
        console.print("\n[bold]Files by Language:[/bold]")
        for lang, count in result['files_by_language'].items():
            console.print(f"  {lang}: {count}")


@main.command()
@click.argument('pattern')
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--type', 'search_type', type=click.Choice(['functions', 'classes', 'files']), default='functions')
@click.option('--limit', default=20, help='Maximum results')
def query(pattern, db, search_type, limit):
    """Search for functions, classes, or files.
    
    Examples:
      orc query auth
      orc query login --type functions
      orc query User --type classes
    """
    from orc.ai_tools import ORCTools
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first.")
        sys.exit(1)
    
    tools = ORCTools(db_path=str(db_path))
    
    if search_type == 'functions':
        result = tools.query_functions(pattern=pattern, limit=limit)
        items = result.get('functions', [])
        title = "Functions"
    elif search_type == 'classes':
        result = tools.query_classes(pattern=pattern, limit=limit)
        items = result.get('classes', [])
        title = "Classes"
    else:
        result = tools.query_files(pattern=pattern, limit=limit)
        items = result.get('files', [])
        title = "Files"
    
    if 'error' in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)
    
    if not items:
        console.print(f"[yellow]No {search_type} found matching:[/yellow] {pattern}")
        return
    
    console.print(f"\n[bold cyan]{title} matching '{pattern}':[/bold cyan]")
    console.print(f"Found {len(items)} results\n")
    
    for item in items:
        if search_type == 'functions':
            console.print(f"[green]{item['name']}()[/green]")
            console.print(f"  File: {Path(item['file_path']).name}")
            console.print(f"  Lines: {item['start_line']}-{item['end_line']}")
            console.print(f"  Complexity: {item['complexity']}")
        elif search_type == 'classes':
            console.print(f"[green]{item['name']}[/green]")
            console.print(f"  File: {Path(item['file_path']).name}")
            console.print(f"  Language: {item['language']}")
        else:
            console.print(f"[green]{item['file_path']}[/green]")
            console.print(f"  Language: {item['language']}")
            console.print(f"  Size: {item['size']} lines")
        console.print()


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--limit', default=10, help='Results per category')
def hotspots(db, limit):
    """Find complexity and size hotspots.
    
    Shows the most complex functions, largest files, and highly coupled modules.
    """
    from orc.tools.codebase_mapper import CodebaseMapper
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first.")
        sys.exit(1)
    
    mapper = CodebaseMapper(db_path)
    result = mapper.get_hotspots(limit=limit)
    
    # Complexity hotspots
    console.print("\n[bold red]Complexity Hotspots:[/bold red]")
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
    
    # Coupling hotspots
    if result.get('coupling_hotspots'):
        console.print("\n[bold magenta]Highly Coupled Modules:[/bold magenta]")
        for item in result.get('coupling_hotspots', [])[:limit]:
            console.print(f"[magenta]{item.get('module_name', 'unknown')}[/magenta]")
            console.print(f"  Imported by: {item.get('imported_by_count', 0)} files")


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
def analyze(db):
    """Analyze codebase for issues.
    
    Runs multiple analyses: complexity, dead code, security issues.
    """
    from orc.tools.codebase_mapper import CodebaseMapper
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first.")
        sys.exit(1)
    
    mapper = CodebaseMapper(db_path)
    
    console.print("\n[bold cyan]Analyzing Codebase[/bold cyan]\n")
    
    # Get statistics
    stats = mapper.get_statistics()
    console.print(f"[yellow]Analyzing {stats.get('total_files', 0)} files...[/yellow]\n")
    
    # Complexity analysis
    hotspots = mapper.get_hotspots(limit=5)
    
    console.print("[bold red]High Complexity Functions:[/bold red]")
    for item in hotspots.get('complexity_hotspots', [])[:5]:
        console.print(f"  {item.get('name', 'unknown')}() - Complexity: {item.get('complexity', 0)}")
    
    console.print("\n[bold yellow]Large Files:[/bold yellow]")
    for item in hotspots.get('large_files', [])[:5]:
        console.print(f"  {Path(item.get('path', '')).name} - {item.get('loc', 0)} lines")
    
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Average Complexity: {stats.get('average_complexity', 0):.2f}")
    console.print(f"  Max Complexity: {stats.get('max_complexity', 0)}")
    console.print(f"  Total LOC: {stats.get('total_loc', 0):,}")


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--confidence', default=0.7, type=float, help='Confidence threshold (0.0-1.0)')
@click.option('--limit', default=30, help='Maximum results')
@click.option('--timeout', default=30, type=int, help='Timeout in seconds')
def dead(db, confidence, limit, timeout):
    """Find potentially unused/dead code.
    
    Scans for functions that appear to have no callers.
    """
    # No auth required for basic dead code detection
    from orc.ai_tools import ORCTools
    import signal
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first.")
        sys.exit(1)
    
    console.print("[yellow]Scanning for dead code...[/yellow]")
    
    # Timeout handler
    def timeout_handler(signum, frame):
        raise TimeoutError("Dead code analysis timed out")
    
    try:
        # Set timeout on Unix systems
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        tools = ORCTools(db_path=str(db_path))
        result = tools.get_dead_code(confidence_threshold=confidence, limit=limit)
        
        # Cancel timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        if 'error' in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            sys.exit(1)
        
        summary = result.get('summary', {})
        console.print(f"\nAnalyzed {summary.get('total_functions_analyzed', 0)} functions")
        console.print(f"Found {summary.get('total_potentially_unused', 0)} potentially unused\n")
        
        # Safe to delete
        safe = result.get('safe_to_delete', [])
        if safe:
            console.print("[bold red]Safe to Delete (90%+ confidence):[/bold red]")
            for item in safe[:limit]:
                console.print(f"[red]{item['name']}()[/red]")
                console.print(f"  File: {Path(item['file_path']).name}")
                console.print(f"  Confidence: {item['confidence']}")
                console.print(f"  Reasons: {', '.join(item['reasons'])}")
                console.print()
        
        # Review needed
        review = result.get('review_needed', [])
        if review:
            console.print("[bold yellow]Review Needed (70-90% confidence):[/bold yellow]")
            for item in review[:limit]:
                console.print(f"[yellow]{item['name']}()[/yellow]")
                console.print(f"  File: {Path(item['file_path']).name}")
                console.print(f"  Confidence: {item['confidence']}")
                console.print()
    
    except TimeoutError:
        console.print(f"[red]Analysis timed out after {timeout} seconds.[/red]")
        console.print("Try using --limit to reduce scope or --timeout to increase time.")
        sys.exit(1)


@main.command()
@click.option('--db', default='.orc/index.db', help='Database path')
@click.option('--threshold', default=10, type=int, help='Complexity threshold')
@click.option('--limit', default=20, help='Maximum results')
def complexity(db, threshold, limit):
    """Show complexity metrics and analysis.
    
    Displays functions with high cyclomatic complexity.
    """
    # No auth required for basic complexity analysis
    from orc.ai_tools import ORCTools
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first.")
        sys.exit(1)
    
    tools = ORCTools(db_path=str(db_path))
    result = tools.get_complexity_report(min_complexity=threshold, limit=limit)
    
    if 'error' in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)
    
    summary = result.get('summary', {})
    console.print("\n[bold cyan]Complexity Analysis[/bold cyan]")
    console.print(f"Total Functions: {summary.get('total_functions', 0)}")
    console.print(f"Average Complexity: {summary.get('average_complexity', 0):.2f}")
    console.print(f"Max Complexity: {summary.get('max_complexity', 0)}")
    console.print(f"Critical (20+): {summary.get('critical_count', 0)}")
    console.print(f"High (10-19): {summary.get('high_count', 0)}")
    console.print(f"Medium (5-9): {summary.get('medium_count', 0)}\n")
    
    # Distribution
    dist = result.get('distribution', {})
    if dist:
        console.print("[bold]Complexity Distribution:[/bold]")
        for range_key, count in sorted(dist.items()):
            console.print(f"  {range_key}: {count}")
        console.print()
    
    # High complexity functions
    high_complexity = result.get('high_complexity_functions', [])
    if high_complexity:
        console.print(f"[bold red]Functions with Complexity > {threshold}:[/bold red]")
        for item in high_complexity[:limit]:
            console.print(f"[red]{item['name']}()[/red]")
            console.print(f"  Complexity: {item['complexity']}")
            console.print(f"  File: {Path(item['file_path']).name}")
            console.print(f"  Lines: {item['start_line']}-{item['end_line']}")
            console.print()


@main.command()
def init():
    """Initialize ORC in the current directory.
    
    Creates .orc directory, .orcrc config file, and .orcignore file.
    """
    import yaml
    
    # Create .orc directory
    orc_dir = Path('.orc')
    orc_dir.mkdir(exist_ok=True)
    console.print("[green]✓[/green] Created .orc/ directory")
    
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
        console.print("[green]✓[/green] Created .orcrc config file")
    
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
        console.print("[green]✓[/green] Created .orcignore file")
    
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
    
    console.print(f"[green]✓[/green] Set {key} = {parsed_value}")


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
        
        console.print(f"[green]✓[/green] Added '{pattern}' to ignore list")
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
    
    console.print(f"[green]✓[/green] Added '{pattern}' to .orcignore")


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


@main.command()
@click.option('--port', default=5000, type=int, help='Port to run server on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--db', default='.orc/index.db', help='Database path')
def serve(port, host, db):
    """Start ORC web interface and API server.
    
    Launches a web dashboard for interactive code analysis.
    NOTE: Web interface requires separate installation (orc-cli[web])
    """
    try:
        from orc.web import app
    except ImportError:
        console.print(f"\n[red]Error:[/red] Web interface not installed.")
        console.print("\nThe web interface is deployed separately from the CLI.")
        console.print("To install web dependencies locally, run:")
        console.print("  [cyan]pip install orc-cli[web][/cyan]\n")
        console.print("Or deploy the web app separately to a domain.")
        sys.exit(1)
    
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[red]Error:[/red] Database not found: {db_path}")
        console.print("Run [cyan]orc index[/cyan] first to create the database.")
        sys.exit(1)
    
    console.print(f"\n[bold cyan]Starting ORC Server[/bold cyan]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Database: {db_path}")
    console.print(f"\n[green]Server running at:[/green] http://{host}:{port}")
    console.print("Press Ctrl+C to stop\n")
    
    try:
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Server error:[/red] {e}")
        sys.exit(1)




@main.command()
@click.option('--token', help='Authentication token from web interface')
@click.option('--apikey', help='Direct API key (alternative to web token)')
@click.option('--url', help='Web server URL', default='http://127.0.0.1:5000')
def login(token, apikey, url):
    """Connect CLI to ORC web application.
    
    Two ways to authenticate:
    1. Web token: Get from http://127.0.0.1:5000/account
    2. API key: Use --apikey flag with your key
    
    Examples:
      orc login
      orc login --token YOUR_TOKEN
      orc login --apikey YOUR_API_KEY
    """
    # If apikey is provided, use it directly
    if apikey:
        from orc.cli_auth import save_config
        console.print("\n[cyan]Setting up direct API key authentication...[/cyan]\n")
        save_config({
            'web_url': url,
            'web_token': apikey,
            'direct_apikey': True
        })
        console.print("[green]✓ API key saved successfully![/green]")
        console.print("\n[dim]You can now use ORC with your API key.[/dim]\n")
        return
    
    success = login_flow(token=token, web_url=url)
    if not success:
        raise SystemExit(1)


@main.command()
def logout():
    """Sign out from ORC web application."""
    from orc.cli_auth import logout as do_logout
    do_logout()


@main.command()
def status():
    """Show authentication status."""
    from orc.cli_auth import get_config, get_web_url
    
    if is_authenticated():
        config = get_config()
        web_url = get_web_url()
        
        console.print()
        console.print("[green]?[/green] Authenticated")
        console.print(f"[cyan]Web URL:[/cyan] {web_url}")
        console.print()
        
        # Try to get user info
        api_config = get_api_config()
        if api_config:
            console.print("[cyan]Default AI Provider:[/cyan]", api_config.get('provider', 'None'))
            console.print()
    else:
        console.print()
        console.print("[red]?[/red] Not authenticated")
        console.print("[yellow]Run:[/yellow] orc login")
        console.print()

if __name__ == '__main__':
    main()

