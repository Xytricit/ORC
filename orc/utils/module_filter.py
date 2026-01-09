"""
Utility to filter modules based on .orcignore patterns.
"""
from pathlib import Path
from typing import Dict, List


def read_orcignore(root_path: Path = None) -> List[str]:
    """Read .orcignore file and return glob patterns.
    
    Returns patterns that can be used with pathlib.Path.match()
    """
    if root_path is None:
        root_path = Path('.')
    
    orcignore_path = root_path / '.orcignore'
    patterns = []
    
    if not orcignore_path.exists():
        # Default patterns if no .orcignore
        return [
            '**/.venv/**',
            '**/venv/**',
            '**/node_modules/**',
            '**/__pycache__/**',
            '**/.git/**',
            '**/*.pyc'
        ]
    
    try:
        with orcignore_path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Convert .orcignore patterns to glob patterns
                if line.endswith('/'):
                    # Directory pattern: ".venv/" -> "**/.venv/**"
                    name = line.rstrip('/').lstrip('./')
                    pattern = f"**/{name}/**"
                else:
                    # File/pattern: "*.pyc" -> "**/*.pyc"
                    pattern = f"**/{line}"
                
                patterns.append(pattern)
    except Exception:
        return []
    
    return patterns


def should_ignore(path: str, patterns: List[str] = None) -> bool:
    """Check if a path should be ignored based on patterns.
    
    Args:
        path: File path to check
        patterns: List of glob patterns (if None, reads from .orcignore)
    
    Returns:
        True if path should be ignored
    """
    if patterns is None:
        patterns = read_orcignore()
    
    # Normalize path separators to forward slashes for consistent matching
    normalized_path = str(path).replace('\\', '/')
    
    # Check for common ignored directories directly (faster)
    if any(ignored in normalized_path for ignored in ['/.venv/', '/venv/', '/node_modules/', '/__pycache__/']):
        return True
    
    # Also check with pathlib for glob patterns
    path_obj = Path(normalized_path)
    for pattern in patterns:
        if path_obj.match(pattern):
            return True
    
    return False


def filter_modules(modules: Dict, patterns: List[str] = None) -> Dict:
    """Filter out modules that match ignore patterns.
    
    Args:
        modules: Dict of module_path -> ModuleInfo
        patterns: List of glob patterns (if None, reads from .orcignore)
    
    Returns:
        Filtered dict with ignored modules removed
    """
    if patterns is None:
        patterns = read_orcignore()
    
    filtered = {}
    ignored_count = 0
    
    for module_path, module_info in modules.items():
        if should_ignore(module_path, patterns):
            ignored_count += 1
            continue
        
        filtered[module_path] = module_info
    
    return filtered
