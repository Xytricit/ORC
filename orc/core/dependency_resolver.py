"""
Dependency Resolver - Resolves function calls and file dependencies

This module resolves:
- Function calls to their actual file locations
- Import statements to actual modules
- Circular dependencies between files
- Call chains between functions
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class DependencyResolver:
    """Resolves dependencies and builds dependency graphs"""
    
    def __init__(self):
        self.function_map = {}  # name -> file_path mapping
        self.file_modules = {}  # file_path -> module mapping
        
    def resolve(self, parse_result: Dict) -> Dict:
        """
        Resolve all dependencies in parse result
        
        Args:
            parse_result: Dictionary from parallel_indexer containing:
                - files: Dict of file data
                - functions: Dict of function data
                - imports_detailed: List of import statements
                - entry_points: List of entry points
                
        Returns:
            Dictionary with resolved dependencies:
                - file_dependencies: List of file-to-file deps
                - function_calls_resolved: List of resolved function calls
                - circular_dependencies: List of circular deps found
        """
        # Build lookup maps
        self._build_function_map(parse_result.get('functions', {}))
        self._build_file_modules(parse_result.get('files', {}))
        
        # Resolve file dependencies from imports
        file_deps = self._resolve_file_dependencies(
            parse_result.get('imports_detailed', []),
            parse_result.get('files', {})
        )
        
        # Resolve function calls
        function_calls = self._resolve_function_calls(
            parse_result.get('functions', {})
        )
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(file_deps)
        
        return {
            'file_dependencies': file_deps,
            'function_calls_resolved': function_calls,
            'circular_dependencies': circular_deps
        }
    
    def _build_function_map(self, functions: Dict):
        """Build mapping of function names to file paths"""
        self.function_map = {}
        
        for func_id, func_data in functions.items():
            func_name = func_data.get('name')
            file_path = func_data.get('file')
            
            if func_name and file_path:
                # Handle multiple functions with same name
                if func_name not in self.function_map:
                    self.function_map[func_name] = []
                self.function_map[func_name].append({
                    'file': file_path,
                    'id': func_id,
                    'line': func_data.get('line_start', 0)
                })
    
    def _build_file_modules(self, files: Dict):
        """Build mapping of file paths to module names"""
        self.file_modules = {}
        
        for file_path in files.keys():
            # Convert file path to module name
            # e.g., /path/to/project/src/utils.py -> src.utils
            path_obj = Path(file_path)
            parts = path_obj.parts
            
            # Find reasonable module name
            if len(parts) > 1:
                module_parts = []
                for part in reversed(parts):
                    if part in ['.venv', 'venv', 'node_modules', '.git']:
                        break
                    module_parts.insert(0, part)
                
                module_name = '.'.join(module_parts).replace('.py', '')
                self.file_modules[file_path] = module_name
    
    def _resolve_file_dependencies(
        self, 
        imports_detailed: List[Dict],
        files: Dict
    ) -> List[Dict]:
        """
        Resolve import statements to actual file dependencies
        
        Returns list of file dependency records
        """
        file_deps = []
        file_paths = set(files.keys())
        
        for imp in imports_detailed:
            source_file = imp.get('source_file', '')
            module = imp.get('module', '')
            import_statement = imp.get('import_statement', '')
            line_number = imp.get('line_number', 0)
            import_type = imp.get('import_type', '')
            
            # Try to resolve module to actual file
            target_file = self._resolve_module_to_file(module, file_paths, source_file)
            
            file_deps.append({
                'source_file': source_file,
                'target_file': target_file if target_file else module,
                'import_statement': import_statement,
                'line_number': line_number,
                'import_type': import_type,
                'is_resolved': target_file is not None,
                'is_external': target_file is None
            })
        
        return file_deps
    
    def _resolve_module_to_file(
        self, 
        module: str, 
        file_paths: Set[str],
        source_file: str
    ) -> Optional[str]:
        """
        Try to resolve a module name to an actual file path
        
        Args:
            module: Module name (e.g., 'utils', 'src.utils')
            file_paths: Set of all known file paths
            source_file: File doing the importing (for relative imports)
            
        Returns:
            Resolved file path or None if external/not found
        """
        # Check if it's a relative import (starts with .)
        if module.startswith('.'):
            return self._resolve_relative_import(module, source_file, file_paths)
        
        # Check for direct matches
        for file_path in file_paths:
            file_path_lower = file_path.lower()
            
            # Try various patterns
            module_lower = module.lower().replace('.', '/')
            
            if (f'{module_lower}.py' in file_path_lower or
                f'/{module_lower}/' in file_path_lower or
                f'\\{module_lower}\\' in file_path_lower or
                file_path_lower.endswith(f'/{module_lower}.py') or
                file_path_lower.endswith(f'\\{module_lower}.py')):
                return file_path
        
        # Not found - likely external module
        return None
    
    def _resolve_relative_import(
        self,
        module: str,
        source_file: str,
        file_paths: Set[str]
    ) -> Optional[str]:
        """Resolve relative import (e.g., from .utils import X)"""
        if not source_file:
            return None
        
        source_path = Path(source_file)
        source_dir = source_path.parent
        
        # Count leading dots
        dots = len(module) - len(module.lstrip('.'))
        module_name = module.lstrip('.')
        
        # Go up directory levels based on dots
        target_dir = source_dir
        for _ in range(dots - 1):
            target_dir = target_dir.parent
        
        # Construct target path
        if module_name:
            target_path = target_dir / f"{module_name.replace('.', '/')}.py"
        else:
            target_path = target_dir / "__init__.py"
        
        target_str = str(target_path)
        
        # Check if it exists in our file_paths
        for file_path in file_paths:
            if Path(file_path).resolve() == target_path.resolve():
                return file_path
        
        return None
    
    def _resolve_function_calls(self, functions: Dict) -> List[Dict]:
        """
        Resolve function calls to their actual file locations
        
        Returns list of resolved function call records
        """
        resolved_calls = []
        
        for func_id, func_data in functions.items():
            caller_name = func_data.get('name')
            caller_file = func_data.get('file')
            calls = func_data.get('calls', [])
            
            for call_name in calls:
                # Try to resolve this call
                resolved = self._resolve_call(call_name, caller_file)
                
                resolved_calls.append({
                    'caller_function_id': func_id,
                    'caller_file': caller_file,
                    'caller_line': func_data.get('line_start', 0),
                    'callee_function_name': call_name,
                    'callee_function_id': resolved.get('id') if resolved else None,
                    'callee_file': resolved.get('file') if resolved else None,
                    'is_resolved': resolved is not None,
                    'is_external': resolved is None,
                    'call_type': 'direct'
                })
        
        return resolved_calls
    
    def _resolve_call(self, call_name: str, caller_file: str) -> Optional[Dict]:
        """
        Try to resolve a function call to its definition
        
        Returns dict with 'file', 'id', 'line' or None
        """
        # Look up in function map
        if call_name in self.function_map:
            matches = self.function_map[call_name]
            
            # Prefer matches in same file
            for match in matches:
                if match['file'] == caller_file:
                    return match
            
            # Return first match if not in same file
            if matches:
                return matches[0]
        
        return None
    
    def _detect_circular_dependencies(
        self, 
        file_deps: List[Dict]
    ) -> List[List[str]]:
        """
        Detect circular dependencies using DFS
        
        Returns list of circular dependency chains
        """
        # Build adjacency list
        graph = {}
        for dep in file_deps:
            source = dep['source_file']
            target = dep['target_file']
            
            if dep['is_resolved']:  # Only consider resolved deps
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
        
        # Find cycles using DFS
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
        
        # Run DFS from each unvisited node
        for node in graph.keys():
            if node not in visited:
                dfs(node, [])
        
        return cycles
