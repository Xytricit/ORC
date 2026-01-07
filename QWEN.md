# Qwen Code Configuration

## Project-Specific Settings
This file contains settings for Qwen Code interactions specific to this project.

## Project Context
- Project Name: ORC (Optimization & Refactoring Catalyst)
- Main Language: Python
- Project Type: Codebase intelligence agent for WEB projects
- Purpose: Analyzes code to find dead code, circular dependencies, complexity issues, and provides AI-powered querying capabilities
- Core Innovation: Context Compression Engine that transforms large codebases into queryable indexes for AI tools
- Primary Components: acli.exe, test_code.py, WARP.md

## Coding Preferences
- Follow existing code style in the project
- Maintain consistency with current implementation patterns
- Use type hints where appropriate
- Prefer readability and maintainability over clever code
- Follow Python's PEP 8 style guide
- Follow the modular architecture with separate components for config, core, storage, analysis, context, optimization, API, CLI, and web

## Testing Guidelines
- When modifying code, ensure existing tests still pass
- Add new tests for new functionality
- Run tests before finalizing changes
- Use pytest for testing if available in the project
- Follow the existing test structure in the project
- Test files are located in the `tests/` directory with fixtures for different languages

## Project Structure Notes
- Main code in the `orc/` directory with modular architecture
- Separate packages: `orc_package/` (working implementation) and `orc/` (v2.0 architecture)
- Tests may be in `test_project/` or alongside main code
- Configuration files: `.orcignore`, `.orcrc`
- Database/cache: `.orc/index.db`, `.orc/cache/`
- Virtual environment: `.venv/`
- Entry point: `run_orc.py`

## File Descriptions
- `acli.exe`: The main command-line executable
- `test_code.py`: Test file with used and unused functions for dead code detection testing
- `WARP.md`: Documentation file containing guidance for working with the ORC codebase
- `.orcignore`: Files and patterns to ignore during ORC operations
- `.orcrc`: Configuration file for ORC tool
- `.orc/`: Directory containing ORC state, cache, and index database
- `orc/`: Main project directory with the complete architecture
- `run_orc.py`: Entry point script that wraps the CLI

## Architecture Components
- `config/`: Configuration management and pattern definitions
- `core/`: Indexing, graph building, and analysis orchestration
- `parsers/`: Language-specific parsers (Python, JavaScript, TypeScript, etc.)
- `analysis/`: Dead code detection, complexity analysis, pattern matching
- `storage/`: Database and caching layers (SQLite, vector store)
- `context/`: Context compression and AI integration
- `optimization/`: Algorithm detection and optimization suggestions
- `api/`: REST API for AI tools integration
- `cli/`: Command-line interface
- `web/`: Web dashboard (enterprise)
- `integrations/`: External tool integrations (Git, CI/CD, IDEs)

## Key Features
- Dead code detection
- Dependency graph analysis
- Complexity metrics and algorithmic complexity detection (O(n), O(n²), etc.)
- Natural language querying
- Context compression engine for AI tools
- Multi-language support (Python, JavaScript, TypeScript, React, etc.)
- REST API for AI integration
- CLI and web interface
- Change impact assessment

## Common Commands
- `orc index <path>`: Index a codebase
- `orc analyze`: Analyze the indexed codebase
- `orc query "<query>"`: Query using natural language
- `orc deadcode`: Find dead code
- `orc complexity`: Check complexity metrics
- `orc optimize`: Get optimization suggestions
- `orc serve`: Start the web interface/API server

## Interaction Preferences
- When exploring the codebase, start by examining the `orc/` directory structure following the modular architecture
- For bug fixes, look for existing test files to understand expected behavior
- When adding features, follow the same patterns as existing functionality
- Always consider backward compatibility when making changes
- Provide explanations for complex code changes
- Focus on the v2.0 architecture which includes multi-language support, context compression, and AI integration
- When working with the dual package structure, be aware that `run_orc.py` imports from `orc_package/` for the CLI while `orc/` contains the v2.0 architectural components

## Commands and Tools
- Default Python environment: Use the virtual environment in `.venv/`
- Common commands to use: `python`, `pip`, `pytest`, `orc`
- Check for existing Makefile or build scripts before creating new ones
- Use the existing test structure in the `tests/` directory
- Follow the database schema in the architecture documentation when modifying storage components