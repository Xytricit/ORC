"""Very small HTML/CSS parser.

We do two things:

* record the file with language + LOC
* extract CSS/HTML "classes" (``class="..."`` in HTML, ``.class`` in CSS)
"""
from pathlib import Path
from typing import Dict, Set
import re

from .base_parser import BaseParser

_HTML_CLASS_RE = re.compile(r"class=\"([^\"]+)\"")
_CSS_CLASS_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*[{,]")


class HTMLCSSParser(BaseParser):
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        ext = path.suffix.lower()

        language = "html" if ext in {".html", ".htm"} else "css"
        files: Dict[str, Dict] = {
            str(path): {"language": language, "loc": len(lines)}
        }

        classes: Dict[str, Dict] = {}
        seen: Set[str] = set()

        for lineno, line in enumerate(lines, start=1):
            # HTML class="foo bar"
            for m in _HTML_CLASS_RE.finditer(line):
                for cls in m.group(1).split():
                    key = f"{path}::{cls}"
                    if key not in seen:
                        seen.add(key)
                        classes[key] = {
                            "id": key,
                            "name": cls,
                            "file": str(path),
                            "line_start": lineno,
                            "line_end": lineno,
                            "kind": "css_class",
                        }

            # CSS .class { ... }
            for m in _CSS_CLASS_RE.finditer(line):
                cls = m.group(1)
                key = f"{path}::{cls}"
                if key not in seen:
                    seen.add(key)
                    classes[key] = {
                        "id": key,
                        "name": cls,
                        "file": str(path),
                        "line_start": lineno,
                        "line_end": lineno,
                        "kind": "css_class",
                    }

        return {
            "files": files,
            "functions": {},
            "classes": classes,
            "imports": {},
            "exports": {},
        }
