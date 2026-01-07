# ORC v2.0: Codebase Intelligence & Context Compression System
## Complete Architecture & Implementation Guide

---

## 🎯 Project Vision

**ORC (Optimization & Refactoring Catalyst)** is a codebase intelligence system that creates compressed, queryable maps of massive codebases, enabling AI tools to work effectively without context limits while providing developers with powerful analysis and optimization capabilities.

### Core Innovation: The "Context Compression Engine"
ORC transforms 100,000+ line codebases into intelligent, queryable indexes that allow AI assistants to access exactly the code they need without reading everything.

---

## 🏗️ System Architecture

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
│  │   • Vector Store (Embeddings - Optional)           │    │
│  │   • Graph Database (NetworkX → Serialized)         │    │
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

---

## 📁 File Structure

```
orc/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── setup.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # Configuration management
│   ├── patterns.yaml            # Known patterns/antipatterns
│   └── optimization_rules.yaml  # Optimization rule definitions
│
├── core/
│   ├── __init__.py
│   ├── indexer.py               # Multi-language dispatcher
│   ├── graph_builder.py         # Dependency & call graph construction
│   ├── compressor.py            # [NEW] Context compression algorithm
│   └── cache_manager.py         # [NEW] Intelligent caching
│
├── parsers/                     # [NEW] Language-specific parsers
│   ├── __init__.py
│   ├── python_parser.py         # Python AST parser
│   ├── javascript_parser.py     # JavaScript/Node parser
│   ├── typescript_parser.py     # TypeScript parser
│   ├── react_parser.py          # React/JSX parser
│   ├── html_css_parser.py       # HTML/CSS static analyzer
│   ├── django_parser.py         # Django-specific patterns
│   ├── fastapi_parser.py        # FastAPI-specific patterns
│   └── base_parser.py           # Abstract base parser
│
├── analysis/
│   ├── __init__.py
│   ├── dead_code.py             # Dead code detection
│   ├── complexity.py            # [NEW] Complexity analysis (O notation)
│   ├── patterns.py              # Pattern matching & duplication
│   ├── dependencies.py          # Circular deps & coupling
│   ├── optimizer.py             # [NEW] Optimization suggestions
│   ├── security.py              # [NEW] Basic security checks
│   └── metrics.py               # Code quality metrics
│
├── storage/
│   ├── __init__.py
│   ├── graph_db.py              # Graph storage (SQLite + NetworkX)
│   ├── vector_store.py          # [NEW] Vector embeddings storage
│   ├── cache.py                 # Fast lookup cache
│   └── migrations/              # [NEW] Database migrations
│       └── v1_initial.sql
│
├── context/                     # [NEW] Context compression & AI integration
│   ├── __init__.py
│   ├── builder.py               # Context assembly for AI
│   ├── query_parser.py          # Parse natural language queries
│   ├── relevance_ranker.py      # Rank code by relevance
│   ├── embeddings.py            # Semantic embeddings (optional)
│   └── llm_client.py            # LLM API client (Claude/OpenAI)
│
├── optimization/                # [NEW] Optimization engine
│   ├── __init__.py
│   ├── algorithm_detector.py    # Detect algorithmic patterns
│   ├── suggester.py             # Generate optimization suggestions
│   ├── code_generator.py        # Generate optimized code snippets
│   └── rules/
│       ├── python_rules.py      # Python-specific optimizations
│       ├── javascript_rules.py  # JS-specific optimizations
│       └── react_rules.py       # React-specific optimizations
│
├── api/                         # [NEW] REST API for AI tools
│   ├── __init__.py
│   ├── server.py                # FastAPI application
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── context.py           # Context endpoints
│   │   ├── analysis.py          # Analysis endpoints
│   │   ├── optimization.py      # Optimization endpoints
│   │   └── query.py             # Query endpoints
│   ├── middleware.py            # Auth, rate limiting
│   └── schemas.py               # Pydantic models
│
├── cli/
│   ├── __init__.py
│   ├── commands.py              # CLI command definitions
│   ├── visualizer.py            # Terminal visualization
│   └── progress.py              # [NEW] Progress indicators
│
├── web/                         # [NEW] Web dashboard (Enterprise)
│   ├── __init__.py
│   ├── app.py                   # Flask/FastAPI web app
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── analysis.py
│   │   └── api_proxy.py
│   ├── static/
│   │   ├── css/
│   │   │   └── dashboard.css
│   │   └── js/
│   │       ├── graph-viz.js
│   │       └── metrics.js
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── graph.html
│       ├── complexity.html
│       └── recommendations.html
│
├── integrations/                # [NEW] External integrations
│   ├── __init__.py
│   ├── git.py                   # Git integration (PR analysis)
│   ├── ci_cd.py                 # CI/CD helpers
│   ├── vscode/                  # VS Code extension
│   └── cursor/                  # Cursor IDE integration
│
├── tests/
│   ├── __init__.py
│   ├── test_parsers.py          # [NEW]
│   ├── test_indexer.py
│   ├── test_analyzer.py
│   ├── test_graph.py
│   ├── test_compression.py      # [NEW]
│   ├── test_api.py              # [NEW]
│   ├── test_optimization.py     # [NEW]
│   └── fixtures/
│       ├── sample_python/
│       ├── sample_javascript/
│       ├── sample_react/
│       └── sample_django/
│
├── scripts/
│   ├── benchmark.py             # Performance benchmarking
│   ├── migrate.py               # Database migrations
│   ├── sample_data.py           # [NEW] Generate test data
│   └── deploy.py                # [NEW] Deployment scripts
│
└── docs/                        # [NEW] Documentation
    ├── getting_started.md
    ├── api_reference.md
    ├── architecture.md
    ├── optimization_rules.md
    ├── contributing.md
    └── examples/
        ├── basic_usage.md
        ├── ai_integration.md
        └── enterprise_setup.md
```

---

## 🧠 The Context Compression Algorithm (Core Innovation)

### The Problem
- AI tools have context limits (200K tokens ≈ 50K lines)
- Large codebases are 100K+ lines
- Reading entire codebase per query is slow and expensive

### The Solution: ORC's Compression Recipe

```python
"""
ORC Context Compression Algorithm
Transforms 100K lines → 50MB queryable database
"""

# Step 1: Parse & Extract
for file in codebase:
    ast = parse(file)
    extract:
        - Functions (name, params, return type, complexity)
        - Classes (methods, inheritance)
        - Imports/Exports
        - Variables (scope, type, usage)
        - Comments/Docstrings

# Step 2: Build Relationships
graph = {
    'calls': {},      # function_a calls function_b
    'imports': {},    # module_a imports module_b
    'dataflow': {},   # variable_x flows to function_y
    'inheritance': {} # class_a extends class_b
}

# Step 3: Generate Metadata
for function in all_functions:
    metadata[function] = {
        'complexity': calculate_complexity(function),  # O(n), O(n²)
        'summary': extract_docstring(function),
        'calls': find_calls(function),
        'called_by': find_callers(function),
        'loc': count_lines(function),
        'embedding': None  # Optional: semantic vector
    }

# Step 4: Compress & Store
database = {
    'functions': metadata,
    'graph': serialize(graph),
    'index': create_search_index(metadata),
    'embeddings': None  # Optional: for semantic search
}

# Result: 100K lines → 50MB database
# Query time: <100ms
# AI gets exactly what it needs, not everything
```

### Query Flow Example

```python
# AI Tool asks: "Show me authentication code"

1. Parse query → Extract intent: "authentication"
2. Search index → Find relevant functions:
   - login(), authenticate(), verify_token()
3. Get dependencies → What these functions call/need
4. Rank by relevance → Score each function
5. Build minimal context → Return top 10 functions (500 lines)
   Include: function code + dependencies + usage examples
6. Return to AI → AI now has perfect context!

# Instead of 100K lines, AI gets 500 relevant lines
# 200x compression!
```

---

## 🔧 Core Components Implementation

### 1. Multi-Language Indexer (`core/indexer.py`)

```python
"""
Multi-Language Indexer Dispatcher
"""
from pathlib import Path
from typing import Dict, List
from parsers import (
    PythonParser, JavaScriptParser, TypeScriptParser,
    ReactParser, HTMLCSSParser
)

class MultiLanguageIndexer:
    """Coordinate parsing across multiple languages"""
    
    def __init__(self, config: 'ORCConfig'):
        self.config = config
        self.parsers = {
            '.py': PythonParser(),
            '.js': JavaScriptParser(),
            '.ts': TypeScriptParser(),
            '.jsx': ReactParser(),
            '.tsx': ReactParser(),
            '.html': HTMLCSSParser(),
            '.css': HTMLCSSParser()
        }
    
    def index_codebase(self, root_path: Path) -> Dict:
        """Index entire codebase across all supported languages"""
        index = {
            'files': {},
            'functions': {},
            'classes': {},
            'imports': {},
            'exports': {}
        }
        
        for file_path in self._discover_files(root_path):
            ext = file_path.suffix
            if ext in self.parsers:
                parser = self.parsers[ext]
                file_data = parser.parse_file(file_path)
                self._merge_into_index(index, file_data)
        
        return index
    
    def _discover_files(self, root: Path) -> List[Path]:
        """Find all relevant files, respecting ignore patterns"""
        files = []
        for pattern in self.config.file_extensions:
            for file in root.rglob(f'*{pattern}'):
                if not self._should_ignore(file):
                    files.append(file)
        return files
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path matches ignore patterns"""
        return any(path.match(pattern) 
                  for pattern in self.config.ignore_patterns)
```

### 2. Context Builder (`context/builder.py`)

```python
"""
Context Builder for AI Integration
Assembles minimal relevant code for AI queries
"""
from typing import List, Dict, Optional
import numpy as np

class ContextBuilder:
    """Build compressed context for AI tools"""
    
    def __init__(self, index: Dict, graph: 'DependencyGraph'):
        self.index = index
        self.graph = graph
        self.embeddings = None  # Optional
    
    def build_context(self, query: str, max_tokens: int = 8000) -> Dict:
        """
        Build minimal context for a query
        
        Args:
            query: Natural language query or keyword search
            max_tokens: Maximum tokens to return
        
        Returns:
            Compressed context with relevant code
        """
        # Step 1: Find relevant functions/files
        relevant_items = self._find_relevant(query)
        
        # Step 2: Rank by relevance
        ranked = self._rank_by_relevance(relevant_items, query)
        
        # Step 3: Include dependencies
        with_deps = self._include_dependencies(ranked[:10])
        
        # Step 4: Assemble context
        context = self._assemble_context(with_deps, max_tokens)
        
        return context
    
    def _find_relevant(self, query: str) -> List[Dict]:
        """Find relevant code using keyword + optional semantic search"""
        results = []
        
        # Keyword search
        keywords = query.lower().split()
        for func_id, func_data in self.index['functions'].items():
            score = self._keyword_match(func_data, keywords)
            if score > 0:
                results.append({
                    'id': func_id,
                    'data': func_data,
                    'score': score
                })
        
        # Optional: Semantic search with embeddings
        if self.embeddings:
            semantic_results = self._semantic_search(query)
            results = self._merge_results(results, semantic_results)
        
        return results
    
    def _rank_by_relevance(self, items: List[Dict], query: str) -> List[Dict]:
        """Rank items by relevance score"""
        return sorted(items, key=lambda x: x['score'], reverse=True)
    
    def _include_dependencies(self, items: List[Dict]) -> List[Dict]:
        """Include necessary dependencies for each item"""
        enhanced = []
        for item in items:
            deps = self.graph.get_dependencies(item['id'])
            enhanced.append({
                **item,
                'dependencies': deps
            })
        return enhanced
    
    def _assemble_context(self, items: List[Dict], max_tokens: int) -> Dict:
        """Assemble final context within token limit"""
        context = {
            'query': items[0]['id'] if items else None,
            'files': [],
            'functions': [],
            'summary': '',
            'total_tokens': 0
        }
        
        tokens_used = 0
        for item in items:
            item_tokens = self._estimate_tokens(item)
            if tokens_used + item_tokens <= max_tokens:
                context['functions'].append(item['data'])
                tokens_used += item_tokens
            else:
                break
        
        context['total_tokens'] = tokens_used
        return context
    
    def _estimate_tokens(self, item: Dict) -> int:
        """Estimate tokens for an item"""
        # Rough estimate: 1 token ≈ 4 characters
        code = item['data'].get('code', '')
        return len(code) // 4
```

### 3. Complexity Analyzer (`analysis/complexity.py`)

```python
"""
Algorithm Complexity Analysis
Detects time/space complexity patterns
"""
import ast
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ComplexityReport:
    """Complexity analysis result"""
    function: str
    file: str
    time_complexity: str  # "O(n)", "O(n²)", etc.
    space_complexity: str
    hotspot: bool  # Called frequently + complex
    suggestion: str
    estimated_improvement: float

class ComplexityAnalyzer:
    """Analyze algorithmic complexity"""
    
    def __init__(self, index: Dict, graph: 'DependencyGraph'):
        self.index = index
        self.graph = graph
    
    def analyze_all(self) -> List[ComplexityReport]:
        """Analyze complexity of all functions"""
        reports = []
        for func_id, func_data in self.index['functions'].items():
            report = self.analyze_function(func_id, func_data)
            if report.time_complexity in ['O(n²)', 'O(n³)', 'O(2^n)']:
                reports.append(report)
        return sorted(reports, key=lambda r: r.estimated_improvement, reverse=True)
    
    def analyze_function(self, func_id: str, func_data: Dict) -> ComplexityReport:
        """Analyze single function complexity"""
        code = func_data.get('code', '')
        tree = ast.parse(code)
        
        # Detect time complexity
        time_complexity = self._detect_time_complexity(tree)
        
        # Detect space complexity
        space_complexity = self._detect_space_complexity(tree)
        
        # Check if hotspot (called frequently)
        call_count = len(self.graph.get_callers(func_id))
        is_hotspot = call_count > 10 and time_complexity in ['O(n²)', 'O(n³)']
        
        # Generate suggestion
        suggestion = self._generate_suggestion(time_complexity, tree)
        
        # Estimate improvement
        improvement = self._estimate_improvement(time_complexity, call_count)
        
        return ComplexityReport(
            function=func_id.split('::')[-1],
            file=func_id.split('::')[0],
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            hotspot=is_hotspot,
            suggestion=suggestion,
            estimated_improvement=improvement
        )
    
    def _detect_time_complexity(self, tree: ast.AST) -> str:
        """Detect time complexity from AST"""
        loop_depth = 0
        max_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loop_depth += 1
                max_depth = max(max_depth, loop_depth)
            elif isinstance(node, ast.FunctionDef):
                loop_depth = 0
        
        # Simple heuristic
        if max_depth == 0:
            return "O(1)"
        elif max_depth == 1:
            # Check for nested operations
            if self._has_nested_operations(tree):
                return "O(n log n)"
            return "O(n)"
        elif max_depth == 2:
            return "O(n²)"
        elif max_depth >= 3:
            return "O(n³)"
        
        return "O(n)"
    
    def _detect_space_complexity(self, tree: ast.AST) -> str:
        """Detect space complexity"""
        # Check for large data structures being created
        for node in ast.walk(tree):
            if isinstance(node, ast.List) or isinstance(node, ast.Dict):
                return "O(n)"
        return "O(1)"
    
    def _has_nested_operations(self, tree: ast.AST) -> bool:
        """Check for operations like sorting inside loops"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    if node.func.id in ['sorted', 'sort']:
                        return True
        return False
    
    def _generate_suggestion(self, complexity: str, tree: ast.AST) -> str:
        """Generate optimization suggestion"""
        suggestions = {
            "O(n²)": "Consider using hash tables or sets for O(1) lookups instead of nested loops",
            "O(n³)": "Break down into smaller problems or use dynamic programming",
            "O(2^n)": "Use memoization or dynamic programming to reduce exponential complexity"
        }
        return suggestions.get(complexity, "No optimization needed")
    
    def _estimate_improvement(self, complexity: str, call_count: int) -> float:
        """Estimate performance improvement potential"""
        impact = {
            "O(n²)": 0.90,
            "O(n³)": 0.95,
            "O(2^n)": 0.99
        }
        base_impact = impact.get(complexity, 0.0)
        return base_impact * min(call_count / 100, 1.0)
```

### 4. REST API (`api/server.py`)

```python
"""
FastAPI REST API for AI Tools Integration
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn

app = FastAPI(title="ORC API", version="2.0.0")

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ContextQuery(BaseModel):
    query: str
    max_tokens: int = 8000
    include_dependencies: bool = True

class ContextResponse(BaseModel):
    query: str
    files: List[str]
    functions: List[Dict]
    total_tokens: int
    summary: str

class OptimizationRequest(BaseModel):
    file: str
    function: Optional[str] = None
    code: Optional[str] = None

class OptimizationResponse(BaseModel):
    current_complexity: str
    suggested_complexity: str
    suggestion: str
    optimized_code: Optional[str]
    estimated_improvement: float

class DeadCodeResponse(BaseModel):
    unused_functions: List[Dict]
    unused_files: List[str]
    estimated_lines_saved: int

# API Endpoints
@app.post("/api/context", response_model=ContextResponse)
async def get_context(query: ContextQuery):
    """
    Get compressed context for AI query
    
    This is the main endpoint AI tools use to get relevant code
    """
    try:
        context_builder = get_context_builder()
        context = context_builder.build_context(
            query.query,
            max_tokens=query.max_tokens
        )
        return ContextResponse(**context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_code(request: OptimizationRequest):
    """Get optimization suggestions for code"""
    try:
        optimizer = get_optimizer()
        result = optimizer.analyze_and_suggest(
            file=request.file,
            function=request.function,
            code=request.code
        )
        return OptimizationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deadcode", response_model=DeadCodeResponse)
async def get_dead_code():
    """Get dead code analysis"""
    try:
        analyzer = get_dead_code_analyzer()
        report = analyzer.analyze()
        return DeadCodeResponse(
            unused_functions=report.unused_functions,
            unused_files=report.unused_files,
            estimated_lines_saved=report.estimated_lines_saved
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/impact")
async def get_impact_analysis(file: str, function: str):
    """Analyze impact of changing/deleting a function"""
    try:
        graph = get_dependency_graph()
        func_id = f"{file}::{function}"
        
        callers = graph.get_callers(func_id)
        dependencies = graph.get_dependencies(func_id)
        
        return {
            "function": function,
            "file": file,
            "called_by": callers,
            "depends_on": dependencies,
            "impact_score": len(callers) * 10,
            "risk_level": "high" if len(callers) > 10 else "low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_codebase(query: str):
    """Natural language query of codebase"""
    try:
        query_engine = get_query_engine()
        results = query_engine.search(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

# Dependency injection helpers
def get_context_builder():
    """Get ContextBuilder instance"""
    # Load from global state or create new
    pass

def get_optimizer():
    """Get Optimizer instance"""
    pass

def get_dead_code_analyzer():
    """Get DeadCodeAnalyzer instance"""
    pass

def get_dependency_graph():
    """Get DependencyGraph instance"""
    pass

def get_query_engine():
    """Get QueryEngine instance"""
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🎮 CLI Commands

### Basic Usage

```bash
# Index a codebase
orc index /path/to/project
# → Creates .orc/index.db

# Analyze for issues
orc analyze
# → Shows dead code, complexity hotspots, optimization opportunities

# Find dead code
orc deadcode
# → Lists unused functions, files, imports

# Check complexity
orc complexity
# → Shows functions with O(n²), O(n³) etc.

# Get optimization suggestions
orc optimize
# → Suggests algorithmic improvements

# Query codebase (natural language or keywords)
orc query "authentication code"
# → Returns relevant files/functions

# Check impact of changes
orc impact src/auth.py:login
# → Shows what depends on this function

# Run in CI/CD
orc check --fail-on-deadcode --max-complexity=O(n²)
# → Exit code 1 if issues found

# Start API server
orc serve --port 8000
# → Starts REST API for AI tools

# Export report
orc report --format json --output report.json
# → Generates JSON/HTML/Markdown report
```

### Advanced Usage

```bash
# Index with custom config
orc index --config .orcrc --ignore "tests/*,*.min.js"

# Analyze specific files
orc analyze src/payments/*.py

# Watch mode (re-index on changes)
orc watch

# Compare branches (git integration)
orc diff main..feature-branch
# → Shows complexity changes between branches

# Integration with AI tools
curl http://localhost:8000/api/context?query="payment processing"
# → AI tools query ORC for context
```

---

## 🔍 Dead Code Detection Algorithm

### How ORC Finds Unused Code

```python
"""
Dead Code Detection Algorithm
Finds unused functions, imports, files
"""

class DeadCodeDetector:
    """Detect unreachable/unused code"""
    
    def detect(self, index: Dict, graph: 'DependencyGraph') -> 'DeadCodeReport':
        """
        Multi-phase dead code detection:
        
        1. Find entry points (main, __init__, exports, routes)
        2. Traverse graph from entry points
        3. Mark all reachable code
        4. Everything unmarked = dead code
        """
        
        # Phase 1: Identify entry points
        entry_points = self._find_entry_points(index)
        # Examples: main(), if __name__ == "__main__", @app.route()
        
        # Phase 2: Mark reachable code (BFS/DFS)
        reachable = set()
        to_visit = list(entry_points)
        
        while to_visit:
            current = to_visit.pop()
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Add all functions this calls
            calls = graph.get_callees(current)
            to_visit.extend(calls)
            
            # Add all imports this uses
            imports = graph.get_imports(current)
            to_visit.extend(imports)
        
        # Phase 3: Find dead code
        all_functions = set(index['functions'].keys())
        dead_functions = all_functions - reachable
        
        # Phase 4: Find dead files (all functions in file are dead)
        dead_files = self._find_dead_files(dead_functions, index)
        
        # Phase 5: Find unused imports
        unused_imports = self._find_unused_imports(index, graph)
        
        return DeadCodeReport(
            unused_functions=list(dead_functions),
            unused_files=dead_files,
            unused_imports=unused_imports,
            estimated_lines_saved=self._count_lines(dead_functions, index)
        )
    
    def _find_entry_points(self, index: Dict) -> List[str]:
        """Find entry points in codebase"""
        entry_points = []
        
        for func_id, func_data in index['functions'].items():
            # Python entry points
            if func_data.get('name') in ['main', '__main__']:
                entry_points.append(func_id)
            
            # Web framework routes
            if any(d in func_data.get('decorators', []) 
                   for d in ['@app.route', '@api.get', '@api.post']):
                entry_points.append(func_id)
            
            # Exported functions
            if func_data.get('exported', False):
                entry_points.append(func_id)
            
            # CLI commands
            if '@click.command' in func_data.get('decorators', []):
                entry_points.append(func_id)
        
        return entry_points
    
    def _find_dead_files(self, dead_functions: Set[str], index: Dict) -> List[str]:
        """Find files where ALL functions are dead"""
        file_function_map = {}
        
        for func_id in index['functions'].keys():
            file = func_id.split('::')[0]
            if file not in file_function_map:
                file_function_map[file] = []
            file_function_map[file].append(func_id)
        
        dead_files = []
        for file, functions in file_function_map.items():
            if all(f in dead_functions for f in functions):
                dead_files.append(file)
        
        return dead_files
    
    def _find_unused_imports(self, index: Dict, graph: 'DependencyGraph') -> List[Dict]:
        """Find imports that are never used"""
        unused = []
        
        for file, imports in index['imports'].items():
            for imp in imports:
                if not graph.is_import_used(file, imp):
                    unused.append({
                        'file': file,
                        'import': imp,
                        'line': imp.get('line', 0)
                    })
        
        return unused
```

---

## 💾 Storage & Database Schema

### SQLite Schema (Primary Storage)

```sql
-- Main index database (.orc/index.db)

-- Files table
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    language TEXT NOT NULL,
    size INTEGER,
    lines_of_code INTEGER,
    last_modified TIMESTAMP,
    hash TEXT,  -- Content hash for change detection
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Functions table
CREATE TABLE functions (
    id INTEGER PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    name TEXT NOT NULL,
    qualified_name TEXT UNIQUE,  -- "file.py::ClassName::method_name"
    start_line INTEGER,
    end_line INTEGER,
    complexity_score REAL,
    time_complexity TEXT,  -- "O(n)", "O(n²)", etc.
    space_complexity TEXT,
    is_async BOOLEAN,
    is_exported BOOLEAN,
    docstring TEXT,
    signature TEXT,  -- "def func(a: int, b: str) -> bool"
    code_hash TEXT,
    UNIQUE(file_id, name, start_line)
);

-- Classes table
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    name TEXT NOT NULL,
    qualified_name TEXT UNIQUE,
    start_line INTEGER,
    end_line INTEGER,
    base_classes TEXT,  -- JSON array
    is_abstract BOOLEAN
);

-- Imports table
CREATE TABLE imports (
    id INTEGER PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    module TEXT NOT NULL,
    imported_names TEXT,  -- JSON array
    alias TEXT,
    is_used BOOLEAN DEFAULT FALSE,
    line INTEGER
);

-- Call graph edges
CREATE TABLE call_edges (
    id INTEGER PRIMARY KEY,
    caller_id INTEGER REFERENCES functions(id),
    callee_id INTEGER REFERENCES functions(id),
    call_count INTEGER DEFAULT 1,
    UNIQUE(caller_id, callee_id)
);

-- Import dependencies
CREATE TABLE dependency_edges (
    id INTEGER PRIMARY KEY,
    source_file_id INTEGER REFERENCES files(id),
    target_file_id INTEGER REFERENCES files(id),
    import_type TEXT,  -- "import", "from_import"
    UNIQUE(source_file_id, target_file_id)
);

-- Metrics table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    entity_type TEXT,  -- "function", "class", "file"
    entity_id INTEGER,
    metric_name TEXT,
    metric_value REAL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast queries
CREATE INDEX idx_functions_file ON functions(file_id);
CREATE INDEX idx_functions_name ON functions(name);
CREATE INDEX idx_functions_complexity ON functions(complexity_score);
CREATE INDEX idx_call_edges_caller ON call_edges(caller_id);
CREATE INDEX idx_call_edges_callee ON call_edges(callee_id);
CREATE INDEX idx_imports_file ON imports(file_id);
CREATE INDEX idx_imports_module ON imports(module);
```

### Vector Store Schema (Optional - for Semantic Search)

```python
"""
Vector embeddings stored separately
Uses FAISS or ChromaDB for similarity search
"""

# Structure:
{
    "function_id": "src/auth.py::login",
    "embedding": [0.123, 0.456, ...],  # 384-dim vector
    "metadata": {
        "name": "login",
        "file": "src/auth.py",
        "docstring": "Authenticate user with credentials"
    }
}

# Storage: .orc/embeddings.faiss (or .orc/embeddings/)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Indexing (MVP) ✅
**Goal:** Basic indexing and analysis for Python

- [x] Python AST parser
- [x] Basic dependency graph
- [x] Dead code detection
- [x] SQLite storage
- [x] CLI commands: `index`, `analyze`, `deadcode`

**Duration:** 2-3 weeks

### Phase 2: Context Compression Engine 🔄
**Goal:** Make the "huge map recipe" work

- [ ] Context builder implementation
- [ ] Query parser (keyword search)
- [ ] Relevance ranking algorithm
- [ ] Minimal context assembly
- [ ] API endpoints: `/api/context`

**Duration:** 3-4 weeks

### Phase 3: Multi-Language Support 🔄
**Goal:** JavaScript, TypeScript, React support

- [ ] JavaScript parser (Babel/ESTree)
- [ ] TypeScript parser
- [ ] React/JSX parser
- [ ] HTML/CSS static analyzer
- [ ] Cross-language linking

**Duration:** 4-5 weeks

### Phase 4: Optimization Engine 📋
**Goal:** Complexity analysis and suggestions

- [ ] Complexity analyzer (O notation detection)
- [ ] Algorithm pattern detector
- [ ] Optimization rule engine
- [ ] Code generator (optimized snippets)
- [ ] CLI command: `optimize`

**Duration:** 3-4 weeks

### Phase 5: AI Integration API 📋
**Goal:** Full REST API for AI tools

- [ ] FastAPI server
- [ ] All API endpoints
- [ ] Authentication/rate limiting
- [ ] Documentation (OpenAPI)
- [ ] Example integrations (Claude, Cursor)

**Duration:** 2-3 weeks

### Phase 6: Advanced Features 📋
**Goal:** Enterprise-ready features

- [ ] Semantic search (embeddings)
- [ ] LLM integration (Claude API)
- [ ] Web dashboard
- [ ] Git integration
- [ ] CI/CD integration
- [ ] Performance optimizations

**Duration:** 4-6 weeks

### Phase 7: Polish & Release 📋
**Goal:** Production-ready 1.0

- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Performance benchmarks
- [ ] Security audit
- [ ] Package for PyPI
- [ ] Marketing materials

**Duration:** 2-3 weeks

**Total Estimated Time:** 5-6 months

---

## 🔌 API Usage Examples

### Example 1: Claude Desktop Integration

```python
"""
Claude Desktop MCP Server for ORC
Allows Claude to query ORC for context
"""
import anthropic
import requests

class ORCContextProvider:
    """Provide ORC context to Claude"""
    
    def __init__(self, orc_api_url="http://localhost:8000"):
        self.orc_url = orc_api_url
        self.claude = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def query_with_context(self, user_query: str) -> str:
        """Query Claude with ORC context"""
        
        # Step 1: Get relevant context from ORC
        context_response = requests.post(
            f"{self.orc_url}/api/context",
            json={
                "query": user_query,
                "max_tokens": 8000
            }
        )
        context = context_response.json()
        
        # Step 2: Build prompt with context
        prompt = f"""Here is the relevant code context:

{self._format_context(context)}

User Question: {user_query}

Please answer based on the code context provided."""
        
        # Step 3: Query Claude
        response = self.claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _format_context(self, context: dict) -> str:
