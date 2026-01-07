"""
ORC CLI: Terminal Visualizer
"""
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from typing import Dict, List, Any

class Visualizer:
    """Terminal visualizations using Rich library"""

    def __init__(self):
        self.console = Console()

    def show_table(self, title: str, headers: List[str], rows: List[List[Any]], 
                   header_styles: List[str] = None):
        """Display data in a Rich table"""
        table = Table(title=title)
        
        # Add headers
        for i, header in enumerate(headers):
            style = header_styles[i] if header_styles and i < len(header_styles) else "bold"
            table.add_column(header, style=style)
        
        # Add rows
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)

    def show_dead_code_report(self, report: Dict):
        """Visualize dead code report"""
        # Show unused functions
        if report.get('unused_functions'):
            self.console.print("\n[bold red]Unused Functions:[/bold red]")
            table = Table()
            table.add_column("Function", style="cyan")
            table.add_column("File", style="magenta")
            table.add_column("Lines", justify="right")
            table.add_column("Complexity", justify="right", style="red")
            
            for func in report['unused_functions'][:20]:  # Show top 20
                table.add_row(
                    func.get('function', 'N/A'),
                    func.get('file', 'N/A'),
                    str(func.get('lines', 0)),
                    str(func.get('complexity', 0))
                )
            
            self.console.print(table)
        
        # Show unused files
        if report.get('unused_files'):
            self.console.print(f"\n[bold red]Unused Files:[/bold red] ({len(report['unused_files'])} files)")
            for file_path in report['unused_files'][:10]:  # Show top 10
                self.console.print(f"  • {file_path}")
            if len(report['unused_files']) > 10:
                self.console.print(f"  ... and {len(report['unused_files']) - 10} more")

    def show_metrics_report(self, metrics: Dict):
        """Visualize code metrics"""
        self.console.print("\n[bold blue]Code Metrics:[/bold blue]")
        
        # Overall metrics
        overall = metrics.get('overall', {})
        if overall:
            self.console.print(f"  Total Files: {overall.get('total_files', 0)}")
            self.console.print(f"  Total Lines: {overall.get('total_lines', 0)}")
            self.console.print(f"  Total Functions: {overall.get('total_functions', 0)}")
            self.console.print(f"  Average Complexity: {overall.get('avg_complexity', 0):.2f}")
        
        # Complex functions
        functions = metrics.get('functions', {})
        complex_funcs = []
        for func_id, func_metrics in functions.items():
            if func_metrics.get('complexity', 0) > 10:  # Threshold
                complex_funcs.append(func_metrics)
        
        if complex_funcs:
            self.console.print(f"\n[bold red]High Complexity Functions (>10):[/bold red]")
            table = Table()
            table.add_column("Function", style="cyan")
            table.add_column("File", style="magenta")
            table.add_column("Complexity", justify="right", style="red")
            
            for func in sorted(complex_funcs, key=lambda x: x['complexity'], reverse=True)[:10]:
                table.add_row(
                    func.get('name', 'N/A'),
                    func.get('file', 'N/A'),
                    str(func.get('complexity', 0))
                )
            
            self.console.print(table)

    def show_dependencies(self, deps_data: Dict):
        """Visualize dependency information"""
        self.console.print("\n[bold blue]Dependencies:[/bold blue]")
        
        # Show circular dependencies if any
        if deps_data.get('circular_dependencies'):
            self.console.print("[bold red]Circular Dependencies:[/bold red]")
            for cycle in deps_data['circular_dependencies']:
                self.console.print(f"  • {' -> '.join(cycle)}")

    def show_recommendations(self, recommendations: List[Dict]):
        """Visualize recommendations"""
        if not recommendations:
            self.console.print("\n[bold green]No recommendations at this time.[/bold green]")
            return

        self.console.print(f"\n[bold blue]Recommendations ({len(recommendations)}):[/bold blue]")
        
        for i, rec in enumerate(recommendations[:10]):  # Show top 10
            priority = rec.get('priority', 'N/A').upper()
            color = "red" if priority == "CRITICAL" else "yellow" if priority == "HIGH" else "blue"
            
            self.console.print(f"\n[{color}]{i+1}. {rec.get('title', 'N/A')} [/{color}]")
            self.console.print(f"   Description: {rec.get('description', 'N/A')}")
            self.console.print(f"   Priority: [{color}]{priority}[/{color}]")
            self.console.print(f"   Impact: {rec.get('impact', 'N/A')}")
            self.console.print(f"   Effort: {rec.get('effort', 'N/A')}")

    def show_code_structure(self, modules: Dict):
        """Visualize code structure as a tree"""
        self.console.print("\n[bold blue]Code Structure:[/bold blue]")
        
        # Group files by directory
        dirs = {}
        for path in modules.keys():
            parts = Path(path).parts
            current = dirs
            for part in parts[:-1]:  # All parts except the file name
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = True  # Mark file
        
        # Build tree visualization
        def build_tree(node, prefix=""):
            tree = Tree(prefix) if prefix else Tree("Project Root")
            for key, value in node.items():
                if isinstance(value, dict):
                    subtree = build_tree(value, key)
                    tree.add(subtree)
                else:
                    tree.add(key)
            return tree
        
        tree = build_tree(dirs)
        self.console.print(tree)

    def show_summary(self, summary: Dict):
        """Show a summary dashboard"""
        self.console.print("\n[bold blue]Analysis Summary Dashboard[/bold blue]")
        self.console.print("=" * 50)
        
        # Create a summary table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()
        
        table.add_row("Total Files:", str(summary.get('total_files', 0)))
        table.add_row("Total Functions:", str(summary.get('total_functions', 0)))
        table.add_row("Total Lines:", str(summary.get('total_lines', 0)))
        table.add_row("Average Functions per File:", f"{summary.get('avg_functions_per_file', 0):.2f}")
        table.add_row("Average Lines per File:", f"{summary.get('avg_lines_per_file', 0):.2f}")
        
        self.console.print(table)

from pathlib import Path