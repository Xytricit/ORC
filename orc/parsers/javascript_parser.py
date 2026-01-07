"""Lightweight JavaScript parser based on regular expressions.

This is *not* a full JS parser; it only extracts obvious top-level
``function`` / ``class`` declarations and ``import`` / ``export``
statements using simple line-based heuristics. It is dependency-free and
good enough for indexing and navigation.
"""
from pathlib import Path
from typing import Dict, List
import re

from .base_parser import BaseParser

# Simple patterns for top-level declarations
_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_IMPORT_RE = re.compile(r"\bimport\b.*?\bfrom\b\s*['\"]([^'\"]+)['\"]")
_EXPORT_FUNC_RE = re.compile(r"\bexport\s+function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_EXPORT_CLASS_RE = re.compile(r"\bexport\s+class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_EXPORT_DEFAULT_RE = re.compile(r"\bexport\s+default\s+([A-Za-z_][A-Za-z0-9_]*)")


class JavaScriptParser(BaseParser):
    """Heuristic JavaScript parser (no external dependencies)."""

    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        files: Dict[str, Dict] = {
            str(path): {"language": "javascript", "loc": len(lines)}
        }
        functions: Dict[str, Dict] = {}
        classes: Dict[str, Dict] = {}
        imports: Dict[str, Dict] = {}
        exports: Dict[str, Dict] = {}

        for lineno, line in enumerate(lines, start=1):
            # Imports
            m_import = _IMPORT_RE.search(line)
            if m_import:
                module = m_import.group(1)
                entry = imports.setdefault(module, {"count": 0})
                entry["count"] += 1

            # Functions
            for m in _FUNC_RE.finditer(line):
                name = m.group(1)
                func_id = f"{path}::{name}"
                functions.setdefault(
                    func_id,
                    {
                        "id": func_id,
                        "name": name,
                        "file": str(path),
                        "line_start": lineno,
                        "line_end": lineno,
                        "complexity": 1,
                        "calls": [],
                        "parameters": [],
                        "docstring": None,
                        "code": line.strip(),
                    },
                )

            # Classes
            for m in _CLASS_RE.finditer(line):
                name = m.group(1)
                cls_id = f"{path}::{name}"
                classes.setdefault(
                    cls_id,
                    {
                        "id": cls_id,
                        "name": name,
                        "file": str(path),
                        "line_start": lineno,
                        "line_end": lineno,
                    },
                )

            # Exports
            for m in _EXPORT_FUNC_RE.finditer(line):
                exports[m.group(1)] = {"kind": "function"}
            for m in _EXPORT_CLASS_RE.finditer(line):
                exports[m.group(1)] = {"kind": "class"}
            for m in _EXPORT_DEFAULT_RE.finditer(line):
                # Prefer not to overwrite named exports
                exports.setdefault(m.group(1), {"kind": "default"})

        return {
            "files": files,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
        }
