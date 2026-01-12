# Architecture: How Everything Connects

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER RUNS COMMAND                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI (cli_main.py)                        │
│  Commands: orc index, orc find, orc                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌──────────────────────┐
│  INDEX FLOW      │              │  CHAT FLOW (orc)     │
│  (Builds data)   │              │  (Uses data)         │
└────────┬─────────┘              └──────────┬───────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────────────────────────────────────────────────┐
│              ENHANCED DATABASE                              │
│  - Functions, classes, files                                │
│  - Dependencies, imports, exports                           │
│  - AI summaries                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 1: Building the Database (Indexing)

### Step-by-Step Connection

```
1. USER RUNS:
   $ orc index --with-ai
   
   ↓

2. CLI (cli_main.py) calls:
   index_directory_parallel(path, with_ai=True)
   
   ↓

3. INDEXER (parallel_indexer.py):
   ┌─────────────────────────────────────┐
   │ For each file:                      │
   │   → Call Parser                     │
   │   → Get structure + code            │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ PARSER (python_parser.py)           │
   │                                     │
   │ Extracts:                           │
   │   - Functions (name, code, params)  │
   │   - Classes (name, methods)         │
   │   - Imports (from X import Y)       │
   │   - Exports (__all__ = [...])       │
   │   - Entry points (if __name__)      │
   │                                     │
   │ Returns: {                          │
   │   'functions': {...},               │
   │   'classes': {...},                 │
   │   'imports': {...},                 │
   │   'exports': {...}                  │
   │ }                                   │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ DEPENDENCY RESOLVER                 │
   │ (dependency_resolver.py)            │
   │                                     │
   │ Resolves:                           │
   │   - "login()" calls what?           │
   │   - Where is "get_user()" defined?  │
   │   - Which file imports which?       │
   │                                     │
   │ Returns: {                          │
   │   'file_dependencies': [...],       │
   │   'function_calls_resolved': [...]  │
   │ }                                   │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ AI SUMMARIZER (if --with-ai)        │
   │ (ai_summarizer.py)                  │
   │                                     │
   │ For each function/class/file:       │
   │   → Send code to AI                 │
   │   → Get summary back                │
   │                                     │
   │ Returns: {                          │
   │   'summaries': {                    │
   │     'function_id': {                │
   │       'summary': '...',             │
   │       'business_rules': [...]       │
   │     }                               │
   │   }                                 │
   │ }                                   │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ STORE IN DATABASE                   │
   │ (graph_db.py)                       │
   │                                     │
   │ Tables Updated:                     │
   │   ✅ function_index                 │
   │   ✅ class_index                    │
   │   ✅ import_index                   │
   │   ✅ export_index                   │
   │   ✅ file_dependencies              │
   │   ✅ function_calls_resolved        │
   │   ✅ code_summaries (AI)            │
   │   ✅ entry_points                   │
   └─────────────────────────────────────┘
```

---

## Flow 2: ORC AI Using the Database (Chat)

### Step-by-Step Connection

```
1. USER RUNS:
   $ orc
   > What does login() do?
   
   ↓

2. CLI (cli_main.py) starts:
   interactive_chat_loop()
   
   ↓

3. CHAT LOOP (cli_loop.py):
   ┌─────────────────────────────────────┐
   │ User message: "What does login()?"  │
   │                                     │
   │ → Get AI client                     │
   │ → Build context with tools          │
   │ → Send to AI                        │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ AI CLIENT (ai_client.py)            │
   │                                     │
   │ AI receives:                        │
   │   - User question                   │
   │   - System prompt                   │
   │   - Available tools                 │
   │                                     │
   │ AI thinks: "I need to find login()" │
   │                                     │
   │ AI decides to call tool:            │
   │   get_function_with_summary("login")│
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ AI TOOLS (ai_tools.py)              │
   │                                     │
   │ Tool: get_function_with_summary()   │
   │                                     │
   │ Executes SQL:                       │
   │   SELECT                            │
   │     f.name,                         │
   │     f.file_path,                    │
   │     f.line_start,                   │
   │     f.complexity,                   │
   │     f.calls_json,                   │
   │     s.summary_short,                │
   │     s.summary_detailed,             │
   │     s.business_rules,               │
   │     s.inputs,                       │
   │     s.outputs                       │
   │   FROM function_index f             │
   │   LEFT JOIN code_summaries s        │
   │     ON f.id = s.target_id           │
   │   WHERE f.name = 'login'            │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ DATABASE (graph_db.py)              │
   │                                     │
   │ Returns:                            │
   │ {                                   │
   │   "name": "login",                  │
   │   "file": "auth.py",                │
   │   "line": 45,                       │
   │   "complexity": 8,                  │
   │   "calls": ["get_user", "verify"],  │
   │   "summary": "Authenticates user...",│
   │   "business_rules": [               │
   │     "Max 3 attempts",               │
   │     "Password with bcrypt"          │
   │   ]                                 │
   │ }                                   │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ BACK TO AI                          │
   │                                     │
   │ AI receives tool result             │
   │                                     │
   │ AI reads summary (NOT code!)        │
   │                                     │
   │ AI formulates response:             │
   │ "The login() function authenticates │
   │  user credentials. It validates     │
   │  email, checks password with bcrypt,│
   │  implements rate limiting (max 3    │
   │  attempts), and creates a session   │
   │  token on success."                 │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │ DISPLAY TO USER                     │
   └─────────────────────────────────────┘
```

---

## The Key Files and Their Roles

### 1. **Database Layer** (Storage)

```python
# orc/storage/graph_db.py
class GraphStorage:
    def __init__(self, db_path):
        # Initialize SQLite connection
        # Create all tables
    
    # EXISTING METHODS (keep these)
    def upsert_file_index(...)
    def bulk_upsert_functions(...)
    def bulk_upsert_classes(...)
    
    # NEW METHODS (add these)
    def store_imports(self, imports_list):
        """Store imports in import_index table"""
        
    def store_exports(self, exports_list):
        """Store exports in export_index table"""
        
    def store_file_dependencies(self, deps):
        """Store file-to-file dependencies"""
        
    def store_resolved_calls(self, calls):
        """Store function calls with file resolution"""
        
    def store_entry_points(self, entry_points):
        """Store detected entry points"""
        
    def store_summary(self, target_id, summary):
        """Store AI-generated summary"""
        
    def get_function_with_summary(self, name):
        """Get function + AI summary (for AI tools)"""
        return {
            'structure': {...},  # from function_index
            'summary': {...}     # from code_summaries
        }
```

### 2. **Parser Layer** (Extraction)

```python
# orc/parsers/python_parser.py
class PythonParser(BaseParser):
    def parse_file(self, file_path):
        # EXISTING (keep these)
        result = {
            'files': {...},
            'functions': {...},
            'classes': {...}
        }
        
        # NEW (add these)
        result['imports'] = self._extract_imports(tree)
        result['exports'] = self._extract_exports(tree)
        result['entry_points'] = self._detect_entry_points(tree)
        
        return result
    
    # NEW METHOD
    def _extract_imports(self, tree):
        """Extract all import statements with line numbers"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Extract: import math
                imports.append({
                    'module': node.names[0].name,
                    'line': node.lineno,
                    'type': 'import'
                })
            elif isinstance(node, ast.ImportFrom):
                # Extract: from os import path
                imports.append({
                    'module': node.module,
                    'names': [alias.name for alias in node.names],
                    'line': node.lineno,
                    'type': 'from_import'
                })
        return imports
```

### 3. **Indexer Layer** (Orchestration)

```python
# orc/core/parallel_indexer.py
def index_directory_parallel(directory, with_ai=False, ai_client=None):
    # STEP 1: Parse files (existing)
    result = parse_all_files(directory)
    
    # STEP 2: Resolve dependencies (NEW)
    resolver = DependencyResolver()
    result['dependencies'] = resolver.resolve(result)
    
    # STEP 3: Generate AI summaries (NEW, optional)
    if with_ai:
        summarizer = AICodeSummarizer(ai_client)
        result['summaries'] = summarizer.generate_summaries(result)
    
    # STEP 4: Store everything (enhanced)
    db = GraphStorage(db_path)
    
    # Existing storage
    db.bulk_upsert_functions(result['functions'])
    db.bulk_upsert_classes(result['classes'])
    
    # NEW storage
    db.store_imports(result['imports'])
    db.store_exports(result['exports'])
    db.store_file_dependencies(result['dependencies']['files'])
    db.store_resolved_calls(result['dependencies']['calls'])
    db.store_entry_points(result['entry_points'])
    
    # AI summaries storage (if generated)
    if 'summaries' in result:
        for target_id, summary in result['summaries'].items():
            db.store_summary(target_id, summary)
    
    return result
```

### 4. **AI Summarizer** (NEW)

```python
# orc/ai_summarizer.py
class AICodeSummarizer:
    def __init__(self, ai_client=None):
        from orc.ai_client import get_ai_client
        self.ai_client = ai_client or get_ai_client()
        self.batch = []
    
    def generate_summaries(self, parse_result):
        """Generate summaries for all functions/classes/files"""
        summaries = {}
        
        # Summarize functions
        for func_id, func_data in parse_result['functions'].items():
            summary = self._summarize_function(
                code=func_data.get('code', ''),
                name=func_data['name'],
                context=func_data
            )
            summaries[func_id] = summary
        
        # Summarize classes
        for class_id, class_data in parse_result['classes'].items():
            summary = self._summarize_class(
                code=class_data.get('code', ''),
                name=class_data['name'],
                methods=class_data.get('methods', [])
            )
            summaries[class_id] = summary
        
        return summaries
    
    def _summarize_function(self, code, name, context):
        """Call AI to summarize a function"""
        prompt = f"""
        Summarize this function:
        
        Name: {name}
        Code:
        ```python
        {code}
        ```
        
        Provide:
        1. One-line summary
        2. Detailed explanation
        3. Business rules
        4. Inputs/outputs
        
        Respond in JSON format.
        """
        
        response = self.ai_client.chat([
            {"role": "system", "content": "You are a code documentation expert."},
            {"role": "user", "content": prompt}
        ])
        
        return json.loads(response)
```

### 5. **AI Tools** (Enhanced)

```python
# orc/ai_tools.py
class ORCTools:
    def __init__(self, db_path):
        self.db = GraphStorage(db_path)
    
    # EXISTING TOOLS (keep these, enhance them)
    def query_functions(self, pattern, limit=20):
        """Enhanced to include AI summaries"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                f.name,
                f.file_path,
                f.line_start,
                f.complexity,
                s.summary_short,
                s.summary_detailed,
                s.business_rules
            FROM function_index f
            LEFT JOIN code_summaries s ON f.id = s.target_id
            WHERE f.name LIKE ?
            LIMIT ?
        ''', (f'%{pattern}%', limit))
        
        results = cursor.fetchall()
        
        return {
            'functions': [
                {
                    'name': r[0],
                    'file_path': r[1],
                    'line_start': r[2],
                    'complexity': r[3],
                    'summary': r[4],           # NEW!
                    'details': r[5],           # NEW!
                    'business_rules': r[6]     # NEW!
                }
                for r in results
            ]
        }
    
    # NEW TOOLS (add these)
    def get_function_summary(self, function_name):
        """Get AI summary of a function"""
        return self.db.get_function_with_summary(function_name)
    
    def get_file_dependencies(self, file_path):
        """Get what a file imports and who imports it"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # What this file imports
        cursor.execute('''
            SELECT target_file, import_statement
            FROM file_dependencies
            WHERE source_file = ?
        ''', (file_path,))
        imports = cursor.fetchall()
        
        # Who imports this file
        cursor.execute('''
            SELECT source_file, import_statement
            FROM file_dependencies
            WHERE target_file = ?
        ''', (file_path,))
        imported_by = cursor.fetchall()
        
        return {
            'imports': imports,
            'imported_by': imported_by
        }
    
    def find_entry_points(self):
        """Find all entry points in codebase"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, entry_type, function_name, line_number
            FROM entry_points
            ORDER BY confidence DESC
        ''')
        
        return {
            'entry_points': [
                {
                    'file': r[0],
                    'type': r[1],
                    'function': r[2],
                    'line': r[3]
                }
                for r in cursor.fetchall()
            ]
        }
    
    def trace_call_chain(self, from_func, to_func):
        """Show path from one function to another"""
        # This would use graph traversal
        # For now, simplified version
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                caller_function_id,
                callee_function_id,
                callee_file
            FROM function_calls_resolved
            WHERE caller_function_id LIKE ?
        ''', (f'%{from_func}%',))
        
        # Build path (simplified - real version would use BFS/DFS)
        return {'path': [...]}
```

### 6. **AI Guidelines** (Updated)

```python
# orc/ai_guidelines.py
SYSTEM_PROMPT = """
You are ORC AI, a coding assistant with access to a complete codebase index.

YOU HAVE ACCESS TO:
- Complete code structure (files, functions, classes)
- Dependencies and relationships (who imports who, who calls what)
- AI-generated summaries of all code
- Entry points and architecture

WHEN USER ASKS ABOUT CODE:
1. Query the database for structure
2. Get AI summaries (NOT the actual code)
3. Answer based on summaries
4. Only show actual code if user specifically requests it

AVAILABLE TOOLS:
- query_functions(pattern) - Find functions with AI summaries
- get_function_summary(name) - Get detailed function summary
- get_file_dependencies(file) - Show imports and dependents
- find_entry_points() - Find where code starts
- trace_call_chain(from, to) - Show execution path

EXAMPLE WORKFLOW:
User: "What does login() do?"
You:
  1. Call get_function_summary("login")
  2. Read the AI summary (not code!)
  3. Explain based on summary:
     "The login() function authenticates user credentials.
      It validates email, checks password with bcrypt,
      implements rate limiting (max 3 attempts), and
      creates a session on success."

Only show actual code if user says "show me the code".
"""
```

---

## Complete Data Flow Diagram

```
USER COMMAND
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                  CLI (cli_main.py)                      │
│  - orc index --with-ai                                  │
│  - orc find login                                       │
│  - orc (starts chat)                                    │
└──────────────┬──────────────────────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
INDEX PATH          CHAT PATH
     │                   │
     │                   │
     ▼                   ▼
┌──────────┐      ┌──────────────┐
│ Indexer  │      │  AI Client   │
│          │      │              │
│ Calls:   │      │  Calls:      │
│ ↓Parser  │      │  ↓AI Tools   │
│ ↓AI Sum  │      └──────┬───────┘
└────┬─────┘             │
     │                   │
     │                   ▼
     │            ┌──────────────┐
     │            │  AI Tools    │
     │            │  (queries    │
     │            │   database)  │
     │            └──────┬───────┘
     │                   │
     └─────────┬─────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              DATABASE (graph_db.py)                     │
│                                                         │
│  STRUCTURE TABLES:        AI TABLES:                    │
│  - function_index         - code_summaries              │
│  - class_index                                          │
│  - import_index                                         │
│  - file_dependencies                                    │
│  - function_calls_resolved                              │
│  - entry_points                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Summary: How It All Connects

### **Building Phase (orc index --with-ai):**
1. CLI → Indexer → Parser → Extract everything
2. Indexer → Dependency Resolver → Resolve relationships
3. Indexer → AI Summarizer → Generate summaries
4. Indexer → Database → Store everything

### **Usage Phase (orc chat):**
1. CLI → Chat Loop → AI Client → Send user question
2. AI Client → AI Tools → Query database
3. AI Tools → Database → Get structure + summaries
4. Database → AI Tools → Return data
5. AI Tools → AI Client → Tool result
6. AI Client → User → Answer (based on summaries!)

### **Key Insight:**
**The AI never reads actual code!** It only reads:
- Structure (from parsers)
- Summaries (from AI summarizer)
- Relationships (from dependency resolver)

This makes it:
- ✅ Fast (no need to read large code files)
- ✅ Accurate (summaries are curated)
- ✅ Efficient (queries database, not files)

---

Ready to implement? Everything connects through the database!
