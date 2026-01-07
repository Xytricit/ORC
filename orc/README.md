# ORC (Optimization & Refactoring Catalyst) v1

ORC v1 is a comprehensive codebase intelligence agent for Python projects that helps developers analyze, optimize, and understand their code. It features dead code detection, complexity analysis, dependency mapping, and natural language querying capabilities with multi-language support.

## Features

- **Dead Code Detection**: Identifies unused functions, classes, and files with confidence scoring
- **Complexity Analysis**: Calculates algorithmic complexity (O(n), O(n²), etc.) and identifies performance hotspots
- **Dependency Analysis**: Builds comprehensive call graphs and detects circular dependencies
- **Code Metrics**: Provides detailed project statistics and function-level metrics
- **Pattern Detection**: Identifies code antipatterns and good practices
- **Optimization Suggestions**: Provides specific recommendations for code improvements with example code
- **Natural Language Querying**: Query your codebase using plain English
- **Multi-language Support**: Primary focus on Python with support for JavaScript, TypeScript, React, HTML/CSS, and more
- **Dependency Mapping**: Creates detailed graphs of module and function relationships
- **AI Integration**: Context compression engine for AI tools with natural language interface

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Initialize ORC in your project
orc init

# Index your codebase (supports Python, JS, TS, React, and more)
orc index /path/to/your/project

# Analyze for issues (dead code, complexity, dependencies, patterns)
orc analyze

# Find dead code
orc dead

# Query using natural language
orc query "show circular dependencies"
orc query "find complex functions"
orc query "who calls authenticate_user"

# Start web interface
orc serve
```

### Advanced Usage

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

# Get optimization suggestions
orc ai "suggest optimizations for complex functions"
```

### Example Output

```
$ orc dead
Dead Code Findings:
[D-01] src/auth.py - unused_function
[D-02] src/utils.py - deprecated_helper

$ orc query "show complex functions"
High Complexity Functions
Function          File            Complexity    Lines
complex_algorithm src/algo.py     O(n²)         150
data_processor    src/process.py  O(n³)         200
```

## Architecture

ORC v1 follows a modular architecture:

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

## Commands

### Core Commands
- `orc index <path>`: Index a codebase (supports multiple languages)
- `orc analyze`: Run full analysis (dead code, complexity, dependencies, patterns)
- `orc dead`: Show dead code with confidence scores
- `orc query "<query>"`: Natural language query of codebase
- `orc serve`: Start web interface

### Management Commands
- `orc init`: Create configuration file
- `orc config`: View/modify configuration
- `orc ignore <target>`: Ignore code permanently
- `orc explain <finding_id>`: Explain a dead code finding
- `orc delete <finding_id>`: Delete dead code (marks only in v1)

### AI Integration Commands
- `orc ai "<prompt>"`: Talk to ORC AI with code context
- `orc query "<natural language>"`: Natural language codebase queries

## Configuration

ORC uses a `.orcrc` file for configuration:

```yaml
ignore:
  - 'tests/*'
  - 'venv/*'
  - 'node_modules/*'
  - '__pycache__/*'

dynamic_patterns:
  - 'eval'
  - 'reflection'
  - 'getattr'
  - 'hasattr'
```

## Multi-language Support

ORC supports multiple programming languages:

- **Python**: Full AST-based analysis with complexity detection
- **JavaScript/TypeScript**: Parser support with dependency tracking
- **React/JSX**: Component analysis and dependency mapping
- **HTML/CSS**: Static analysis and structure mapping
- **JSON/YAML/Markdown**: Basic structure analysis

## AI Integration

ORC provides natural language querying and AI integration:

- Natural language codebase queries
- Context compression for AI tools
- Relevance ranking for code snippets
- Integration-ready REST API

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
orc/
├── config/          # Configuration management
├── core/            # Indexing and analysis orchestration
├── parsers/         # Language-specific parsers
├── analysis/        # Analysis modules
├── storage/         # Database and caching
├── context/         # AI integration
├── optimization/    # Optimization engine
├── api/             # REST API
├── cli/             # Command-line interface
├── web/             # Web dashboard
├── tests/           # Test suite
└── docs/            # Documentation
```

## Performance

ORC is designed to handle large codebases efficiently:

- Uses SQLite for fast storage and retrieval
- Implements caching to avoid re-parsing unchanged files
- Uses thread pools for parallel processing
- Implements incremental indexing
- Provides approximate token counting for context building

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue in the GitHub repository.