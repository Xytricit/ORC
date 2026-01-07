"""JSON parser.

Returns a shape compatible with other ORC parsers:

    {
        "files": {"/abs/file.json": {"language": "json", "loc": 10}},
        "functions": {},
        "classes": {},
        "imports": {},
        "exports": {},
        "json": <parsed-or-None>,
    }
"""
from pathlib import Path
from typing import Dict
import json


class JSONParser:
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        try:
            data = json.loads(text)
        except Exception:
            data = None

        files = {str(path): {"language": "json", "loc": len(lines)}}

        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "json": data,
        }
