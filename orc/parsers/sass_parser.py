"""SASS parser (indentation-based SCSS syntax).

Similar to SCSS but uses indentation instead of braces.
Extracts same features as SCSS parser.
"""
from pathlib import Path
from typing import Dict
from .scss_parser import SCSSParser


class SASSParser(SCSSParser):
    """SASS parser - inherits from SCSS with syntax tweaks."""
    
    def parse_file(self, path: Path) -> Dict:
        """Parse SASS file (indented syntax)."""
        # SASS is similar to SCSS but with indentation
        # Most regex patterns work the same way
        data = super().parse_file(path)
        
        # Update language tag
        for meta in data.get("files", {}).values():
            meta["language"] = "sass"
        
        return data
