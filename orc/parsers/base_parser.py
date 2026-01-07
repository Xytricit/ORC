"""Base parser interface for language-specific parsers."""
from pathlib import Path
from typing import Dict


class BaseParser:
    def parse_file(self, path: Path) -> Dict:
        """Parse a source file and return a dictionary with metadata.

        Expected keys: 'files', 'functions', 'classes', 'imports', 'exports'
        """
        raise NotImplementedError()
