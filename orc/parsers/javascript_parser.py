"""Enhanced JavaScript/TypeScript parser based on regular expressions.

Extracts:
- Functions (function, arrow functions, async)
- Classes (class declarations, extends)
- Imports (ES6, CommonJS)
- Exports (named, default)
- Methods (in classes)
- JSX components

Still regex-based for speed, but with much better detection.
"""
from pathlib import Path
from typing import Dict, List
import re

from .base_parser import BaseParser

# Enhanced patterns for modern JavaScript/TypeScript
_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
_ASYNC_FUNC_RE = re.compile(r"\basync\s+function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
_ARROW_FUNC_RE = re.compile(r"\b(const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")
_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_$][A-Za-z0-9_$]*)(?:\s+extends\s+([A-Za-z_$][A-Za-z0-9_$]*))?")
_METHOD_RE = re.compile(r"^\s*(?:async\s+)?([A-Za-z_$][A-Za-z0-9_$]*)\s*\([^)]*\)\s*\{")
_IMPORT_FROM_RE = re.compile(r"\bimport\b.*?\bfrom\b\s*['\"]([^'\"]+)['\"]")
_IMPORT_REQUIRE_RE = re.compile(r"\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_EXPORT_FUNC_RE = re.compile(r"\bexport\s+(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(")
_EXPORT_CLASS_RE = re.compile(r"\bexport\s+class\s+([A-Za-z_$][A-Za-z0-9_$]*)")
_EXPORT_CONST_RE = re.compile(r"\bexport\s+const\s+([A-Za-z_$][A-Za-z0-9_$]*)")
_EXPORT_DEFAULT_RE = re.compile(r"\bexport\s+default\s+(?:function\s+)?([A-Za-z_$][A-Za-z0-9_$]*)")
_JSX_COMPONENT_RE = re.compile(r"\b(?:const|function)\s+([A-Z][A-Za-z0-9_$]*)\s*[=\(].*?(?:return\s*\(?\s*<|=>.*?<)")

# Complexity indicators
_IF_RE = re.compile(r"\b(if|else\s+if)\s*\(")
_LOOP_RE = re.compile(r"\b(for|while|do)\s*\(")
_SWITCH_RE = re.compile(r"\bswitch\s*\(")
_CASE_RE = re.compile(r"\bcase\s+")
_TERNARY_RE = re.compile(r"\?[^:]+:")
_LOGICAL_RE = re.compile(r"(\|\||&&)")
_TRY_RE = re.compile(r"\btry\s*\{")
_CATCH_RE = re.compile(r"\bcatch\s*\(")


class JavaScriptParser(BaseParser):
    """Enhanced JavaScript/TypeScript parser with better detection."""

    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        # Detect language
        extension = path.suffix.lower()
        if extension in ['.ts', '.tsx']:
            language = "typescript"
        elif extension in ['.jsx', '.tsx']:
            language = "jsx"
        else:
            language = "javascript"

        files: Dict[str, Dict] = {
            str(path): {"language": language, "loc": len(lines)}
        }
        functions: Dict[str, Dict] = {}
        classes: Dict[str, Dict] = {}
        imports: Dict[str, Dict] = {}
        exports: Dict[str, Dict] = {}
        
        current_class = None
        brace_depth = 0

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            
            # Track braces for class scope
            brace_depth += line.count('{') - line.count('}')
            
            # Imports - ES6 and CommonJS
            for m in _IMPORT_FROM_RE.finditer(line):
                module = m.group(1)
                entry = imports.setdefault(module, {"count": 0})
                entry["count"] += 1
            
            for m in _IMPORT_REQUIRE_RE.finditer(line):
                module = m.group(1)
                entry = imports.setdefault(module, {"count": 0})
                entry["count"] += 1

            # Classes
            for m in _CLASS_RE.finditer(line):
                name = m.group(1)
                base_class = m.group(2) if m.lastindex >= 2 else None
                cls_id = f"{path}::{name}"
                current_class = name
                
                classes[cls_id] = {
                    "id": cls_id,
                    "name": name,
                    "file": str(path),
                    "line_start": lineno,
                    "line_end": lineno,  # Updated later
                    "bases": [base_class] if base_class else [],
                    "methods": [],
                }
            
            # Regular functions
            for m in _FUNC_RE.finditer(line):
                name = m.group(1)
                func_id = f"{path}::{name}"
                is_async = 'async' in line[:m.start()]
                
                functions[func_id] = {
                    "id": func_id,
                    "name": name,
                    "file": str(path),
                    "line_start": lineno,
                    "line_end": lineno,  # Approximation
                    "complexity": self._calculate_complexity(line),
                    "calls": self._extract_calls(line),
                    "parameters": self._extract_params(line),
                    "docstring": None,
                    "code": line.strip(),
                    "is_async": is_async,
                }
            
            # Async functions
            for m in _ASYNC_FUNC_RE.finditer(line):
                name = m.group(1)
                func_id = f"{path}::{name}"
                
                functions[func_id] = {
                    "id": func_id,
                    "name": name,
                    "file": str(path),
                    "line_start": lineno,
                    "line_end": lineno,
                    "complexity": self._calculate_complexity(line),
                    "calls": self._extract_calls(line),
                    "parameters": self._extract_params(line),
                    "docstring": None,
                    "code": line.strip(),
                    "is_async": True,
                }
            
            # Arrow functions
            for m in _ARROW_FUNC_RE.finditer(line):
                name = m.group(2)
                func_id = f"{path}::{name}"
                is_async = 'async' in line
                
                functions[func_id] = {
                    "id": func_id,
                    "name": name,
                    "file": str(path),
                    "line_start": lineno,
                    "line_end": lineno,
                    "complexity": self._calculate_complexity(line),
                    "calls": self._extract_calls(line),
                    "parameters": self._extract_params(line),
                    "docstring": None,
                    "code": line.strip(),
                    "is_async": is_async,
                    "is_arrow": True,
                }
            
            # JSX Components
            for m in _JSX_COMPONENT_RE.finditer(line):
                name = m.group(1)
                func_id = f"{path}::{name}"
                
                functions[func_id] = {
                    "id": func_id,
                    "name": name,
                    "file": str(path),
                    "line_start": lineno,
                    "line_end": lineno,
                    "complexity": self._calculate_complexity(line),
                    "calls": self._extract_calls(line),
                    "parameters": [],
                    "docstring": None,
                    "code": line.strip(),
                    "is_component": True,
                }
            
            # Methods within classes
            if current_class and brace_depth > 0:
                for m in _METHOD_RE.finditer(line):
                    method_name = m.group(1)
                    cls_id = f"{path}::{current_class}"
                    if cls_id in classes:
                        is_async = 'async' in line[:m.start()]
                        classes[cls_id]["methods"].append({
                            "name": method_name,
                            "line": lineno,
                            "is_async": is_async,
                        })
            
            # Reset current class when exiting
            if current_class and brace_depth == 0:
                current_class = None

            # Exports
            for m in _EXPORT_FUNC_RE.finditer(line):
                exports[m.group(1)] = {"kind": "function"}
            for m in _EXPORT_CLASS_RE.finditer(line):
                exports[m.group(1)] = {"kind": "class"}
            for m in _EXPORT_CONST_RE.finditer(line):
                exports[m.group(1)] = {"kind": "const"}
            for m in _EXPORT_DEFAULT_RE.finditer(line):
                exports.setdefault(m.group(1), {"kind": "default"})

        return {
            "files": files,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
        }
    
    def _calculate_complexity(self, line: str) -> int:
        """Calculate cyclomatic complexity for a line/block."""
        complexity = 1
        complexity += len(_IF_RE.findall(line))
        complexity += len(_LOOP_RE.findall(line))
        complexity += len(_SWITCH_RE.findall(line))
        complexity += len(_CASE_RE.findall(line))
        complexity += len(_TERNARY_RE.findall(line))
        complexity += len(_LOGICAL_RE.findall(line))
        complexity += len(_TRY_RE.findall(line))
        complexity += len(_CATCH_RE.findall(line))
        return complexity
    
    def _extract_calls(self, line: str) -> List[str]:
        """Extract function calls from a line."""
        # Match function calls: functionName( or obj.method(
        call_pattern = re.compile(r'([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)\s*\(')
        calls = []
        for m in call_pattern.finditer(line):
            call_name = m.group(1)
            if call_name not in ['if', 'for', 'while', 'switch', 'catch', 'function']:
                calls.append(call_name)
        return calls
    
    def _extract_params(self, line: str) -> List[str]:
        """Extract function parameters."""
        # Simple parameter extraction from function signature
        param_match = re.search(r'\(([^)]*)\)', line)
        if param_match:
            params_str = param_match.group(1).strip()
            if params_str:
                # Split by comma, handle destructuring basics
                return [p.strip().split('=')[0].strip() for p in params_str.split(',')]
        return []
