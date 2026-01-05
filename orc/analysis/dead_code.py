"""
Dead Code Detection
"""
from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class DeadCodeReport:
    """Report of dead code findings"""
    unused_functions: List[Dict]
    unused_exports: List[Dict]
    unused_files: List[str]
    estimated_lines_saved: int
    confidence_scores: Dict[str, float]

class DeadCodeAnalyzer:
    """Detect unused code in the codebase"""
    
    def __init__(self, graph: 'DependencyGraph', modules: Dict[str, 'ModuleInfo']):
        self.graph = graph
        self.modules = modules
    
    def analyze(self) -> DeadCodeReport:
        """Run comprehensive dead code analysis"""
        
        unused_functions = self._find_unused_functions()
        unused_exports = self._find_unused_exports()
        unused_files = self._find_unused_files()
        
        lines_saved = sum(
            item['lines'] for item in unused_functions
        ) + sum(
            self.modules[f]['lines'] if isinstance(self.modules[f], dict) else self.modules[f].lines for f in unused_files if f in self.modules
        )
        
        return DeadCodeReport(
            unused_functions=unused_functions,
            unused_exports=unused_exports,
            unused_files=unused_files,
            estimated_lines_saved=lines_saved,
            confidence_scores=self._calculate_confidence(
                unused_functions, unused_exports
            )
        )
    
    def _find_unused_functions(self) -> List[Dict]:
        orphans = self.graph.find_orphaned_functions()
        results = []
        for func_id in orphans:
            file_path, func_name = func_id.split('::')
            if file_path in self.modules:
                module = self.modules[file_path]
                functions = module['functions'] if isinstance(module, dict) else module.functions
                if func_name in functions:
                    func = functions[func_name]
                    line_start = func['line_start'] if isinstance(func, dict) else func.line_start
                    line_end = func['line_end'] if isinstance(func, dict) else func.line_end
                    results.append({
                        'function': func_name,
                        'file': file_path,
                        'lines': line_end - line_start,
                        'reason': 'Never called',
                        'line_range': (line_start, line_end)
                    })
        return results
    
    def _find_unused_exports(self) -> List[Dict]:
        unused = []
        for path, module in self.modules.items():
            exports = module['exports'] if isinstance(module, dict) else module.exports
            for export in exports:
                if not self._is_export_used(export, path):
                    unused.append({
                        'symbol': export,
                        'file': path,
                        'reason': 'Exported but never imported'
                    })
        return unused
    
    def _find_unused_files(self) -> List[str]:
        unused = []
        for path in self.modules.keys():
            deps = self.graph.get_module_dependencies(path)
            if not deps['depended_by']:
                if not self._is_entry_file(path):
                    unused.append(path)
        return unused
    
    def _is_export_used(self, export: str, source_path: str) -> bool:
        for path, module in self.modules.items():
            if path == source_path:
                continue
            imports = module['imports'] if isinstance(module, dict) else module.imports
            if any(export in imp for imp in imports):
                return True
            functions = module['functions'] if isinstance(module, dict) else module.functions
            for func in functions.values():
                calls = func['calls'] if isinstance(func, dict) else func.calls
                if export in calls:
                    return True
        return False
    
    def _is_entry_file(self, path: str) -> bool:
        entry_patterns = ['__main__.py', 'main.py', 'app.py', 'setup.py']
        return any(pattern in path for pattern in entry_patterns)
    
    def _calculate_confidence(self, functions: List, exports: List) -> Dict[str, float]:
        scores = {}
        for func in functions:
            confidence = 0.85
            scores[func['function']] = confidence
        for exp in exports:
            confidence = 0.90
            scores[exp['symbol']] = confidence
        return scores
