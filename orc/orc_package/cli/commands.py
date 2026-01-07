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


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=ORC_VERSION, prog_name="ORC")
def cli(ctx):
    """ORC - Codebase Intelligence Agent"""
    # Show banner and chat interface if no subcommand is provided
    if ctx.invoked_subcommand is None:
        console.print(ORC_BANNER, style="bold green")
        start_chat_interface()
    # Banner is shown only on first index/analyse via _maybe_show_welcome


def start_chat_interface():
    """Start an interactive chat-like interface for ORC commands."""
    # Print the banner with enhanced styling
    console.print(ORC_BANNER, style="bold green")

    # Add a separator line
    console.print("[bold blue]" + "="*60 + "[/bold blue]")

    # Welcome message with ASCII art
    welcome_art = r"""
    ╭─────────────────────────────────────────────────╮
    │  🤖  Welcome to ORC Interactive Mode! 🤖        │
    │                                                 │
    │  I'm your AI-powered code analysis assistant.   │
    │  Ask me about your codebase or type 'help'.     │
    ╰─────────────────────────────────────────────────╯
    """
    console.print(welcome_art, style="bold yellow")

    console.print("\n[bold cyan]Examples of what you can ask:[/bold cyan]")
    console.print("  🟢 'find complex functions'")
    console.print("  🔴 'show dead code'")
    console.print("  🟡 'analyze performance'")
    console.print("  🔵 'suggest optimizations'")
    console.print("  ❌ 'quit' or 'exit' to leave\n")

    # Add a separator line
    console.print("[bold blue]" + "="*60 + "[/bold blue]")

    while True:
        try:
            user_input = input("[bold magenta]ORC> [/bold magenta]").strip()

            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                goodbye_art = r"""
    ╭─────────────────────────────────────────╮
    │  👋 Goodbye! Thanks for using ORC! 👋  │
    │                                         │
    │      May your code be clean & fast!     │
    ╰─────────────────────────────────────────╯
                """
                console.print(goodbye_art, style="bold yellow")
                break
            elif user_input.lower() in ['help', 'h', '?', 'commands']:
                show_help()
            elif user_input.lower() in ['banner', 'art']:
                console.print(ORC_BANNER, style="bold green")
            elif user_input.lower() in ['version', 'ver']:
                version_art = r"""
    ╔══════════════════════════════════════════════════╗
    ║              🤖 ORC VERSION INFO 🤖             ║
    ║                                                  ║
    ║                 Version: 1.0.0                  ║
    ║         AI-Powered Code Analysis Tool            ║
    ║        Optimization & Refactoring Catalyst       ║
    ╚══════════════════════════════════════════════════╝
                """
                console.print(version_art, style="bold cyan")
            else:
                # Process natural language input to determine appropriate command
                console.print(f"[cyan]Processing: {user_input}...[/cyan]")
                command_executed = process_natural_language_command(user_input)
                if not command_executed:
                    console.print(f"[yellow]I can help you with code analysis. Try:[/yellow]")
                    console.print("  🟢 'find complex functions'")
                    console.print("  🔴 'show dead code'")
                    console.print("  🟡 'analyze performance'")
                    console.print("  🔵 'suggest optimizations'")

        except (KeyboardInterrupt, EOFError):
            goodbye_art = r"""
    ╭─────────────────────────────────────────╮
    │  👋 Goodbye! Thanks for using ORC! 👋  │
    │                                         │
    │      May your code be clean & fast!     │
    ╰─────────────────────────────────────────╯
                """
            console.print("\n")
            console.print(goodbye_art, style="bold yellow")
            break


def process_natural_language_command(user_input: str) -> bool:
    """Process natural language input and execute appropriate command."""
    user_lower = user_input.lower()

    # Determine intent based on keywords
    if any(keyword in user_lower for keyword in ['analyze', 'analysis', 'full', 'complete']):
        console.print("[yellow]Running analysis...[/yellow]")
        # Execute the analyze command directly
        try:
            analyse(file=None, config="config.yaml")
        except Exception as e:
            console.print(f"[red]Error running analysis: {str(e)}[/red]")
        return True
    elif any(keyword in user_lower for keyword in ['complex', 'complexity', 'performance', 'slow', 'bottleneck']):
        console.print("[yellow]Looking for complex functions...[/yellow]")
        # Execute the complexity command directly
        try:
            complexity(threshold=10)
        except Exception as e:
            console.print(f"[red]Error running complexity analysis: {str(e)}[/red]")
        return True
    elif any(keyword in user_lower for keyword in ['dead', 'unused', 'unreachable', 'remove']):
        console.print("[yellow]Searching for dead code...[/yellow]")
        # Execute the dead command directly
        try:
            dead()
        except Exception as e:
            console.print(f"[red]Error running dead code analysis: {str(e)}[/red]")
        return True
    elif any(keyword in user_lower for keyword in ['optimize', 'optimization', 'improve', 'better']):
        console.print("[yellow]Looking for optimization opportunities...[/yellow]")
        # Execute the optimize command directly
        try:
            optimize(file=None, function=None, threshold=10)
        except Exception as e:
            console.print(f"[red]Error running optimization analysis: {str(e)}[/red]")
        return True
    elif any(keyword in user_lower for keyword in ['query', 'find', 'search', 'show', 'where', 'what']):
        # Extract the actual query by removing common prefixes
        query_text = user_lower
        for prefix in ['query', 'find', 'search', 'show', 'where is', 'what is']:
            if query_text.startswith(prefix):
                query_text = query_text[len(prefix):].strip()
                break

        if query_text:
            console.print(f"[yellow]Querying for: {query_text}[/yellow]")
            # Execute the query command directly
            try:
                query(query=query_text, config="config.yaml")
            except Exception as e:
                console.print(f"[red]Error running query: {str(e)}[/red]")
            return True
        else:
            console.print("[red]Please provide a query. Example: 'find authentication code'[/red]")
            return False
    else:
        # Default to query if we can't determine the intent
        console.print(f"[yellow]Querying for: {user_input}[/yellow]")
        try:
            query(query=user_input, config="config.yaml")
        except Exception as e:
            console.print(f"[red]Error running query: {str(e)}[/red]")
        return True


def show_help():
    """Display help information for the chat interface."""
    help_art = r"""
    ╭─────────────────────────────────────────────────────╮
    │                📚 ORC COMMANDS GUIDE 📚             │
    ╰─────────────────────────────────────────────────────╯
    """
    console.print(help_art, style="bold blue")

    console.print("\n[bold yellow]🔍 ANALYSIS COMMANDS:[/bold yellow]")
    console.print("  [green]analyze[/green]           - Run full code analysis")
    console.print("  [green]complex[/green]           - Find complex functions")
    console.print("  [green]dead[/green]              - Find dead/unused code")
    console.print("  [green]optimize[/green]          - Get optimization suggestions")
    console.print("  [green]query <text>[/green]      - Natural language query")

    console.print("\n[bold yellow]⚙️  UTILITY COMMANDS:[/bold yellow]")
    console.print("  [green]help[/green]              - Show this help")
    console.print("  [green]banner[/green]            - Show the ORC banner")
    console.print("  [green]version[/green]           - Show ORC version")

    console.print("\n[bold yellow]🚪 EXIT COMMANDS:[/bold yellow]")
    console.print("  [green]quit/exit/q/bye[/green]  - Exit interactive mode\n")

    console.print("[bold cyan]💡 TIP: You can also use natural language like:[/bold cyan]")
    console.print("  • 'Find functions that are too complex'")
    console.print("  • 'Show me dead code in my project'")
    console.print("  • 'How can I optimize this code?'")
    console.print("  • 'What are the performance bottlenecks?'\n")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', default='config.yaml', help='Config file path')
def index(path, config):
    """Index a codebase (Python + all supported language parsers)."""
    from orc_package.config.settings import load_config
    from ..core.index_service import IndexService

    cfg = load_config(config)
    cfg.project_root = Path(path)

    _maybe_show_welcome(cfg.project_root)

    console.print(f"[bold blue]Indexing codebase at:[/bold blue] {path}")

    service = IndexService(cfg)
    service.index_project(Path(path))

    console.print("[green]✓[/green] Indexing complete. Database updated at " + str(cfg.index_path))

@cli.command()
@click.argument('file', required=False)
@click.option('--config', default='config.yaml', help='Config file path')
def analyse(file, config):
    """Run full analysis on the codebase.

    This will (re)index the project using all parsers, then run the
    Python analyzers (dead code, dependencies, metrics, patterns) on the
    stored index.
    """
    from orc_package.config.settings import load_config
    from core.index_service import IndexService
    from storage.graph_db import GraphStorage
    from core.analyzer import Analyzer

    cfg = load_config(config)
    service = IndexService(cfg)

    _maybe_show_welcome(cfg.project_root)

    # Kick off indexing first so DB + graphs + multi-language index are fresh
    if file:
        console.print(f"[bold blue]Analyzing file: {file} (full index still runs for context)[/bold blue]")
        with console.status("[bold blue]Indexing project...[/bold blue]", spinner="dots"):
            service.index_project()
    else:
        # Professional, compact status indicator instead of ad-hoc dot
        # printing and per-file spam.
        with console.status("[bold blue]Analyzing entire codebase...[/bold blue]", spinner="dots"):
            service.index_project()

    # Load modules from DB and run analyzers
    storage = GraphStorage(cfg.index_path)
    modules = storage.load_modules()

    analyzer = Analyzer(cfg)
    report = analyzer.run_all(modules)

    console.print("[green]+[/green] Analysis complete (index + Python analyzers)")
    return report

@cli.command()
def dead():
    """Show dead / unused code (runs fresh analysis)."""
    from storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc_package.analysis.dead_code import DeadCodeAnalyzer

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    if not modules:
        console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
        return

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
        console.print("[green]No dead code found.")
        return

    console.print("[bold]Dead Code Findings:[/bold]")
    for i, finding in enumerate(findings[:20], 1):  # Show top 20
        func_name = finding.get('function', 'unknown')
        file_path = finding.get('file', 'unknown')
        console.print(f"[D-{i:02d}] {file_path} - {func_name}")

    if len(findings) > 20:
        console.print(f"[dim]... and {len(findings) - 20} more findings[/dim]")

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
    from storage.graph_db import GraphStorage
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

        console.print(f"[green]+[/green] Marked {file_path}::{func_name} for deletion")
        console.print("[dim]Note: Actual file modification not implemented in v1[/dim]")
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

    # In v1, we just mark as deleted (actual deletion is not yet wired).
    for finding in candidates:
        file_path = finding.get('file', 'unknown')
        func_name = finding.get('function', 'unknown')
        console.print(f"[green]+[/green] Marked {file_path}::{func_name} for deletion")

    console.print("[dim]Note: Actual file modification not implemented in v1[/dim]")


@cli.command()
@click.option('--file', default=None, help='Specific file to analyze for optimizations')
@click.option('--function', default=None, help='Specific function to analyze for optimizations')
@click.option('--threshold', default=10, help='Minimum complexity threshold for optimization suggestions')
def optimize(file, function, threshold):
    """Get optimization suggestions for complex functions."""
    from storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc_package.optimization.suggester import Suggester
    from orc_package.analysis.complexity import ComplexityAnalyzer
    from core.analyzer import Analyzer

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

    for func_data in complex_functions[:20]:  # Show top 20
        file_path = func_data['file']
        func_name = func_data['function']
        complexity = func_data['complexity']

        # Extract function code
        code = _extract_function_code(file_path, func_data['info'])

        # Get optimization suggestions
        suggester = Suggester()
        result = suggester.suggest(file_path, func_name, code)

        console.print(f"\n[blue]{func_name}[/blue] in [green]{file_path}[/green] (complexity: {complexity})")
        console.print(f"  Suggestion: {result['suggestion']}")
        console.print(f"  Estimated improvement: {result['estimated_improvement']:.2f}")


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
@click.option('--threshold', default=10, help='Minimum complexity threshold for reporting')
def complexity(threshold):
    """Show high complexity functions in the codebase."""
    from storage.graph_db import GraphStorage
    from orc_package.config.settings import load_config
    from orc_package.analysis.complexity import ComplexityAnalyzer

    cfg = load_config("config.yaml")
    storage = GraphStorage(cfg.index_path)

    modules = storage.load_modules()
    if not modules:
        console.print("[yellow]No indexed modules found. Run 'orc index' or 'orc analyse' first.[/yellow]")
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
        console.print(f"[green]No functions found with complexity >= {threshold}.[/green]")
        return

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
@click.argument('query')
@click.option('--config', default='config.yaml', help='Config file path')
def query(query, config):
    """Query the codebase using natural language + multi-language index.

    Special queries ("circular dependencies", "dead code", "metrics",
    etc.) are handled by the Python-aware QueryEngine over the AST index
    stored in the SQLite DB. For more free-form searches, we fall back to
    a multi-language search over the compressed index produced by all
    parsers and saved by ``orc analyse``.
    """
    from orc_package.config.settings import load_config
    from storage.graph_db import GraphStorage
    from orc_package.agent.query_engine import QueryEngine
    from ..core.graph_builder import DependencyGraph

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
@click.option('--host', default='127.0.0.1', help='Host for web server')
@click.option('--port', default=5000, help='Port for web server')
def serve(host, port):
    """Start the web interface"""
    try:
        from web.app import app
        console.print(f"[bold blue]Starting web server at http://{host}:{port}[/bold blue]")
        app.run(host=host, port=port, debug=True)
    except ImportError as e:
        console.print(f"[red]Error starting web server:[/red] {e}")
        console.print("[yellow]Web interface not fully implemented.[/yellow]")


@cli.command()
@click.argument('prompt', required=False)
@click.option('--model', default='llama-3.1-8b-instant', show_default=True,
              help='Groq model name to use for ORC AI')
@click.option('--no-context', is_flag=True,
              help='Do not include indexed code context in the AI request')
@click.option('--config', default='config.yaml', show_default=True,
              help='Config file path used to locate the index DB')
def ai(prompt, model, no_context, config):
    """Talk to ORC AI powered by Groq.

    Examples:

    \b
    # One-shot question about your codebase
    orc ai "why is my dead code detection flagging X?"

    # Use a different Groq model
    orc ai "summarise this repo" --model llama-3.1-70b-versatile

    # Pure chat with no code context
    orc ai "write a bash one-liner" --no-context
    """
    import os

    try:
        from groq import Groq  # type: ignore[import]
    except ImportError:
        console.print(
            "[red]groq Python package is not installed.[/red] "
            "Install it with: [italic]pip install groq[/italic]"
        )
        return

    from orc_package.config.settings import load_config
    from core.index_service import IndexService

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        console.print(
            "[red]GROQ_API_KEY environment variable is not set.[/red] "
            "Set it to your Groq API key before running 'orc ai'."
        )
        return

    cfg = load_config(config)
    service = IndexService(cfg)

    client = Groq(api_key=api_key)

    def _run_once(user_prompt: str) -> None:
        # Optionally build ORC context for the prompt
        context_block = ""
        if not no_context:
            ctx = service.build_context(user_prompt, max_tokens=6000)
            snippets = []
            for fn in ctx.get('functions', []):
                header = (
                    f"### {fn.get('kind', 'symbol')} {fn.get('name', '')} "
                    f"({fn.get('file', '')}:{fn.get('line_start', 1)}-"
                    f"{fn.get('line_end', 1)})"
                )
                code = fn.get('code', '')
                snippets.append(header + "\n" + code)
            context_block = "\n\n".join(snippets)

        messages = [
            {
                'role': 'system',
                'content': (
                    "You are ORC AI, an assistant for understanding and "
                    "refactoring the user's codebase. When helpful, suggest "
                    "concrete code changes and CLI commands (like 'orc "
                    "analyse', 'orc dead', 'orc delete D-02 --confidence 95'). "
                    "Do not execute commands yourself; just describe them."
                ),
            },
            {
                'role': 'user',
                'content': (
                    f"User query:\n{user_prompt}\n\n"
                    f"Code context (may be empty):\n{context_block}"
                ),
            },
        ]

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as e:  # pragma: no cover - network/runtime issues
            console.print(f"[red]Error calling Groq API:[/red] {e}")
            return

        content = ''
        try:
            choice = resp.choices[0]
            content = getattr(choice.message, 'content', '') or ''
        except Exception:
            pass

        if not content:
            console.print("[yellow]No content returned from Groq.[/yellow]")
            return

        console.print(content)

    # If prompt is provided, run once; otherwise enter an interactive loop
    if prompt:
        _run_once(prompt)
    else:
        console.print(
            "[bold green]ORC AI interactive mode.[/bold green] "
            "Type 'exit' or 'quit' to leave."
        )
        while True:
            try:
                user = input("orc-ai> ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
            if not user or user.lower() in {"exit", "quit"}:
                break
            _run_once(user)


if __name__ == '__main__':
    cli()
