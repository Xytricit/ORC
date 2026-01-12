"""Full-featured SCSS parser.

Extracts:
- Variables ($variable)
- Mixins (@mixin)
- Functions (@function)
- Imports (@import, @use, @forward)
- Nesting structures
- Extends (@extend)
- Placeholders (%)
- Control directives (@if, @for, @each, @while)
- CSS classes and IDs
"""
import re
from pathlib import Path
from typing import Dict, List


class SCSSParser:
    """Enhanced SCSS parser with comprehensive feature extraction."""
    
    # SCSS-specific patterns
    VARIABLE_RE = re.compile(r'\$([a-zA-Z0-9_-]+)\s*:')
    MIXIN_RE = re.compile(r'@mixin\s+([a-zA-Z0-9_-]+)\s*(?:\([^)]*\))?\s*\{')
    FUNCTION_RE = re.compile(r'@function\s+([a-zA-Z0-9_-]+)\s*\([^)]*\)\s*\{')
    IMPORT_RE = re.compile(r'@import\s+["\']([^"\']+)["\']')
    USE_RE = re.compile(r'@use\s+["\']([^"\']+)["\']')
    FORWARD_RE = re.compile(r'@forward\s+["\']([^"\']+)["\']')
    INCLUDE_RE = re.compile(r'@include\s+([a-zA-Z0-9_-]+)')
    EXTEND_RE = re.compile(r'@extend\s+([.%#]?[a-zA-Z0-9_-]+)')
    PLACEHOLDER_RE = re.compile(r'%([a-zA-Z0-9_-]+)\s*\{')
    CLASS_RE = re.compile(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)')
    ID_RE = re.compile(r'#([a-zA-Z_-][a-zA-Z0-9_-]*)')
    NESTED_RE = re.compile(r'&')
    IF_RE = re.compile(r'@if\s+')
    FOR_RE = re.compile(r'@for\s+')
    EACH_RE = re.compile(r'@each\s+')
    WHILE_RE = re.compile(r'@while\s+')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse SCSS file and extract all SCSS-specific features."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        
        # Extract SCSS features
        variables = self._extract_variables(text, path)
        mixins = self._extract_mixins(text, path)
        functions = self._extract_functions(text, path)
        imports = self._extract_imports(text)
        includes = self._extract_includes(text)
        extends = self._extract_extends(text)
        placeholders = self._extract_placeholders(text, path)
        classes = self._extract_classes(text, path)
        ids = self._extract_ids(text, path)
        control_directives = self._extract_control_directives(text)
        
        files = {
            str(path): {
                "language": "scss",
                "loc": len(lines),
                "scss_features": {
                    "variables": len(variables),
                    "mixins": len(mixins),
                    "functions": len(functions),
                    "imports": len(imports['import']) + len(imports['use']) + len(imports['forward']),
                    "includes": len(includes),
                    "extends": len(extends),
                    "placeholders": len(placeholders),
                    "classes": len(classes),
                    "control_directives": sum(control_directives.values()),
                }
            }
        }
        
        return {
            "files": files,
            "functions": functions,
            "classes": {**classes, **placeholders},
            "imports": imports,
            "exports": {},
            "scss_variables": variables,
            "scss_mixins": mixins,
            "scss_includes": includes,
            "scss_extends": extends,
            "scss_ids": ids,
            "scss_control": control_directives,
        }
    
    def _empty_result(self, path: Path) -> Dict:
        """Return empty parsing result."""
        return {
            "files": {str(path): {"language": "scss", "loc": 0}},
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
        }
    
    def _extract_variables(self, text: str, path: Path) -> Dict:
        """Extract SCSS variables."""
        variables = {}
        seen = set()
        
        for match in self.VARIABLE_RE.finditer(text):
            var_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{path}::{var_name}"
            if key not in seen:
                seen.add(key)
                variables[key] = {
                    "id": key,
                    "name": f"${var_name}",
                    "file": str(path),
                    "line": line_no,
                    "kind": "scss_variable",
                }
        
        return variables
    
    def _extract_mixins(self, text: str, path: Path) -> Dict:
        """Extract SCSS mixins."""
        mixins = {}
        
        for match in self.MIXIN_RE.finditer(text):
            mixin_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            mixins[f"{path}::{mixin_name}"] = {
                "id": f"{path}::{mixin_name}",
                "name": mixin_name,
                "file": str(path),
                "line": line_no,
                "kind": "scss_mixin",
            }
        
        return mixins
    
    def _extract_functions(self, text: str, path: Path) -> Dict:
        """Extract SCSS functions."""
        functions = {}
        
        for match in self.FUNCTION_RE.finditer(text):
            func_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            functions[f"{path}::{func_name}"] = {
                "id": f"{path}::{func_name}",
                "name": func_name,
                "file": str(path),
                "line": line_no,
                "kind": "scss_function",
            }
        
        return functions
    
    def _extract_imports(self, text: str) -> Dict:
        """Extract SCSS imports (@import, @use, @forward)."""
        imports = {
            "import": [match.group(1) for match in self.IMPORT_RE.finditer(text)],
            "use": [match.group(1) for match in self.USE_RE.finditer(text)],
            "forward": [match.group(1) for match in self.FORWARD_RE.finditer(text)],
        }
        return imports
    
    def _extract_includes(self, text: str) -> List[Dict]:
        """Extract @include statements."""
        includes = []
        seen = set()
        
        for match in self.INCLUDE_RE.finditer(text):
            mixin_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{mixin_name}:{line_no}"
            if key not in seen:
                seen.add(key)
                includes.append({
                    "mixin": mixin_name,
                    "line": line_no,
                })
        
        return includes
    
    def _extract_extends(self, text: str) -> List[Dict]:
        """Extract @extend statements."""
        extends = []
        seen = set()
        
        for match in self.EXTEND_RE.finditer(text):
            selector = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{selector}:{line_no}"
            if key not in seen:
                seen.add(key)
                extends.append({
                    "selector": selector,
                    "line": line_no,
                })
        
        return extends
    
    def _extract_placeholders(self, text: str, path: Path) -> Dict:
        """Extract SCSS placeholders."""
        placeholders = {}
        
        for match in self.PLACEHOLDER_RE.finditer(text):
            placeholder_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            placeholders[f"{path}::%{placeholder_name}"] = {
                "id": f"{path}::%{placeholder_name}",
                "name": f"%{placeholder_name}",
                "file": str(path),
                "line": line_no,
                "kind": "scss_placeholder",
            }
        
        return placeholders
    
    def _extract_classes(self, text: str, path: Path) -> Dict:
        """Extract CSS classes."""
        classes = {}
        seen = set()
        
        for match in self.CLASS_RE.finditer(text):
            class_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{path}::.{class_name}"
            if key not in seen:
                seen.add(key)
                classes[key] = {
                    "id": key,
                    "name": f".{class_name}",
                    "file": str(path),
                    "line": line_no,
                    "kind": "css_class",
                }
        
        return classes
    
    def _extract_ids(self, text: str, path: Path) -> Dict:
        """Extract CSS IDs."""
        ids = {}
        seen = set()
        
        for match in self.ID_RE.finditer(text):
            id_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{path}::#{id_name}"
            if key not in seen:
                seen.add(key)
                ids[key] = {
                    "id": key,
                    "name": f"#{id_name}",
                    "file": str(path),
                    "line": line_no,
                    "kind": "css_id",
                }
        
        return ids
    
    def _extract_control_directives(self, text: str) -> Dict:
        """Count control directives."""
        return {
            "if": len(self.IF_RE.findall(text)),
            "for": len(self.FOR_RE.findall(text)),
            "each": len(self.EACH_RE.findall(text)),
            "while": len(self.WHILE_RE.findall(text)),
        }
