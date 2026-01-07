"""SCSS parser stub."""
from pathlib import Path
from typing import Dict


class SCSSParser:
    def parse_file(self, path: Path) -> Dict:
        text = path.read_text(encoding="utf-8")
        return {"files": {str(path): text}, "functions": {}, "classes": {}, "imports": {}, "exports": {}}
