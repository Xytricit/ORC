# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ORC (Optimization & Refactoring Catalyst) is a codebase intelligence agent for Python projects. It analyzes code to find dead code, circular dependencies, complexity issues, and provides AI-powered querying capabilities. The core innovation is a "Context Compression Engine" that transforms large codebases into queryable indexes for AI tools.

## Development Setup

### Installation

```powershell
# Install dependencies
pip install -r requirements.txt

# Alternative: Using setup.py
pip install -e .
```

### Running ORC

The entry point is `run_orc.py` which wraps the CLI:

```powershell
# Run the CLI directly
python run_orc.py <command>

# If installed via setup.py
orc <command>
```

## Common Commands

### Indexing and Analysis

```powershell
# Index a codebase (creates .orc/index.db)
python run_orc.py index <path/to/project>

# Analyze the entire indexed codebase
python run_orc.py analyse

# Analyze a specific file
python run_orc.py analyse <file_path>

# Find dead code
python run_orc.py dead

# Query using natural language
python run_orc.py query "show circular dependencies"
python run_orc.py query "find complex functions"
python run_orc.py query "who calls authenticate_user"
```

### Configuration

```powershell
# Initialize ORC config file (.orcrc)
python run_orc.py init

# View current configuration
python run_orc.py config show

# Add ignore patterns
python run_orc.py config add ignore "src/experimental/*"

# Ignore specific code permanently
python run_orc.py ignore <target>
```

### Managing Findings

```powershell
# Explain a dead code finding
python run_orc.py explain D-12

# Delete dead code (with confirmation)
python run_orc.py delete D-12

# Delete without confirmation
python run_orc.py delete D-12 --yes
```

### Testing

```powershell
# Run all tests
pytest

# Run specific test module
pytest tests/test_indexer.py

# Run with verbose output
pytest -v

# Run tests with coverage
pytest --cov=orc_package
```

## Architecture

### Dual Package Structure

The codebase has two parallel implementations:

1. **`orc_package/`** - The working implementation with CLI commands and analysis
2. **`orc/` (at root level)** - Architectural skeleton following the v2.0 design from `architecture.md`

When developing, be aware that:
- `run_orc.py` imports from `orc_package/` for the CLI
- The `orc/` directory contains architectural components (context builder, API server, etc.) that are mostly incomplete or skeletal

### Key Components in `orc_package/`

- **`config/`**: Configuration management (`settings.py`, `patterns.yaml`)
- **`core/`**: Indexing (`indexer.py`), graph building (`graph_builder.py`), and analysis orchestration (`analyzer.py`)
- **`storage/`**: SQLite database and graph storage (`graph_db.py`)
- **`analysis/`**: Dead code detection, dependency analysis, metrics, and pattern detection
- **`agent/`**: Query engine for natural language queries, impact analysis, and recommendations
- **`cli/`**: Command-line interface (`commands.py`) using Click and Rich

### Import Paths

When modifying code, note the import structure:
- CLI commands import from `orc_package.*`
- Some imports reference `core.*` and `storage.*` directly (without package prefix)
- The v2.0 architecture uses `orc.*` imports but many files are incomplete

### Data Flow

1. **Indexing**: `PythonIndexer` parses Python AST → Creates `ModuleInfo` objects
2. **Graph Building**: `DependencyGraph` builds relationships from modules
3. **Storage**: `GraphStorage` saves to SQLite (`.orc/index.db`)
4. **Analysis**: Various analyzers process stored data → Generate reports
5. **Query**: `QueryEngine` translates natural language to searches

## Configuration Files

### `.orcrc` (User Config)

Created by `orc init`. Contains:
- `ignore`: Patterns to skip during analysis
- `dynamic_patterns`: Patterns indicating dynamic code usage (e.g., reflection)

### `config.yaml` (Project Config)

Optional YAML config with:
```yaml
project_root: "/path/to/project"
index_path: ".orc/index.db"
cache_path: ".orc/cache/"
min_complexity_threshold: 10
dead_code_confidence: 0.85
max_function_lines: 100
parallel_workers: 4
```

Default values are defined in `orc_package/config/settings.py` (`ORCConfig` class).

## Code Patterns

### Analysis Reports

Analysis results use dataclasses:
```python
@dataclass
class DeadCodeReport:
    unused_functions: List[Dict]
    unused_exports: List[Dict]
    unused_files: List[str]
    estimated_lines_saved: int
    confidence_scores: Dict[str, float]
```

### Module Information

Indexed code is represented as:
```python
@dataclass
class ModuleInfo:
    path: str
    functions: Dict[str, FunctionInfo]
    classes: Dict[str, ClassInfo]
    imports: List[str]
    exports: List[str]
```

### CLI Pattern

Commands use Click with Rich formatting:
```python
@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', default='config.yaml')
def command_name(path, config):
    console.print("[bold blue]Status message[/bold blue]")
```

## Working with Windows Paths

ORC runs on Windows. When dealing with file paths:
- Use `Path` from `pathlib` for cross-platform compatibility
- The codebase root uses forward slashes in Python strings
- Windows long path prefix `\\?\` may appear in absolute paths
- Use `.as_posix()` when displaying paths to users

## Known Limitations

- V2.0 architecture (multi-language support, REST API, web dashboard) is incomplete
- Only Python parsing is fully implemented
- Context compression and AI integration (`orc/context/`, `orc/api/`) are skeletal
- Vector embeddings and semantic search are not yet functional
- File deletion in `orc delete` only marks findings, doesn't modify files

## Future Development (from architecture.md)

The v2.0 vision includes:
- Multi-language parsers (JavaScript, TypeScript, React, Django, FastAPI)
- Context compression engine for AI integration
- REST API for external tools (`api/server.py`)
- Web dashboard (Flask/FastAPI)
- Optimization engine with algorithmic complexity detection
- Vector embeddings for semantic search

When implementing these features, follow the structure defined in `orc/architecture.md` and create components under the `orc/` directory hierarchy.
