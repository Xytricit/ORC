"""
ORC CLI: Command Line Interface
"""
import click
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

ORC_VERSION = "1.0.0"

ORC_BANNER = r"""
    ____        __          __
   / __ \____  / /_  ____  / /_____  _____
  / / / / __ \/ __ \/ __ \/ __/ __ \/ ___/
 / /_/ / /_/ / /_/ / /_/ / /_/ /_/ / /
/_____/\____/_.___/\____/\__/\____/_/

   ██████  ███████ ███████ ██████  █████  ██████  ███████
  ██       ██      ██      ██   ██ ██   ██ ██   ██ ██
  ██   ███ █████   █████   ██████  ███████ ██████  █████
  ██    ██ ██      ██      ██      ██   ██ ██      ██
   ██████  ███████ ███████ ██      ██   ██ ██      ███████

      ORC - Optimization & Refactoring Catalyst
         v1.0.0 - AI-Powered Code Analysis
"""


def _maybe_show_welcome(project_root: Path) -> None:
    """Show a one-time welcome message per project root.

    State is stored under <project_root>/.orc/state.json so we do not
    spam the user on every run.
    """
    try:
        state_dir = project_root / ".orc"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file = state_dir / "state.json"

        if state_file.exists():
            with state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("welcome_shown"):
                return
    except Exception:
        # If anything goes wrong, just skip state tracking.
        pass

    console.print(ORC_BANNER, style="bold green")
    console.print(
        f"[bold green]Welcome to ORC v{ORC_VERSION} – Optimization & Refactoring Catalyst.[/bold green]",
    )
    console.print("Index your first project with: [italic]orc index /path/to/project[/italic]\n")

    try:
        with (project_root / ".orc" / "state.json").open("w", encoding="utf-8") as f:
            json.dump({"welcome_shown": True}, f)
    except Exception:
        # Non-fatal; welcome is best-effort.
        pass


# Global options that apply to all commands
GLOBAL_OPTIONS = [
    click.option('--json', 'output_json', is_flag=True, help='Output in JSON format'),
    click.option('--quiet', '-q', 'quiet_mode', is_flag=True, help='Suppress all output except errors'),
    click.option('--format', type=click.Choice(['table', 'json', 'text']), default='table',
                 help='Output format (default: table)')
]

def add_global_options(func):
    """Decorator to add global options to commands"""
    for option in reversed(GLOBAL_OPTIONS):
        func = option(func)
    return func


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=ORC_VERSION, prog_name="ORC")
@add_global_options
def cli(ctx, output_json, quiet_mode, format):
    """ORC - Codebase Intelligence Agent

    Optimization & Refactoring Catalyst - Static Analysis Tool
    Use 'orc --help' to see available commands.

    Run 'orc' without arguments to start the AI chat interface.
    """
    ctx.ensure_object(dict)
    ctx.obj['OUTPUT_JSON'] = output_json
    ctx.obj['QUIET_MODE'] = quiet_mode
    ctx.obj['FORMAT'] = format

    # If no command provided, start AI chat
    if ctx.invoked_subcommand is None:
        from orc.cli_loop import run_cli_session
        run_cli_session()
        ctx.exit(0)



@cli.command()
@click.pass_context
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', default='config.yaml', help='Config file path')
def index(ctx, path, config):
    """Index a codebase (Python + all supported language parsers)."""
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    format = ctx.obj.get('FORMAT', 'table')

    from orc_package.config.settings import load_config
    from orc.core.index_service import IndexService

    cfg = load_config(config)
    cfg.project_root = Path(path)

    if not quiet_mode:
        _maybe_show_welcome(cfg.project_root)

    if not quiet_mode:
        console.print(f"[bold blue]Indexing codebase at:[/bold blue] {path}")
        with console.status("[bold blue]Indexing files...[/bold blue]", spinner="dots"):
            service = IndexService(cfg)
            service.index_project(Path(path))
        console.print("[green]✓[/green] Indexing complete. Database updated at " + str(cfg.index_path))
    elif output_json:
        service = IndexService(cfg)
        service.index_project(Path(path))
    else:
        service = IndexService(cfg)
        service.index_project(Path(path))
    
    if output_json:
        import json
        result = {
            "status": "success",
            "message": "Indexing complete",
            "database_path": str(cfg.index_path)
        }
        click.echo(json.dumps(result))

@cli.command()
@click.pass_context
@click.argument('file', required=False)
@click.option('--config', default='config.yaml', help='Config file path')
def analyse(ctx, file, config):
    """Run full analysis on the codebase.

    This will (re)index the project using all parsers, then run the
    Python analyzers (dead code, dependencies, metrics, patterns) on the
    stored index.
    """
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    format = ctx.obj.get('FORMAT', 'table')

    from orc_package.config.settings import load_config
    from orc.core.index_service import IndexService
    from orc.storage.graph_db import GraphStorage
    from orc.core.analyzer import Analyzer

    cfg = load_config(config)
    service = IndexService(cfg)

    if not quiet_mode:
        _maybe_show_welcome(cfg.project_root)

    # Kick off indexing first so DB + graphs + multi-language index are fresh
    if file:
        if not quiet_mode:
            console.print(f"[bold blue]Analyzing file: {file} (full index still runs for context)[/bold blue]")
            with console.status("[bold blue]Indexing project...[/bold blue]", spinner="dots"):
                service.index_project()
        else:
            service.index_project()
    else:
        # Professional, compact status indicator instead of ad-hoc dot
        # printing and per-file spam.
        if not quiet_mode:
            with console.status("[bold blue]Analyzing entire codebase...[/bold blue]", spinner="dots"):
                service.index_project()
        else:
            service.index_project()

    # Load modules from DB and run analyzers
    storage = GraphStorage(cfg.index_path)
    modules = storage.load_modules()

    analyzer = Analyzer(cfg)
    report = analyzer.run_all(modules)

    if not quiet_mode:
        console.print("[green]+[/green] Analysis complete (index + Python analyzers)")
    elif output_json:
        import json
        result = {
            "status": "success",
            "message": "Analysis complete",
            "report": str(report) if report else None
        }
        click.echo(json.dumps(result))

    return report

@cli.command()
@click.pass_context
def dead(ctx):
    """Show dead / unused code (runs fresh analysis)."""
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    format = ctx.obj.get('FORMAT', 'table')

    from orc.storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc_package.analysis.dead_code import DeadCodeAnalyzer
    from orc.utils.module_filter import filter_modules

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    # Filter out .venv and other ignored paths
    modules = filter_modules(modules)
    
    if not modules:
        if not quiet_mode:
            console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
        elif output_json:
            import json
            result = {
                "error": "No indexed modules found. Run 'orc index' or 'orc analyse' first."
            }
            click.echo(json.dumps(result))
        return

    if not quiet_mode:
        with console.status("[bold blue]Analyzing code for unused functions...[/bold blue]", spinner="dots"):
            analyzer = DeadCodeAnalyzer(cfg)
            report = analyzer.analyze(modules)
    else:
        analyzer = DeadCodeAnalyzer(cfg)
        report = analyzer.analyze(modules)

    # Flatten findings and attach lifecycle fields for compatibility with
    # delete/explain commands.
    findings = []
    for f in report.unused_functions:
        key = f"{f['file']}::{f['function']}"
        confidence = report.confidence_scores.get(key, 0.7)
        finding = dict(f)
        finding["lifecycle_status"] = "DEAD"
        finding["lifecycle_confidence"] = int(confidence * 100)
        findings.append(finding)

    if not findings:
        if not quiet_mode:
            console.print("[green]No dead code found.")
        elif output_json:
            import json
            result = {"dead_code_findings": []}
            click.echo(json.dumps(result))
        return

    if output_json:
        import json
        result = {"dead_code_findings": findings}
        click.echo(json.dumps(result))
    elif not quiet_mode:
        console.print("[bold]Dead Code Findings:[/bold]")
        for i, finding in enumerate(findings[:20], 1):  # Show top 20
            func_name = finding.get('function', 'unknown')
            file_path = finding.get('file', 'unknown')
            console.print(f"[D-{i:02d}] {file_path} - {func_name}")

        if len(findings) > 20:
            console.print(f"[dim]... and {len(findings) - 20} more findings[/dim]")
        
        # Show ORC Verdict
        console.print("")
        from orc.verdict_formatter import OrcVerdict
        stats = {
            'total_functions_analyzed': len(modules),
            'total_potentially_unused': len(findings),
            'safe_to_delete_count': len([f for f in findings if f.get('lifecycle_confidence', 0) >= 90])
        }
        OrcVerdict.dead_code_verdict(stats)

@cli.command()
@click.argument('finding_id', required=False)
@click.option('--confidence', 'min_confidence', type=int, default=None,
              help='Only act on findings with at least this confidence percentage')
@click.option('--all', 'delete_all', is_flag=True,
              help='Apply to all findings that meet the confidence threshold')
@click.option('--yes', is_flag=True, help='Skip confirmation')
def delete(finding_id, min_confidence, delete_all, yes):
    """Delete dead code (explicit action, re-runs analysis).

    Usage patterns:

    \b
    # Delete a single finding by ID
    orc delete D-02

    # Delete a single finding only if confidence >= 95%
    orc delete D-02 --confidence 95

    # Delete all findings with confidence >= 95% (v1 marks them only)
    orc delete --confidence 95 --all --yes
    """
    from orc.storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc_package.analysis.dead_code import DeadCodeAnalyzer

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    if not modules:
        console.print("[red]No indexed modules found. Run 'orc analyse' first.[/red]")
        return

    analyzer = DeadCodeAnalyzer(cfg)
    report = analyzer.analyze(modules)

    # Flatten findings and attach lifecycle/confidence
    findings = []
    for f in report.unused_functions:
        key = f"{f['file']}::{f['function']}"
        confidence = report.confidence_scores.get(key, 0.7)
        finding = dict(f)
        finding["lifecycle_status"] = "DEAD"
        finding["lifecycle_confidence"] = int(confidence * 100)
        findings.append(finding)

    if not findings:
        console.print("[green]No dead code findings available to delete.[/green]")
        return

    # Helper to filter by confidence threshold if provided
    def meets_confidence(f) -> bool:
        if min_confidence is None:
            return True
        return int(f.get("lifecycle_confidence", 0)) >= int(min_confidence)

    # ------------------------------------------------------------------
    # Mode 1: delete a specific finding by ID (D-02)
    # ------------------------------------------------------------------
    if not delete_all and finding_id:
        if not finding_id.startswith('D-'):
            console.print("[red]Invalid finding ID. Use format D-12[/red]")
            return

        try:
            finding_num = int(finding_id[2:])
        except ValueError:
            console.print("[red]Invalid finding ID. Use format D-12[/red]")
            return

        if finding_num < 1 or finding_num > len(findings):
            console.print("[red]Finding not found[/red]")
            return

        finding = findings[finding_num - 1]
        if not meets_confidence(finding):
            console.print(
                f"[yellow]Skipping {finding_id} because its confidence "
                f"({finding.get('lifecycle_confidence', 0)}%) is below the "
                f"requested threshold ({min_confidence}%).[/yellow]"
            )
            return

        file_path = finding.get('file', 'unknown')
        func_name = finding.get('function', 'unknown')

        console.print(f"[bold]Delete confirmation:[/bold]")
        console.print(f"File: {file_path}")
        console.print(f"Function: {func_name}")
        console.print(
            f"Status: {finding.get('lifecycle_status')} "
            f"({finding.get('lifecycle_confidence')}% confidence)"
        )

        if not yes:
            confirm = input("Delete this code? (y/n): ")
            if confirm.lower() != 'y':
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Actually delete the function from the file
        from orc.utils.file_modifier import FileModifier
        success = FileModifier.remove_function_from_file(file_path, func_name)
        if success:
            console.print(f"[green]+[/green] Deleted {file_path}::{func_name}")
        else:
            console.print(f"[red]-[/red] Failed to delete {file_path}::{func_name}")
        return

    # ------------------------------------------------------------------
    # Mode 2: bulk delete by confidence threshold
    # ------------------------------------------------------------------
    # If user passed --all or omitted an ID entirely, operate over all
    # findings that meet the confidence requirement.
    candidates = [f for f in findings if meets_confidence(f)]

    if not candidates:
        if min_confidence is not None:
            console.print(
                f"[yellow]No findings meet the requested confidence "
                f"threshold ({min_confidence}%).[/yellow]"
            )
        else:
            console.print("[yellow]No dead code findings available to delete.[/yellow]")
        return

    console.print("[bold]Bulk delete summary:[/bold]")
    for i, finding in enumerate(candidates, 1):
        console.print(
            f"[D-{i:02d}] {finding.get('file', 'unknown')} - "
            f"{finding.get('function', 'unknown')} "
            f"({finding.get('lifecycle_confidence', 0)}% confidence)"
        )

    if not yes:
        confirm = input(
            f"Delete {len(candidates)} findings"
            + (f" with >= {min_confidence}% confidence" if min_confidence is not None else "")
            + "? (y/n): "
        )
        if confirm.lower() != 'y':
            console.print("[yellow]Cancelled[/yellow]")
            return

    # Actually delete the functions from their respective files
    from orc.utils.file_modifier import FileModifier
    success_count = 0
    for finding in candidates:
        file_path = finding.get('file', 'unknown')
        func_name = finding.get('function', 'unknown')
        success = FileModifier.remove_function_from_file(file_path, func_name)
        if success:
            success_count += 1
            console.print(f"[green]+[/green] Deleted {file_path}::{func_name}")
        else:
            console.print(f"[red]-[/red] Failed to delete {file_path}::{func_name}")

    console.print(f"[green]Successfully deleted {success_count}/{len(candidates)} functions.[/green]")


@cli.command()
@click.option('--file', default=None, help='Specific file to analyze for optimizations')
@click.option('--function', default=None, help='Specific function to analyze for optimizations')
@click.option('--threshold', default=10, help='Minimum complexity threshold for optimization suggestions')
def optimize(file, function, threshold):
    """Get optimization suggestions for complex functions."""
    from orc.storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc.optimization.suggester import Suggester
    from orc.analysis.complexity import ComplexityAnalyzer
    from orc.core.analyzer import Analyzer

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    if not modules:
        console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
        return

    # Get complexity analyzer to identify complex functions
    complexity_analyzer = ComplexityAnalyzer({}, None)  # Pass empty index and graph for now

    # If specific file and function are provided
    if file and function:
        # Find the specific function in the modules
        for module_path, module_info in modules.items():
            if module_path.endswith(file):
                if function in module_info.functions:
                    func_info = module_info.functions[function]
                    code = _extract_function_code(module_path, func_info)

                    # Get optimization suggestions
                    suggester = Suggester()
                    result = suggester.suggest(file, function, code)

                    console.print(f"[bold]Optimization suggestions for {file}::{function}:[/bold]")
                    console.print(f"Suggestion: {result['suggestion']}")
                    console.print(f"Estimated improvement: {result['estimated_improvement']:.2f}")
                    if 'example' in result and result['example']:
                        console.print(f"Example:\n{result['example']}")
                    return

        console.print(f"[red]Function {function} not found in {file}[/red]")
        return

    # Otherwise, analyze all functions with complexity above threshold
    complex_functions = []

    for module_path, module_info in modules.items():
        if file and not module_path.endswith(file):
            continue

        for func_name, func_info in module_info.functions.items():
            if func_info.complexity >= threshold:
                complex_functions.append({
                    'file': module_path,
                    'function': func_name,
                    'complexity': func_info.complexity,
                    'info': func_info
                })

    if not complex_functions:
        console.print(f"[green]No functions found with complexity >= {threshold}.[/green]")
        return

    # Sort by complexity (descending)
    complex_functions.sort(key=lambda x: x['complexity'], reverse=True)

    console.print(f"[bold]Functions with complexity >= {threshold}:[/bold]")

    with console.status("[bold blue]Analyzing and generating optimization suggestions...[/bold blue]", spinner="dots"):
        optimization_results = []
        for func_data in complex_functions[:20]:  # Show top 20
            file_path = func_data['file']
            func_name = func_data['function']
            complexity = func_data['complexity']

            # Extract function code
            code = _extract_function_code(file_path, func_data['info'])

            # Get optimization suggestions
            suggester = Suggester()
            result = suggester.suggest(file_path, func_name, code)
            
            optimization_results.append({
                'func_name': func_name,
                'file_path': file_path,
                'complexity': complexity,
                'suggestion': result['suggestion'],
                'improvement': result['estimated_improvement']
            })
    
    # Display results
    for opt in optimization_results:
        console.print(f"\n[blue]{opt['func_name']}[/blue] in [green]{opt['file_path']}[/green] (complexity: {opt['complexity']})")
        console.print(f"  Suggestion: {opt['suggestion']}")
        console.print(f"  Estimated improvement: {opt['improvement']:.2f}")


def _extract_function_code(file_path: str, func_info) -> str:
    """Extract the code for a specific function from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_line = func_info.line_start - 1  # Convert to 0-based index
        end_line = func_info.line_end

        # Extract the function code
        func_lines = lines[start_line:end_line]
        return "".join(func_lines).strip()
    except Exception:
        return ""


@cli.command()
@click.pass_context
@click.option('--threshold', default=10, help='Minimum complexity threshold for reporting')
def complexity(ctx, threshold):
    """Show high complexity functions in the codebase."""
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    format = ctx.obj.get('FORMAT', 'table')

    from orc.storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc.analysis.complexity import ComplexityAnalyzer
    from orc.utils.module_filter import filter_modules

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    # Filter out .venv and other ignored paths
    modules = filter_modules(modules)
    
    if not modules:
        if not quiet_mode:
            console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
        elif output_json:
            import json
            result = {
                "error": "No indexed modules found. Run 'orc index' or 'orc analyse' first."
            }
            click.echo(json.dumps(result))
        return

    # Create a simple index for the analyzer
    index = {}
    for module_path, module_info in modules.items():
        for func_name, func_info in module_info.functions.items():
            func_id = f"{module_path}::{func_name}"
            index[func_id] = {
                'name': func_name,
                'file': module_path,
                'complexity': func_info.complexity,
                'code': _extract_function_code(module_path, func_info)
            }

    analyzer = ComplexityAnalyzer(index, None)
    complex_functions = analyzer.get_complex_functions(threshold=threshold)

    if not complex_functions:
        if not quiet_mode:
            console.print(f"[green]No functions found with complexity >= {threshold}.[/green]")
        elif output_json:
            import json
            result = {"complex_functions": []}
            click.echo(json.dumps(result))
        return

    if output_json:
        import json
        # Convert complex objects to serializable format
        serialized_functions = []
        for report in complex_functions[:20]:  # Show top 20
            serialized_functions.append({
                "function": report.function,
                "file": report.file,
                "time_complexity": report.time_complexity,
                "space_complexity": report.space_complexity,
                "score": report.complexity_score
            })
        result = {"complex_functions": serialized_functions}
        click.echo(json.dumps(result))
    elif not quiet_mode:
        console.print(f"[bold]Functions with complexity >= {threshold}:[/bold]")
        table = Table()
        table.add_column("Function", style="cyan")
        table.add_column("File", style="magenta")
        table.add_column("Time Complexity", style="red")
        table.add_column("Space Complexity", style="green")
        table.add_column("Score", justify="right")

        for report in complex_functions[:20]:  # Show top 20
            table.add_row(
                report.function,
                report.file,
                report.time_complexity,
                report.space_complexity,
                str(report.complexity_score)
            )

        console.print(table)
        
        # Show ORC Verdict
        console.print("")
        from orc.verdict_formatter import OrcVerdict
        stats = {
            'average_complexity': sum(r.complexity_score for r in complex_functions) / len(complex_functions) if complex_functions else 0,
            'max_complexity': max((r.complexity_score for r in complex_functions), default=0),
            'critical_count': len([r for r in complex_functions if r.complexity_score >= 20]),
            'high_count': len([r for r in complex_functions if 10 <= r.complexity_score < 20]),
            'total_functions': len(modules)
        }
        OrcVerdict.complexity_verdict(stats)

@cli.command()
@click.argument('target', required=False)
def ignore(target):
    """Ignore code permanently"""
    from orc_package.config.settings import load_config
    import yaml
    import os

    cfg = load_config("config.yaml")
    config_file = ".orcrc"

    # Create config if doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            yaml.dump({'ignore': [], 'dynamic_patterns': []}, f)

    # Load config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    if target:
        # Add to ignore list
        if target not in config['ignore']:
            config['ignore'].append(target)
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            console.print(f"[green]+[/green] Added {target} to ignore list")
        else:
            console.print(f"[yellow]{target} already ignored[/yellow]")
    else:
        # Show current ignore list
        console.print("[bold]Current ignore list:[/bold]")
        for item in config['ignore']:
            console.print(f"- {item}")

@cli.command()
def init():
    """Create an ORC configuration file"""
    import yaml
    import os

    config_file = ".orcrc"

    if os.path.exists(config_file):
        console.print(f"[yellow]{config_file} already exists[/yellow]")
        return

    # Create default config
    config = {
        'ignore': ['src/experimental/*'],
        'dynamic_patterns': ['eval', 'reflection']
    }

    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    console.print(f"[green]+[/green] Created {config_file}")
    console.print("[dim]Edit to customize ignore rules and dynamic patterns[/dim]")

@cli.command()
@click.argument('action', required=False)
@click.argument('category', required=False)
@click.argument('value', required=False)
def config(action, category, value):
    """View or modify ORC configuration"""
    import yaml
    import os

    config_file = ".orcrc"

    if not os.path.exists(config_file):
        console.print("[red]No config found. Run 'orc init' first.[/red]")
        return

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    if not action or action == 'show':
        # Show current config
        console.print("[bold]Current ORC Configuration:[/bold]")
        console.print("\n[bold]Ignore rules:[/bold]")
        for item in config.get('ignore', []):
            console.print(f"- {item}")

        console.print("\n[bold]Dynamic patterns:[/bold]")
        for item in config.get('dynamic_patterns', []):
            console.print(f"- {item}")

    elif action == 'add' and category and value:
        # Add to config
        if category in ['ignore', 'dynamic']:
            if category not in config:
                config[category] = []

            if value not in config[category]:
                config[category].append(value)
                with open(config_file, 'w') as f:
                    yaml.dump(config, f)
                console.print(f"[green]+[/green] Added {value} to {category}")
            else:
                console.print(f"[yellow]{value} already in {category}[/yellow]")
        else:
            console.print(f"[red]Unknown category: {category}[/red]")

    else:
        console.print("[red]Usage: orc config [show|add <category> <value>][/red]")

def _display_analysis_report(report: dict):
    """Display analysis report in terminal"""
    console = Console()


def _search_multilanguage_index(index: dict, query: str):
    """Search the multi-language index stored in the database.

    This performs a simple keyword search across function names,
    class names and file paths, regardless of language. It uses only
    the data produced by the parsers and saved by ``orc analyse``.
    """
    q = query.lower().strip()
    if not q:
        return []

    results = []

    files = index.get('files', {}) or {}
    functions = index.get('functions', {}) or {}
    classes = index.get('classes', {}) or {}

    # Search functions
    for fid, fmeta in functions.items():
        name = str(fmeta.get('name', ''))
        if q in name.lower():
            file_path = str(fmeta.get('file', ''))
            lang = (files.get(file_path, {}) or {}).get('language', 'unknown')
            results.append({
                'kind': 'function',
                'name': name,
                'file': file_path,
                'language': lang,
            })

    # Search classes
    for cid, cmeta in classes.items():
        name = str(cmeta.get('name', ''))
        if q in name.lower():
            file_path = str(cmeta.get('file', ''))
            lang = (files.get(file_path, {}) or {}).get('language', 'unknown')
            results.append({
                'kind': 'class',
                'name': name,
                'file': file_path,
                'language': lang,
            })

    # Search file paths / names
    for file_path, meta in files.items():
        filename = Path(file_path).name.lower()
        if q in filename:
            results.append({
                'kind': 'file',
                'name': Path(file_path).name,
                'file': file_path,
                'language': meta.get('language', 'unknown'),
            })

    # Deduplicate (favour more specific function/class hits over file hits)
    seen = set()
    uniq = []
    for r in results:
        key = (r['kind'], r['file'], r['name'])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    return uniq

    # Dead code results
    dead_code = report.get('dead_code', None)
    if dead_code and dead_code.unused_functions:
        table = Table(title="Dead Code - Unused Functions")
        table.add_column("Function", style="cyan")
        table.add_column("File", style="magenta")
        table.add_column("Lines", justify="right", style="green")
        table.add_column("Complexity", justify="right", style="red")

        for func in dead_code.unused_functions[:20]:  # Top 20
            table.add_row(
                func.get('function', 'N/A'),
                Path(func.get('file', '')).name,
                str(func.get('lines', 0)),
                str(func.get('complexity', 0))
            )

        console.print(table)

    # Complexity results
    metrics = report.get('metrics', {})
    if metrics:
        complex_funcs = []
        for func_id, func_metrics in metrics.get('functions', {}).items():
            if func_metrics.get('complexity', 0) > 10:  # Threshold
                complex_funcs.append(func_metrics)

        if complex_funcs:
            table = Table(title="High Complexity Functions")
            table.add_column("Function", style="cyan")
            table.add_column("File", style="magenta")
            table.add_column("Complexity", justify="right", style="red")
            table.add_column("Lines", justify="right", style="green")

            for func in sorted(complex_funcs, key=lambda x: x['complexity'], reverse=True)[:20]:
                table.add_row(
                    func.get('name', 'N/A'),
                    Path(func.get('file', '')).name,
                    str(func.get('complexity', 0)),
                    str(func.get('lines_of_code', 0))
                )

            console.print(table)

    # Summary
    summary = report.get('summary', {})
    if summary:
        console.print(f"\n[bold]Analysis Summary:[/bold]")
        console.print(f"  Total files: {summary.get('total_files', 0)}")
        console.print(f"  Total functions: {summary.get('total_functions', 0)}")
        console.print(f"  Total lines: {summary.get('total_lines', 0)}")

@cli.command()
@click.pass_context
@click.argument('query')
@click.option('--config', default='config.yaml', help='Config file path')
def query(ctx, query, config):
    """Query the codebase using natural language + multi-language index.

    Special queries ("circular dependencies", "dead code", "metrics",
    etc.) are handled by the Python-aware QueryEngine over the AST index
    stored in the SQLite DB. For more free-form searches, we fall back to
    a multi-language search over the compressed index produced by all
    parsers and saved by ``orc analyse``.
    """
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    format = ctx.obj.get('FORMAT', 'table')

    from orc_package.config.settings import load_config
    from orc.storage.graph_db import GraphStorage
    from orc_package.agent.query_engine import QueryEngine  # agent directory in orc_package
    from orc.core.graph_builder import DependencyGraph

    cfg = load_config(config)
    storage = GraphStorage(cfg.index_path)

    # Load Python AST index and dependency graph from DB
    modules = storage.load_modules()
    graph = storage.load_graph('dependency')
    if graph is None and modules:
        # If no stored graph is available (first run or DB reset),
        # rebuild it once from the modules. Normal usage relies on the
        # graph persisted by the indexer.
        graph = DependencyGraph()
        graph.build_from_modules(modules)

    # Load latest multi-language index if present
    ml_results = storage.load_analysis_results('multi_language_index') or []
    ml_index = ml_results[0] if ml_results else None

    engine = QueryEngine(cfg, modules, graph)
    result = engine.process_query(query)

    # If QueryEngine didn't understand the query and we have a
    # multi-language index, try a generic search over all parsed files.
    if result.result_type == 'help' and ml_index:
        matches = _search_multilanguage_index(ml_index, query)
        if matches:
            if output_json:
                import json
                result_data = {
                    "query": query,
                    "matches": matches,
                    "result_type": "multilanguage_search"
                }
                click.echo(json.dumps(result_data))
            elif not quiet_mode:
                console.print(f"[bold blue]Query (multi-language search):[/bold blue] {query}")
                console.print(f"[bold green]Matches:[/bold green]")
                table = Table()
                table.add_column("Type", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("File", style="green")
                table.add_column("Language", style="yellow")
                for m in matches[:30]:  # Limit display
                    table.add_row(
                        m.get('kind', ''),
                        m.get('name', ''),
                        m.get('file', ''),
                        m.get('language', ''),
                    )
                console.print(table)
            return

    if output_json:
        import json
        result_data = {
            "query": query,
            "result_type": result.result_type,
            "data": result.data
        }
        click.echo(json.dumps(result_data))
    elif not quiet_mode:
        console.print(f"[bold blue]Query:[/bold blue] {query}")
        console.print(f"[bold green]Result:[/bold green]")

        if result.result_type == 'list':
            table = Table()
            table.add_column("Item", style="cyan")
            for item in result.data[:20]:  # Limit results
                if isinstance(item, dict):
                    table.add_row(str(item))
                else:
                    table.add_row(str(item))
            console.print(table)
        elif result.result_type == 'metric':
            for key, value in result.data.items():
                console.print(f"  {key}: {value}")
        elif result.result_type == 'help':
            console.print("Available queries:")
            for q in result.data.get('available_queries', []):
                console.print(f"  • {q}")
        else:
            console.print(result.data)

@cli.command()
@click.pass_context
@click.option('--limit', default=10, help='Maximum number of hotspots to show')
def hotspots(ctx, limit):
    """Identify complexity hotspots and problem areas in the codebase."""
    output_json = ctx.obj.get('OUTPUT_JSON', False)
    quiet_mode = ctx.obj.get('QUIET_MODE', False)
    
    from orc.storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc.tools.codebase_mapper import CodebaseMapper
    from orc.utils.module_filter import filter_modules
    
    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)
    
    modules = storage.load_modules()
    # Filter out .venv and other ignored paths
    modules = filter_modules(modules)
    
    if not modules:
        if not quiet_mode:
            console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
        elif output_json:
            import json
            result = {"error": "No indexed modules found"}
            click.echo(json.dumps(result))
        return
    
    mapper = CodebaseMapper(cfg.index_path)
    hotspots_data = mapper.get_hotspots(limit=limit)
    
    if output_json:
        import json
        click.echo(json.dumps(hotspots_data))
    elif not quiet_mode:
        console.print("\n[bold cyan]Complexity Hotspots[/bold cyan]")
        complexity_hotspots = hotspots_data.get('complexity_hotspots', [])
        if complexity_hotspots:
            for i, item in enumerate(complexity_hotspots, 1):
                console.print(f"{i}. [red]{item.get('file_path', 'unknown')}[/red]")
                console.print(f"   Complex Functions: {item.get('complex_functions', 0)}")
                console.print(f"   Avg Complexity: {item.get('avg_complexity', 0):.2f}")
                console.print(f"   Max Complexity: {item.get('max_complexity', 0)}")
                console.print()
        else:
            console.print("[green]No complexity hotspots found.[/green]\n")
        
        console.print("[bold cyan]Large Files[/bold cyan]")
        large_files = hotspots_data.get('large_files', [])
        if large_files:
            for i, item in enumerate(large_files, 1):
                console.print(f"{i}. [yellow]{item.get('path', 'unknown')}[/yellow]")
                console.print(f"   Lines: {item.get('loc', 0)}")
                console.print(f"   Language: {item.get('language', 'unknown')}")
                console.print()
        else:
            console.print("[green]No large files found.[/green]\n")
        
        console.print("[bold cyan]Coupling Hotspots (Most Imported)[/bold cyan]")
        coupling_hotspots = hotspots_data.get('coupling_hotspots', [])
        if coupling_hotspots:
            for i, item in enumerate(coupling_hotspots, 1):
                console.print(f"{i}. [magenta]{item.get('module', 'unknown')}[/magenta]")
                console.print(f"   Imported By: {item.get('imported_by_count', 0)} files")
                console.print()
        else:
            console.print("[green]No coupling hotspots found.[/green]\n")
        
        # Show ORC Verdict
        console.print("")
        from orc.verdict_formatter import OrcVerdict
        OrcVerdict.hotspots_verdict(hotspots_data)


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host for web server')
@click.option('--port', default=5000, help='Port for web server')
def serve(host, port):
    """Start the web interface"""
    console.print("[yellow]Web interface has been archived.[/yellow]")
    console.print("[blue]The web app is available in archive/orc_web_flask/[/blue]")
    console.print("[blue]To run it: cd archive/orc_web_flask && python app_new.py[/blue]")
    return
    
    # Note: Web module has been archived
    # try:
    #     from orc.web.app import app
    #     console.print(f"[bold blue]Starting web server at http://{host}:{port}[/bold blue]")
    #     app.run(host=host, port=port, debug=True)
    # except ImportError as e:
    #     console.print(f"[red]Error starting web server:[/red] {e}")
    #     console.print("[yellow]Make sure the web dependencies are installed.[/yellow]")




if __name__ == '__main__':
    cli()
