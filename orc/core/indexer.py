"""
Static Analysis & AST-based Indexing
"""
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
import hashlib

@dataclass
class FunctionInfo:
    """Information about a function"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    complexity: int
    calls: List[str] = field(default_factory=list)
    called_by: Set[str] = field(default_factory=set)
    parameters: List[str] = field(default_factory=list)
    is_exported: bool = False
    is_used: bool = False
    docstring: Optional[str] = None

@dataclass
class ModuleInfo:
    """Information about a module/file"""
    path: str
    lines: int
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)
    classes: List[str] = field(default_factory=list)
    last_modified: float = 0.0
    hash: str = ""

class PythonIndexer:
    """Index Python files using AST"""
    
    def __init__(self, config: 'ORCConfig'):
        self.config = config
        self.modules: Dict[str, ModuleInfo] = {}
    
    def index_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """Parse and index a single Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            module = ModuleInfo(
                path=str(file_path),
                lines=len(content.splitlines()),
                last_modified=file_path.stat().st_mtime,
                hash=hashlib.md5(content.encode()).hexdigest()
            )
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    module.imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module.imports.append(node.module)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function(node, str(file_path))
                    module.functions[func_info.name] = func_info
                    if not node.name.startswith('_'):
                        module.exports.append(node.name)
                
                elif isinstance(node, ast.ClassDef):
                    module.classes.append(node.name)
                    if not node.name.startswith('_'):
                        module.exports.append(node.name)
            
            return module
            
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
            return None
    
    def _extract_function(self, node: ast.FunctionDef, file_path: str) -> FunctionInfo:
        """Extract function information from AST node"""
        complexity = self._calculate_complexity(node)
        calls = self._extract_calls(node)
        
        return FunctionInfo(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            complexity=complexity,
            calls=calls,
            parameters=[arg.arg for arg in node.args.args],
            docstring=ast.get_docstring(node)
        )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _extract_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls
    
    def index_directory(self, root_path: Path) -> Dict[str, ModuleInfo]:
        """Index all Python files in a directory"""
        for pattern in self.config.file_extensions:
            if '.py' in pattern:
                for file_path in root_path.rglob('*.py'):
                    # Skip ignored patterns
                    if any(file_path.match(ignore) 
                           for ignore in self.config.ignore_patterns):
                        continue
                    
                    module = self.index_file(file_path)
                    if module:
                        self.modules[str(file_path)] = module
        
        return self.modules
