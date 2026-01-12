"""Full-featured HTML/CSS parser.

Extracts:
- HTML: Tags, IDs, classes, attributes, links, scripts, meta tags
- CSS: Selectors, classes, IDs, pseudo-classes, media queries, keyframes
- Structure: DOM hierarchy, CSS rules organization
"""
from pathlib import Path
from typing import Dict, Set, List
import re

from .base_parser import BaseParser


class HTMLCSSParser(BaseParser):
    """Enhanced HTML/CSS parser with comprehensive feature extraction."""
    
    # HTML patterns
    HTML_TAG_RE = re.compile(r'<([a-z][a-z0-9]*)[^>]*>', re.IGNORECASE)
    HTML_CLASS_RE = re.compile(r'class=["\']([^"\']+)["\']')
    HTML_ID_RE = re.compile(r'id=["\']([^"\']+)["\']')
    HTML_LINK_RE = re.compile(r'<link[^>]+href=["\']([^"\']+)["\']')
    HTML_SCRIPT_RE = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']')
    HTML_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
    HTML_A_HREF_RE = re.compile(r'<a[^>]+href=["\']([^"\']+)["\']')
    HTML_META_RE = re.compile(r'<meta[^>]+name=["\']([^"\']+)["\']')
    
    # CSS patterns
    CSS_CLASS_RE = re.compile(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)')
    CSS_ID_RE = re.compile(r'#([a-zA-Z_-][a-zA-Z0-9_-]*)')
    CSS_SELECTOR_RE = re.compile(r'([^{]+)\s*\{')
    CSS_PSEUDO_RE = re.compile(r':([a-z-]+)')
    CSS_MEDIA_QUERY_RE = re.compile(r'@media\s+([^{]+)\s*\{')
    CSS_KEYFRAMES_RE = re.compile(r'@keyframes\s+([a-zA-Z_-][a-zA-Z0-9_-]*)')
    CSS_VARIABLE_RE = re.compile(r'--([a-zA-Z0-9_-]+)\s*:')
    CSS_IMPORT_RE = re.compile(r'@import\s+["\']([^"\']+)["\']')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse HTML or CSS file and extract all elements."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        ext = path.suffix.lower()
        
        if ext in {".html", ".htm"}:
            return self._parse_html(text, lines, path)
        elif ext in {".css"}:
            return self._parse_css(text, lines, path)
        else:
            return self._empty_result(path)
    
    def _empty_result(self, path: Path) -> Dict:
        """Return empty parsing result."""
        return {
            "files": {str(path): {"language": "unknown", "loc": 0}},
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
        }
    
    def _parse_html(self, text: str, lines: List[str], path: Path) -> Dict:
        """Parse HTML file."""
        # Extract HTML features
        tags = self._extract_html_tags(text)
        classes = self._extract_html_classes(text, path)
        ids = self._extract_html_ids(text, path)
        links = self._extract_html_links(text)
        scripts = self._extract_html_scripts(text)
        images = self._extract_html_images(text)
        anchors = self._extract_html_anchors(text)
        meta_tags = self._extract_html_meta(text)
        
        files = {
            str(path): {
                "language": "html",
                "loc": len(lines),
                "html_features": {
                    "unique_tags": len(set(tags)),
                    "total_tags": len(tags),
                    "classes": len(classes),
                    "ids": len(ids),
                    "external_links": len(links),
                    "scripts": len(scripts),
                    "images": len(images),
                    "anchors": len(anchors),
                    "meta_tags": len(meta_tags),
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": classes,
            "imports": {"stylesheets": links, "scripts": scripts},
            "exports": {},
            "html_tags": tags,
            "html_ids": ids,
            "html_images": images,
            "html_anchors": anchors,
            "html_meta": meta_tags,
        }
    
    def _parse_css(self, text: str, lines: List[str], path: Path) -> Dict:
        """Parse CSS file."""
        # Extract CSS features
        classes = self._extract_css_classes(text, path)
        ids = self._extract_css_ids(text, path)
        selectors = self._extract_css_selectors(text)
        pseudo_classes = self._extract_css_pseudo_classes(text)
        media_queries = self._extract_css_media_queries(text)
        keyframes = self._extract_css_keyframes(text, path)
        variables = self._extract_css_variables(text)
        imports = self._extract_css_imports(text)
        
        files = {
            str(path): {
                "language": "css",
                "loc": len(lines),
                "css_features": {
                    "classes": len(classes),
                    "ids": len(ids),
                    "selectors": len(selectors),
                    "pseudo_classes": len(set(pseudo_classes)),
                    "media_queries": len(media_queries),
                    "keyframes": len(keyframes),
                    "css_variables": len(variables),
                    "imports": len(imports),
                }
            }
        }
        
        return {
            "files": files,
            "functions": keyframes,  # Keyframes are like functions
            "classes": classes,
            "imports": {"css_files": imports},
            "exports": {},
            "css_ids": ids,
            "css_selectors": selectors,
            "css_pseudo_classes": pseudo_classes,
            "css_media_queries": media_queries,
            "css_variables": variables,
        }
    
    # HTML extraction methods
    def _extract_html_tags(self, text: str) -> List[str]:
        """Extract all HTML tags."""
        return [match.group(1).lower() for match in self.HTML_TAG_RE.finditer(text)]
    
    def _extract_html_classes(self, text: str, path: Path) -> Dict:
        """Extract HTML classes."""
        classes = {}
        seen = set()
        
        for match in self.HTML_CLASS_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            for cls in match.group(1).split():
                key = f"{path}::{cls}"
                if key not in seen:
                    seen.add(key)
                    classes[key] = {
                        "id": key,
                        "name": cls,
                        "file": str(path),
                        "line": line_no,
                        "kind": "html_class",
                    }
        
        return classes
    
    def _extract_html_ids(self, text: str, path: Path) -> Dict:
        """Extract HTML IDs."""
        ids = {}
        seen = set()
        
        for match in self.HTML_ID_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            id_name = match.group(1)
            key = f"{path}::{id_name}"
            if key not in seen:
                seen.add(key)
                ids[key] = {
                    "id": key,
                    "name": id_name,
                    "file": str(path),
                    "line": line_no,
                    "kind": "html_id",
                }
        
        return ids
    
    def _extract_html_links(self, text: str) -> List[str]:
        """Extract external stylesheet links."""
        return [match.group(1) for match in self.HTML_LINK_RE.finditer(text)]
    
    def _extract_html_scripts(self, text: str) -> List[str]:
        """Extract external script sources."""
        return [match.group(1) for match in self.HTML_SCRIPT_RE.finditer(text)]
    
    def _extract_html_images(self, text: str) -> List[str]:
        """Extract image sources."""
        return [match.group(1) for match in self.HTML_IMG_RE.finditer(text)]
    
    def _extract_html_anchors(self, text: str) -> List[str]:
        """Extract anchor hrefs."""
        return [match.group(1) for match in self.HTML_A_HREF_RE.finditer(text)]
    
    def _extract_html_meta(self, text: str) -> List[str]:
        """Extract meta tag names."""
        return [match.group(1) for match in self.HTML_META_RE.finditer(text)]
    
    # CSS extraction methods
    def _extract_css_classes(self, text: str, path: Path) -> Dict:
        """Extract CSS classes."""
        classes = {}
        seen = set()
        
        for match in self.CSS_CLASS_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            cls = match.group(1)
            key = f"{path}::{cls}"
            if key not in seen:
                seen.add(key)
                classes[key] = {
                    "id": key,
                    "name": cls,
                    "file": str(path),
                    "line": line_no,
                    "kind": "css_class",
                }
        
        return classes
    
    def _extract_css_ids(self, text: str, path: Path) -> Dict:
        """Extract CSS IDs."""
        ids = {}
        seen = set()
        
        for match in self.CSS_ID_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            id_name = match.group(1)
            key = f"{path}::{id_name}"
            if key not in seen:
                seen.add(key)
                ids[key] = {
                    "id": key,
                    "name": id_name,
                    "file": str(path),
                    "line": line_no,
                    "kind": "css_id",
                }
        
        return ids
    
    def _extract_css_selectors(self, text: str) -> List[str]:
        """Extract all CSS selectors."""
        selectors = []
        for match in self.CSS_SELECTOR_RE.finditer(text):
            selector = match.group(1).strip()
            if selector and not selector.startswith('@'):
                selectors.append(selector)
        return selectors
    
    def _extract_css_pseudo_classes(self, text: str) -> List[str]:
        """Extract pseudo-classes and pseudo-elements."""
        return [match.group(1) for match in self.CSS_PSEUDO_RE.finditer(text)]
    
    def _extract_css_media_queries(self, text: str) -> List[Dict]:
        """Extract media queries."""
        media_queries = []
        for match in self.CSS_MEDIA_QUERY_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            media_queries.append({
                "query": match.group(1).strip(),
                "line": line_no,
            })
        return media_queries
    
    def _extract_css_keyframes(self, text: str, path: Path) -> Dict:
        """Extract CSS keyframes (animations)."""
        keyframes = {}
        for match in self.CSS_KEYFRAMES_RE.finditer(text):
            name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            keyframes[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line": line_no,
                "kind": "keyframe",
            }
        return keyframes
    
    def _extract_css_variables(self, text: str) -> List[Dict]:
        """Extract CSS custom properties (variables)."""
        variables = []
        seen = set()
        for match in self.CSS_VARIABLE_RE.finditer(text):
            var_name = match.group(1)
            if var_name not in seen:
                seen.add(var_name)
                line_no = text[:match.start()].count('\n') + 1
                variables.append({
                    "name": f"--{var_name}",
                    "line": line_no,
                })
        return variables
    
    def _extract_css_imports(self, text: str) -> List[str]:
        """Extract CSS @import statements."""
        return [match.group(1) for match in self.CSS_IMPORT_RE.finditer(text)]
