"""TypeScript parser built on top of the JavaScript heuristics.

We reuse the JavaScript regex-based parser but tag the language as
"typescript" in the file metadata.
"""
from pathlib import Path
from typing import Dict

from .javascript_parser import JavaScriptParser


class TypeScriptParser(JavaScriptParser):
    def parse_file(self, path: Path) -> Dict:
        data = super().parse_file(path)
        # Override language tag for all files in this result
        for meta in data.get("files", {}).values():
            meta["language"] = "typescript"
        return data
