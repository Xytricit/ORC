"""
ORC Configuration Management
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set
import yaml

@dataclass
class ORCConfig:
    """Main configuration for ORC"""

    # Paths
    project_root: Path
    index_path: Path = Path(".orc/index.db")
    cache_path: Path = Path(".orc/cache/")

    # Indexing settings
    file_extensions: Set[str] = None
    ignore_patterns: List[str] = None
    max_file_size_mb: int = 10

    # Analysis settings
    min_complexity_threshold: int = 10
    dead_code_confidence: float = 0.85
    max_function_lines: int = 100

    # Performance
    parallel_workers: int = 4
    chunk_size: int = 100

    def __post_init__(self):
        if self.file_extensions is None:
            # Default to all extensions understood by the current
            # parsers. PythonIndexer still only consumes ``.py`` but the
            # multi-language indexer uses this as a declarative list of
            # supported source types.
            self.file_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm',
                '.css', '.json', '.md', '.markdown', '.yml', '.yaml',
                '.scss', '.sass', '.less',
            }
        if self.ignore_patterns is None:
            # Default ignore patterns for common noise / environment dirs.
            # These are used by both the legacy Python indexer and the
            # multi-language indexer, and are also mirrored into a default
            # .orcignore created on first run.
            self.ignore_patterns = [
                '**/node_modules/**',
                '**/venv/**',        # conventional virtualenv name
                '**/.venv/**',       # dot-venv (very common)
                '**/.env/**',        # generic env dirs
                '**/__pycache__/**',
                '**/dist/**',
                '**/build/**',
                '**/.git/**',
                '**/.pytest_cache/**',
                '**/.orc/**',        # ORC's own working directory
            ]

def load_config(config_path: str = "config.yaml") -> ORCConfig:
    """Load configuration from YAML file"""
    if Path(config_path).exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
            return ORCConfig(**data)
    return ORCConfig(project_root=Path.cwd())
