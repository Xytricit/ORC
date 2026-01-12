"""Tailwind CSS parser.

Extracts:
- Tailwind utility classes
- Config files (tailwind.config.js/ts)
- Custom classes and theme values
- @apply directives
- @layer directives
"""
from pathlib import Path
from typing import Dict, List
import re


class TailwindParser:
    """Tailwind parser for utility classes and configuration."""
    
    UTILITY_CLASS_RE = re.compile(r'\b([a-z][\w-]*:)?([a-z][\w-]*-(?:\d+|[a-z]+))\b')
    APPLY_RE = re.compile(r'@apply\s+([^;]+);')
    LAYER_RE = re.compile(r'@layer\s+(\w+)')
    CONFIG_THEME_RE = re.compile(r'theme:\s*\{')
    CONFIG_EXTEND_RE = re.compile(r'extend:\s*\{')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse Tailwind file (CSS or config)."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        is_config = path.suffix in ['.js', '.ts'] and 'tailwind' in path.name
        
        if is_config:
            return self._parse_config(text, lines, path)
        else:
            return self._parse_css(text, lines, path)
    
    def _parse_css(self, text: str, lines: List[str], path: Path) -> Dict:
        """Parse Tailwind CSS file."""
        utility_classes = self._extract_utility_classes(text)
        apply_directives = self._extract_apply_directives(text)
        layer_directives = self._extract_layer_directives(text)
        
        files = {
            str(path): {
                "language": "tailwind",
                "loc": len(lines),
                "tailwind_features": {
                    "utility_classes": len(set(utility_classes)),
                    "apply_directives": len(apply_directives),
                    "layers": len(layer_directives),
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "tailwind_classes": list(set(utility_classes)),
            "tailwind_apply": apply_directives,
            "tailwind_layers": layer_directives,
        }
    
    def _parse_config(self, text: str, lines: List[str], path: Path) -> Dict:
        """Parse Tailwind config file."""
        has_theme = bool(self.CONFIG_THEME_RE.search(text))
        has_extend = bool(self.CONFIG_EXTEND_RE.search(text))
        
        files = {
            str(path): {
                "language": "tailwind_config",
                "loc": len(lines),
                "tailwind_config": {
                    "has_theme": has_theme,
                    "has_extend": has_extend,
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
        }
    
    def _empty_result(self, path: Path) -> Dict:
        return {
            "files": {str(path): {"language": "tailwind", "loc": 0}},
            "functions": {}, "classes": {}, "imports": {}, "exports": {},
        }
    
    def _extract_utility_classes(self, text: str) -> List[str]:
        """Extract Tailwind utility classes."""
        classes = []
        for match in self.UTILITY_CLASS_RE.finditer(text):
            full_class = match.group(0)
            classes.append(full_class)
        return classes
    
    def _extract_apply_directives(self, text: str) -> List[Dict]:
        """Extract @apply directives."""
        applies = []
        for match in self.APPLY_RE.finditer(text):
            classes = match.group(1).strip().split()
            line_no = text[:match.start()].count('\n') + 1
            applies.append({
                "classes": classes,
                "line": line_no,
            })
        return applies
    
    def _extract_layer_directives(self, text: str) -> List[str]:
        """Extract @layer directives."""
        return [match.group(1) for match in self.LAYER_RE.finditer(text)]
