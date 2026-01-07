"""FastAPI-specific parser built on top of :class:`PythonParser`.

We rely on the Python AST parser and annotate file metadata with a
``framework = 'fastapi'`` flag.
"""
from pathlib import Path
from typing import Dict

from .python_parser import PythonParser


class FastAPIParser(PythonParser):
    def parse_file(self, path: Path) -> Dict:
        data = super().parse_file(path)
        for meta in data.get("files", {}).values():
            meta["framework"] = "fastapi"
        return data
