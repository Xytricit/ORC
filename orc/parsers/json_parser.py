"""Enhanced JSON parser with schema detection.

Extracts:
- JSON validity
- Top-level keys
- Schema detection (package.json, tsconfig.json, etc.)
- Nested structure depth
- Array/object counts
"""
from pathlib import Path
from typing import Dict, Any
import json


class JSONParser:
    """Enhanced JSON parser with structure analysis."""
    
    def parse_file(self, path: Path) -> Dict:
        """Parse JSON file and analyze structure."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        
        # Attempt to parse
        try:
            data = json.loads(text)
            is_valid = True
        except json.JSONDecodeError:
            data = None
            is_valid = False
        
        # Analyze structure
        if is_valid and data:
            top_keys = list(data.keys()) if isinstance(data, dict) else []
            schema_type = self._detect_schema_type(path, data)
            depth = self._calculate_depth(data)
            counts = self._count_structures(data)
        else:
            top_keys = []
            schema_type = "unknown"
            depth = 0
            counts = {"objects": 0, "arrays": 0}
        
        files = {
            str(path): {
                "language": "json",
                "loc": len(lines),
                "json_features": {
                    "valid": is_valid,
                    "schema_type": schema_type,
                    "top_level_keys": len(top_keys),
                    "depth": depth,
                    "objects": counts["objects"],
                    "arrays": counts["arrays"],
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "json": data,
            "json_valid": is_valid,
            "json_schema_type": schema_type,
            "json_top_keys": top_keys,
            "json_depth": depth,
        }
    
    def _empty_result(self, path: Path) -> Dict:
        return {
            "files": {str(path): {"language": "json", "loc": 0}},
            "functions": {}, "classes": {}, "imports": {}, "exports": {},
            "json": None, "json_valid": False,
        }
    
    def _detect_schema_type(self, path: Path, data: Any) -> str:
        """Detect common JSON schema types."""
        filename = path.name.lower()
        
        if filename == "package.json":
            return "package.json"
        elif filename == "tsconfig.json":
            return "tsconfig.json"
        elif filename.endswith("config.json"):
            return "config"
        elif isinstance(data, dict):
            if "openapi" in data or "swagger" in data:
                return "openapi"
            elif "$schema" in data:
                return "json_schema"
            elif "scripts" in data and "dependencies" in data:
                return "package.json"
        
        return "generic"
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        if not isinstance(obj, (dict, list)):
            return current_depth
        
        max_depth = current_depth
        if isinstance(obj, dict):
            for value in obj.values():
                depth = self._calculate_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
        elif isinstance(obj, list):
            for item in obj:
                depth = self._calculate_depth(item, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _count_structures(self, obj: Any) -> Dict[str, int]:
        """Count objects and arrays in the JSON."""
        counts = {"objects": 0, "arrays": 0}
        
        def count_recursive(item):
            if isinstance(item, dict):
                counts["objects"] += 1
                for value in item.values():
                    count_recursive(value)
            elif isinstance(item, list):
                counts["arrays"] += 1
                for element in item:
                    count_recursive(element)
        
        count_recursive(obj)
        return counts
