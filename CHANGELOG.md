# Changelog

All notable changes to ORC will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-09

### Added
- AI-powered code analysis with multiple provider support (Ollama, Groq, Gemini, DeepSeek, OpenAI, Anthropic)
- Interactive CLI with `orc chat` command for conversational code assistance
- Smart context compression for efficient token usage
- Multi-language support (Python, JavaScript, TypeScript, React, HTML, CSS, SCSS, SASS, LESS, Markdown, JSON, YAML)
- Dead code detection and analysis
- Dependency analysis and visualization
- Complexity analysis with cyclomatic complexity calculations
- Optimization suggestions based on detected patterns
- Pattern detection for common anti-patterns and code smells
- Security vulnerability detection
- Web dashboard for visualization and interactive analysis
- RESTful API with FastAPI for programmatic access
- Docker support with production-ready configuration
- Production configuration with environment-based secrets
- GitHub Actions CI/CD workflow
- Comprehensive test suite with 40+ tests
- Token-efficient context building for large codebases
- Parallel indexing for improved performance
- Graph database integration for dependency tracking
- Vector store for semantic code search

### Changed
- Complete rewrite from v1.0 with modern architecture
- Modular parser system for extensibility
- Improved CLI UX with Rich formatting and progress bars
- Better error handling and user feedback
- More efficient memory usage for large codebases
- Enhanced configuration system with `.orcignore` support

### Fixed
- Token optimization for large codebases (now handles 100k+ LOC projects)
- Import path issues across all modules
- Invalid escape sequences in regex patterns
- Hard-coded security keys (now uses environment variables)
- Docker configuration with correct paths and health checks

### Security
- Secure SECRET_KEY using environment variables
- No hard-coded credentials in codebase
- Proper `.gitignore` to prevent accidental secret commits
- Session security settings for web interface
- Non-root user in Docker containers

## [1.0.0] - 2026-01-08

### Added
- Initial release
- Basic Python code analysis using AST
- Simple CLI interface
- Function and class extraction
- Basic dependency detection
