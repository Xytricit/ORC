"""
ORC Analysis: Code Metrics Calculator
"""
from typing import Dict, List
from orc.core.indexer import ModuleInfo

class MetricsAnalyzer:
    """Calculate code metrics like complexity, lines of code, etc."""

    def __init__(self, config):
        self.config = config

    def analyze(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Calculate various code metrics"""
        
        overall_metrics = self._calculate_overall_metrics(modules)
        module_metrics = self._calculate_module_metrics(modules)
        function_metrics = self._calculate_function_metrics(modules)
        
        return {
            'overall': overall_metrics,
            'modules': module_metrics,
            'functions': function_metrics
        }

    def _calculate_overall_metrics(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Calculate overall project metrics"""
        total_files = len(modules)
        total_lines = sum(module.lines for module in modules.values())
        total_functions = sum(len(module.functions) for module in modules.values())
        total_classes = sum(len(module.classes) for module in modules.values())
        
        # Calculate average complexity
        total_complexity = 0
        complexity_count = 0
        for module in modules.values():
            for func in module.functions.values():
                total_complexity += func.complexity
                complexity_count += 1
        
        avg_complexity = total_complexity / complexity_count if complexity_count > 0 else 0
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0,
            'avg_functions_per_file': total_functions / total_files if total_files > 0 else 0,
            'avg_complexity': avg_complexity,
            'max_complexity': self._get_max_complexity(modules)
        }

    def _calculate_module_metrics(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Calculate metrics for each module"""
        module_metrics = {}
        
        for path, module in modules.items():
            # Calculate module-specific metrics
            total_complexity = sum(func.complexity for func in module.functions.values())
            avg_complexity = total_complexity / len(module.functions) if module.functions else 0
            
            module_metrics[path] = {
                'lines': module.lines,
                'functions_count': len(module.functions),
                'classes_count': len(module.classes),
                'imports_count': len(module.imports),
                'exports_count': len(module.exports),
                'total_complexity': total_complexity,
                'avg_complexity': avg_complexity,
                'max_complexity': max((func.complexity for func in module.functions.values()), default=0)
            }
        
        return module_metrics

    def _calculate_function_metrics(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Calculate metrics for each function"""
        function_metrics = {}
        
        for path, module in modules.items():
            for name, func in module.functions.items():
                func_id = f"{path}::{name}"
                function_metrics[func_id] = {
                    'name': name,
                    'file': path,
                    'line_start': func.line_start,
                    'line_end': func.line_end,
                    'lines_of_code': func.line_end - func.line_start + 1,
                    'complexity': func.complexity,
                    'parameters_count': len(func.parameters),
                    'is_exported': func.is_exported,
                    'calls_count': len(func.calls)
                }
        
        return function_metrics

    def _get_max_complexity(self, modules: Dict[str, ModuleInfo]) -> int:
        """Get the maximum complexity across all functions"""
        max_complexity = 0
        for module in modules.values():
            for func in module.functions.values():
                if func.complexity > max_complexity:
                    max_complexity = func.complexity
        return max_complexity

    def get_complex_functions(self, modules: Dict[str, ModuleInfo], 
                            threshold: int = None) -> List[Dict]:
        """Get functions with complexity above threshold"""
        if threshold is None:
            threshold = self.config.min_complexity_threshold
        
        complex_functions = []
        for path, module in modules.items():
            for name, func in module.functions.items():
                if func.complexity >= threshold:
                    complex_functions.append({
                        'function': f"{path}::{name}",
                        'complexity': func.complexity,
                        'file': path,
                        'name': name,
                        'line_start': func.line_start
                    })
        
        return complex_functions