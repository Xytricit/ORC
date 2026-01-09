"""
ORC Analysis: Pattern Detection
"""
from typing import Dict, List
from orc.core.indexer import ModuleInfo

class PatternAnalyzer:
    """Detect code patterns, duplication, and antipatterns"""

    def __init__(self, config):
        self.config = config
        self.patterns_config = self._load_patterns_config()

    def _load_patterns_config(self):
        """Load pattern definitions from config"""
        # In a real implementation, this would load from patterns.yaml
        # For now, we'll define some default patterns
        return {
            'antipatterns': [
                {
                    'name': 'God Object',
                    'description': 'Class with too many methods',
                    'threshold': 20,  # More than 20 methods
                    'field': 'method_count'
                },
                {
                    'name': 'Long Method',
                    'description': 'Method with too many lines',
                    'threshold': 50,  # More than 50 lines
                    'field': 'lines_of_code'
                },
                {
                    'name': 'Complex Method',
                    'description': 'Method with high cyclomatic complexity',
                    'threshold': 10,  # Complexity > 10
                    'field': 'complexity'
                }
            ]
        }

    def analyze(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Analyze code for patterns and antipatterns"""
        
        antipatterns = self._detect_antipatterns(modules)
        duplication = self._detect_duplication(modules)
        good_patterns = self._detect_good_patterns(modules)
        
        return {
            'antipatterns': antipatterns,
            'duplication': duplication,
            'good_patterns': good_patterns
        }

    def _detect_antipatterns(self, modules: Dict[str, ModuleInfo]) -> List[Dict]:
        """Detect antipatterns in the codebase"""
        antipatterns = []
        
        for path, module in modules.items():
            # Check for functions that exceed complexity thresholds
            for func_name, func in module.functions.items():
                for pattern in self.patterns_config['antipatterns']:
                    if pattern['field'] == 'complexity' and func.complexity > pattern['threshold']:
                        antipatterns.append({
                            'type': pattern['name'],
                            'description': pattern['description'],
                            'function': f"{path}::{func_name}",
                            'file': path,
                            'function_name': func_name,
                            'value': func.complexity,
                            'threshold': pattern['threshold']
                        })
        
        return antipatterns

    def _detect_duplication(self, modules: Dict[str, ModuleInfo]) -> List[Dict]:
        """Detect code duplication"""
        # This is a simplified implementation
        # A real implementation would compare AST structures or code similarity
        duplication = []
        
        # For now, we'll look for functions with identical names across modules
        # which might indicate duplicated functionality
        function_names = {}
        
        for path, module in modules.items():
            for func_name, func in module.functions.items():
                if func_name not in function_names:
                    function_names[func_name] = []
                function_names[func_name].append({
                    'file': path,
                    'function': func_name,
                    'complexity': func.complexity
                })
        
        # Find functions with same name in different files (potential duplication)
        for func_name, occurrences in function_names.items():
            if len(occurrences) > 1:
                duplication.append({
                    'type': 'potential_duplication',
                    'function_name': func_name,
                    'occurrences': occurrences,
                    'count': len(occurrences)
                })
        
        return duplication

    def _detect_good_patterns(self, modules: Dict[str, ModuleInfo]) -> List[Dict]:
        """Detect good patterns in the codebase"""
        good_patterns = []
        
        for path, module in modules.items():
            for func_name, func in module.functions.items():
                # Look for patterns like factory methods (create*, make*, build*)
                if any(func_name.startswith(prefix) for prefix in ['create', 'make', 'build', 'new']):
                    good_patterns.append({
                        'type': 'Factory Pattern',
                        'function': f"{path}::{func_name}",
                        'file': path,
                        'function_name': func_name,
                        'description': 'Method name suggests factory pattern usage'
                    })
                
                # Look for observer pattern methods
                if any(pattern in func_name.lower() for pattern in ['subscribe', 'notify', 'update', 'listen']):
                    good_patterns.append({
                        'type': 'Observer Pattern',
                        'function': f"{path}::{func_name}",
                        'file': path,
                        'function_name': func_name,
                        'description': 'Method name suggests observer pattern usage'
                    })
        
        return good_patterns

    def get_pattern_summary(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Get a summary of pattern detection results"""
        results = self.analyze(modules)
        
        return {
            'total_antipatterns': len(results['antipatterns']),
            'total_duplication_instances': len(results['duplication']),
            'total_good_patterns': len(results['good_patterns']),
            'antipatterns_by_type': self._count_by_type(results['antipatterns']),
            'duplication_by_type': self._count_by_type(results['duplication'])
        }

    def _count_by_type(self, items: List[Dict]) -> Dict[str, int]:
        """Count items by their type"""
        counts = {}
        for item in items:
            pattern_type = item.get('type', 'unknown')
            counts[pattern_type] = counts.get(pattern_type, 0) + 1
        return counts