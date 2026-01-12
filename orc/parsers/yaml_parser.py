"""Enhanced YAML parser with structure detection.

Extracts:
- YAML validity
- Top-level keys
- Document type (config, CI/CD, Kubernetes, etc.)
- Nested structure depth
- Lists/mappings counts
"""
from pathlib import Path
from typing import Dict, Any
try:
    import yaml  # optional dependency
except Exception:
    yaml = None


class YAMLParser:
    """Enhanced YAML parser with structure analysis."""
    
    def parse_file(self, path: Path) -> Dict:
        """Parse YAML file and analyze structure."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return self._empty_result(path)
        
        lines = text.splitlines()
        
        # Attempt to parse
        parsed = None
        is_valid = False
        if yaml:
            try:
                parsed = yaml.safe_load(text)
                is_valid = parsed is not None
            except Exception:
                pass
        
        # Analyze structure
        if is_valid and parsed:
            top_keys = list(parsed.keys()) if isinstance(parsed, dict) else []
            doc_type = self._detect_document_type(path, parsed)
            depth = self._calculate_depth(parsed)
            counts = self._count_structures(parsed)
        else:
            top_keys = []
            doc_type = "unknown"
            depth = 0
            counts = {"mappings": 0, "sequences": 0}
        
        files = {
            str(path): {
                "language": "yaml",
                "loc": len(lines),
                "yaml_features": {
                    "valid": is_valid,
                    "document_type": doc_type,
                    "top_level_keys": len(top_keys),
                    "depth": depth,
                    "mappings": counts["mappings"],
                    "sequences": counts["sequences"],
                }
            }
        }
        
        return {
            "files": files,
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "yaml": parsed,
            "yaml_valid": is_valid,
            "yaml_document_type": doc_type,
            "yaml_top_keys": top_keys,
            "yaml_depth": depth,
        }
    
    def _empty_result(self, path: Path) -> Dict:
        return {
            "files": {str(path): {"language": "yaml", "loc": 0}},
            "functions": {}, "classes": {}, "imports": {}, "exports": {},
            "yaml": None, "yaml_valid": False,
        }
    
    def _detect_document_type(self, path: Path, data: Any) -> str:
        """Detect common YAML document types."""
        filename = path.name.lower()
        
        if "workflows" in str(path) or filename in ["ci.yml", "ci.yaml"]:
            return "github_actions"
        elif filename.startswith("docker-compose"):
            return "docker_compose"
        elif isinstance(data, dict):
            if "apiVersion" in data and "kind" in data:
                return "kubernetes"
            elif "version" in data and "services" in data:
                return "docker_compose"
            elif "name" in data and "on" in data:
                return "github_actions"
            elif "stages" in data or "jobs" in data:
                return "ci_cd"
        
        return "config"
    
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
        """Count mappings (dicts) and sequences (lists) in the YAML."""
        counts = {"mappings": 0, "sequences": 0}
        
        def count_recursive(item):
            if isinstance(item, dict):
                counts["mappings"] += 1
                for value in item.values():
                    count_recursive(value)
            elif isinstance(item, list):
                counts["sequences"] += 1
                for element in item:
                    count_recursive(element)
        
        count_recursive(obj)
        return counts
