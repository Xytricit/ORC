"""Python parser using ``ast`` to extract basic structure.

This parser is intentionally lightweight: it only looks at *top-level*
functions, classes and imports, and returns a dictionary shape that is
compatible with the v2 index used by ``ContextBuilder`` and
``ComplexityAnalyzer``.

The returned mapping looks like:

.. code-block:: python

    {
        "files": {"/abs/path.py": {"language": "python", "loc": 42}},
        "functions": {
            "/abs/path.py::func": {
                "id": "/abs/path.py::func",
                "name": "func",
                "file": "/abs/path.py",
                "line_start": 10,
                "line_end": 20,
                "complexity": 3,
                "calls": ["other"],
                "parameters": ["x"],
                "docstring": "...",
                "code": "def func(...): ...",
            },
        },
        "classes": {"/abs/path.py::Cls": {...}},
        "imports": {"module": {"count": 2}},
        "exports": {"func": {"kind": "function"}},
    }
"""
import ast
from pathlib import Path
from typing import Dict, List

from .base_parser import BaseParser


class PythonParser(BaseParser):
    """Parse Python source using ``ast`` and return structured metadata."""

    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except Exception:
            # On syntax errors or decoding issues, fall back to a minimal result
            return {
                "files": {str(path): {"language": "python", "loc": len(text.splitlines())}},
                "functions": {},
                "classes": {},
                "imports": {},
                "exports": {},
            }

        files: Dict[str, Dict] = {
            str(path): {"language": "python", "loc": len(text.splitlines())}
        }
        functions: Dict[str, Dict] = {}
        classes: Dict[str, Dict] = {}
        imports: Dict[str, Dict] = {}
        exports: Dict[str, Dict] = {}
        
        # Enhanced: Store detailed import info (for database)
        imports_detailed = []  # List of import statements with line numbers
        entry_points = []  # Detect entry points

        # Collect imports with detailed info
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    entry = imports.setdefault(mod, {"count": 0})
                    entry["count"] += 1
                    # Store detailed import info
                    imports_detailed.append({
                        "module": mod,
                        "imported_names": [alias.asname or alias.name],
                        "line_number": node.lineno,
                        "import_type": "import",
                        "import_statement": f"import {mod}" + (f" as {alias.asname}" if alias.asname else "")
                    })
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                entry = imports.setdefault(mod, {"count": 0})
                entry["count"] += 1
                # Store detailed import info
                imported_names = [alias.name for alias in node.names]
                imports_detailed.append({
                    "module": mod,
                    "imported_names": imported_names,
                    "line_number": node.lineno,
                    "import_type": "from_import",
                    "import_statement": f"from {mod} import {', '.join(imported_names)}"
                })

        # Only consider top-level defs for functions/classes
        for node in getattr(tree, "body", []):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                func_id = f"{path}::{func_name}"
                complexity = self._calculate_complexity(node)
                calls = self._extract_calls(node)
                
                # Extract parameters with defaults and type hints
                parameters = []
                for arg in node.args.args:
                    param_info = arg.arg
                    # Add type annotation if present
                    if arg.annotation:
                        try:
                            param_info += f": {ast.unparse(arg.annotation)}"
                        except:
                            pass
                    parameters.append(param_info)
                
                # Detect if async
                is_async = isinstance(node, ast.AsyncFunctionDef)
                
                # Extract decorators
                decorators = []
                for dec in node.decorator_list:
                    try:
                        if isinstance(dec, ast.Name):
                            decorators.append(dec.id)
                        elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                            decorators.append(dec.func.id)
                        else:
                            decorators.append(ast.unparse(dec))
                    except:
                        pass
                
                # Extract return type hint
                return_type = None
                if node.returns:
                    try:
                        return_type = ast.unparse(node.returns)
                    except:
                        pass
                
                line_start = node.lineno
                line_end = getattr(node, "end_lineno", node.lineno)
                code_snippet = self._get_source_segment(text, line_start, line_end)

                functions[func_id] = {
                    "id": func_id,
                    "name": func_name,
                    "file": str(path),
                    "line_start": line_start,
                    "line_end": line_end,
                    "complexity": complexity,
                    "calls": calls,
                    "parameters": parameters,
                    "docstring": ast.get_docstring(node),
                    "code": code_snippet,
                    "is_async": is_async,
                    "decorators": decorators,
                    "return_type": return_type,
                }

                # Detect if function is exported (not private)
                if not func_name.startswith("_"):
                    exports.setdefault(func_name, {
                        "kind": "function",
                        "line": line_start,
                        "is_async": is_async
                    })

            elif isinstance(node, ast.ClassDef):
                cls_name = node.name
                cls_id = f"{path}::{cls_name}"
                line_start = node.lineno
                line_end = getattr(node, "end_lineno", node.lineno)
                
                # Extract base classes with better detection
                bases: List[str] = []
                for base in node.bases:
                    try:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            # Handle module.ClassName
                            bases.append(ast.unparse(base))
                        else:
                            bases.append(ast.unparse(base))
                    except:
                        pass
                
                # Extract decorators
                decorators = []
                for dec in node.decorator_list:
                    try:
                        if isinstance(dec, ast.Name):
                            decorators.append(dec.id)
                        elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                            decorators.append(dec.func.id)
                        else:
                            decorators.append(ast.unparse(dec))
                    except:
                        pass
                
                # Extract methods
                methods = []
                for class_node in node.body:
                    if isinstance(class_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = class_node.name
                        is_async = isinstance(class_node, ast.AsyncFunctionDef)
                        is_classmethod = any(
                            (isinstance(d, ast.Name) and d.id == 'classmethod') or
                            (isinstance(d, ast.Attribute) and d.attr == 'classmethod')
                            for d in class_node.decorator_list
                        )
                        is_staticmethod = any(
                            (isinstance(d, ast.Name) and d.id == 'staticmethod') or
                            (isinstance(d, ast.Attribute) and d.attr == 'staticmethod')
                            for d in class_node.decorator_list
                        )
                        is_property = any(
                            (isinstance(d, ast.Name) and d.id == 'property') or
                            (isinstance(d, ast.Attribute) and d.attr == 'property')
                            for d in class_node.decorator_list
                        )
                        
                        methods.append({
                            "name": method_name,
                            "is_async": is_async,
                            "is_classmethod": is_classmethod,
                            "is_staticmethod": is_staticmethod,
                            "is_property": is_property,
                            "is_private": method_name.startswith("_"),
                        })

                classes[cls_id] = {
                    "id": cls_id,
                    "name": cls_name,
                    "file": str(path),
                    "line_start": line_start,
                    "line_end": line_end,
                    "bases": bases,
                    "decorators": decorators,
                    "methods": methods,
                    "docstring": ast.get_docstring(node),
                }

                if not cls_name.startswith("_"):
                    exports.setdefault(cls_name, {"kind": "class", "line": line_start})
        
        # Detect entry points (if __name__ == "__main__")
        for node in tree.body:
            if isinstance(node, ast.If):
                # Check if it's if __name__ == "__main__":
                if isinstance(node.test, ast.Compare):
                    left = node.test.left
                    if isinstance(left, ast.Name) and left.id == "__name__":
                        # Found entry point
                        entry_points.append({
                            "file_path": str(path),
                            "entry_type": "main",
                            "function_name": "__main__",
                            "line_number": node.lineno,
                            "confidence": 1.0
                        })

        return {
            "files": files,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
            "imports_detailed": imports_detailed,  # NEW: Detailed import info
            "entry_points": entry_points,          # NEW: Entry point detection
        }

    # --- helpers ---------------------------------------------------------

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Enhanced cyclomatic complexity calculation.
        
        Accounts for:
        - Control flow (if, for, while, try/except)
        - Boolean operators (and, or)
        - Comprehensions (list/dict/set/generator)
        - Pattern matching (match/case in Python 3.10+)
        - Ternary expressions
        """
        complexity = 1
        for child in ast.walk(node):
            # Basic control flow
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Assert)):
                complexity += 1
            
            # Exception handling
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            
            # Try/except adds complexity per handler
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            
            # Boolean operations (and/or)
            elif isinstance(child, ast.BoolOp):
                complexity += max(0, len(child.values) - 1)
            
            # Comprehensions add complexity
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
                # Each filter in comprehension adds complexity
                for generator in child.generators:
                    complexity += len(generator.ifs)
            
            # Ternary expressions (x if cond else y)
            elif isinstance(child, ast.IfExp):
                complexity += 1
            
            # Pattern matching (Python 3.10+)
            elif hasattr(ast, 'Match') and isinstance(child, ast.Match):
                complexity += len(child.cases)
        
        return complexity

    def _extract_calls(self, node: ast.AST) -> List[str]:
        """Extract function calls with better detection.
        
        Handles:
        - Simple calls: func()
        - Method calls: obj.method()
        - Chained calls: obj.method().another()
        - Module calls: module.func()
        """
        calls: List[str] = []
        seen = set()  # Avoid duplicates
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                call_name = None
                
                if isinstance(func, ast.Name):
                    # Simple function call: func()
                    call_name = func.id
                    
                elif isinstance(func, ast.Attribute):
                    # Method/attribute call: obj.method()
                    # Try to build full path: module.submodule.func
                    parts = []
                    current = func
                    
                    while isinstance(current, ast.Attribute):
                        parts.append(current.attr)
                        current = current.value
                    
                    if isinstance(current, ast.Name):
                        parts.append(current.id)
                    
                    if parts:
                        # Reverse to get correct order
                        call_name = '.'.join(reversed(parts))
                
                if call_name and call_name not in seen:
                    calls.append(call_name)
                    seen.add(call_name)
        
        return calls

    def _get_source_segment(self, text: str, line_start: int, line_end: int) -> str:
        """Return the source lines corresponding to a node.

        We keep this intentionally simple; perfect fidelity is not required for
        ORC's summary/compression use-cases.
        """
        try:
            lines = text.splitlines()
            # ``line_end`` is inclusive in our metadata
            return "\n".join(lines[line_start - 1 : line_end])
        except Exception:
            return ""
