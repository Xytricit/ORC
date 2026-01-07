"""Markdown parser.

For now we just record the file and mark that it is markdown; higher
layers can decide what to do with the content itself.
"""
from pathlib import Path
from typing import Dict


class MarkdownParser:
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        files = {str(path): {"language": "markdown", "loc": len(lines)}}

        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "markdown": True,
        }
