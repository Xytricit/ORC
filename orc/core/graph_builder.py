"""
Dependency Graph Construction
"""
import networkx as nx
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class DependencyGraph:
    """Build and query dependency relationships"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.call_graph = nx.DiGraph()
        self.module_graph = nx.DiGraph()
    
    def build_from_modules(self, modules: Dict[str, 'ModuleInfo']):
        """Build graph from indexed modules"""
        
        # Add module nodes
        for path, module in modules.items():
            self.module_graph.add_node(
                path,
                lines=module['lines'] if isinstance(module, dict) else module.lines,
                exports=len(module['exports']) if isinstance(module, dict) else len(module.exports),
                functions=len(module['functions']) if isinstance(module, dict) else len(module.functions)
            )
        
        # Add module dependencies
        for path, module in modules.items():
            imports = module['imports'] if isinstance(module, dict) else module.imports
            for import_name in imports:
                # Try to resolve import to actual file
                target = self._resolve_import(import_name, modules)
                if target:
                    self.module_graph.add_edge(path, target)
        
        # Build call graph
        for path, module in modules.items():
            functions = module['functions'] if isinstance(module, dict) else module.functions
            for func_name, func_info in functions.items():
                node_id = f"{path}::{func_name}"
                complexity = func_info['complexity'] if isinstance(func_info, dict) else func_info.complexity
                line_start = func_info['line_start'] if isinstance(func_info, dict) else func_info.line_start
                line_end = func_info['line_end'] if isinstance(func_info, dict) else func_info.line_end
                calls = func_info['calls'] if isinstance(func_info, dict) else func_info.calls
                self.call_graph.add_node(
                    node_id,
                    complexity=complexity,
                    lines=line_end - line_start
                )
                
                # Add call edges
                for called_func in calls:
                    called_id = self._resolve_function_call(
                        called_func, path, modules
                    )
                    if called_id:
                        self.call_graph.add_edge(node_id, called_id)
    
    def _resolve_import(self, import_name: str, 
                       modules: Dict[str, 'ModuleInfo']) -> str:
        """Try to resolve an import to a file path"""
        for path in modules.keys():
            if import_name.replace('.', '/') in path:
                return path
        return None
    
    def _resolve_function_call(self, func_name: str, current_file: str,
                              modules: Dict[str, 'ModuleInfo']) -> str:
        """Resolve a function call to its definition"""
        if current_file in modules:
            functions = modules[current_file]['functions'] if isinstance(modules[current_file], dict) else modules[current_file].functions
            if func_name in functions:
                return f"{current_file}::{func_name}"
        if current_file in modules:
            imports = modules[current_file]['imports'] if isinstance(modules[current_file], dict) else modules[current_file].imports
            for import_name in imports:
                target = self._resolve_import(import_name, modules)
                if target and target in modules:
                    functions = modules[target]['functions'] if isinstance(modules[target], dict) else modules[target].functions
                    if func_name in functions:
                        return f"{target}::{func_name}"
        return None
    
    def find_circular_dependencies(self) -> List[List[str]]:
        try:
            cycles = list(nx.simple_cycles(self.module_graph))
            return [cycle for cycle in cycles if len(cycle) > 1]
        except:
            return []
    
    def find_orphaned_functions(self) -> List[str]:
        orphans = []
        for node in self.call_graph.nodes():
            if self.call_graph.in_degree(node) == 0:
                func_name = node.split('::')[-1]
                if not self._is_entry_point(func_name):
                    orphans.append(node)
        return orphans
    
    def _is_entry_point(self, func_name: str) -> bool:
        entry_patterns = ['main', 'test_', '__main__', 'run', 'start']
        return any(pattern in func_name.lower() for pattern in entry_patterns)
    
    def get_function_callers(self, func_id: str) -> List[str]:
        return list(self.call_graph.predecessors(func_id))
    
    def get_module_dependencies(self, module_path: str) -> Dict[str, Set[str]]:
        return {
            'depends_on': set(self.module_graph.successors(module_path)),
            'depended_by': set(self.module_graph.predecessors(module_path))
        }
    
    def calculate_coupling(self, module_path: str) -> float:
        deps = self.get_module_dependencies(module_path)
        total = len(deps['depends_on']) + len(deps['depended_by'])
        return total / max(len(self.module_graph.nodes()), 1)
