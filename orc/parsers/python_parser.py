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

        # Collect imports (all levels)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    entry = imports.setdefault(mod, {"count": 0})
                    entry["count"] += 1
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                entry = imports.setdefault(mod, {"count": 0})
                entry["count"] += 1

        # Only consider top-level defs for functions/classes
        for node in getattr(tree, "body", []):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                func_id = f"{path}::{func_name}"
                complexity = self._calculate_complexity(node)
                calls = self._extract_calls(node)
                parameters = [arg.arg for arg in node.args.args]
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
                }

                if not func_name.startswith("_"):
                    exports.setdefault(func_name, {"kind": "function"})

            elif isinstance(node, ast.ClassDef):
                cls_name = node.name
                cls_id = f"{path}::{cls_name}"
                line_start = node.lineno
                line_end = getattr(node, "end_lineno", node.lineno)
                bases: List[str] = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)

                classes[cls_id] = {
                    "id": cls_id,
                    "name": cls_name,
                    "file": str(path),
                    "line_start": line_start,
                    "line_end": line_end,
                    "bases": bases,
                }

                if not cls_name.startswith("_"):
                    exports.setdefault(cls_name, {"kind": "class"})

        return {
            "files": files,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
        }

    # --- helpers ---------------------------------------------------------

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Very small cyclomatic complexity approximation."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(
                child,
                (ast.If, ast.For, ast.While, ast.With, ast.Assert, ast.ExceptHandler),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += max(0, len(child.values) - 1)
        return complexity

    def _extract_calls(self, node: ast.AST) -> List[str]:
        calls: List[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name):
                    calls.append(func.id)
                elif isinstance(func, ast.Attribute):
                    calls.append(func.attr)
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
