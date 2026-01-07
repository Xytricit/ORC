"""
ORC Agent: Natural Language Query Engine
"""
from typing import Dict, Any
from dataclasses import dataclass
import re
from core.indexer import ModuleInfo
from core.graph_builder import DependencyGraph

@dataclass
class QueryResult:
    """Structured query result"""
    query: str
    result_type: str  # 'list', 'graph', 'metric', 'recommendation'
    data: Any
    metadata: Dict[str, Any]

class QueryEngine:
    """Process natural language queries about the codebase"""

    def __init__(self, config, modules: Dict[str, ModuleInfo], graph: DependencyGraph):
        self.config = config
        self.modules = modules
        self.graph = graph
        self._query_handlers = self._initialize_handlers()

    def _initialize_handlers(self) -> Dict[str, callable]:
        """Map query patterns to handler functions"""
        return {
            r'circular.*dependencies?': self._handle_circular_deps,
            r'dead.*code': self._handle_dead_code,
            r'unused.*functions?': self._handle_unused_functions,
            r'complex.*functions?': self._handle_complex_functions,
            r'files?.*with.*most.*functions?': self._handle_largest_files,
            r'dependencies?.*of.*(.+)': self._handle_module_dependencies,
            r'who.*calls?.*(.+)': self._handle_function_callers,
            r'metrics?': self._handle_metrics_summary,
        }

    def process_query(self, query: str) -> QueryResult:
        """Main entry point for query processing"""
        query_lower = query.lower().strip()

        # Match query to handler
        for pattern, handler in self._query_handlers.items():
            match = re.search(pattern, query_lower)
            if match:
                return handler(query, match)

        # Default: return help message
        return self._handle_unknown_query(query)

    def _handle_circular_deps(self, query: str, match: re.Match) -> QueryResult:
        """Find circular dependencies"""
        cycles = self.graph.find_circular_dependencies()
        return QueryResult(
            query=query,
            result_type='list',
            data=cycles,
            metadata={'count': len(cycles)}
        )

    def _handle_dead_code(self, query: str, match: re.Match) -> QueryResult:
        """Analyze dead code"""
        # Use the v1 dead-code analyzer from orc_package.analysis
        from orc_package.analysis.dead_code import DeadCodeAnalyzer
        analyzer = DeadCodeAnalyzer(self.config)
        report = analyzer.analyze(self.modules)

        return QueryResult(
            query=query,
            result_type='recommendation',
            data={
                'unused_functions': report.unused_functions[:10],  # Limit for display
                'unused_files': report.unused_files,
                'lines_saved': report.estimated_lines_saved
            },
            metadata={'report': report}
        )

    def _handle_unused_functions(self, query: str, match: re.Match) -> QueryResult:
        """List unused functions"""
        from orc_package.analysis.dead_code import DeadCodeAnalyzer
        analyzer = DeadCodeAnalyzer(self.config)
        report = analyzer.analyze(self.modules)

        return QueryResult(
            query=query,
            result_type='list',
            data=report.unused_functions,
            metadata={'total_unused': len(report.unused_functions)}
        )

    def _handle_complex_functions(self, query: str, match: re.Match) -> QueryResult:
        """Find functions with high complexity"""
        complex_funcs = []

        for path, module in self.modules.items():
            for func_name, func_info in module.functions.items():
                if func_info.complexity > self.config.min_complexity_threshold:
                    complex_funcs.append({
                        'name': func_name,
                        'file': path,
                        'complexity': func_info.complexity,
                        'line_start': func_info.line_start,
                        'line_end': func_info.line_end
                    })

        complex_funcs.sort(key=lambda x: x['complexity'], reverse=True)

        return QueryResult(
            query=query,
            result_type='list',
            data=complex_funcs[:20],  # Limit results
            metadata={'threshold': self.config.min_complexity_threshold}
        )

    def _handle_largest_files(self, query: str, match: re.Match) -> QueryResult:
        """Find files with most functions"""
        file_stats = []

        for path, module in self.modules.items():
            file_stats.append({
                'file': path,
                'functions': len(module.functions),
                'lines': module.lines,
                'classes': len(module.classes)
            })

        file_stats.sort(key=lambda x: x['functions'], reverse=True)

        return QueryResult(
            query=query,
            result_type='list',
            data=file_stats[:20],  # Limit results
            metadata={'total_files': len(self.modules)}
        )

    def _handle_module_dependencies(self, query: str, match: re.Match) -> QueryResult:
        """Get dependencies for a specific module"""
        module_name = match.group(1).strip()

        # Find matching module (partial match)
        target_path = None
        for path in self.modules.keys():
            if module_name in path or module_name.replace('.', '/') in path:
                target_path = path
                break

        if not target_path:
            return QueryResult(
                query=query,
                result_type='error',
                data={'error': f'Module "{module_name}" not found'},
                metadata={}
            )

        deps = self.graph.get_module_dependencies(target_path)

        return QueryResult(
            query=query,
            result_type='graph',
            data={
                'module': target_path,
                'depends_on': list(deps['depends_on']),
                'depended_by': list(deps['depended_by'])
            },
            metadata={'coupling_score': self.graph.calculate_module_coupling(target_path)}
        )

    def _handle_function_callers(self, query: str, match: re.Match) -> QueryResult:
        """Find who calls a specific function"""
        func_name = match.group(1).strip()

        # Search for function across modules
        func_id = None
        for path, module in self.modules.items():
            if func_name in module.functions:
                func_id = f"{path}::{func_name}"
                break

        if not func_id:
            return QueryResult(
                query=query,
                result_type='error',
                data={'error': f'Function "{func_name}" not found'},
                metadata={}
            )

        callers = self.graph.get_function_callers(func_id)

        return QueryResult(
            query=query,
            result_type='list',
            data=[{'caller': c} for c in callers],
            metadata={'function': func_id, 'caller_count': len(callers)}
        )

    def _handle_metrics_summary(self, query: str, match: re.Match) -> QueryResult:
        """Generate overall metrics summary"""
        from orc_package.analysis.metrics import MetricsAnalyzer
        analyzer = MetricsAnalyzer(self.config)
        metrics = analyzer.analyze(self.modules)

        return QueryResult(
            query=query,
            result_type='metric',
            data=metrics['overall'],
            metadata={}
        )

    def _handle_unknown_query(self, query: str) -> QueryResult:
        """Handle unrecognized queries"""
        available_queries = [
            "Show circular dependencies",
            "Find dead code",
            "List unused functions",
            "Show complex functions",
            "Files with most functions",
            "Dependencies of [module_name]",
            "Who calls [function_name]",
            "Show metrics"
        ]

        return QueryResult(
            query=query,
            result_type='help',
            data={'available_queries': available_queries},
            metadata={'error': 'Query not recognized'}
        )