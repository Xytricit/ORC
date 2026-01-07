"""YAML parser.

Similar contract to :class:`JSONParser` – it records the file with a
``language`` + ``loc`` entry and, if PyYAML is available, attaches a
parsed representation under the top-level ``yaml`` key.
"""
from pathlib import Path
from typing import Dict
try:
    import yaml  # optional dependency
except Exception:
    yaml = None


class YAMLParser:
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        data = None
        if yaml:
            try:
                data = yaml.safe_load(text)
            except Exception:
                data = None

        files = {str(path): {"language": "yaml", "loc": len(lines)}}

        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "yaml": data,
        }
