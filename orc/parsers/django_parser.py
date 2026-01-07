"""Django-specific parser built on top of :class:`PythonParser`.

For now this simply delegates to the Python parser and tags the file
metadata with ``framework = 'django'`` so higher-level tooling can
special-case Django projects.
"""
from pathlib import Path
from typing import Dict

from .python_parser import PythonParser


class DjangoParser(PythonParser):
    def parse_file(self, path: Path) -> Dict:
        data = super().parse_file(path)
        for meta in data.get("files", {}).values():
            meta["framework"] = "django"
        return data
