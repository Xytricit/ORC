"""LESS parser (CSS preprocessor).

Extracts:
- Variables (@variable)
- Mixins (.mixin)
- Imports (@import)
- Classes and IDs
"""
import re
from pathlib import Path
from typing import Dict, List


class LESSParser:
    """LESS parser with LESS-specific feature extraction."""
    
    # LESS-specific patterns (uses @ for variables instead of $)
    VARIABLE_RE = re.compile(r'@([a-zA-Z0-9_-]+)\s*:')
    MIXIN_RE = re.compile(r'\.([a-zA-Z0-9_-]+)\s*\([^)]*\)\s*\{')
    IMPORT_RE = re.compile(r'@import\s+["\']([^"\']+)["\']')
    CLASS_RE = re.compile(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)')
    ID_RE = re.compile(r'#([a-zA-Z_-][a-zA-Z0-9_-]*)')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse LESS file."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        
        # Extract LESS features
        variables = self._extract_variables(text, path)
        mixins = self._extract_mixins(text, path)
        imports = self._extract_imports(text)
        classes = self._extract_classes(text, path)
        ids = self._extract_ids(text, path)
        
        files = {
            str(path): {
                "language": "less",
                "loc": len(lines),
                "less_features": {
                    "variables": len(variables),
                    "mixins": len(mixins),
                    "imports": len(imports),
                    "classes": len(classes),
                }
            }
        }
        
        return {
            "files": files,
            "functions": mixins,
            "classes": classes,
            "imports": {"import": imports},
            "exports": {},
            "less_variables": variables,
            "less_ids": ids,
        }
    
    def _empty_result(self, path: Path) -> Dict:
        return {
            "files": {str(path): {"language": "less", "loc": 0}},
            "functions": {}, "classes": {}, "imports": {}, "exports": {},
        }
    
    def _extract_variables(self, text: str, path: Path) -> Dict:
        variables = {}
        seen = set()
        for match in self.VARIABLE_RE.finditer(text):
            var_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            key = f"{path}::{var_name}"
            if key not in seen:
                seen.add(key)
                variables[key] = {
                    "id": key, "name": f"@{var_name}",
                    "file": str(path), "line": line_no, "kind": "less_variable",
                }
        return variables
    
    def _extract_mixins(self, text: str, path: Path) -> Dict:
        mixins = {}
        for match in self.MIXIN_RE.finditer(text):
            mixin_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            mixins[f"{path}::{mixin_name}"] = {
                "id": f"{path}::{mixin_name}", "name": mixin_name,
                "file": str(path), "line": line_no, "kind": "less_mixin",
            }
        return mixins
    
    def _extract_imports(self, text: str) -> List[str]:
        return [match.group(1) for match in self.IMPORT_RE.finditer(text)]
    
    def _extract_classes(self, text: str, path: Path) -> Dict:
        classes = {}
        seen = set()
        for match in self.CLASS_RE.finditer(text):
            class_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            key = f"{path}::.{class_name}"
            if key not in seen:
                seen.add(key)
                classes[key] = {
                    "id": key, "name": f".{class_name}",
                    "file": str(path), "line": line_no, "kind": "css_class",
                }
        return classes
    
    def _extract_ids(self, text: str, path: Path) -> Dict:
        ids = {}
        seen = set()
        for match in self.ID_RE.finditer(text):
            id_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            key = f"{path}::#{id_name}"
            if key not in seen:
                seen.add(key)
                ids[key] = {
                    "id": key, "name": f"#{id_name}",
                    "file": str(path), "line": line_no, "kind": "css_id",
                }
        return ids
