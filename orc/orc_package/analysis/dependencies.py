"""
ORC Analysis: Dependency Analysis
"""
from typing import Dict, List
from orc.core.indexer import ModuleInfo
from orc.core.graph_builder import DependencyGraph

class DependencyAnalyzer:
    """Analyze dependencies and coupling in the codebase"""

    def __init__(self, config):
        self.config = config

    def analyze(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """Analyze dependencies in the codebase"""
        
        # Build dependency graph
        graph_builder = DependencyGraph()
        graph_builder.build_from_modules(modules)
        
        # Find circular dependencies
        circular_deps = graph_builder.find_circular_dependencies()
        
        # Analyze coupling metrics
        coupling_metrics = self._analyze_coupling(graph_builder, modules)
        
        # Analyze other dependency issues
        dependency_issues = self._find_dependency_issues(modules, graph_builder)
        
        return {
            'circular_dependencies': circular_deps,
            'coupling_metrics': coupling_metrics,
            'dependency_issues': dependency_issues
        }

    def _analyze_coupling(self, graph: DependencyGraph, modules: Dict[str, ModuleInfo]) -> Dict:
        """Analyze coupling metrics for modules"""
        coupling_data = {}
        
        for module_path in modules.keys():
            coupling_score = graph.calculate_module_coupling(module_path)
            deps = graph.get_module_dependencies(module_path)
            
            coupling_data[module_path] = {
                'coupling_score': coupling_score,
                'depends_on_count': len(deps['depends_on']),
                'depended_by_count': len(deps['depended_by']),
                'depends_on': list(deps['depends_on']),
                'depended_by': list(deps['depended_by'])
            }
        
        return coupling_data

    def _find_dependency_issues(self, modules: Dict[str, ModuleInfo], 
                               graph: DependencyGraph) -> List[Dict]:
        """Find various dependency-related issues"""
        issues = []
        
        # Find highly coupled modules
        for module_path in modules.keys():
            coupling_score = graph.calculate_module_coupling(module_path)
            deps = graph.get_module_dependencies(module_path)
            
            if deps.get('depends_on_count', 0) > 10:  # Arbitrary threshold
                issues.append({
                    'type': 'high_coupling',
                    'module': module_path,
                    'depends_on_count': deps.get('depends_on_count', 0),
                    'message': f'Module depends on {deps.get("depends_on_count", 0)} other modules'
                })
        
        # Find modules with no incoming dependencies (potentially unused)
        for module_path in modules.keys():
            deps = graph.get_module_dependencies(module_path)
            if len(deps['depended_by']) == 0 and not self._is_entry_module(module_path):
                issues.append({
                    'type': 'orphan_module',
                    'module': module_path,
                    'message': 'Module is not depended on by any other module'
                })
        
        return issues

    def _is_entry_module(self, module_path: str) -> bool:
        """Check if module is an entry point (should not be considered orphaned)"""
        entry_patterns = [
            '__main__.py', 'main.py', 'app.py', 'server.py',
            'setup.py', 'test_', 'tests/'
        ]
        return any(pattern in module_path for pattern in entry_patterns)