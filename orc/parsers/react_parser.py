"""React/JSX parser built on top of the JavaScript heuristics.

JSX/TSX have richer syntax, but for ORC's purposes we only need to know
where components/functions/classes live, which the base JS regex parser
already approximates reasonably well.
"""
from pathlib import Path
from typing import Dict

from .javascript_parser import JavaScriptParser


class ReactParser(JavaScriptParser):
    def parse_file(self, path: Path) -> Dict:
        data = super().parse_file(path)
        for meta in data.get("files", {}).values():
            meta["language"] = "react"
        return data
