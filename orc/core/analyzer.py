"""
ORC Core: Analysis Orchestrator
"""
from typing import Dict, Any
from .indexer import ModuleInfo
from orc_package.analysis.dead_code import DeadCodeAnalyzer
from orc_package.analysis.dependencies import DependencyAnalyzer
from orc_package.analysis.metrics import MetricsAnalyzer
from orc_package.analysis.patterns import PatternAnalyzer

class Analyzer:
    """Orchestrate analysis across different analyzers"""

    def __init__(self, config):
        self.config = config
        self.dead_code_analyzer = DeadCodeAnalyzer(config)
        self.dependency_analyzer = DependencyAnalyzer(config)
        self.metrics_analyzer = MetricsAnalyzer(config)
        self.pattern_analyzer = PatternAnalyzer(config)

    def run_all(self, modules: Dict[str, ModuleInfo]) -> Dict[str, Any]:
        """Run all analysis modules and return comprehensive report"""

        report = {
            'dead_code': self.dead_code_analyzer.analyze(modules),
            'dependencies': self.dependency_analyzer.analyze(modules),
            'metrics': self.metrics_analyzer.analyze(modules),
            'patterns': self.pattern_analyzer.analyze(modules),
            'summary': self._generate_summary(modules)
        }

        return report

    def _generate_summary(self, modules: Dict[str, ModuleInfo]) -> Dict[str, Any]:
        """Generate a summary of the analysis"""
        total_files = len(modules)
        total_functions = sum(len(module.functions) for module in modules.values())
        total_lines = sum(module.lines for module in modules.values())

        return {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_lines': total_lines,
            'avg_functions_per_file': total_functions / total_files if total_files > 0 else 0,
            'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0
        }
