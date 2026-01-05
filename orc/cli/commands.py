"""
Command Line Interface
"""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

@click.group()
def cli():
    """ORC - Codebase Intelligence Agent"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', default='config.yaml', help='Config file path')
def index(path, config):
    """Index a codebase"""
    from core.indexer import PythonIndexer
    from core.graph_builder import DependencyGraph
    from config.settings import load_config
    from storage.graph_db import GraphStorage
    
    cfg = load_config(config)
    cfg.project_root = Path(path)
    
    console.print(f"[bold blue]Indexing codebase at:[/bold blue] {path}")
    
    # Index files
    indexer = PythonIndexer(cfg)
    modules = indexer.index_directory(Path(path))
    
    console.print(f"[green]✓[/green] Indexed {len(modules)} modules")
    
    # Build graph
    graph = DependencyGraph()
    graph.build_from_modules(modules)
    
    console.print(f"[green]✓[/green] Built dependency graph")
    
    # Store
    storage = GraphStorage(cfg.index_path)
    storage.save(modules, graph)
    
    console.print(f"[green]✓[/green] Saved index to {cfg.index_path}")

@cli.command()
@click.option('--config', default='config.yaml')
def analyze(config):
    """Analyze codebase for dead code"""
    from config.settings import load_config
    from storage.graph_db import GraphStorage
    from analysis.dead_code import DeadCodeAnalyzer
    
    cfg = load_config(config)
    storage = GraphStorage(cfg.index_path)
    modules, graph = storage.load()
    
    console.print("[bold blue]Analyzing codebase...[/bold blue]")
    
    analyzer = DeadCodeAnalyzer(graph, modules)
    report = analyzer.analyze()
    
    # Display results
    _display_dead_code_report(report)

def _display_dead_code_report(report: 'DeadCodeReport'):
    """Display dead code report in terminal"""
    
    # Unused functions table
    if report.unused_functions:
        table = Table(title="Unused Functions")
        table.add_column("Function", style="cyan")
        table.add_column("File", style="magenta")
        table.add_column("Lines", justify="right", style="green")
        
        for func in report.unused_functions[:20]:  # Top 20
            table.add_row(
                func['function'],
                Path(func['file']).name,
                str(func['lines'])
            )
        
        console.print(table)
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Unused functions: {len(report.unused_functions)}")
    console.print(f"  Unused exports: {len(report.unused_exports)}")
    console.print(f"  Unused files: {len(report.unused_files)}")
    console.print(f"  [green]Estimated lines saved: {report.estimated_lines_saved}[/green]")

@cli.command()
@click.argument('query')
@click.option('--config', default='config.yaml')
def query(query, config):
    """Query the codebase"""
    from agent.query_engine import QueryEngine
    from config.settings import load_config
    from storage.graph_db import GraphStorage
    
    cfg = load_config(config)
    storage = GraphStorage(cfg.index_path)
    modules, graph = storage.load()
    
    engine = QueryEngine(modules, graph)
    result = engine.process_query(query)
    
    console.print(result)

if __name__ == '__main__':
    cli()
