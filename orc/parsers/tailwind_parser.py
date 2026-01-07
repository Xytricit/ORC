"""Tailwind/CSS utility-focused parser stub.

This stub reads files and provides a tiny detector for Tailwind-style
utility classes (very small heuristic). Real implementation should
parse CSS/HTML and extract utility usage and configuration.
"""
import re
from pathlib import Path
from typing import Dict


TAILWIND_RE = re.compile(r"\b(?:bg|text|p|m|w|h|flex|grid|items|justify|gap)-[\w:-]+\b")


class TailwindParser:
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        utilities = set(TAILWIND_RE.findall(text))
        return {"files": {str(path): text}, "functions": {}, "classes": {}, "imports": {}, "exports": {}, "tailwind_utils": list(utilities)}
