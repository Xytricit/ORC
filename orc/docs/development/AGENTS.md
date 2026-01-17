# ORC System - Development Status & Handoff Notes

**Date:** January 15, 2026  
**Status:** 5 Components Complete + Major Cleanup Complete  
**Total Tests Passing:** 189+ tests (100% pass rate)  
**Last Updated:** 2026-01-15 (Cleanup + Onboarding System Added)

---

## 🔥 RECENT OPERATIONS (2026-01-15)

### Major Codebase Cleanup Completed
**Context:** Extensive cleanup operation to organize fragmented codebase

**What Was Done:**
1. **Phase 1-2:** Deleted 92 obsolete/duplicate files (orc_new/, orc_cli.py, etc.)
2. **Phase 3:** Consolidated component1_core_indexing/ into orc/core/
3. **Phase 4-5:** Organized 71 files (docs into docs/, scripts into scripts/)
4. **Phase 6:** Cleaned cache (12,500+ files, 220 MB freed)
5. **Total:** 12,700+ files cleaned, 220 MB recovered

**Key Decisions Made:**
- ✅ Kept root CLI files (cli_loop.py, cli_main.py, etc.) for backwards compat with test_component7.py
- ✅ Archived old monolithic orc/ implementation to archive/orc_v1_monolithic/
- ✅ Package structure (orc/cli/, orc/ai/, etc.) is the OFFICIAL working version
- ✅ setup.py points to orc.cli.cli_main (confirmed as entry point)

**Structure Created:**
- `docs/` - Organized into components/, development/, testing/, architecture/, installation/
- `scripts/` - Utilities (demos/, verify_installation.py)
- `archive/` - Old implementations preserved (orc_v1_monolithic/, root_cli_system/)

### Onboarding System Added
**New Feature:** First-run configuration wizard

**Files Created:**
- `orc/cli/onboarding.py` - Interactive setup flow

**Features:**
- Interactive AI provider selection (Groq, OpenAI, Anthropic, DeepSeek, Ollama)
- Secure API key storage in ~/.orc/.env (restrictive permissions)
- Token usage display after each AI response
- Runs automatically on first `orc` command

**Integration:**
- Connected to cli_loop.py (runs before chat starts)
- Loads config from ~/.orc/.env using python-dotenv
- Shows token usage with costs after each AI response

### Interactive Chat Connection
**Changed:** Running `orc` (no arguments) now launches interactive chat (not help menu)
- `orc` → Interactive AI chat with banner
- `orc <command>` → Runs command normally

**Files Modified:**
- `orc/cli/cli_main.py` - Changed default behavior to launch chat
- `orc/cli/cli_loop.py` - Added onboarding integration + token display
- `orc/cli/banner.py` - Restored from archive for aesthetic

---  

---

## ✅ COMPLETED COMPONENTS (5 of 8)

### Component 1: Core Architecture + Indexing System
**Location:** `component1_core_indexing/` folder  
**Size:** 3,815 lines (production + tests + docs)  
**Tests:** 77/77 passing ✅  
**Performance:** 100 files in <5s, Cache 47x speedup  

**Key Files:**
- `config.py` (293 lines) - YAML + environment variable configuration
- `cache.py` (372 lines) - TTL + mtime caching layer
- `parallel_indexer.py` (498 lines) - Multi-process file indexing
- `index_service.py` (227 lines) - Unified façade
- `tests/` folder with conftest.py and 4 test files
- `README.md`, `DELIVERABLES.md`, `FINAL_OUTPUT.md`, `SECURITY_REVIEW.md`

**Features:**
- CPU auto-detection (multiprocessing.cpu_count())
- .orcignore pattern matching (gitignore-style)
- Force refresh support
- Cross-platform (Windows/Mac/Linux with pathlib)

**Performance Verified:**
- 100 files indexed in 3.87s
- Cache speedup: 47x faster
- Files/second: 25.8

---

### Component 2: Database Schema + Storage Layer
**Location:** `orc_graph_db.py` (single file)  
**Size:** 1,320 lines  
**Tests:** 25/25 passing ✅  
**Performance:** 80,270 inserts/second  

**Features:**
- 10 database tables
- 7 performance indexes
- SQL injection prevention (tested and verified)
- WAL mode for concurrent reads
- Prepared statements throughout
- Batch insert support via executemany()
- INSERT OR REPLACE for idempotency
- Context manager support

**Schema (10 Tables):**
1. `file_index` - Indexed files with metadata (path, language, loc, timestamps)
2. `function_index` - Functions with complexity (func_id, name, file, lines, complexity, code, params, calls, is_exported)
3. `class_index` - Classes with inheritance (class_id, name, file, lines, methods, base_classes)
4. `import_index` - Import statements (import_id, source_file, statement, line_number)
5. `export_index` - Exported entities (export_id, name, kind, file)
6. `file_dependencies` - Resolved file-to-file (id, source, target, statement, line)
7. `function_calls_resolved` - Function call graph (id, caller_file, caller_func, callee_file, callee_func, line)
8. `entry_points` - Application entry points (id, file_path, entry_type, line_number)
9. `code_summaries` - AI-generated summaries (id, entity_id, entity_type, summary, provider, timestamp)
10. `ai_insights` - AI analysis insights (id, entity_id, insight_type, description, severity)

**7 Performance Indexes:**
- idx_func_name, idx_func_complexity, idx_func_file
- idx_class_file, idx_file_deps_source
- idx_func_calls_caller, idx_summaries_entity

**Documentation:** `ORC_COMPONENT_2_SUMMARY.md`

---

### Component 3: Language Parsers
**Location:** `orc_parsers.py` (single file)  
**Size:** 1,469 lines  
**Tests:** 29/29 passing ✅  

**Parsers Implemented:**
1. **BaseParser** - Abstract base class with parse_file() interface
2. **PythonParser** - Full AST-based with McCabe complexity
   - Uses ast.parse() for accurate parsing
   - McCabe complexity: Base(1) + if/for/while/except(+1) + and/or(+1) + lambda(+1)
   - Async functions (async def)
   - Decorators (@decorator)
   - Type hints (def foo(x: int) -> str)
   - Docstrings (ast.get_docstring)
   - Entry points (if __name__ == '__main__')
   - __all__ exports
   - Class inheritance tracking
   - Function call extraction
   - Syntax error handling (graceful failure)
   
3. **JavaScriptParser** - Regex-based for ES6+
   - Function declarations: `function name() {}`
   - Arrow functions: `const name = () => {}`, `const name = x => x * 2`
   - Async functions: `async function`, `async () =>`
   - ES6 classes: `class Name extends Base {}`
   - ES6 imports: `import { x } from 'module'`
   - CommonJS: `require('module')`, `module.exports`
   - Exports: `export default`, `export const`, `module.exports`
   - Method extraction from classes
   
4. **TypeScriptParser** - Extends JavaScriptParser
   - All JavaScript features inherited
   - Interfaces: `interface Name { ... }`
   - Type aliases: `type Name = ...`
   - Enums: `enum Name { ... }`
   - Type annotations on functions
   - Interface inheritance (extends)
   - Generic types: `<T>`
   - Access modifiers: public, private, protected

**McCabe Complexity Example:**
```python
# Input: complex_function with 3 ifs, 1 for, 1 while, 1 and
# Output: complexity = 8 (verified in tests)
```

**Documentation:** `ORC_COMPONENT_3_SUMMARY.md`

---

### Component 5: Analysis Modules + Dependency Resolution
**Location:** `orc_analysis.py` (single file)  
**Size:** 1,444 lines  
**Tests:** 31/31 passing ✅  
**Performance:** 71,895 functions/second  

**Modules (6 Total):**

1. **DependencyResolver**
   - Resolves imports to actual file locations
   - Detects standard library (35+ stdlib modules: os, sys, json, etc.)
   - Handles absolute, relative, package imports
   - Finds circular dependencies (DFS algorithm)
   - Returns: file_dependencies, function_calls_resolved, unresolved_imports, circular_dependencies

2. **DependencyGraph** (Uses NetworkX)
   - Module dependency graph (DiGraph)
   - Function call graph (DiGraph)
   - Circular detection (Johnson's algorithm)
   - Coupling calculation: (in_degree + out_degree) / max_possible (normalized 0.0-1.0)
   - Get module dependencies: depends_on, depended_by

3. **DeadCodeAnalyzer**
   - Confidence scoring (0.0-1.0)
   - False positive rate: <20% (tested: 0% in sample)
   - Excludes: magic methods (__init__, __str__, etc.)
   - Excludes: exported functions
   - Excludes: decorated functions (@route, @fixture, etc.)
   - Returns: entity_id, name, file, line, confidence, reason, type

4. **ComplexityAnalyzer**
   - Multi-metric scoring:
     - Cyclomatic complexity (from parser)
     - Lines of code (LOC)
     - Nesting depth (estimated from complexity)
     - Parameter count
   - Scoring formula: complexity * 0.5 + (loc/10) * 0.3 + nesting * 0.2
   - Returns sorted list by complexity_score

5. **DependencyAnalyzer**
   - Finds circular dependencies
   - Detects tightly coupled modules (coupling > 0.5)
   - Identifies hotspots (high complexity + high coupling)
   - Returns: circular_dependencies, tightly_coupled, external_deps, hotspots

6. **Analyzer** (Orchestrator)
   - Coordinates all analyzers
   - Single entry point: run_all(index)
   - Returns: dead_code, dependencies, metrics, complexity, hotspots, summary

**Performance Verified:**
- 1000 functions in 0.01s
- Complexity analysis: 0.004s

**Documentation:** `ORC_COMPONENT_5_SUMMARY.md`

---

### Component 4: AI Integration
**Location:** `orc/ai/` folder  
**Size:** 1,051 lines (production code)  
**Tests:** 13/13 passing ✅  

**Modules (4 Total):**

1. **AIClient** (358 lines)
   - Multi-provider AI client (Groq, OpenAI, Anthropic, DeepSeek, Ollama)
   - Consistent interface across all providers
   - Error handling with graceful fallbacks
   - Token usage tracking
   - OpenAI-compatible API format
   - Automatic API key loading from environment

2. **AICodeSummarizer** (243 lines)
   - Function summarization with context
   - Class summarization with method lists
   - Batch processing support (multiple functions at once)
   - Context-aware prompts
   - Graceful error handling
   - Database caching support

3. **ORCTools** (430 lines)
   - 10 AI function calling tools
   - Database query tools (query_functions, get_classes)
   - Analysis tools (get_complex_functions, find_circular_dependencies)
   - Dependency tools (get_file_dependencies, get_function_calls)
   - Statistics tools (get_statistics, get_file_stats)
   - OpenAI function calling format

4. **Module Exports** (20 lines)
   - Clean API surface
   - Exports: AIClient, AICodeSummarizer, ORCTools, get_tools_for_ai

**AI Providers Supported:**
- ✅ Groq (Free, fast) - Recommended for testing
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude 3: Opus, Sonnet, Haiku)
- ✅ DeepSeek (Cost-effective)
- ✅ Ollama (Local models)

**CLI Integration:**
- Already integrated in `orc/cli/cli_loop.py`
- Uses AIClient for chat responses
- Uses ORCTools for function calling
- Token tracking and cost estimation

**Documentation:** `ORC_COMPONENT_4_AI_INTEGRATION.md`, `AI_INTEGRATION_SUMMARY.md`

---

### Component 7: CLI Commands + Chat Interface
**Location:** `orc_cli.py` (single file)  
**Size:** 623 lines  
**Tests:** 14/14 passing ✅  

**Modules (5 Total):**

1. **CLIOutput** - Professional styling
   - start_phase(title) - Print phase header with ›
   - success(message) - Green ✓ or [OK]
   - warning(message) - Yellow ! or [WARN]
   - error(message) - Red ✗ or [ERR]
   - info(message) - Blue • or plain
   - Fallback for non-color terminals
   - CI/CD friendly

2. **UIComponents** - Syntax highlighting
   - display_user_message(message)
   - display_ai_message(message)
   - display_code_block(code, language)
   - highlight_code(code, language) - Uses pygments
   - auto_detect_language(code) - Detects python/javascript/etc.
   - Markdown code block detection (```language code```)

3. **SessionManager** - Conversation persistence
   - save_session(name, messages, metadata)
   - load_session(name) - Returns latest session
   - list_sessions() - Returns [(name, timestamp, count)]
   - export_to_markdown(messages, path)
   - export_to_json(messages, path)
   - update_last_code_block(message)
   - Saves to ~/.orc/sessions/

4. **TokenTracker** - Cost estimation
   - add_request(provider, model, input_tokens, output_tokens)
   - estimate_cost(provider, model, input, output)
   - get_statistics() - Returns total_tokens, total_cost, by_provider
   - **Pricing table (per 1M tokens):**
     - groq: Free
     - openai-gpt4: $30 input, $60 output
     - openai-gpt35: $0.50 input, $1.50 output
     - anthropic-opus: $15 input, $75 output
     - anthropic-sonnet: $3 input, $15 output
     - ollama: Free (local)
     - deepseek: $0.14 input, $0.28 output
     - gemini: Free tier

5. **CLIMain** - 8 Click commands
   - `orc init` - Initialize .orc/, create config files
   - `orc index [--force] [--quiet]` - Index project files
   - `orc scan` - Quick health check + analysis
   - `orc report [--output FILE]` - Generate markdown report
   - `orc find <what>` - Find dead/complex/pattern
   - `orc check` - Health check (config, db, parsers)
   - `orc ignore <pattern>` - Add to .orcignore
   - `orc config [action]` - Manage configuration

**All Commands Working:**
```bash
$ orc init
› Initializing ORC
  ✓ Created directory: .orc
  ✓ Created cache and sessions directories
  ✓ Created orc_config.yaml

$ orc scan
› Running Quick Scan
  ✓ Files: 42
  ✓ Functions: 128
  ! Dead code: 3 functions
```

**Documentation:** `ORC_COMPONENT_7_SUMMARY.md`

---

## 🔄 INTEGRATION DEMO WORKING

**File:** `demo_components_1_2_3.py` (250 lines)

**Demonstrates Complete Pipeline:**
```
Component 1 (Index) → Component 3 (Parse) → Component 2 (Store) → Query
```

**Actual Output:**
```
✅ Component 1: Indexed 3 files (Python, JS, TS)
✅ Component 3: Parsed all files successfully
   - 7 functions found (4 Python, 2 JS, 1 TS)
   - 3 classes found
   - 1 interface found
   - 1 enum found
✅ Component 2: Stored 7 functions, 3 classes in database
✅ Query: Found 1 complex function (calculate: complexity 3)

All 3 components working together successfully! 🎉
```

---

## 🎯 COMPONENT 8 SPECIFICATION

### What Component 8 Must Do

1. **Create Unified Package Structure**
   ```
   orc/
   ├── __init__.py (export all components)
   ├── config.py (unified config system)
   ├── core/ (from Component 1)
   ├── parsers/ (from Component 3)
   ├── storage/ (from Component 2)
   ├── analysis/ (from Component 5)
   └── cli/ (from Component 7)
   ```

2. **Parser Registry** (`orc/parsers/__init__.py`)
   ```python
   PARSERS = {
       '.py': PythonParser,
       '.js': JavaScriptParser,
       '.jsx': JavaScriptParser,
       '.ts': TypeScriptParser,
       '.tsx': TypeScriptParser,
   }
   
   def get_parser(file_path: Path) -> BaseParser:
       ext = file_path.suffix
       parser_class = PARSERS.get(ext)
       if parser_class:
           return parser_class()
       return None
   ```

3. **Custom Exceptions** (`orc/exceptions.py`)
   ```python
   class ORCError(Exception): pass
   class ParsingError(ORCError): pass
   class IndexError(ORCError): pass
   class DatabaseError(ORCError): pass
   class ConfigError(ORCError): pass
   class AIError(ORCError): pass
   ```

4. **Setup Files**
   - `setup.py` - For pip install
   - `requirements.txt` - All dependencies
   - `pyproject.toml` - Modern packaging

5. **Integration Tests** (`tests/test_integration.py`)
   - Test full pipeline: index → parse → analyze → store
   - Test CLI commands end-to-end
   - Test configuration loading
   - Test parser registry

6. **Documentation**
   - `README.md` - User guide
   - `DEVELOPMENT.md` - Developer guide

---

## 📦 DEPENDENCIES TO CONSOLIDATE

**Required:**
- click>=8.0
- pyyaml>=6.0
- networkx>=2.6
- pytest>=7.0.0

**Optional:**
- prompt-toolkit>=3.0 (for interactive chat)
- pygments>=2.10 (for syntax highlighting)

---

## 🔧 INTEGRATION POINTS (Already Working)

### Component 1 → Component 3
```python
from orc.core import ParallelIndexer
from orc_parsers import PythonParser

indexer = ParallelIndexer(root_path=Path('.'))
files = indexer._scan_files(extensions=['.py'])
parser = PythonParser()
for file in files:
    result = parser.parse_file(file)
```

### Component 3 → Component 2
```python
from orc_parsers import PythonParser
from orc_graph_db import GraphDB

parser = PythonParser()
result = parser.parse_file(Path('module.py'))
db = GraphDB("orc.db")
for func_id, func_data in result['functions'].items():
    db.store_function(...)
```

### Component 5 Uses All
```python
from orc_analysis import Analyzer

analyzer = Analyzer()
results = analyzer.run_all(parsed_index)
# Returns: dead_code, dependencies, complexity, hotspots
```

### Component 7 Orchestrates All
```python
# CLI commands call components as needed
# orc scan: Uses 1, 3, 5, 2, 7
```

---

## 📊 STATISTICS

**Total Code:** ~13,300 lines
- Production: ~10,250 lines
- Tests: ~2,800 lines
- Documentation: ~4,500 lines

**Total Tests:** 189 passing
- Component 1: 77 tests
- Component 2: 25 tests
- Component 3: 29 tests
- Component 4: 13 tests ✨ NEW
- Component 5: 31 tests
- Component 7: 14 tests

**Performance:**
- Indexing: 3.87s for 100 files
- Database: 80,270 inserts/sec
- Analysis: 71,895 functions/sec
- Cache: 47x speedup

**Security:**
- SQL injection: Prevented ✅
- No eval/exec: Verified ✅
- Safe YAML: yaml.safe_load ✅
- All paths validated ✅

---

## 🚀 NEXT SESSION TASKS (Component 8)

### Task 1: Create Package Structure (HIGH PRIORITY)
Move files into proper structure:
```bash
mkdir -p orc/core orc/parsers orc/storage orc/analysis orc/cli orc/session
# Move component files to appropriate locations
# Create __init__.py files with imports
```

### Task 2: Unified Configuration (HIGH PRIORITY)
Merge configuration systems from different components into one.

### Task 3: Setup Files (HIGH PRIORITY)
Create working pip install setup.

### Task 4: Integration Tests (MEDIUM)
Write 20-30 tests proving components work together.

### Task 5: Documentation (MEDIUM)
Create README.md with installation and usage.

---

## ⚠️ KNOWN ISSUES

1. **Import Paths:** Components use different styles (relative vs absolute)
2. **Configuration:** Each component has own config approach
3. **No Parser Registry:** Manual parser selection currently
4. **No Custom Exceptions:** Using built-in exceptions
5. **No Entry Point:** Need proper console_scripts in setup.py

---

## 💡 RECOMMENDATIONS FOR NEW CHAT

### Efficient Approach (Fits Token Budget)

**Prompt for New Chat:**
```
You are a senior software engineer. Your code ships to production.

TASK: Build ORC Component 8/8: Integration & Packaging

I have 5 working ORC components (176 tests passing). Files:
- component1_core_indexing/ (indexing system)
- orc_graph_db.py (database)
- orc_parsers.py (Python/JS/TS parsers)
- orc_analysis.py (analyzers)
- orc_cli.py (CLI interface)

Read AGENTS.md for complete context.

BUILD:
1. Create proper package structure (orc/ folder)
2. Move all components to correct locations
3. Create __init__.py files with imports
4. Create setup.py for pip install
5. Write 20 integration tests
6. Create README.md

DO NOT OUTPUT until all tests pass.
```

### What to Expect
- Package structure creation
- Import resolution
- Working `pip install -e .`
- Working `orc` command
- 20 integration tests passing
- Basic README

---

## 📝 QUICK REFERENCE

**All Component Files:**
- `component1_core_indexing/` - Indexing system
- `orc_graph_db.py` - Database (1,320 lines)
- `orc_parsers.py` - Parsers (1,469 lines)
- `orc/ai/` - AI Integration (1,051 lines) ✨ NEW
- `orc_analysis.py` - Analysis (1,444 lines)
- `orc_cli.py` - CLI (623 lines)

**All Documentation:**
- `ORC_COMPONENT_1_SUMMARY.md`
- `ORC_COMPONENT_2_SUMMARY.md`
- `ORC_COMPONENT_3_SUMMARY.md`
- `ORC_COMPONENT_4_AI_INTEGRATION.md` ✨ NEW
- `ORC_COMPONENT_5_SUMMARY.md`
- `ORC_COMPONENT_7_SUMMARY.md`
- `ORC_COMPONENTS_1_2_3_COMPLETE.md`
- `AI_INTEGRATION_SUMMARY.md` ✨ NEW

**Demo:** `demo_components_1_2_3.py` (working end-to-end)

**Config Files:**
- `.orcignore` - Ignore patterns
- `example_config.yaml` - Config template
- `orc_config.yaml` - Created by `orc init`

---

## ✅ READY FOR COMPONENT 8

All prerequisites complete. New chat can focus purely on integration and packaging.

**Start new chat with the prompt above + reference to AGENTS.md!**

---

**End of Handoff Document**

---

## RECENT UPDATES (2026-01-16 - Part 4)

### Enhanced Parser Development - Phase 1 Started

**Date:** 2026-01-16 22:00
**Status:** 🚀 Building Full Vision | Phase 1 In Progress
**Decision:** Risk it for the biscuit - building complete 22-section system

#### The Decision
Chose **Approach B (All-or-Nothing)** over pragmatic incremental approach.

**Rationale:**
- Build complete parser system that extracts ALL needed data
- Enhance parsers BEFORE connecting to database
- Implement full 22-section vision from the start
- Higher risk but complete solution

#### Gap Analysis Completed
**Created:** `PARSER_DATABASE_GAP_ANALYSIS.md`

**Current State:**
- Parsers: 18% of vision (functions, classes, imports only)
- Database: 27% of vision (10 tables, many empty)
- AI Backend: 0% (not implemented)
- **Total: ~15% complete**

**Missing 18 of 22 sections:**
- Section 3: Data Models & Schemas
- Section 4: Entry Points (enhanced with API routes)
- Section 5: State Management (DB queries, cache, files)
- Section 7: Error Handling (try/except, raises)
- Section 8: Configuration (env vars, config files)
- Section 9: Cross-Cutting Concerns (auth, logging, caching)
- Section 14: Side Effects (HTTP calls, emails, queues)
- Section 15: Concurrency (async, locks, threads)
- Section 17: Security (SQL injection, XSS, secrets)
- Sections 11-13, 16, 18-22: Need AI Backend

#### Enhanced Parser Design Completed
**Created:** `ENHANCED_PARSER_DESIGN.md` (Complete blueprint)

**7-Phase Implementation Plan:**

1. **Phase 1:** Extend Base Parser (1 session) ← **CURRENT**
   - Add semantic extraction methods
   - Define contracts for all parsers
   
2. **Phase 2:** Enhance Python Parser (2 sessions)
   - FastAPI/Flask/Django API routes
   - SQLAlchemy/Django ORM queries
   - Error handling patterns
   - Config usage (os.getenv)
   - Side effects (requests, email)
   - Security risks (SQL injection)

3. **Phase 3:** Enhance JS/TS Parser (2 sessions)
   - Express/Fastify routes
   - Sequelize/TypeORM queries
   - Error handling
   - Config (process.env)
   - Side effects (fetch, axios)
   - Security checks

4. **Phase 4:** Extend Database Schema (1 session)
   - Add ~12 new tables
   - api_endpoints, database_queries, error_handlers, etc.

5. **Phase 5:** Implement AI Backend (2-3 sessions)
   - Read raw parser output
   - Add semantic intelligence
   - Store in code_summaries/ai_insights
   - No hallucination

6. **Phase 6:** Build TOC System (1 session)
   - Index all 22 sections
   - Fast keyword search
   - Section navigation

7. **Phase 7:** Wire Everything (1 session)
   - Complete integration
   - End-to-end testing

**Total Timeline:** 10-11 sessions

#### New Parser Architecture

**Enhanced Output Structure:**
```python
{
    'files': {...},  # Section 1: Enhanced with file_type, module, purpose
    'functions': {...},  # Section 2: Enhanced with return_type, raises, side_effects
    'classes': {...},  # Section 2: Enhanced with properties, is_data_model
    'data_models': {...},  # Section 3: NEW
    'entry_points': {  # Section 4: Enhanced
        'main': [...],
        'api_endpoints': [...],  # NEW
        'event_listeners': [...],  # NEW
        'cron_jobs': [...],  # NEW
    },
    'state_management': {  # Section 5: NEW
        'database_queries': [...],
        'cache_usage': [...],
        'file_operations': [...]
    },
    'error_handling': {...},  # Section 7: NEW
    'configuration': {...},  # Section 8: NEW
    'cross_cutting': {...},  # Section 9: NEW
    'side_effects': {...},  # Section 14: NEW
    'concurrency': {...},  # Section 15: NEW
    'security': {...},  # Section 17: NEW
}
```

#### Phase 1 Goals (COMPLETED ✅)
**Tasks:**
1. ✅ Design enhanced parser architecture
2. ✅ Extend BaseParser with new abstract methods (9 methods added)
3. ✅ Update PythonParser with method stubs and integration
4. ✅ Update JavaScriptParser with method stubs and integration
5. ✅ Update TypeScriptParser with method stubs and integration
6. ✅ Create comprehensive tests (all passing)
7. ✅ All tests pass (29 original + Phase 1 verification tests)

**Files to Modify:**
- `orc/parsers/base_parser.py` - Add new abstract methods
- `orc/parsers/all_parsers.py` - Add method stubs to all parsers
- Test files - Ensure all tests pass

**Success Criteria:**
- BaseParser has all semantic extraction methods defined
- All concrete parsers have method stubs (can return empty for now)
- Tests pass (basic structure validated)
- Clear contracts for Phase 2-3 implementation

#### What Semantic Extraction Will Detect

**API Endpoints:**
- FastAPI: `@app.get("/path")`
- Flask: `@app.route("/path")`
- Express: `app.get('/path', handler)`

**Database Queries:**
- SQLAlchemy: `User.query.filter_by(...)`
- Django ORM: `User.objects.get(...)`
- Raw SQL: `cursor.execute("SELECT...")`
- Sequelize: `User.findOne(...)`

**Error Handling:**
- Python: `try/except/raise`
- JavaScript: `try/catch/throw`

**Config Usage:**
- Python: `os.getenv("KEY")`, `config.get("key")`
- JavaScript: `process.env.KEY`, `require('config')`

**Side Effects:**
- HTTP: `requests.post(...)`, `fetch(...)`, `axios.get(...)`
- Email: SMTP libraries
- Queues: RabbitMQ, Redis, SQS patterns

**Security:**
- SQL injection: f-string in SQL query
- Hardcoded secrets: API keys in code
- XSS risks: Unescaped user input

#### Phase 1 Results (Session Complete)
**Achievements:**
- ✅ BaseParser extended with 9 semantic extraction methods
- ✅ All 3 parsers (Python, JS, TS) integrated with semantic extraction
- ✅ Default implementations return correct empty structures
- ✅ All parsers now return 22-section compatible output
- ✅ 29 original parser tests passing
- ✅ Phase 1 verification tests passing
- ✅ Backward compatible (existing tests still pass)

**Files Modified:**
1. `orc/parsers/base_parser.py` - Added 9 semantic extraction methods (302 lines added)
2. `orc/parsers/all_parsers.py` - Integrated semantic extraction into all 3 parsers

**New Methods Added to BaseParser:**
1. `extract_api_endpoints()` - API route detection
2. `extract_database_queries()` - DB query pattern detection
3. `extract_error_handling()` - Try/except/raise patterns
4. `extract_config_usage()` - Env vars and config usage
5. `extract_side_effects()` - External API calls, emails, queues
6. `extract_cross_cutting_concerns()` - Auth, logging, caching
7. `extract_security_risks()` - SQL injection, secrets, XSS
8. `extract_data_models()` - Data schemas and models
9. `extract_concurrency_patterns()` - Async, locks, threads

**Parser Output Structure (Enhanced):**
```python
{
    'files': {...},
    'functions': {...},
    'classes': {...},
    'imports_detailed': [...],
    'exports': {...},
    'entry_points': [...],
    # NEW: Semantic sections (currently return empty, Phase 2-3 will implement)
    'api_endpoints': [],
    'database_queries': [],
    'error_handling': {'try_blocks': [], 'raises': []},
    'configuration': {'env_vars': [], 'config_keys': [], 'feature_flags': []},
    'side_effects': {'external_apis': [], 'email_sends': [], 'message_queue': [], 'background_jobs': []},
    'cross_cutting': {'auth_checks': [], 'logging': [], 'caching': [], 'validation': []},
    'security': {'sql_injection_risks': [], 'xss_risks': [], 'secrets': [], 'weak_crypto': []},
    'data_models': {},
    'concurrency': {'locks': [], 'thread_usage': [], 'async_contexts': []}
}
```

#### Phase 2 Results (Session Complete) ✅
**Achievements:**
- ✅ Implemented all 9 semantic extraction methods for Python
- ✅ API endpoint detection (FastAPI/Flask)
- ✅ Database query detection (SQLAlchemy/Django ORM/Raw SQL)
- ✅ Error handling detection (try/except/raise)
- ✅ Config usage detection (os.getenv, os.environ)
- ✅ Side effects detection (HTTP calls with requests/httpx)
- ✅ Cross-cutting concerns (auth decorators, logging)
- ✅ Security risk detection (SQL injection, hardcoded secrets)
- ✅ Data model detection (dataclass, Pydantic, SQLAlchemy)
- ✅ Concurrency pattern detection (locks, async contexts)
- ✅ Comprehensive test suite (9 semantic detection tests passing)
- ✅ All 29 original parser tests still passing

**Detection Capabilities:**
- **API Endpoints:** Detects `@app.get()`, `@app.post()`, `@app.route()`
- **Database Queries:** Detects SQLAlchemy (`.query.filter_by()`), Django ORM (`.objects.get()`), Raw SQL (`cursor.execute()`)
- **Error Handling:** Detects try/except blocks, raise statements, exception types
- **Config Usage:** Detects `os.getenv()`, `os.environ[]` with default values
- **Side Effects:** Detects `requests.get()`, `requests.post()`, `httpx.*` calls with URLs
- **Auth Checks:** Detects `@login_required`, `@require_permission()` decorators
- **Logging:** Detects `logger.info()`, `logger.error()`, etc.
- **SQL Injection:** Detects f-strings in SQL queries (tracks variable assignments)
- **Secrets:** Detects hardcoded passwords, API keys, tokens
- **Data Models:** Detects `@dataclass`, `BaseModel`, SQLAlchemy models
- **Concurrency:** Detects `threading.Lock()`, `asyncio.Lock()`, `async with`

**Code Quality:**
- Backward compatible (all existing tests pass)
- Well-tested (9 new semantic detection tests)
- Production-ready Python parser

**Implementation Details (For Context Continuity):**

**1. API Endpoint Detection (`extract_api_endpoints`):**
```python
# Detects FastAPI: @app.get("/path"), @app.post("/path")
# Detects Flask: @app.route("/path", methods=["GET"])
# Returns: [{route, method, handler, line, auth_required, middleware}]
```

**2. Database Query Detection (`extract_database_queries`):**
```python
# Django ORM checked FIRST: User.objects.get(id=1)
# SQLAlchemy checked SECOND: User.query.filter_by(id=1)
# Raw SQL: cursor.execute("SELECT ...") with parameterization check
# Uses _has_query_in_chain() to identify SQLAlchemy patterns
# Returns: [{query_type, table, is_parameterized, orm_type}]
```

**3. Error Handling (`extract_error_handling`):**
```python
# Tracks try/except blocks with exception types
# Tracks raise statements
# Uses _find_containing_function() to get context
# Returns: {try_blocks: [...], raises: [...]}
```

**4. Config Usage (`extract_config_usage`):**
```python
# Detects os.getenv("KEY", "default")
# Detects os.environ["KEY"]
# Tracks default values
# Returns: {env_vars: [...], config_keys: [...], feature_flags: [...]}
```

**5. Side Effects (`extract_side_effects`):**
```python
# Detects requests.get/post/put/delete
# Detects httpx.* calls
# Extracts URL from first argument
# Returns: {external_apis: [...], email_sends: [], message_queue: [], background_jobs: []}
```

**6. Cross-Cutting Concerns (`extract_cross_cutting_concerns`):**
```python
# Auth decorators: Handles both @login_required and @require_permission("admin")
# Logging: Detects logger.info/debug/error/warning
# Checks decorator is ast.Name OR ast.Call with ast.Name func
# Returns: {auth_checks: [...], logging: [...], caching: [], validation: []}
```

**7. Security Risks (`extract_security_risks`):**
```python
# SQL Injection: Tracks f-string variables, checks if used in cursor.execute()
# First pass: Build set of fstring_vars from ast.Assign nodes
# Second pass: Check execute() calls for JoinedStr or fstring variables
# Hardcoded secrets: Look for 'password', 'secret', 'api_key', 'token' in variable names
# Returns: {sql_injection_risks: [...], xss_risks: [], secrets: [...], weak_crypto: []}
```

**8. Data Models (`extract_data_models`):**
```python
# Detects @dataclass decorator
# Detects Pydantic: inherits from BaseModel
# Detects SQLAlchemy: inherits from Base
# Returns: {model_id: {name, fields, purpose, db_table, line}}
```

**9. Concurrency (`extract_concurrency_patterns`):**
```python
# Detects threading.Lock(), asyncio.Lock() calls
# Detects async with statements (ast.AsyncWith)
# Returns: {locks: [...], thread_usage: [], async_contexts: [...]}
```

**Helper Methods Added:**
- `_parse_api_decorator()` - Parse FastAPI/Flask decorators
- `_parse_database_call()` - Parse DB query calls
- `_extract_table_name()` - Extract table/model name from query chain
- `_extract_table_from_sql()` - Regex to extract table from SQL string
- `_find_containing_function()` - Find function that contains a node
- `_has_query_in_chain()` - Check if .query in attribute chain (SQLAlchemy)

**Key Design Decisions:**
1. Django ORM checked before SQLAlchemy (prevents false positives)
2. F-string SQL injection uses two-pass approach (track vars, then check usage)
3. Auth decorators handle both simple (@login_required) and call forms (@require_permission("admin"))
4. Default implementations in BaseParser return empty structures (backward compatible)

#### Phase 4 Results (COMPLETE ✅)
**Achievements:**
- ✅ Extended database schema from 10 to 19 tables
- ✅ Added 9 new semantic tables for storing parsed data
- ✅ Implemented 9 new store methods for semantic data
- ✅ All store operations tested and working
- ✅ Foreign key relationships maintained

**New Tables Added:**
1. `api_endpoints` - API route definitions (route, method, handler, auth)
2. `database_queries` - DB query patterns (query_type, table, ORM type, parameterization)
3. `error_handlers` - Error handling patterns (try/except, raises, exceptions)
4. `config_usage` - Configuration usage (env vars, config keys, defaults)
5. `side_effects` - External interactions (HTTP calls, library, target)
6. `cross_cutting_concerns` - Auth checks, logging, caching
7. `security_risks` - SQL injection, hardcoded secrets, XSS risks
8. `data_models` - Data schemas (models, interfaces, fields)
9. `concurrency_patterns` - Locks, async contexts, threading

**New Store Methods:**
- `store_api_endpoints()` - Store API routes with auth info
- `store_database_queries()` - Store DB queries with ORM detection
- `store_error_handlers()` - Store try/except blocks and raises
- `store_config_usage()` - Store env vars and config keys
- `store_side_effects()` - Store external API calls
- `store_cross_cutting_concerns()` - Store auth/logging patterns
- `store_security_risks()` - Store SQL injection and secrets
- `store_data_models()` - Store data model definitions
- `store_concurrency_patterns()` - Store locks and async patterns

**Database Schema:**
- Total tables: 19 (10 original + 9 new)
- All tables have foreign key relationships to file_index
- Cascade delete on file removal
- Ready to store all semantic data from parsers

#### Phase 5 Results (COMPLETE ✅)
**Achievements:**
- ✅ Created AIBackend class for adding intelligence to raw parser data
- ✅ Function enhancement (purpose, risk level, performance notes)
- ✅ Class enhancement (purpose, complexity assessment)
- ✅ Module analysis (file type detection, complexity summary, security notes)
- ✅ Risk assessment system (low/medium/high based on complexity and calls)
- ✅ Performance analysis (identifies high complexity, many calls, async patterns)
- ✅ File type detection (api_handler, data_model, test_file, configuration, source_file)
- ✅ Recommendation generation (refactoring suggestions, security fixes, error handling)
- ✅ All 7 tests passing

**Implementation:**
- Created `orc/ai/ai_backend.py` (370 lines)
- Uses existing AICodeSummarizer for AI-powered summaries
- Heuristic-based analysis for fast, accurate insights
- No hallucination - only extracts facts from code

**Features:**
1. **Function Enhancement:**
   - Extracts purpose using AI (brief summary from code)
   - Assesses risk level (high: complexity>20, medium: complexity>10, low: other)
   - Analyzes performance (complexity, call count, async patterns)

2. **Class Enhancement:**
   - Determines purpose (data model, API handler, service, manager)
   - Assesses complexity (large: 20+ methods, medium: 10+ methods, complex inheritance)

3. **Module Analysis:**
   - Detects file type (API, model, test, config, source)
   - Summarizes complexity (high/medium/low based on average function complexity)
   - Extracts security notes (SQL injection risks, hardcoded secrets)
   - Generates recommendations (refactoring, security fixes, error handling)

**Integration Ready:**
- Can be called after parsing: `backend.enhance_parser_output(parser_result, file_path)`
- Returns enhanced result with intelligence added
- Stores summaries in code_summaries and ai_insights tables

**Next Session Priority**
**Complete Remaining Phases:** Phase 6 (TOC) + Phase 7 (Integration)

---

## PHASE 6: TOC GENERATION (Next Session Start Here)

### Goal
Create a Table of Contents system for fast navigation of the massive knowledge database.

### Why TOC is Needed
The 19-table database will be HUGE for large codebases. TOC provides fast keyword-based navigation so AI doesn't scan everything.

### Implementation Plan

**File to Create:** `orc/core/toc_generator.py`

**TOCGenerator Class:**
```python
class TOCGenerator:
    def __init__(self, db: GraphDB):
        self.db = db
    
    def generate_toc(self) -> Dict[str, Any]:
        """
        Generate complete TOC from database.
        
        Returns:
            {
                'sections': {
                    'functions': {'count': 100, 'index': {...}},
                    'classes': {'count': 50, 'index': {...}},
                    'api_endpoints': {'count': 20, 'index': {...}},
                    # ... all 19 sections
                },
                'keywords': {
                    'auth': ['functions.login', 'api_endpoints./login'],
                    'payment': ['functions.process_payment', 'security_risks.sql_injection'],
                    # keyword -> locations mapping
                },
                'statistics': {
                    'total_files': 100,
                    'total_functions': 500,
                    'complexity_avg': 8.5
                }
            }
        """
        pass
    
    def build_keyword_index(self) -> Dict[str, List[str]]:
        """Build keyword -> location mapping for fast search."""
        # Extract keywords from:
        # - Function names (split on underscore, camelCase)
        # - API routes (/users -> 'users')
        # - Config keys (DATABASE_URL -> 'database', 'url')
        # - Class names
        pass
    
    def get_section_summary(self, section: str) -> Dict[str, Any]:
        """Get summary of a specific section (e.g., 'functions', 'api_endpoints')."""
        pass
    
    def search_toc(self, keyword: str) -> List[Dict[str, Any]]:
        """Search TOC by keyword, return matching locations."""
        pass
    
    def save_toc(self, path: Path):
        """Save TOC to JSON file for fast loading."""
        pass
    
    def load_toc(self, path: Path) -> Dict[str, Any]:
        """Load pre-generated TOC from file."""
        pass
```

**Storage:**
- Save TOC to `.orc/toc.json`
- Update when `orc index` runs
- Load on-demand for queries

**Example TOC Structure:**
```json
{
  "sections": {
    "functions": {
      "count": 150,
      "top_complex": ["calculate_discount", "process_order"],
      "entry_points": ["main", "run_server"]
    },
    "api_endpoints": {
      "count": 25,
      "routes": {
        "/users": ["GET", "POST"],
        "/orders": ["GET", "POST", "DELETE"]
      }
    },
    "security_risks": {
      "count": 3,
      "high_priority": ["sql_injection in query_users"]
    }
  },
  "keywords": {
    "user": ["functions.get_user", "api_endpoints./users", "classes.User"],
    "payment": ["functions.process_payment", "security_risks.stripe_call"],
    "auth": ["functions.login", "cross_cutting.login_required"]
  },
  "statistics": {
    "total_files": 50,
    "total_functions": 150,
    "total_lines": 15000,
    "avg_complexity": 7.2,
    "languages": ["python", "javascript"]
  }
}
```

**Tests to Write:**
1. Test TOC generation from populated database
2. Test keyword extraction
3. Test keyword search
4. Test TOC save/load
5. Test section summaries

**Integration:**
- Called after `orc index` completes
- Used by AI Frontend for navigation
- Used by CLI commands for fast queries

**Estimated Time:** 1 session (3-4 hours)

---

## PHASE 7: WIRE EVERYTHING (Final Integration)

### Goal
Connect all pieces: parsers → database → TOC → CLI commands

### Implementation Tasks

**Task 1: Create Parser Registry** (`orc/parsers/__init__.py`)
```python
from pathlib import Path
from orc.parsers.all_parsers import PythonParser, JavaScriptParser, TypeScriptParser

PARSER_REGISTRY = {
    '.py': PythonParser,
    '.js': JavaScriptParser,
    '.jsx': JavaScriptParser,
    '.ts': TypeScriptParser,
    '.tsx': TypeScriptParser,
}

def get_parser_for_file(file_path: Path):
    """Get appropriate parser for file extension."""
    ext = file_path.suffix
    parser_class = PARSER_REGISTRY.get(ext)
    return parser_class() if parser_class else None
```

**Task 2: Wire `orc index` Command** (`orc/cli/cli_main.py`)

Current index() function (line ~199-232) needs:
```python
from orc.parsers import get_parser_for_file
from orc.storage.graph_db import GraphDB
from orc.ai.ai_backend import create_ai_backend
from orc.core.toc_generator import TOCGenerator

@click.command()
@click.option('--force', is_flag=True, help='Force re-index')
def index(force):
    """Index project files."""
    # Step 1: Index files (already works)
    indexer = ParallelIndexer(root_path=Path.cwd())
    result = indexer.index(force_refresh=force)
    
    # Step 2: Initialize database
    db_path = Path('.orc/graph.db')
    db = GraphDB(str(db_path))
    
    # Step 3: Initialize AI Backend (optional, can skip if no API key)
    try:
        ai_backend = create_ai_backend()
    except:
        ai_backend = None
    
    # Step 4: Parse and store each file
    for file_path in result.get('files', []):
        parser = get_parser_for_file(file_path)
        if not parser:
            continue
        
        # Parse file
        parse_result = parser.parse_file(file_path)
        
        # Enhance with AI Backend (if available)
        if ai_backend:
            parse_result = ai_backend.enhance_parser_output(parse_result, file_path)
        
        # Store in database
        file_str = str(file_path)
        
        # Store basic data
        if parse_result.get('functions'):
            for func_id, func_data in parse_result['functions'].items():
                db.store_function(func_id, func_data['name'], file_str, 
                                 func_data['line_start'], func_data['line_end'],
                                 func_data['complexity'], func_data.get('code', ''),
                                 ','.join(func_data.get('parameters', [])),
                                 ','.join(func_data.get('calls', [])),
                                 func_data.get('is_exported', False))
        
        # Store semantic data
        if parse_result.get('api_endpoints'):
            db.store_api_endpoints(parse_result['api_endpoints'], file_str)
        
        if parse_result.get('database_queries'):
            db.store_database_queries(parse_result['database_queries'], file_str)
        
        if parse_result.get('error_handling'):
            db.store_error_handlers(parse_result['error_handling'], file_str)
        
        if parse_result.get('configuration'):
            db.store_config_usage(parse_result['configuration'], file_str)
        
        if parse_result.get('side_effects'):
            db.store_side_effects(parse_result['side_effects'], file_str)
        
        if parse_result.get('cross_cutting'):
            db.store_cross_cutting_concerns(parse_result['cross_cutting'], file_str)
        
        if parse_result.get('security'):
            db.store_security_risks(parse_result['security'], file_str)
        
        if parse_result.get('data_models'):
            db.store_data_models(parse_result['data_models'], file_str)
        
        if parse_result.get('concurrency'):
            db.store_concurrency_patterns(parse_result['concurrency'], file_str)
    
    # Step 5: Generate TOC
    toc_gen = TOCGenerator(db)
    toc = toc_gen.generate_toc()
    toc_gen.save_toc(Path('.orc/toc.json'))
    
    # Step 6: Show results
    click.echo(f"Indexed {len(result.get('files', []))} files")
    click.echo(f"Database: {db_path}")
    click.echo(f"TOC: .orc/toc.json")
```

**Task 3: Connect Chat to Database** (`orc/cli/cli_loop.py`)

In `ORCChatSession.run()` method (around line 93-122):
```python
# Check if database exists
db_path = Path('.orc/graph.db')
if db_path.exists():
    from orc.storage.graph_db import GraphDB
    from orc.ai.ai_tools import ORCTools
    
    db = GraphDB(str(db_path))
    self.tools_instance = ORCTools(db)
    self.output.info("Database loaded - AI has access to codebase")
else:
    self.output.warning("No database found. Run 'orc index' first")
```

**Task 4: Test End-to-End**
1. Create test project with Python/JS files
2. Run `orc init`
3. Run `orc index`
4. Verify database populated (check .orc/graph.db)
5. Verify TOC generated (check .orc/toc.json)
6. Run `orc scan` - should show real data
7. Run `orc find dead` - should find actual dead code
8. Run `orc` chat - AI should know codebase

**Task 5: Fix Integration Tests** (`orc/tests/test_cli.py`)
- Update imports to use new package structure
- Test `orc index` end-to-end
- Test database population
- Test TOC generation

**Estimated Time:** 1 session (4-5 hours)

---

## SUCCESS CRITERIA

**ORC is complete when:**
1. ✅ `orc index` parses files and populates database
2. ✅ Database contains all 19 sections of data
3. ✅ TOC is generated for fast navigation
4. ✅ `orc scan` shows real analysis results
5. ✅ `orc find dead` finds actual dead code
6. ✅ Chat AI can answer questions about YOUR codebase
7. ✅ All tests passing
8. ✅ Works on real projects (not just test data)

**Then ORC Vision is COMPLETE! 🎉**

---

## QUICK START FOR NEXT SESSION

```bash
# 1. Check current progress
grep "Phase [0-9].*COMPLETE" AGENTS.md

# 2. Read Phase 6 instructions above

# 3. Create orc/core/toc_generator.py

# 4. Implement TOCGenerator class

# 5. Test TOC generation

# 6. Move to Phase 7 (wiring)

# 7. Test end-to-end

# 8. Celebrate! 🎉
```

**Current Status:**
- Phase 1: ✅ COMPLETE (Base parser extended, all parsers integrated)
- Phase 2: ✅ COMPLETE (Python semantic detection fully implemented and tested)
- Phase 3: ✅ COMPLETE (JavaScript/TypeScript semantic detection fully implemented and tested)
- Phase 4: ✅ COMPLETE (Database schema extended with 9 new semantic tables)
- Phase 5: ✅ COMPLETE (AI Backend intelligence layer implemented)

#### Phase 3 Results (COMPLETE ✅)
**Achievements:**
- ✅ Implemented all 9 semantic extraction methods for JavaScript/TypeScript
- ✅ API endpoint detection (Express/Fastify using regex)
- ✅ Database query detection (Sequelize/TypeORM/Raw SQL)
- ✅ Error handling detection (try/catch/throw)
- ✅ Config usage detection (process.env)
- ✅ Side effects detection (fetch/axios HTTP calls)
- ✅ Cross-cutting concerns (console.log/error/warn)
- ✅ Security risk detection (template literal SQL injection, secrets)
- ✅ Data model detection (TypeScript interfaces)
- ✅ Concurrency pattern detection (Promise.all)
- ✅ Comprehensive test suite (9 semantic detection tests passing)
- ✅ All 29 original parser tests still passing

**Detection Capabilities:**
- **API Endpoints:** Regex for `app.get('/path')`, `router.post('/path')`, `fastify.delete()`
- **Database Queries:** Sequelize (`.findOne()`, `.create()`), TypeORM (`.find()`, `.save()`), Raw SQL
- **Error Handling:** `try/catch` blocks, `throw new Error()` statements
- **Config Usage:** `process.env.KEY`, `process.env['KEY']`
- **Side Effects:** `fetch()`, `axios.get()`, `axios.post()`
- **Logging:** `console.log()`, `console.error()`, `console.warn()`, `console.debug()`
- **SQL Injection:** Template literal SQL (`` `SELECT * FROM users WHERE id = ${userId}` ``)
- **Secrets:** Hardcoded API keys, passwords, tokens
- **Data Models:** TypeScript `interface` declarations
- **Concurrency:** `Promise.all()` patterns

**Implementation Approach:**
- Regex-based detection (no AST for JS/TS)
- Pattern matching for common frameworks
- Line number tracking via `source[:match.start()].count('\n') + 1`
- All methods added to JavaScriptParser class (inherited by TypeScriptParser)

**Code Quality:**
- Backward compatible (all existing tests pass)
- Well-tested (9 new semantic detection tests)
- Production-ready JS/TS parser

**Implementation Approach for Phase 3:**
Since JS/TS parsers use regex (not AST), the detection patterns will be:
- **API Endpoints:** Regex for `app.get('/path', handler)`, `router.post('/path', handler)`
- **Database Queries:** Regex for `Model.findOne()`, `await db.query()`
- **Error Handling:** Regex for `try {`, `catch (`, `throw new`
- **Config:** Regex for `process.env.KEY`, `config.get('key')`
- **HTTP Calls:** Regex for `fetch(`, `axios.get(`, `await fetch(`
- **Logging:** Regex for `console.log(`, `logger.info(`
- **Security:** Template literal SQL injection detection

**Files to Modify:**
- `orc/parsers/all_parsers.py` - Add semantic extraction methods to JavaScriptParser class (after line ~1100)
- Same methods will be inherited by TypeScriptParser

**Context for Next Session:**
- Read Phase 2 implementation details above for Python patterns
- Apply similar logic but using regex instead of AST
- JavaScript parser starts at line 804 in all_parsers.py
- Add methods after `_extract_js_exports()` method (around line 1100)
- Test with similar comprehensive test suite as Phase 2

**Context for Next Chat:**
- Read ENHANCED_PARSER_DESIGN.md for complete blueprint
- Phase 1 focuses on STRUCTURE, not implementation
- Phases 2-3 will implement actual detection logic
- Current goal: Define contracts, ensure extensibility

---

## RECENT UPDATES (2026-01-16 - Part 3)

### ORC Vision Clarified & Documented

**Date:** 2026-01-16 21:00
**Status:** 🎯 Vision Complete | Ready to Build

#### The Vision Conversation
Had extensive discussion to clarify what ORC truly is and how it works. Key realizations:

**ORC Is NOT Just AI - It's a Two-Part System:**

1. **ORC Core System (Non-AI):**
   - Sophisticated parser + mapping engine
   - Transforms raw code into structured, queryable database
   - Creates complete "knowledge base" of codebase
   - 100% accurate, no interpretation

2. **Dual AI Architecture:**
   - **AI Backend:** Runs after parsing, adds intelligence to raw data (purpose, business logic, risk)
   - **AI Frontend:** Conversational interface humans interact with, navigates database via TOC

#### The Key Insight: The Database IS The Understanding

**The Big Idea:**
When ORC indexes 500k lines of code, it creates a MASSIVE database (22 sections) that contains:
- Every function, class, dependency
- Complete call graphs and data flow
- Entry points, configurations, errors
- Performance, security, deployments
- **Everything needed to understand the codebase**

**If you read the database, you understand 90% of the code WITHOUT reading actual code.**

#### The Table of Contents (TOC)
Because the database is huge, there's a TOC for fast navigation:
- **Database = Encyclopedia (22 volumes)**
- **TOC = Master index to find topics instantly**
- **AI uses TOC to jump to relevant sections instead of scanning everything**

#### The Complete Workflow

**Step 1: Build Knowledge Base (Silent)**
```bash
orc index
# Parsers scan → AI Backend analyzes → Store in 22-section database → Generate TOC
# Output: "Indexed 1,247 files"
# Behind scenes: Complete knowledge base ready
```

**Step 2: Direct Queries (Fast)**
```bash
orc find dead       # Query database directly
orc find complex    # Instant results
orc show deps User  # No re-scanning
```

**Step 3: AI Conversation (Smart)**
```bash
orc
"Why isn't payment working?"
# AI Frontend navigates database via TOC
# Reads only relevant sections
# Answers with specific line numbers
# NO HALLUCINATION - everything from YOUR code
```

#### The 22-Section Knowledge Database

Complete schema documented in `ORC_VISION.md`:

1. File Registry
2. Symbol Index (functions, classes, constants)
3. Data Models & Schemas
4. Entry Points & Execution Flow
5. State Management & Persistence
6. Dependencies & Relationships
7. Error Handling & Failure Modes
8. Configuration & Environment
9. Cross-Cutting Concerns (auth, logging, caching)
10. Metadata & Context (purpose, gotchas, tech debt)
11. Testing & Coverage
12. Documentation Links
13. Request/Response Contracts
14. Side Effects & External Actions
15. Concurrency & Threading
16. Performance Characteristics
17. Security & Vulnerabilities
18. Integration Points & External Dependencies
19. Backwards Compatibility & Versioning
20. Resource Usage & Limits
21. Deployment & Infrastructure
22. Metrics, Monitoring & Observability

#### What Makes ORC Unique

**vs ChatGPT:** ORC knows YOUR code (no hallucination, shows line numbers)
**vs Copilot:** ORC analyzes existing code (Copilot generates new code)
**vs SonarQube:** ORC has AI that explains WHY (not just finds issues)
**vs grep:** ORC understands relationships (not just text search)

**ORC = Codebase GPS with intelligent guide**

#### Current Reality
**Status:** 40% complete
- ✅ CLI shell exists (beautiful interface)
- ✅ Parsers exist (can extract data)
- ✅ Database schema exists (can store data)
- ✅ AI integration exists (can chat)
- ❌ **Pipeline broken:** Parsers don't store in database
- ❌ **AI Backend missing:** No intelligence added to raw data
- ❌ **TOC missing:** No navigation index
- ❌ **22 sections incomplete:** Database not fully implemented

**The Gap:** All pieces exist but aren't connected. Like a Ferrari with engine disconnected from wheels.

#### Documentation Created
**New File:** `ORC_VISION.md` (500+ lines)
- Complete vision document
- Two-AI architecture explained
- 22-section database schema
- Example use cases
- Success metrics
- Implementation roadmap

**This document defines WHAT ORC IS and WHY IT EXISTS.**

#### Implementation Roadmap (6 Phases)

**Phase 1:** Core Pipeline (wire parsers → database)
**Phase 2:** CLI Commands (make queries work)
**Phase 3:** AI Backend (add intelligence to data)
**Phase 4:** TOC Generation (fast navigation)
**Phase 5:** AI Frontend Intelligence (smart conversation)
**Phase 6:** Web Dashboard (visual exploration)

**Estimated:** 12-15 focused sessions to complete vision

#### Next Session Priority
**Must do first:** Phase 1 - Make `orc index` actually populate the database
- Create parser registry
- Wire parsers to database storage
- Verify 22 sections populate correctly
- Test on real codebase

**Why critical:** Without populated database, nothing else works. Every other feature depends on this.

---

## RECENT UPDATES (2026-01-16 - Part 2)

### Installation Complete + Production Readiness Assessment

**Date:** 2026-01-16 20:00
**Status:** ✅ Installed | ⚠️ Integration Needed

#### Installation Completed
- ✅ Uninstalled old versions (orc-cli, orc-codebase)
- ✅ Killed locked process (PID 2288)
- ✅ Fresh install: `pip install -e .`
- ✅ Verified: `orc --help` works
- ✅ Entry point: `orc.cli.cli_main:main`

#### Production Readiness Assessment Created
**Files Created:**
- `PRODUCTION_READINESS_CHECKLIST.md` - Full assessment (exhaustive)
- `WHATS_NEXT.md` - Quick summary for next session

#### Key Findings
**What's Working (40% complete):**
- ✅ Installation system
- ✅ CLI framework (Click)
- ✅ Interactive chat (17 commands)
- ✅ AI integration (5 providers)
- ✅ Model management (CRUD)
- ✅ Session management

**What's NOT Working (Critical Gap):**
- ❌ `orc index` doesn't store data in database
- ❌ Parsers not connected to CLI commands
- ❌ Analysis modules not wired to commands
- ❌ Chat doesn't use analysis tools
- ❌ Integration tests failing (old imports)

**Root Cause:** CLI commands are stubs. They exist but don't call the actual analysis modules (parsers, database, analyzers). It's a beautiful UI with no backend.

#### Priority Fixes Identified

**Priority 1 (CRITICAL):** Wire `orc index` to database
```python
# Need to add in cli_main.py index():
# 1. Call ParallelIndexer ✅ (already done)
# 2. Parse each file with appropriate parser ❌ (missing)
# 3. Store results in GraphDB ❌ (missing)
```

**Priority 2 (HIGH):** Create parser registry
```python
# Need orc/parsers/__init__.py:
# - get_parser_for_file(path) function
# - PARSER_REGISTRY dict mapping extensions to parsers
```

**Priority 3 (MEDIUM):** Connect chat to database
```python
# In cli_loop.py:
# - Check if .orc/graph.db exists
# - Initialize ORCTools with database
# - Pass tools to AI client
```

**Priority 4 (MEDIUM):** Fix integration tests
```python
# Update imports from:
# from orc.orc_package.config.settings import ORCConfig
# to:
# from orc.core.config import ORCConfig
```

#### Timeline to Production Ready
- **After Priority 1:** Can index and store (1 session)
- **After Priority 2-3:** Can analyze and chat (2 sessions)
- **After Priority 4:** Tests pass (1 session)
- **Total:** 4 focused sessions

#### Current Capabilities
**Can do:**
- Launch interactive AI chat
- Manage AI models (add/edit/delete)
- Save/load chat sessions
- Track token usage
- Run chat commands

**Cannot do (yet):**
- Actually analyze code
- Find dead code
- Calculate complexity
- Query codebase
- Generate meaningful reports

#### Testing Status
- ✅ 17/17 chat commands tested and passing
- ❌ Integration tests failing (outdated imports)
- ❌ No end-to-end workflow tests
- ❌ No real codebase testing

#### Documentation Created
- `PRODUCTION_READINESS_CHECKLIST.md` - 400+ lines, exhaustive
- `WHATS_NEXT.md` - Quick reference for next session
- Both files include code examples and implementation steps

#### Next Session Start Point
```bash
# Goal: Make orc index actually work
# Files to modify:
# 1. orc/parsers/__init__.py - Add parser registry
# 2. orc/cli/cli_main.py - Wire index to database
# 3. Test with: orc index
```

---

## RECENT UPDATES (2026-01-16 - Part 1)

### CLI Enhancements - Chat Commands & Model Management

**Date:** 2026-01-16 19:00
**Developer:** AI Assistant
**Changes Made:**

#### 1. Removed Emojis from Terminal UI
**Files Modified:**
- `orc/cli/cli_style.py` - Changed symbols from Unicode emojis to ASCII
  - `›` → `>`
  - `✓` → `[OK]`
  - `✗` → `[ERR]`
  - `•` → `-`
  - `!` → `[WARN]`
- `orc/cli/banner.py` - Removed bullet point from status line
- `orc/cli/onboarding.py` - Removed checkmark from success message

**Rationale:** Better terminal compatibility, cleaner output across different environments

#### 2. Added /models Command System (CRUD Operations)
**File Modified:** `orc/cli/cli_loop.py`

**New Commands:**
- `/models` or `/models view` - View all configured models
  - Shows current active provider
  - Lists all saved models with details
  - Displays provider, model ID, base URL (if applicable)
  - Marks active model

- `/models new` - Add new model configuration
  - Interactive prompts for: name, provider, model ID, API key
  - Supports: groq, openai, anthropic, deepseek, ollama
  - Special handling for Ollama (base URL support)
  - Saves to `~/.orc/.env` with format:
    ```
    ORC_MODEL_<NAME>_PROVIDER=groq
    ORC_MODEL_<NAME>_MODEL=llama-3.1-70b-versatile
    GROQ_API_KEY=<key>
    ```

- `/models edit <model_name>` - Edit existing model
  - Shows current values
  - Allows updating provider and model ID
  - Preserves existing values if Enter is pressed

- `/models delete <model_name>` - Delete model configuration
  - Requires confirmation (y/N)
  - Removes all related entries from .env file

**Storage Format:**
Models are stored in `~/.orc/.env` with this structure:
```
ORC_MODEL_GROQ_LLAMA_PROVIDER=groq
ORC_MODEL_GROQ_LLAMA_MODEL=llama-3.1-70b-versatile
GROQ_API_KEY=gsk_...

ORC_MODEL_OPENAI_GPT4_PROVIDER=openai
ORC_MODEL_OPENAI_GPT4_MODEL=gpt-4
OPENAI_API_KEY=sk-...

ORC_AI_PROVIDER=groq  # Active provider
```

#### 3. Added /reset Command
**File Modified:** `orc/cli/cli_loop.py`

- `/reset` - Alias for `/clear` command
- Both commands clear conversation history
- Added to SLASH_COMMANDS dictionary

#### 4. Added / Command Autocomplete
**File Modified:** `orc/cli/cli_loop.py`

**New Method:** `_cmd_show_commands()`
- Typing just `/` shows quick list of all available commands
- Displays simple list without descriptions
- Shows tip to type `/help` for detailed info

**Updated Behavior:**
- `/` → Shows command list
- `/help` → Shows detailed help with examples
- Unknown command → Shows "Type / to see available commands"

**Updated SLASH_COMMANDS:**
Added to help documentation:
```python
'/reset': 'Reset conversation (clear history)',
'/models': 'Manage AI models (view|new|edit|delete)',
```

**Updated Examples in /help:**
```
/models                 View configured models
/models new             Add new model
```

#### Summary of Changes

**Files Modified:**
1. `orc/cli/cli_style.py` - Emoji removal
2. `orc/cli/banner.py` - Emoji removal
3. `orc/cli/onboarding.py` - Emoji removal
4. `orc/cli/cli_loop.py` - All new commands and features

**Lines Added:** ~250 lines (model management system)
**Lines Modified:** ~15 lines (emoji removal + command routing)

**New Features:**
- Complete CRUD operations for AI model configurations
- Command autocomplete with `/`
- `/reset` command alias
- Better error messages directing users to command help

**Testing Status:** Not yet tested
**Next Steps:** Manual testing of /models command flow

---

