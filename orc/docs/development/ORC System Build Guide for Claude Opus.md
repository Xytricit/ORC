# ORC System Build Guide for Claude Opus 4.5
## Strategic Decomposition for Efficient Development

**Purpose:** This guide breaks down the ORC (Optimization & Refactoring Catalyst) system into 8 focused prompts, each optimized for Opus 4.5's capabilities. Follow them sequentially for maximum efficiency.

---

## Overview: What We're Building

A production-ready AI-powered codebase intelligence platform with:
- Multi-language parsing (11 language types)
- SQLite graph database with 10 tables
- Parallel indexing with dependency resolution
- AI integration (6 providers: Groq, OpenAI, Anthropic, Ollama, DeepSeek, Gemini)
- Interactive CLI with session management
- Advanced code analysis (complexity, dead code, security, performance)

**Total Scope:** ~50 modules, ~15,000 lines of production code
**Recommended Timeline:** 5-7 days (1 prompt per day)
**Token Budget:** ~2-3M tokens total across all prompts

---

## Phase 1: Foundation & Architecture (Days 1-2)

### Prompt 1: Core Architecture + Indexing System
**Duration:** 2-3 hours | **Complexity:** HIGH | **Token Cost:** ~300-400k

**What You'll Get:**
- `orc/core/indexer.py` (legacy sequential indexer)
- `orc/core/parallel_indexer.py` (production parallel indexer)
- `orc/core/index_service.py` (unified service façade)
- Project directory structure
- Configuration system with .orcignore support

**Key Design Decisions:**
- Parallel processing using multiprocessing (CPU core count auto-detection)
- Caching strategy with file mtime validation
- Configuration management (config file + environment variables)

**How to Prompt Opus:**
```
"Build the core indexing system for ORC. Focus on:
1. ParallelIndexer class with multiprocessing
2. File scanning with .orcignore pattern matching
3. Caching layer with TTL and mtime validation
4. Configuration management system
5. IndexService as unified entry point

Requirements:
- Use pathlib for cross-platform file handling
- Implement proper error handling and logging
- Make parsers pluggable (ParserRegistry pattern)
- Support force_refresh flag for re-indexing

Return complete, production-ready code with docstrings."
```

**Acceptance Criteria:**
- ✅ Parallel indexer faster than sequential (~10x on 8-core)
- ✅ Proper cache invalidation on file changes
- ✅ Configuration system with defaults
- ✅ No hardcoded paths (all use config)

---

### Prompt 2: Database Schema + Storage Layer
**Duration:** 1-2 hours | **Complexity:** MEDIUM | **Token Cost:** ~200-300k

**What You'll Get:**
- `orc/storage/graph_db.py` (SQLite graph database)
- Database schema (10 tables with indexes)
- All CRUD operations with proper error handling
- Batch insert support for performance
- WAL mode for concurrent access

**Schema Overview:**
```
Core Tables:
- file_index (files metadata)
- function_index (functions with complexity)
- class_index (classes with methods)
- import_index (import statements)
- export_index (exports)

Enhanced Tables:
- file_dependencies (resolved imports)
- function_calls_resolved (call graph)
- entry_points (main execution points)
- code_summaries (AI summaries)
- ai_insights (code smells)
```

**How to Prompt Opus:**
```
"Build the GraphDB storage layer for ORC:

1. Create SQLite schema with 10 tables:
   - file_index: path, language, loc, created_at
   - function_index: func_id, name, file, line_start, line_end, complexity, code, parameters, calls
   - class_index: class_id, name, file, line_start, line_end, methods
   - import_index: import_id, source_file, import_statement, line_number
   - export_index: export_id, name, kind, file
   - file_dependencies: source_file, target_file, import_statement, line_number
   - function_calls_resolved: caller_file, caller_func, callee_file, callee_func, line
   - entry_points: file_path, entry_type, line_number
   - code_summaries: entity_id, entity_type, summary, provider, timestamp
   - ai_insights: entity_id, insight_type, description, severity

2. Implement GraphDB class with methods:
   - store_file(), store_function(), store_class()
   - store_file_dependencies(), store_resolved_function_calls()
   - query_functions(), get_complex_functions(), get_statistics()
   - get_file_dependencies(), get_function_with_summary()

3. Features:
   - 7 performance indexes (on common queries)
   - WAL mode for concurrent reads
   - Prepared statements (no SQL injection)
   - Batch insert support via executemany()
   - INSERT OR REPLACE for idempotency

4. Return complete module with docstrings and example usage."
```

**Acceptance Criteria:**
- ✅ Schema supports all 10 tables with proper relations
- ✅ Indexes on frequently queried columns
- ✅ WAL mode enabled by default
- ✅ All CRUD methods implemented and tested
- ✅ No N+1 query patterns

---

## Phase 2: Parsers (Days 3-4)

### Prompt 3: Language Parsers (Part 1 - Python, JavaScript, TypeScript)
**Duration:** 2-3 hours | **Complexity:** HIGH | **Token Cost:** ~350-400k

**What You'll Get:**
- `orc/parsers/python_parser.py` (full AST-based parser)
- `orc/parsers/javascript_parser.py` (regex-based)
- `orc/parsers/typescript_parser.py` (regex-based with types)
- Base parser interface
- Parser registry system

**Key Features by Parser:**
- **Python:** AST parsing, cyclomatic complexity (McCabe), async support, decorators, docstrings
- **JavaScript:** ES6 imports/exports, CommonJS require, arrow functions, class detection
- **TypeScript:** Type annotations, interfaces, enums, access modifiers, decorators

**How to Prompt Opus:**
```
"Build 3 language parsers for ORC. All inherit from BaseParser with parse_file(path) method.

BaseParser Interface:
```python
class BaseParser:
    def parse_file(self, path) -> dict:
        return {
            'files': {file_path: {language, loc, ...}},
            'functions': {func_id: {name, line_start, line_end, complexity, parameters, calls, code}},
            'classes': {class_id: {name, line_start, line_end, methods, base_classes}},
            'imports': {import_type: [list]},
            'imports_detailed': [(statement, line_number, what_imported)],
            'exports': {export_id: {name, kind}},
            'entry_points': [(type, line_number)]
        }
```

**Python Parser (PythonParser):**
- Use ast module for parsing
- Calculate cyclomatic complexity (McCabe):
  - Base: 1
  - +1 for: if, elif, for, while, except, with, assert
  - +1 for: and, or in conditions
  - +1 for: lambda
- Extract: functions, classes, imports, exports, decorators, docstrings
- Handle: async functions, type hints, __all__ exports
- Detect entry points (if __name__ == '__main__')

**JavaScript Parser (JavaScriptParser):**
- Use regex patterns (no AST available easily)
- Extract: function declarations, arrow functions, async functions
- Extract: class declarations with methods
- Extract: ES6 imports, CommonJS require, module.exports
- Extract: const/let/var at module level
- Handle: destructuring imports, default exports

**TypeScript Parser (TypeScriptParser):**
- Extend JavaScript parser
- Add: type annotations, interfaces, type aliases, enums
- Extract: public/private/protected access modifiers
- Extract: generic types (T, U, etc.)
- Extract: decorators (@Component, etc.)

**Requirements:**
- All parsers must handle syntax errors gracefully
- Return line numbers for all entities
- Calculate complexity for Python only
- Support both relative and absolute imports
- Return complete file content in 'code' field for functions

Return all 3 parsers with comprehensive docstrings and example usage."
```

**Acceptance Criteria:**
- ✅ Python parser correctly extracts complexity scores
- ✅ All parsers handle syntax errors without crashing
- ✅ Imports include line numbers in imports_detailed
- ✅ Entry points detected (main functions, __main__, etc.)
- ✅ Return format consistent across all parsers

---

### Prompt 4: Language Parsers (Part 2 - React, HTML/CSS, Data Formats)
**Duration:** 1.5-2 hours | **Complexity:** MEDIUM | **Token Cost:** ~250-300k

**What You'll Get:**
- `orc/parsers/react_parser.py` (JSX components & hooks)
- `orc/parsers/html_css_parser.py` (HTML tags & CSS selectors)
- `orc/parsers/json_parser.py` (JSON with schema detection)
- `orc/parsers/yaml_parser.py` (YAML with document detection)
- `orc/parsers/markdown_parser.py` (Markdown structure)
- `orc/parsers/scss_parser.py` + `sass_parser.py` + `less_parser.py` (CSS preprocessors)
- `orc/parsers/tailwind_parser.py` (Tailwind utility classes)
- `orc/parsers/django_parser.py` + `fastapi_parser.py` (Framework-specific)

**How to Prompt Opus:**
```
"Build 11 specialized parsers for ORC. Each inherits from BaseParser. Focus on practical extraction:

**React Parser:**
- Detect: functional components, class components, hooks (useState, useEffect, custom hooks)
- Extract: component names, props, propTypes
- Count: JSX elements, state variables
- Return: component_type, hooks_used, props_structure

**HTML/CSS Parser:**
- HTML: Extract tags, attributes, nesting depth
- CSS: Extract selectors (classes, IDs, elements), properties, specificity
- Inline styles: Parse style attributes
- Return: tag_hierarchy, css_classes, css_ids, inline_styles

**JSON Parser:**
- Detect schema type: package.json, tsconfig.json, OpenAPI, JSON Schema, generic config
- Extract: top-level keys, nesting depth, object/array counts
- Validate: JSON syntax
- Return: schema_type, structure_info, validity

**YAML Parser:**
- Detect document type: GitHub Actions, Docker Compose, Kubernetes, CI/CD
- Extract: top-level keys, nesting depth, mapping/sequence counts
- Validate: YAML syntax
- Return: document_type, structure_info, validity

**Markdown Parser:**
- Extract: Headings (H1-H6), code blocks (with language), links, images, lists, tables
- Build: Table of contents from headings
- Return: heading_structure, code_blocks_with_languages, link_targets

**CSS Preprocessors (SCSS, Sass, LESS):**
- SCSS/Sass: Variables ($), mixins, imports, nesting, functions
- LESS: Variables (@), mixins (@), nesting, functions
- Extract: variable names, mixin names, import paths, nesting depth
- Return: variables, mixins, imports, nesting_structure

**Tailwind Parser:**
- Extract: utility classes, @apply directives, @layer directives
- Detect: Tailwind config file
- Return: utility_classes_used, custom_classes, layers

**Django Parser (extends PythonParser):**
- Detect: Models (inheriting from models.Model), Views, URL patterns, Forms, Admin registrations
- Extract: model fields, view methods, URL routes, form fields
- Return: models, views, urls, forms, admin_registrations

**FastAPI Parser (extends PythonParser):**
- Detect: API routes (@app.get, @app.post, etc.), path/query parameters
- Extract: endpoint paths, HTTP methods, request/response models (Pydantic)
- Extract: dependencies, path parameters, query parameters
- Return: routes, parameters, dependencies, models

**General Requirements:**
- All parsers handle missing/incomplete files gracefully
- Return empty dicts for missing sections (don't error)
- Use regex patterns for non-AST parsers
- Include try/except for parsing errors
- Return complete, production-ready code

Return all 11 parsers as separate modules."
```

**Acceptance Criteria:**
- ✅ React hooks correctly identified
- ✅ JSON/YAML schema types detected accurately
- ✅ HTML/CSS structure captured without validation errors
- ✅ Markdown TOC can be generated from heading structure
- ✅ CSS preprocessor variables and mixins extracted
- ✅ Framework-specific features (Django models, FastAPI routes) detected
- ✅ All parsers handle malformed input gracefully

---

## Phase 3: Analysis & AI Integration (Days 5-6)

### Prompt 5: Analysis Modules + Dependency Resolution
**Duration:** 2-2.5 hours | **Complexity:** MEDIUM | **Token Cost:** ~250-350k

**What You'll Get:**
- `orc/core/dependency_resolver.py` (import & function call resolution)
- `orc/core/graph_builder.py` (NetworkX dependency graphs)
- `orc/core/analyzer.py` (orchestrates all analysis)
- Dead code detection module
- Complexity analysis module
- Pattern detection module

**Key Analysis Types:**
1. **Dead Code:** Functions/classes never called
2. **Complexity:** Functions ranked by cyclomatic complexity
3. **Dependencies:** Import chains and circular dependencies
4. **Hotspots:** High-complexity high-usage functions
5. **Patterns:** Code smells and best practices

**How to Prompt Opus:**
```
"Build the analysis layer for ORC:

**DependencyResolver:**
- Input: Code index from parallel_indexer
- Resolve all imports:
  - Absolute imports (import os)
  - Relative imports (from .utils import X)
  - Package imports (from package import X)
  - Skip standard library imports
- Resolve function calls across files (who calls what)
- Detect circular dependencies using DFS
- Output: file_dependencies, function_calls_resolved, unresolved_imports, circular_dependencies
- Performance: O(n*m) where n=files, m=imports per file

**DependencyGraph (uses NetworkX):**
- Build module-level graph (files as nodes)
- Build function-level call graph (functions as nodes)
- Methods:
  - build_from_modules(modules) - populate graphs
  - find_circular_dependencies() - detect cycles (Johnson's algorithm)
  - get_module_dependencies(module_path) - returns depends_on + depended_by
  - calculate_module_coupling(module_path) - coupling score (0.0-1.0)

**DeadCodeAnalyzer:**
- Find functions/classes never called
- Consider: __main__ entry points, exports, public APIs
- Return: List of potentially unused entities with confidence scores
- False positive minimization: Mark as 'suspicious' not 'dead'

**ComplexityAnalyzer:**
- Use cyclomatic complexity scores from parsers
- Calculate additional metrics:
  - Nesting depth
  - Function length (lines of code)
  - Parameter count
- Return: Functions ranked by complexity with scores

**DependencyAnalyzer:**
- Find circular dependencies
- Detect tightly coupled modules (high coupling score)
- Identify external dependencies
- Return: circular_chains, hotspots, external_deps

**Analyzer (Orchestrator):**
- Coordinate all analyzers
- Aggregate results into comprehensive report
- Methods:
  - run_all(modules) → {dead_code, dependencies, metrics, patterns, summary}

**Requirements:**
- Handle incomplete/missing data gracefully
- Provide confidence scores where applicable
- All circular dependency detection uses proper algorithms
- Cache results for performance
- Return all results with line numbers for debugging

Return complete modules with docstrings and example usage."
```

**Acceptance Criteria:**
- ✅ Circular dependencies detected correctly
- ✅ Dead code analysis has <20% false positives
- ✅ Dependency resolution handles all import types
- ✅ Coupling scores calculated correctly
- ✅ Analysis runs in <5 seconds on 10k function codebase

---

### Prompt 6: AI Integration + Code Summarization
**Duration:** 1.5-2 hours | **Complexity:** MEDIUM | **Token Cost:** ~200-300k

**What You'll Get:**
- `orc/ai_client.py` (multi-provider AI client)
- `orc/ai_summarizer.py` (code summarization)
- `orc/ai_tools.py` (19 tool definitions for function calling)
- `orc/ai_guidelines.py` (system prompt for AI)
- Provider integration (Groq, OpenAI, Anthropic, Ollama, DeepSeek, Gemini)

**How to Prompt Opus:**
```
"Build the AI integration layer for ORC:

**AIClient:**
- Support 6 providers: groq, openai, anthropic, ollama, deepseek, gemini
- Methods:
  - __init__(provider, model, api_key)
  - chat(messages, tools=None, stream=False) → string or generator
- Features:
  - Auto-detect API keys from environment
  - Streaming response support
  - Retry logic (3 attempts on failure)
  - Tool calling support (for OpenAI, Anthropic, Groq, Gemini)
- Error handling: Clear messages for missing keys, network errors, rate limits

**AICodeSummarizer:**
- Methods:
  - summarize_function(func_code, func_name, file_path) → {summary, purpose, complexity_note, suggestions}
  - summarize_class(class_code, class_name, file_path) → {summary, methods_summary}
  - summarize_file(file_path, file_content) → {summary, structure}
- Features:
  - Batch multiple summaries per request (10 per batch)
  - Cache results in database
  - Cache invalidation based on code hash
  - Fallback if summarizer unavailable
- Prompt strategy: Ask for JSON response with structured fields

**AITools (19 function definitions):**

Navigation:
- get_codebase_map() - file tree
- get_folder_contents(folder_path) - list files
- get_file_content(file_path) - read file

Search:
- query_files(pattern) - search files
- query_functions(pattern) - search functions
- query_classes(pattern) - search classes
- search_code(keyword) - full-text search

Analysis:
- get_complexity_report() - high complexity functions
- get_dead_code() - unused functions
- get_security_issues() - security concerns
- get_hotspots() - performance bottlenecks
- get_circular_dependencies() - circular deps

Dependencies:
- get_function_with_summary(func_id) - function + AI summary
- get_file_dependencies(file_path) - imports and importers
- get_entry_points() - main execution points

Actions:
- organize_codebase() - folder structure suggestions
- cleanup_imports() - unused imports
- find_duplicates() - code duplication
- generate_docs() - documentation
- suggest_refactoring(file_path) - refactoring suggestions
- analyze_performance() - performance issues
- check_best_practices() - best practice validation

Format each as OpenAI-compatible tool definition with:
- type: 'function'
- function.name, description, parameters

**AIGuidelines:**
- System prompt function: get_system_prompt(memory_context, tools_used_this_session)
- Key principles:
  1. Check memory first before re-querying
  2. Reference previous responses in conversation
  3. Avoid tool calls for simple questions
  4. Use cached data, minimize API calls
  5. Refresh data only if >24 hours old or user requests
- Return well-formatted, concise system prompt

**Requirements:**
- All providers use same interface (AIClient)
- Proper error handling for each provider
- Environment variable support for API keys
- Tool definitions match OpenAI format
- Batch processing for efficiency
- Comprehensive docstrings

Return all modules with complete code and examples."
```

**Acceptance Criteria:**
- ✅ All 6 providers work (or gracefully fail with clear errors)
- ✅ Tool definitions are OpenAI-compatible format
- ✅ Streaming responses work correctly
- ✅ Error messages help user debug issues
- ✅ Batch summarization reduces token usage

---

## Phase 4: CLI & User Interface (Days 7)

### Prompt 7: CLI Commands + Chat Interface
**Duration:** 2-3 hours | **Complexity:** MEDIUM | **Token Cost:** ~300-350k

**What You'll Get:**
- `orc/cli_main.py` (all CLI commands)
- `orc/cli_loop.py` (interactive chat session)
- `orc/cli_style.py` (professional output styling)
- `orc/ui_components.py` (UI components with syntax highlighting)
- `orc/session_manager.py` (conversation persistence)
- `orc/token_tracker.py` (usage tracking)

**CLI Commands:**
```
orc init                    # Initialize .orc directory
orc index [--force]         # Index codebase (parallel)
orc scan                    # One-step index + analyze
orc report [--output file]  # Comprehensive report
orc find <what>             # Smart search (dead/complex/large)
orc check                   # Health check
orc config                  # Manage configuration
orc ignore <pattern>        # Add to .orcignore
orc                         # Enter interactive chat
```

**Chat Slash Commands:**
```
/help, /clear, /mode, /summarizer, /save, /load, /sessions
/export, /copy, /tokens, /cost, /context, /exit
```

**How to Prompt Opus:**
```
"Build the CLI and chat interface for ORC using Click and prompt_toolkit:

**CLIOutput (cli_style.py):**
- Professional styling without decorative elements
- Methods: start_phase(title), success(msg), warning(msg), error(msg), info(msg)
- Symbols: ▸ (chevron), + (plus), ! (exclamation), × (cross), • (bullet)
- Fallback: [OK], [WARN], [ERR] for non-color terminals
- CI/CD friendly (no emojis, works without color)

**UI Components (ui_components.py):**
- display_user_message(message) - clean borders (┌─ └─)
- display_ai_message(message) - syntax-highlighted code blocks
- display_code_block(code, language) - syntax highlighting (pygments)
- display_status_bar(model, tokens_used, cost) - session info
- Support: auto-detect code language in markdown blocks

**CLIMain (cli_main.py):**
Use Click framework. Commands:

1. orc init
   - Create .orc directory structure
   - Generate default config file
   - Create .orcignore template
   - Return: [OK] message

2. orc index [--force] [--quiet]
   - Call ParallelIndexer
   - Display: files scanned, functions found, complexity stats
   - Return: Statistics and timing

3. orc scan
   - One-step: index → analyze → report summary
   - Display all analysis results
   - Return: Comprehensive health check

4. orc report [--output file]
   - Generate markdown report with all analyses
   - Include: complexity, dead code, dependencies, hotspots
   - Return: File path or print to stdout

5. orc find <what>
   - Smart search: 'dead', 'complex', 'large', or search pattern
   - Return: Filtered results with file:line references

6. orc check
   - Quick health check (no full indexing)
   - Return: Status of config, database, cache

7. orc config
   - List/set configuration options
   - Options: ai_provider, ai_model, max_complexity_threshold, etc.

8. orc ignore <pattern>
   - Add pattern to .orcignore
   - Return: Confirmation

9. orc (no args)
   - Enter interactive chat session
   - Call ORCChatSession.run()

**ORCChatSession (cli_loop.py):**
Main class for interactive chat:
- __init__(root_path, config)
- run() → main event loop
- Features:
  - Streaming AI responses
  - Tool calling (AI queries database)
  - Session persistence (auto-save)
  - Token tracking
  - Mode switching (auto/chat/work modes)
  - Syntax-highlighted code blocks

Slash Commands:
- /help - show available commands
- /clear - clear conversation
- /mode [auto|chat|work] - set mode
- /summarizer [provider] - configure summarizer
- /save [name] - save conversation
- /load <name> - load saved session
- /sessions - list saved sessions
- /export [md|json] - export conversation
- /copy - copy last code block to clipboard
- /tokens - show token usage stats
- /cost - show estimated cost
- /context - show context window usage
- /exit - quit chat

Input using prompt_toolkit:
- Tab completion for commands and file paths
- Colored prompt: 'ORC > '
- Streaming AI output with real-time display

**SessionManager (session_manager.py):**
- save_session(name, messages, metadata)
- load_session(name) → messages
- list_sessions() → list with timestamps
- export_to_markdown(messages, output_path)
- export_to_json(messages, output_path)
- auto_save(messages, keep_last=10)
- update_last_code_block(message)

**TokenTracker (token_tracker.py):**
- add_request(provider, model, input_tokens, output_tokens)
- get_statistics() → {total_tokens, requests, per_provider}
- estimate_cost(provider, model, input_tokens, output_tokens) → float

Pricing table (per 1M tokens):
- Groq: Free (rate-limited)
- OpenAI GPT-4: Input $30, Output $60
- OpenAI GPT-3.5: Input $0.50, Output $1.50
- Anthropic Claude: Input varies by model
- Ollama: Free (local)
- DeepSeek: Affordable pricing
- Gemini: Free tier + paid

**Requirements:**
- All CLI output uses CLIOutput styling
- Chat interface uses prompt_toolkit
- Syntax highlighting for code blocks
- Error messages helpful and actionable
- Session persistence automatic
- Token tracking transparent to user
- Works on Windows, Mac, Linux

Return all modules with complete, production-ready code."
```

**Acceptance Criteria:**
- ✅ All CLI commands work without errors
- ✅ Chat streaming responses display in real-time
- ✅ Slash commands function correctly
- ✅ Syntax highlighting works for common languages
- ✅ Sessions persist and restore correctly
- ✅ Token tracking accurate
- ✅ Works on Windows, Mac, Linux

---

### Prompt 8: Integration, Testing, & Documentation
**Duration:** 2-3 hours | **Complexity:** MEDIUM | **Token Cost:** ~250-300k

**What You'll Get:**
- Complete project structure and setup files
- Configuration system fully integrated
- Error handling across all modules
- Basic unit tests for core modules
- README with setup instructions
- Example .orcignore file
- requirements.txt with all dependencies

**How to Prompt Opus:**
```
"Finalize the ORC system. Create:

**1. Project Structure:**
```
orc/
├── __init__.py
├── core/
│   ├── indexer.py
│   ├── parallel_indexer.py
│   ├── analyzer.py
│   ├── dependency_resolver.py
│   ├── graph_builder.py
│   ├── index_service.py
│   └── compressor.py
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py
│   ├── python_parser.py
│   ├── javascript_parser.py
│   ├── typescript_parser.py
│   ├── react_parser.py
│   ├── html_css_parser.py
│   ├── json_parser.py
│   ├── yaml_parser.py
│   ├── markdown_parser.py
│   ├── scss_parser.py
│   ├── sass_parser.py
│   ├── less_parser.py
│   ├── tailwind_parser.py
│   ├── django_parser.py
│   └── fastapi_parser.py
├── storage/
│   ├── graph_db.py
│   ├── cache.py
│   └── vector_store.py
├── ai/
│   ├── ai_client.py
│   ├── ai_summarizer.py
│   ├── ai_tools.py
│   └── ai_guidelines.py
├── cli/
│   ├── cli_main.py
│   ├── cli_loop.py
│   ├── cli_style.py
│   └── ui_components.py
├── session/
│   ├── session_manager.py
│   └── token_tracker.py
├── analysis/
│   ├── dead_code_analyzer.py
│   ├── complexity_analyzer.py
│   └── pattern_analyzer.py
└── config.py

**2. Configuration System (config.py):**
- Default config with all options
- Load from config file (YAML)
- Environment variable overrides
- Validation of required fields
- Example config file

**3. ParserRegistry:**
- Centralized parser management
- Auto-detect file types
- Plugin system for custom parsers
- Fallback handling

**4. Error Handling:**
- Custom exception classes
- Graceful degradation
- User-friendly error messages
- Logging throughout

**5. Unit Tests (tests/ directory):**
Basic tests for:
- ParallelIndexer (mock filesystem)
- Dependency resolver (simple import chains)
- Each parser (sample files)
- GraphDB (in-memory SQLite)
- AIClient (mock API responses)

Use pytest. Return sample test structure and 2-3 example tests.

**6. README.md:**
- Project description
- Installation instructions
- Quick start guide
- CLI command reference
- Chat command reference
- Configuration guide
- Development guide

**7. requirements.txt:**
All dependencies:
- click (CLI)
- prompt-toolkit (interactive input)
- pygments (syntax highlighting)
- networkx (graphs)
- pyyaml (YAML parsing)
- requests/httpx (HTTP)
- python-dotenv (env vars)
- pytest (testing)
- sqlite3 (built-in)

**8. .orcignore Template:**
Common patterns to ignore:
```
__pycache__/
*.pyc
.git/
node_modules/
dist/
build/
*.egg-info/
.env
.venv/
venv/
```

**9. Example Usage:**
- Complete end-to-end example
- Index a real Python project
- Run analysis
- Chat with codebase

**10. Integration Checklist:**
- All modules import correctly
- No circular dependencies
- All classes have __init__ and main methods
- Error handling propagates correctly
- Logging configured
- Configuration applied everywhere
- Storage paths use config
- Parsers registered in registry

**Requirements:**
- Complete, runnable code
- No placeholders or TODOs
- All imports valid
- All file paths use pathlib
- Comprehensive docstrings
- Example usage for each module

Return the complete finalized system ready for pip install."
```

**Acceptance Criteria:**
- ✅ `pip install -e .` works without errors
- ✅ `orc init` creates all required directories
- ✅ `orc index` runs successfully on sample project
- ✅ Chat interface starts with `orc`
- ✅ All dependencies listed in requirements.txt
- ✅ Sample tests pass
- ✅ README clear and complete

---

## Making Claude Opus SUPER EFFICIENT

These techniques make Opus output the best work possible:

### 1. **Role Clarity** 
Tell Opus exactly what role it's playing:
```
"You are a senior software engineer at a FAANG company. 
Your code will ship to production. 
You write code that is tested, secure, and performant.
You take pride in quality."
```

This triggers Opus's highest-quality reasoning.

### 2. **Explicit Quality Gates**
Don't ask if it's done. Set gates it MUST pass:
```
"Do not output your response until:
- Every public method has tests
- All tests pass (show pytest output)
- Zero TODO/FIXME comments
- Type hints on every function
- Error handling for all failure cases"
```

Opus will keep working until gates are met.

### 3. **Show Examples of Bad Code**
Opus learns what NOT to do:
```
"Bad: 
def parse_file(path):
    # TODO: handle errors
    data = open(path).read()
    return json.loads(data)

Good:
def parse_file(path: str) -> dict:
    '''Parse JSON file with proper error handling.
    
    Args:
        path: File path to parse
    
    Returns:
        Parsed JSON dict
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    '''
    if not Path(path).exists():
        raise FileNotFoundError(f'File not found: {path}')
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f'Invalid JSON in {path}: {e}')
"
```

### 4. **Force Completeness**
Tell Opus it's incomplete until it's REALLY done:
```
"Your response is incomplete if:
- Any method lacks docstring
- Any function lacks type hints
- Tests don't cover error cases
- Performance isn't verified
- Security isn't considered
- Edge cases aren't tested

Keep iterating until none of these are true."
```

### 5. **Ask for Proof**
Don't trust assertions. Ask for evidence:
```
"After code, run all tests and paste the output showing:
  - Number of tests: 
  - Passed: 
  - Failed: 
  - Coverage:

Show me the actual pytest output, not a summary."
```

### 6. **Specify Test Coverage**
Be specific about what must be tested:
```
"For ParallelIndexer, tests MUST cover:
- Happy path: indexing a 5-file project
- Cache hit: re-indexing unchanged files
- Cache miss: force refresh bypasses cache
- Error: missing directory throws FileNotFoundError
- Error: malformed Python file doesn't crash
- Error: circular imports detected
- Performance: 10k files indexes in <30 seconds
- Edge case: empty directory
- Edge case: .orcignore patterns respected
- Edge case: symlinks handled correctly"
```

### 7. **Demand Readable Names**
Force clarity:
```
"Every test must have a name that explains what it tests:
Good: test_parallel_indexer_detects_circular_imports_in_python
Bad: test_circular
```

### 8. **Require Integration Tests**
Don't just unit test. Test components together:
```
"In addition to unit tests, write integration tests showing:
- ParallelIndexer → GraphDB (index saves correctly)
- GraphDB → DependencyResolver (imports can be queried)
- DependencyResolver → Analyzer (circular deps detected)

These prove components work together."
```

### 9. **Ask for Performance Benchmarks**
Make Opus think about speed:
```
"After tests pass, add one benchmark test:

def test_performance_indexing_speed():
    start = time.time()
    result = indexer.index(test_project)
    elapsed = time.time() - start
    assert elapsed < 5, f'Indexing took {elapsed}s, target is <5s'
    print(f'Indexed {result['file_count']} files in {elapsed:.2f}s')

This ensures code isn't accidentally slow."
```

### 10. **Demand Security Review**
Make security top-of-mind:
```
"Before finishing, security review:
- No hardcoded credentials
- No unsafe file operations (no path traversal)
- No SQL injection (use parameterized queries)
- No eval/exec
- API keys from environment only
- Error messages don't leak sensitive info

If any security issue exists, fix it first."
```

---

## Execution Strategy

---

## MASTER PROMPT TEMPLATE (Copy This)

**Use this exact template for each prompt. Just fill in [PROMPT_NUMBER] and [COMPONENT]:**

```
You are a senior software engineer. Your code ships to production.

TASK: Build ORC Component [PROMPT_NUMBER]/8: [COMPONENT]

REFERENCE DOCUMENTS:
[PASTE ORC SYSTEM DOCUMENTATION]
[PASTE BUILD GUIDE]

SPECIFICATION FOR THIS COMPONENT:
[PASTE THE EXACT PROMPT FROM BUILD GUIDE]

QUALITY REQUIREMENTS (NON-NEGOTIABLE):
✅ Complete, production-ready code
✅ Zero TODO/FIXME/stub methods
✅ Type hints on EVERY function
✅ Docstrings explain WHY not just WHAT
✅ Error handling for ALL failure modes
✅ Security review (no SQL injection, path traversal, credentials in code)
✅ Performance considered (no obvious bottlenecks)
✅ Edge cases tested (empty input, malformed data, missing files, etc.)
✅ Real error scenarios tested (file not found, parse errors, API failures)

TESTING REQUIREMENTS:
Write comprehensive pytest tests covering:
1. Happy path (normal operation)
2. Error cases (what breaks? handle it gracefully)
3. Edge cases (empty files, special characters, symlinks)
4. Integration (does this work with previous components?)
5. Performance (is it fast enough? Add benchmark test)

Test naming: test_[class]_[what_it_tests]
Example: test_parallel_indexer_handles_missing_directory

DO NOT OUTPUT CODE UNTIL:
- All public methods have tests
- All tests pass (show pytest output)
- Zero placeholder code remains
- Every function has type hints
- Every function has docstring
- Error handling covers all cases

BUILD PROCESS:
1. Write complete code
2. Write comprehensive tests
3. Run tests: pytest tests/test_[component].py -v
4. If ANY test fails, fix code and re-test
5. Repeat until ALL tests pass ✅
6. Paste test output showing all tests passing
7. Paste complete code

SHOW ME:
- Pytest output with all tests passing
- Code with full docstrings and type hints
- Example of how to use the component
- Any security considerations
- Performance characteristics (if relevant)
```

**For Prompt 1 specifically, also add:**
```
FIRST TIME SETUP:
- Create complete directory structure
- Create setup.py for pip install
- Create requirements.txt
- Create .orcignore template
- Create example config file
- Create conftest.py for pytest fixtures

All of these must work together in first prompt.
```

---

## How to Use This Guide

**Message 1 to Opus:**
```
[Paste Master Prompt above, fill in Prompt 1 details]
```

**Opus works until all tests pass, then outputs:**
- Complete working code
- Comprehensive tests
- Test output showing ✅ all passing
- Docstrings and examples

**Message 2 to Opus (after reviewing code):**
```
Excellent. Tests all pass locally ✅

Continue with Prompt 2: Database Schema + Storage Layer

[Paste Master Prompt template, fill in Prompt 2 details]
```

**Repeat for Prompts 3-8**

---

## WHAT YOU'LL GET

After each prompt, you'll have:

✅ **Working code** - Not stubs, not placeholders. Real, complete code.
✅ **Comprehensive tests** - 20-50 tests per component, all passing
✅ **Full documentation** - Docstrings, examples, usage instructions
✅ **No technical debt** - Production-ready, no future refactoring needed
✅ **Error handling** - All failure modes handled gracefully
✅ **Security** - Reviewed, no vulnerabilities
✅ **Performance** - Benchmarked, no obvious bottlenecks
✅ **Type safety** - Full type hints throughout

**Result after 8 prompts:** A complete, tested, documented, production-ready ORC system.

---

## Key Differences from Typical AI Code Generation

| Typical | This Approach |
|---------|---------------|
| AI generates code, you test it | AI generates code AND comprehensive tests, proves tests pass |
| Code has TODOs and placeholders | Zero placeholder code |
| Minimal error handling | Complete error handling for all cases |
| Type hints optional | Type hints on EVERY function |
| Docstrings are brief | Docstrings explain WHY, with examples |
| Security not reviewed | Security explicitly reviewed before output |
| Performance unknown | Performance benchmarked |
| Integration surprises | Integration tests prove components work together |
| Tech debt accumulates | No tech debt, production-ready NOW |

---

## Pre-Work (Before First Prompt)
1. **Create a new git repo** for ORC
2. **Set up project structure** manually (create directories)
3. **Establish coding standards** document
4. **Review ORC documentation** thoroughly
5. **Prepare test codebase** (Python, JS, TypeScript samples)

### During Each Prompt (QUALITY-FIRST APPROACH)

**BEFORE OPUS CODES:**

```
You are Claude Opus. Your job is to build production-grade code with ZERO compromises.

QUALITY STANDARDS (NON-NEGOTIABLE):
1. Every function tested exhaustively - happy path AND edge cases
2. No TODO, FIXME, stub methods, or placeholder code
3. Full error handling with meaningful error messages
4. Type hints on EVERY function parameter and return
5. Docstrings explain WHY not just WHAT
6. Real error scenarios tested (file not found, parse errors, API failures, etc.)
7. Performance: code is as fast as reasonably possible
8. No technical debt - each component is production-ready NOW
9. Security: no SQL injection, path traversal, or unsafe operations
10. Logging at DEBUG/INFO/ERROR levels for debugging

BUILD PROCESS:
1. Write complete, production-ready code first
2. Write comprehensive tests (separate section)
3. Tests MUST pass before you're done
4. Show me test output proving all tests pass
5. If any test fails, fix the code and re-test until green

TESTING REQUIREMENTS:
- Unit tests for every public method
- Integration tests showing components work together
- Edge case tests (empty files, malformed input, missing data)
- Error condition tests (what happens when things fail?)
- Performance sanity checks (doesn't timeout on reasonable input)
- Use pytest with clear test names and assertions
- Mock external dependencies (don't make real API calls)

DOCUMENTATION:
- Every class/function has docstring
- Docstrings include: purpose, parameters, returns, raises (errors)
- Example usage in docstrings for complex functions
- README for component explaining usage

CODE QUALITY GATES:
✅ Code is complete and runnable NOW
✅ Zero placeholder code
✅ All tests pass (show pytest output)
✅ Error handling covers all failure modes
✅ Type hints complete
✅ No security issues
✅ Performance is good
✅ Code is readable and maintainable
```

2. **Copy the exact prompt** (use the formatted version from Build Guide)
3. **Include both original docs** so Opus has full context
4. **Say:** "Build this component. Full production quality, comprehensive tests. Show pytest output proving all tests pass. Only output code when you're 100% confident it works."

**DURING OPUS CODING:**
- Let it work without interruption
- It will write code, then tests, then run tests
- It will iterate if tests fail
- It will keep going until all tests pass

**AFTER OPUS FINISHES:**
1. **Check the test output** - should show ✅ all tests passing
2. **Review the code briefly** - skim for obvious issues
3. **Copy the code to your repo** - save to correct file paths
4. **Run the tests yourself locally** to verify:
   ```bash
   pytest tests/test_[module].py -v
   ```
5. **Only move to next prompt if tests pass locally** ✅

### After Prompt 8
1. **Run full integration test:**
   ```bash
   orc init
   orc index [your_test_project]
   orc report
   orc scan
   ```
2. **Start interactive chat:**
   ```bash
   orc
   > /help
   > What are the most complex functions?
   > /exit
   ```
3. **Test all CLI commands** listed in Prompt 7
4. **Test all parsers** on real sample code
5. **Fix any integration issues**

---

## Testing Protocol (Critical)

**After EACH prompt, include this instruction to Opus:**

```
After writing the code, write comprehensive pytest tests that:

1. Test all public methods
2. Test error cases (missing files, bad input, etc.)
3. Use sample/mock data (don't require real codebase)
4. Can run independently without other modules
5. Include setup/teardown if needed

Return test code in a separate code block.
Then run locally:
  pytest tests/test_[module].py -v

Only move to next prompt once ALL tests pass ✅
```

### Testing Checklist Per Prompt

**Prompt 1 (Indexing):**
- [ ] ParallelIndexer scans directory correctly
- [ ] Cache invalidation works on file changes
- [ ] Parser registry loads correct parser per language
- [ ] Force refresh actually bypasses cache
- [ ] IndexService orchestrates all components

**Prompt 2 (Database):**
- [ ] Database tables created with correct schema
- [ ] INSERT/UPDATE operations work
- [ ] Query operations return correct results
- [ ] Batch insert (executemany) works
- [ ] No SQL injection vulnerabilities in prepared statements

**Prompt 3 (Parsers 1):**
- [ ] Python parser extracts functions, classes, complexity
- [ ] JavaScript parser finds arrow functions, classes, imports
- [ ] TypeScript parser handles type annotations
- [ ] All return correct data structure format
- [ ] Handle syntax errors gracefully (don't crash)

**Prompt 4 (Parsers 2):**
- [ ] React parser identifies hooks and components
- [ ] HTML/CSS parser extracts tags and selectors
- [ ] JSON/YAML parsers detect schema types
- [ ] Markdown parser builds TOC from headings
- [ ] All framework parsers work on sample files

**Prompt 5 (Analysis):**
- [ ] Dependency resolver finds all imports
- [ ] Circular dependency detection works
- [ ] Dead code analyzer identifies unused functions
- [ ] Complexity analyzer ranks functions correctly
- [ ] DependencyGraph builds and queries correctly

**Prompt 6 (AI):**
- [ ] AIClient can initialize with each provider
- [ ] Chat method works (or returns clear error if no API key)
- [ ] Tool definitions are valid JSON format
- [ ] AICodeSummarizer handles batch processing
- [ ] Error handling for API failures

**Prompt 7 (CLI):**
- [ ] `orc init` creates directory structure
- [ ] `orc index` runs without crashing
- [ ] Chat loop starts and exits cleanly
- [ ] All slash commands recognized
- [ ] Output formatting displays correctly

**Prompt 8 (Integration):**
- [ ] Full end-to-end test: init → index → analyze → report
- [ ] All modules import without circular dependencies
- [ ] Configuration system works
- [ ] ParserRegistry auto-detects file types
- [ ] Sample unit tests all pass

---

## Token Budget Breakdown

| Prompt | Duration | Tokens | Component |
|--------|----------|--------|-----------|
| 1 | 2-3h | 300-400k | Core indexing |
| 2 | 1-2h | 200-300k | Database layer |
| 3 | 2-3h | 350-400k | Parsers (Python, JS, TS) |
| 4 | 1.5-2h | 250-300k | Parsers (React, HTML/CSS, data) |
| 5 | 2-2.5h | 250-350k | Analysis & dependency resolution |
| 6 | 1.5-2h | 200-300k | AI integration |
| 7 | 2-3h | 300-350k | CLI & chat |
| 8 | 2-3h | 250-300k | Integration & finalization |
| **TOTAL** | **5-7 days** | **~2-3M tokens** | **Complete system** |

### Cost Estimates (if using paid providers)
- **OpenAI (GPT-4):** ~$60-90 USD
- **Anthropic (Opus):** ~$40-60 USD  
- **DeepSeek:** ~$10-20 USD
- **Groq:** FREE (rate-limited)

---

## Quality Checklist

Before moving to next prompt, verify:

- [ ] All code has comprehensive docstrings
- [ ] No `TODO` or `FIXME` comments left
- [ ] Error handling for all external calls
- [ ] Type hints on all function signatures
- [ ] No hardcoded paths (use config)
- [ ] Proper logging throughout
- [ ] Sample usage documented
- [ ] Edge cases handled (empty dirs, malformed files, etc.)
- [ ] Cross-platform compatible (Windows/Mac/Linux)
- [ ] No circular imports
- [ ] All dependencies in requirements.txt

---

## Risk Mitigation

**Potential Issues & Workarounds:**

| Issue | Risk | Mitigation |
|-------|------|-----------|
| Parser complexity | Medium | Start simple (regex), upgrade to AST if needed |
| AI API failures | Medium | Implement fallback/offline mode |
| Database locks | Low | WAL mode + timeout handling |
| Token explosion | Medium | Batch processing + caching |
| Scope creep | High | Stick strictly to the 8 prompts |
| Import conflicts | Low | Use unique module names |

---

## Success Criteria (Final)

✅ **Complete ORC system** with all 8 components
✅ **All 11 parsers** working on real code
✅ **Database** with all 10 tables
✅ **AI integration** with 6 providers
✅ **CLI** with 8+ commands
✅ **Chat interface** with 12+ slash commands
✅ **<100k token** to run full analysis on 10k function codebase
✅ **Production-ready:** No warnings, proper error handling, clear logging
✅ **Documented:** README, docstrings, examples
✅ **Tested:** Sample tests pass, real-world usage works

---

## Template: What to Say After Each Prompt

**After Opus finishes code, before saying "continue":**

```
TESTING:
1. Review the pytest tests you provided
2. Fix any issues in the test file itself
3. Run locally with sample data/mocks
4. All tests must pass ✅

THEN:

Tests passed ✅ Move to next prompt.
Continue with Prompt [N+1]: [Component Name]
```

**Example after Prompt 1:**
```
Tests passed ✅ Move to next prompt.
Continue with Prompt 2: Database Schema + Storage Layer
```

This ensures **zero integration issues** later because each module is verified independently before moving on.

---

## Next Steps After Completion

1. **Deploy & Use:**
   - Install locally: `pip install -e .`
   - Test on your own codebase
   - Build Claude experience with your code

2. **Extend:**
   - Add custom parsers for your languages
   - Integrate with CI/CD pipeline
   - Build custom analysis tools
   - Create Slack/Discord bot integration

3. **Contribute:**
   - Share improvements
   - Add more languages
   - Optimize performance
   - Build community

---

## Document History

**Version:** 1.0  
**Created:** 2026-01-14  
**For:** Claude Opus 4.5  
**Purpose:** Strategic decomposition of ORC system build into 8 focused, efficient prompts  
**Status:** Ready to execute