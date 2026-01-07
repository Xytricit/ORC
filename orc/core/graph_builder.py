"""
ORC Core: Dependency Graph Builder
"""
import networkx as nx
from typing import Dict, List, Set
from pathlib import Path
from .indexer import ModuleInfo, FunctionInfo

class DependencyGraph:
    """Build dependency graphs from indexed modules"""

    def __init__(self):
        self.module_graph = nx.DiGraph()  # Module-to-module dependencies
        self.call_graph = nx.DiGraph()    # Function call relationships
        self.function_map = {}            # Maps function names to their modules
        # Internal lookup for fast import resolution: maps various module
        # identifiers (dotted path, stem) to canonical file paths.
        self._module_lookup: Dict[str, str] = {}

    def build_from_modules(self, modules: Dict[str, ModuleInfo]):
        """Build dependency graphs from indexed modules"""

        # Build a fast lookup for resolving imports. We normalise paths to
        # use forward slashes and include both dotted and stem variants so
        # that ``import foo.bar`` and ``import bar`` can usually be mapped
        # without scanning the entire modules dict repeatedly.
        self._module_lookup.clear()
        for path in modules.keys():
            norm_path = path.replace('\\', '/')
            if norm_path.endswith('.py'):
                base = norm_path[:-3]
            else:
                base = norm_path
            dotted = base.replace('/', '.')
            stem = Path(norm_path).stem
            for key in {dotted, stem}:
                # Last write wins; in ambiguous cases this is still better
                # than an O(N) scan on every import.
                self._module_lookup.setdefault(key, path)

        # First pass: Add all modules and functions to graphs
        for path, module in modules.items():
            # Add module node
            self.module_graph.add_node(
                path,
                lines=module.lines,
                imports=len(module.imports),
                exports=len(module.exports),
                functions=len(module.functions)
            )

            # Add all functions to function map and call graph
            for func_name, func_info in module.functions.items():
                func_id = f"{path}::{func_name}"
                self.function_map[func_id] = func_info
                self.call_graph.add_node(
                    func_id,
                    complexity=func_info.complexity,
                    lines=func_info.line_end - func_info.line_start,
                    file_path=path,
                    func_name=func_name
                )

        # Second pass: Add dependency edges
        for path, module in modules.items():
            # Add module import dependencies
            for import_name in module.imports:
                # Try to resolve import to actual module path
                target_path = self._resolve_import(import_name, path, modules)
                if target_path and target_path in modules:
                    self.module_graph.add_edge(path, target_path)

            # Add function call dependencies
            for func_name, func_info in module.functions.items():
                func_id = f"{path}::{func_name}"

                for called_func in func_info.calls:
                    # Try to resolve the called function
                    called_id = self._resolve_function_call(called_func, path, modules)
                    if called_id and called_id != func_id:
                        self.call_graph.add_edge(func_id, called_id)

    def _resolve_import(self, import_name: str, current_path: str,
                       modules: Dict[str, ModuleInfo]) -> str:
        """Resolve an import to a module path.

        Previously this scanned all modules on every call; now it uses a
        precomputed lookup for common cases and only falls back to the
        slower heuristics when necessary.
        """
        # Strip leading dots from relative imports for lookup purposes.
        key = import_name.lstrip('.')
        target = self._module_lookup.get(key)
        if target and target in modules:
            return target

        # Try a dotted-path variant if we only got a bare name.
        if '.' not in key:
            for candidate in (f"{key}.__init__", f"{key}.py"):
                target = self._module_lookup.get(candidate)
                if target and target in modules:
                    return target

        # Fallback: relative import resolution based on current path.
        current_dir = '/'.join(current_path.split('/')[:-1])
        potential_path = f"{current_dir}/{import_name.replace('.', '/')}.py"
        if potential_path in modules:
            return potential_path

        return None

    def _resolve_function_call(self, func_name: str, current_path: str,
                              modules: Dict[str, ModuleInfo]) -> str:
        """Resolve a function call to its definition"""
        # First check if it's in the current module
        if current_path in modules:
            if func_name in modules[current_path].functions:
                return f"{current_path}::{func_name}"

        # Check if it's imported from another module
        current_module = modules[current_path]
        for import_name in current_module.imports:
            target_path = self._resolve_import(import_name, current_path, modules)
            if target_path and target_path in modules:
                if func_name in modules[target_path].functions:
                    return f"{target_path}::{func_name}"

        # If not found, return None
        return None

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in module graph"""
        try:
            cycles = list(nx.simple_cycles(self.module_graph))
            return cycles
        except:
            return []

    def get_module_dependencies(self, module_path: str) -> Dict[str, Set[str]]:
        """Get dependencies for a specific module"""
        if module_path in self.module_graph:
            return {
                'depends_on': set(self.module_graph.successors(module_path)),
                'depended_by': set(self.module_graph.predecessors(module_path))
            }
        return {'depends_on': set(), 'depended_by': set()}

    def get_function_callers(self, func_id: str) -> List[str]:
        """Get all functions that call the specified function"""
        if func_id in self.call_graph:
            return list(self.call_graph.predecessors(func_id))
        return []

    def get_function_callees(self, func_id: str) -> List[str]:
        """Get all functions called by the specified function"""
        if func_id in self.call_graph:
            return list(self.call_graph.successors(func_id))
        return []

    def calculate_module_coupling(self, module_path: str) -> float:
        """Calculate coupling metric for a module"""
        deps = self.get_module_dependencies(module_path)
        total_deps = len(deps['depends_on']) + len(deps['depended_by'])
        if len(self.module_graph.nodes()) <= 1:
            return 0.0
        return total_deps / (len(self.module_graph.nodes()) - 1)
