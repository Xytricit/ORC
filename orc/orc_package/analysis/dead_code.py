"""
ORC Analysis: Dead Code Detection
"""
from typing import List, Dict
from dataclasses import dataclass
from orc.core.indexer import ModuleInfo

@dataclass
class DeadCodeReport:
    """Report of dead code findings"""
    unused_functions: List[Dict]        # Functions never called
    unused_exports: List[Dict]          # Exports never imported
    unused_files: List[str]             # Files never imported
    estimated_lines_saved: int          # Total removable lines
    confidence_scores: Dict[str, float] # Confidence per finding

class DeadCodeAnalyzer:
    """Find unused code in the codebase"""

    def __init__(self, config):
        self.config = config

    def analyze(self, modules: Dict[str, ModuleInfo]) -> DeadCodeReport:
        """Analyze modules for dead code"""
        
        unused_functions = self._find_unused_functions(modules)
        unused_exports = self._find_unused_exports(modules)
        unused_files = self._find_unused_files(modules)
        
        # Calculate estimated lines that could be saved
        lines_saved = 0
        for func_info in unused_functions:
            lines_saved += func_info.get('lines', 0)
        
        for file_path in unused_files:
            if file_path in modules:
                lines_saved += modules[file_path].lines
        
        return DeadCodeReport(
            unused_functions=unused_functions,
            unused_exports=unused_exports,
            unused_files=unused_files,
            estimated_lines_saved=lines_saved,
            confidence_scores=self._calculate_confidence_scores(unused_functions, unused_exports)
        )

    def _find_unused_functions(self, modules: Dict[str, ModuleInfo]) -> List[Dict]:
        """Find functions that are never called"""
        all_called_functions = set()
        unused_functions = []
        
        # Collect all called functions (from within other functions)
        for module_path, module in modules.items():
            for func_name, func_info in module.functions.items():
                for called_func in func_info.calls:
                    all_called_functions.add(called_func)
        
        # Also check for module-level calls (like in if __name__ == "__main__")
        # by parsing each module to find calls outside of function definitions
        import ast
        from pathlib import Path
        for module_path, module in modules.items():
            try:
                content = Path(module_path).read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Extract module-level calls (outside function definitions)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Only count if it's a direct module-level call, not inside a function
                        if self._is_module_level_call(node, tree):
                            if isinstance(node.func, ast.Name):
                                all_called_functions.add(node.func.id)
                            elif isinstance(node.func, ast.Attribute):
                                all_called_functions.add(node.func.attr)
            except:
                # If we can't parse, skip this module
                pass
        
        # Find functions that are not called by anyone
        for module_path, module in modules.items():
            for func_name, func_info in module.functions.items():
                # Skip private/internal functions
                if func_name.startswith('_'):
                    continue
                
                # Skip if function is called somewhere
                if func_name in all_called_functions:
                    continue
                
                # Skip if function is an entry point
                if self._is_entry_point(func_name):
                    continue
                
                unused_functions.append({
                    'function': func_name,
                    'file': module_path,
                    'line_start': func_info.line_start,
                    'line_end': func_info.line_end,
                    'lines': func_info.line_end - func_info.line_start + 1,
                    'complexity': func_info.complexity,
                    'reason': 'Function is never called'
                })
        
        return unused_functions

    def _find_unused_exports(self, modules: Dict[str, ModuleInfo]) -> List[Dict]:
        """Find exports that are never imported"""
        all_imported_symbols = set()
        unused_exports = []
        
        # Collect all imported symbols
        for module_path, module in modules.items():
            for imported_module in module.imports:
                # For now, we'll consider all imports as used
                # In a real implementation, we'd need to check specific symbol usage
                pass
        
        # For now, we'll return an empty list
        # A more sophisticated implementation would track symbol usage
        return unused_exports

    def _find_unused_files(self, modules: Dict[str, ModuleInfo]) -> List[str]:
        """Find files that are never imported"""
        all_imported_files = set()
        unused_files = []
        
        # Collect all imported files
        for module_path, module in modules.items():
            for imported in module.imports:
                # Resolve import to actual file path
                resolved_path = self._resolve_import_to_path(imported, module_path, modules)
                if resolved_path:
                    all_imported_files.add(resolved_path)
        
        # Find files that are not imported by anyone
        for module_path in modules.keys():
            if module_path not in all_imported_files:
                if not self._is_entry_file(module_path):
                    unused_files.append(module_path)
        
        return unused_files

    def _is_entry_point(self, func_name: str) -> bool:
        """Check if function is an entry point (should not be considered dead code)"""
        entry_point_patterns = [
            'main', 'test_', 'setup', '__main__',
            'run', 'start', 'init', '__init__'
        ]
        return any(pattern in func_name.lower() for pattern in entry_point_patterns)

    def _is_entry_file(self, file_path: str) -> bool:
        """Check if file is an entry point (should not be considered dead code)"""
        entry_file_patterns = [
            '__main__.py', 'main.py', 'app.py', 'server.py',
            'setup.py', 'test_', 'tests/'
        ]
        return any(pattern in file_path for pattern in entry_file_patterns)

    def _resolve_import_to_path(self, import_name: str, current_path: str, 
                               modules: Dict[str, ModuleInfo]) -> str:
        """Resolve an import to a file path"""
        # This is a simplified implementation
        # In a real system, this would need more sophisticated import resolution
        for path in modules.keys():
            if import_name.replace('.', '/') in path or import_name in path:
                return path
        return None

    def _is_module_level_call(self, call_node: 'ast.Call', tree: 'ast.Module') -> bool:
        """Check if a call is at module level (not inside a function)"""
        import ast
        
        # Walk through all function definitions to check if this call is inside one
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if call_node is within this function
                for child in ast.walk(node):
                    if child is call_node:
                        return False  # It's inside a function
        
        return True  # It's at module level
    
    def _calculate_confidence_scores(self, unused_functions: List[Dict], 
                                    unused_exports: List[Dict]) -> Dict[str, float]:
        """Calculate confidence scores for dead code findings"""
        scores = {}
        
        # Higher confidence for functions with higher complexity that are unused
        for func in unused_functions:
            # Base confidence
            confidence = 0.7
            # Increase confidence if function has high complexity (indicating it's significant)
            if func['complexity'] > 5:
                confidence += min(0.3, (func['complexity'] - 5) * 0.05)
            scores[f"{func['file']}::{func['function']}"] = min(1.0, confidence)
        
        for export in unused_exports:
            scores[f"{export['file']}::{export['symbol']}"] = 0.8
        
        return scores