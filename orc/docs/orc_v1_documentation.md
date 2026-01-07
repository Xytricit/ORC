# ORC v1 Documentation

## Overview

ORC (Optimization & Refactoring Catalyst) v1 is a codebase intelligence agent for Python projects. It analyzes code to find dead code, circular dependencies, complexity issues, and provides AI-powered querying capabilities. The core innovation is a "Context Compression Engine" that transforms large codebases into queryable indexes for AI tools.

## Features

### 1. Dead Code Detection
- Identifies unused functions, classes, and files
- Provides confidence scores for findings
- Supports marking and deletion of dead code
- Handles complex call graphs to determine actual usage

### 2. Complexity Analysis
- Calculates algorithmic complexity (O(n), O(n²), etc.) for functions
- Identifies performance hotspots (frequently called complex functions)
- Provides optimization suggestions based on complexity
- Estimates potential improvement from optimizations

### 3. Dependency Analysis
- Builds call graphs to understand function relationships
- Detects circular dependencies between modules
- Analyzes coupling metrics between components
- Identifies orphaned modules

### 4. Code Metrics
- Calculates overall project metrics (files, functions, lines of code)
- Provides per-module and per-function metrics
- Tracks complexity, line counts, and parameter counts
- Generates summary statistics

### 5. Pattern Detection
- Identifies code antipatterns (God Object, Long Method, Complex Method)
- Detects potential code duplication
- Recognizes good patterns (Factory, Observer)
- Provides pattern-based recommendations

### 6. Optimization Suggestions
- Analyzes code for optimization opportunities
- Provides specific suggestions for improvements
- Generates example code for common optimizations
- Estimates potential performance improvements

### 7. Natural Language Querying
- Query codebase using natural language
- Search for functions, classes, and files
- Ask about dependencies, complexity, and dead code
- Get contextual results based on code relationships

### 8. Multi-language Support
- Python AST parsing and analysis
- Support for JavaScript, TypeScript, React, HTML/CSS
- Extensible parser architecture
- Normalized index format for all languages

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                       ORC SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │   INDEXING ENGINE (Multi-Language)                 │    │
│  │   ─────────────────────────────────                │    │
│  │   • Python Parser (AST)                            │    │
│  │   • JavaScript/TypeScript Parser (Babel/TS)       │    │
│  │   • HTML/CSS Parser                                │    │
│  │   • React/JSX Parser                               │    │
│  │   • Complexity Analyzer (All Languages)            │    │
│  │   • Pattern Detector (Dead Code, Anti-patterns)   │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │   GRAPH BUILDER (Relationship Mapping)             │    │
│  │   ────────────────────────────────────             │    │
│  │   • Dependency Graph (Module → Module)             │    │
│  │   • Call Graph (Function → Function)               │    │
│  │   • Data Flow Graph (Variable → Usage)             │    │
│  │   • Import/Export Tracking                         │    │
│  │   • Cross-Language Links                           │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │   COMPRESSION & STORAGE                            │    │
│  │   ──────────────────────                           │    │
│  │   • SQLite Database (Structured Data)              │    │
│  │   • Cache Layer (Fast Lookups)                     │    │
│  │   • Incremental Updates                            │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │   ANALYSIS ENGINE                                  │    │
│  │   ───────────────                                  │    │
│  │   • Dead Code Detector                             │    │
│  │   • Complexity Scorer (O(n), O(n²), etc.)         │    │
│  │   • Optimization Suggester                         │    │
│  │   • Impact Analyzer (Change Impact)                │    │
│  │   • Security Scanner (Basic)                       │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │   CONTEXT BUILDER (AI Integration)                 │    │
│  │   ────────────────────────────────                 │    │
│  │   • Query Parser                                   │    │
│  │   • Relevance Ranker                               │    │
│  │   • Context Assembler (Minimal Code Return)        │    │
│  │   • Semantic Search (Optional Embeddings)          │    │
│  │   • LLM Client (Claude/OpenAI API)                 │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │   INTERFACES                                       │    │
│  │   ──────────                                       │    │
│  │                                                     │    │
│  │   CLI (Human Developers)                           │    │
│  │   ├─ orc index                                     │    │
│  │   ├─ orc analyze                                   │    │
│  │   ├─ orc optimize                                  │    │
│  │   ├─ orc query "..."                               │    │
│  │   ├─ orc deadcode                                  │    │
│  │   └─ orc check (CI/CD)                             │    │
│  │                                                     │    │
│  │   REST API (AI Tools Integration)                  │    │
│  │   ├─ GET  /api/context?query=...                   │    │
│  │   ├─ POST /api/optimize                            │    │
│  │   ├─ GET  /api/impact?file=...                     │    │
│  │   ├─ GET  /api/deadcode                            │    │
│  │   └─ POST /api/query                               │    │
│  │                                                     │    │
│  │   Web Dashboard (Enterprise)                       │    │
│  │   ├─ Health Score Visualization                    │    │
│  │   ├─ Complexity Heatmaps                           │    │
│  │   ├─ Dependency Graphs                             │    │
│  │   └─ Team Analytics                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

- `config/`: Configuration management and pattern definitions
- `core/`: Indexing, graph building, and analysis orchestration
- `parsers/`: Language-specific parsers (Python, JavaScript, TypeScript, etc.)
- `analysis/`: Dead code detection, complexity analysis, pattern matching
- `storage/`: Database and caching layers (SQLite)
- `context/`: Context compression and AI integration
- `optimization/`: Algorithm detection and optimization suggestions
- `api/`: REST API for AI tools integration
- `cli/`: Command-line interface
- `web/`: Web dashboard (enterprise)
- `integrations/`: External tool integrations (Git, CI/CD, IDEs)

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Commands

```bash
# Index a codebase
orc index /path/to/project

# Analyze the entire codebase
orc analyze

# Find dead code
orc dead

# Query the codebase using natural language
orc query "show circular dependencies"
orc query "find complex functions"
orc query "who calls authenticate_user"

# Start the web interface
orc serve
```

### Advanced Commands

```bash
# Analyze a specific file
orc analyze path/to/file.py

# Explain a dead code finding
orc explain D-12

# Delete dead code (with confirmation)
orc delete D-12

# Delete without confirmation
orc delete D-12 --yes

# Run with specific confidence threshold
orc delete --confidence 95 --all --yes

# Initialize ORC configuration
orc init

# View current configuration
orc config show

# Add ignore patterns
orc config add ignore "src/experimental/*"

# Ignore specific code permanently
orc ignore path/to/file.py
```

### Natural Language Queries

ORC supports various natural language queries:

- "Show circular dependencies"
- "Find dead code"
- "List unused functions"
- "Show complex functions"
- "Files with most functions"
- "Dependencies of [module_name]"
- "Who calls [function_name]"
- "Show metrics"

## Configuration

ORC uses a `.orcrc` configuration file with the following structure:

```yaml
ignore:
  - 'src/experimental/*'
  - 'node_modules/*'
  - 'venv/*'
  - '__pycache__/*'

dynamic_patterns:
  - 'eval'
  - 'reflection'
  - 'getattr'
  - 'hasattr'
```

## API Integration

ORC provides a REST API for AI tools integration:

- `POST /api/context` - Get compressed context for AI queries
- `POST /api/optimize` - Get optimization suggestions
- `GET /api/deadcode` - Get dead code analysis
- `GET /api/impact` - Analyze impact of changes
- `POST /api/query` - Natural language query of codebase

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Parsers

To add support for a new language:

1. Create a new parser in `parsers/` that extends `BaseParser`
2. Implement the `parse_file` method to return the standard index format
3. Add the parser to the `MultiLanguageIndexer` in `core/indexer.py`

### Extending Analysis

To add new analysis capabilities:

1. Create a new analyzer class in `analysis/`
2. Implement the analysis logic
3. Register the analyzer in `core/analyzer.py`

## Performance

ORC is designed to handle large codebases efficiently:

- Uses SQLite for fast storage and retrieval
- Implements caching to avoid re-parsing unchanged files
- Uses thread pools for parallel processing
- Implements incremental indexing
- Provides approximate token counting for context building

## Limitations

- Currently focused on Python with multi-language support in development
- AI integration features are basic in v1
- Web dashboard is not fully implemented in v1
- Some advanced optimization suggestions are pattern-based rather than AST-transformed

## Roadmap

Future enhancements include:

- Enhanced AI integration with vector embeddings
- More sophisticated optimization transformations
- Complete web dashboard
- Enhanced multi-language support
- CI/CD integration
- IDE extensions