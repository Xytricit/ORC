# ORC v1.0: Codebase Intelligence Agent
## Complete Blueprint & Implementation Guide

---

## Project Overview

**ORC (Optimization & Refactoring Catalyst)** is a codebase intelligence system that indexes, analyzes, and optimizes codebases without requiring massive context windows. V1.0 focuses on practical, immediate value for codebases up to 100K lines.

---

## File Structure

```
orc/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuration management
│   └── patterns.yaml         # Known code patterns/antipatterns
├── core/
│   ├── __init__.py
│   ├── indexer.py           # Static analysis & AST parsing
│   ├── graph_builder.py     # Dependency graph construction
│   ├── analyzer.py          # Dead code & pattern detection
│   └── scorer.py            # Entropy & health scoring
├── storage/
│   ├── __init__.py
│   ├── graph_db.py          # Graph storage (NetworkX/SQLite)
│   └── cache.py             # Index caching layer
├── analysis/
│   ├── __init__.py
│   ├── dead_code.py         # Dead code detection algorithms
│   ├── patterns.py          # Pattern matching & duplication
│   ├── dependencies.py      # Circular deps & coupling analysis
│   └── metrics.py           # Code complexity metrics
├── agent/
│   ├── __init__.py
│   ├── query_engine.py      # Natural language query handler
│   ├── recommender.py       # Optimization recommendations
│   └── impact_analyzer.py   # Change impact assessment
├── cli/
│   ├── __init__.py
│   ├── commands.py          # CLI interface
│   └── visualizer.py        # Terminal-based visualization
├── web/
│   ├── __init__.py
│   ├── app.py              # Flask/FastAPI web interface
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── dashboard.html
│       ├── graph.html
│       └── recommendations.html
├── tests/
│   ├── __init__.py
│   ├── test_indexer.py
│   ├── test_analyzer.py
│   ├── test_graph.py
│   └── fixtures/
│       └── sample_codebase/
└── scripts/
    ├── benchmark.py         # Performance benchmarking
    └── migrate.py          # Index migration utilities
```

---

## Core Components

### 1. Configuration (`config/settings.py`)

```python
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
            self.file_extensions = {'.py', '.js', '.ts', '.java', '.go'}
        if self.ignore_patterns is None:
            self.ignore_patterns = [
                '**/node_modules/**',
                '**/venv/**',
                '**/__pycache__/**',
                '**/dist/**',
                '**/build/**',
                '**/.git/**'
            ]

def load_config(config_path: str = "config.yaml") -> ORCConfig:
    """Load configuration from YAML file"""
    if Path(config_path).exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
            return ORCConfig(**data)
    return ORCConfig(project_root=Path.cwd())
```

### 2. Indexer (`core/indexer.py`)

```python
... (rest of the blueprint as provided) ...
```
