# Database Schema for Complete Code Navigation

## Goal
Enable someone to **fully understand and navigate** a huge codebase they've never seen before, just by querying the database. They should be able to answer:

1. "What does this project do?"
2. "Where is the entry point?"
3. "How do I get from A to B?"
4. "What depends on what?"
5. "What are the main components?"

---

## Current State (What We Have)

### ✅ Tables That Exist:
```sql
file_index          -- Files with language, LOC, path
function_index      -- Functions with complexity, calls (as strings)
class_index         -- Classes with name, file, language
import_index        -- EMPTY (not being used)
export_index        -- EMPTY (not being used)
```

### ✅ What We Can Answer Now:
- "Show me all Python files" ✅
- "Find function named 'login'" ✅
- "What functions are most complex?" ✅
- "How many classes exist?" ✅

### ❌ What We CANNOT Answer:
- "Where does this function get called from?" ❌
- "What modules does file X import?" ❌
- "Show me the call chain from main() to database_query()" ❌
- "What files use this utility module?" ❌
- "Is this module an entry point or a library?" ❌
- "What are the layers of this architecture?" ❌

---

## What's Missing for TRUE Code Navigation

### 1. **MODULE/FILE RELATIONSHIPS**

#### What We Need:
```sql
-- File-to-File Dependencies
CREATE TABLE file_dependencies (
    source_file TEXT,           -- File doing the importing
    target_file TEXT,           -- File being imported
    import_type TEXT,           -- 'import', 'from_import', 'require', etc.
    import_statement TEXT,      -- Original: "from utils import helper"
    line_number INTEGER
);

-- Examples stored:
-- auth.py imports database.py
-- main.py imports auth.py
-- utils.py imported by 15 different files
```

#### What This Enables:
- ✅ "What files does auth.py depend on?"
- ✅ "What files depend on database.py?"
- ✅ "Show me all files that import utils"
- ✅ Visualize: File dependency graph
- ✅ Detect: Circular dependencies (A imports B imports A)
- ✅ Analyze: Which modules are most coupled?

---

### 2. **FUNCTION-TO-FUNCTION CALL GRAPH**

#### What We Need (Enhanced):
```sql
-- Currently: calls_json = ["helper_function", "print", "json.loads"]
-- Problem: Don't know WHERE helper_function is defined

-- BETTER: Resolved function calls
CREATE TABLE function_calls (
    caller_function_id TEXT,        -- ID of calling function
    caller_file TEXT,
    caller_line INTEGER,            -- Line where call happens
    
    callee_function_name TEXT,      -- What's being called
    callee_function_id TEXT,        -- ID of target function (if resolved)
    callee_file TEXT,               -- Where it's defined (if known)
    
    is_resolved BOOLEAN,            -- Do we know where it's defined?
    is_external BOOLEAN,            -- Is it from external library?
    call_type TEXT                  -- 'direct', 'method', 'constructor', etc.
);

-- Examples:
-- auth.login() calls database.connect() (resolved to db.py)
-- main.start() calls auth.login() (resolved to auth.py)
-- utils.helper() calls print() (external, stdlib)
```

#### What This Enables:
- ✅ "Who calls this function?" (reverse lookup)
- ✅ "Trace the call path from main() to database_query()"
- ✅ "Show me the full call stack"
- ✅ "Is this function ever called?" (dead code detection)
- ✅ "What's the entry point?" (functions never called by others)

---

### 3. **IMPORTS & EXPORTS (Make Them Work!)**

#### What We Need:
```sql
-- Module Imports (currently empty!)
CREATE TABLE imports (
    file_path TEXT,                 -- File doing the import
    module_name TEXT,               -- What's being imported
    imported_names TEXT,            -- Specific items: ["helper", "utils"]
    alias TEXT,                     -- If renamed: "import pandas as pd"
    line_number INTEGER,
    is_relative BOOLEAN,            -- from .utils vs from myapp.utils
    is_external BOOLEAN             -- Is it from installed package?
);

-- Module Exports (currently empty!)
CREATE TABLE exports (
    file_path TEXT,                 -- File defining the export
    symbol_name TEXT,               -- Function/class/variable name
    symbol_type TEXT,               -- 'function', 'class', 'variable'
    is_public BOOLEAN,              -- Not starting with _
    exported_in_all BOOLEAN         -- Listed in __all__
);

-- Examples:
-- auth.py exports: login(), logout(), is_authenticated()
-- utils.py exports: helper(), format_date()
-- main.py imports: auth.login, database.connect
```

#### What This Enables:
- ✅ "What does this file export?" (public API)
- ✅ "Where is this function imported from?"
- ✅ "Is this a public API or internal?"
- ✅ "Show me all exports of a module"
- ✅ "What's the interface of this module?"

---

### 4. **CLASS RELATIONSHIPS (Inheritance & Composition)**

#### What We Need (Enhanced):
```sql
-- Currently: bases_json might have class names as strings
-- BETTER: Resolved class relationships

CREATE TABLE class_relationships (
    class_id TEXT,
    class_name TEXT,
    class_file TEXT,
    
    relationship_type TEXT,         -- 'inherits', 'uses', 'contains'
    
    related_class_name TEXT,        -- Parent/used class
    related_class_id TEXT,          -- Resolved ID
    related_class_file TEXT,        -- Where it's defined
    
    is_resolved BOOLEAN
);

-- Examples:
-- UserController inherits BaseController (from controllers.py)
-- DatabaseManager uses ConnectionPool (from pool.py)
-- User contains Address (composition)
```

#### What This Enables:
- ✅ "Show me class hierarchy"
- ✅ "What classes inherit from this base class?"
- ✅ "What classes does this class use?"
- ✅ "Draw the inheritance tree"

---

### 5. **ENTRY POINTS & SPECIAL MARKERS**

#### What We Need:
```sql
CREATE TABLE entry_points (
    file_path TEXT,
    entry_type TEXT,                -- 'main', 'cli', 'api_endpoint', 'test'
    function_name TEXT,             -- e.g., "main()", "app.run()"
    line_number INTEGER,
    confidence REAL                 -- How sure are we?
);

-- Entry point types:
-- Python: if __name__ == "__main__"
-- JavaScript: package.json "main" field
-- CLI: click commands, argparse
-- API: @app.route, FastAPI endpoints
-- Tests: test_* functions
```

#### What This Enables:
- ✅ "Where do I start reading this code?"
- ✅ "What are the entry points?"
- ✅ "Is this a library or an application?"
- ✅ "Show me all API endpoints"
- ✅ "Find all CLI commands"

---

### 6. **CALL CHAINS (Pre-computed Paths)**

#### What We Need:
```sql
CREATE TABLE call_paths (
    from_function_id TEXT,
    to_function_id TEXT,
    path_json TEXT,                 -- ["main", "auth.login", "db.connect"]
    depth INTEGER,                  -- How many hops
    is_cyclic BOOLEAN              -- Does it loop back?
);

-- Pre-compute common paths for fast lookup
-- Example: main() → login() → verify_credentials() → database_query()
```

#### What This Enables:
- ✅ "How do I get from function A to function B?"
- ✅ "Show me all paths between these two functions"
- ✅ "What's the deepest call chain?" (complexity metric)
- ✅ "Are there circular call chains?" (code smell)

---

### 7. **ARCHITECTURAL LAYERS**

#### What We Need:
```sql
CREATE TABLE architectural_layers (
    file_path TEXT,
    layer_type TEXT,                -- 'presentation', 'business', 'data', 'utility'
    confidence REAL,
    indicators TEXT                 -- What made us think this?
);

-- Heuristics to detect layers:
-- Contains "controller", "view", "template" → Presentation
-- Contains "service", "business", "logic" → Business Logic
-- Contains "database", "repository", "model" → Data Layer
-- Contains "utils", "helpers" → Utility
```

#### What This Enables:
- ✅ "Show me the architecture"
- ✅ "What's the layering structure?"
- ✅ "Is there layer violation?" (data layer calling presentation)
- ✅ "Visualize: Architecture diagram"

---

### 8. **METADATA & ANNOTATIONS**

#### What We Need:
```sql
CREATE TABLE code_metadata (
    target_type TEXT,               -- 'file', 'function', 'class'
    target_id TEXT,
    
    metadata_type TEXT,             -- 'docstring', 'comment', 'decorator', 'annotation'
    content TEXT,
    line_number INTEGER
);

-- Examples:
-- @login_required decorator
-- @app.route('/api/users') endpoint
-- """This function does X""" docstring
-- # TODO: Refactor this
```

#### What This Enables:
- ✅ "Show me all API endpoints"
- ✅ "Find all TODOs"
- ✅ "What decorators are used?"
- ✅ "Show function documentation"

---

### 9. **VARIABLES & STATE**

#### What We Need:
```sql
CREATE TABLE global_state (
    file_path TEXT,
    variable_name TEXT,
    variable_type TEXT,             -- 'global', 'config', 'constant'
    initial_value TEXT,
    line_number INTEGER,
    is_mutable BOOLEAN
);

CREATE TABLE function_parameters (
    function_id TEXT,
    param_name TEXT,
    param_type TEXT,                -- Type hint if available
    default_value TEXT,
    is_required BOOLEAN,
    position INTEGER
);
```

#### What This Enables:
- ✅ "What global variables exist?"
- ✅ "What configuration is needed?"
- ✅ "What are the function signatures?"

---

## Summary: Minimum Viable Schema for Code Navigation

### **CRITICAL (Must Have):**

1. **`file_dependencies`** - File imports file
   - Enables: "What depends on what?" at file level

2. **`function_calls` (enhanced)** - Function calls function WITH file resolution
   - Enables: "Who calls whom?" with full paths

3. **`imports` (populate it!)** - What each file imports
   - Enables: "Where does this come from?"

4. **`exports` (populate it!)** - What each file exports
   - Enables: "What's the public API?"

5. **`entry_points`** - Where to start reading
   - Enables: "Where do I begin?"

### **IMPORTANT (Should Have):**

6. **`class_relationships`** - Inheritance and composition
   - Enables: "How are classes connected?"

7. **`call_paths`** - Pre-computed call chains
   - Enables: Fast "how do I get from A to B?"

### **NICE TO HAVE:**

8. **`architectural_layers`** - Detect architecture
9. **`code_metadata`** - Decorators, docstrings, TODOs
10. **`function_parameters`** - Function signatures

---

## Example: Navigating Unknown Codebase

### Scenario: New developer joins, never seen the code

**Query 1: "What is this project?"**
```sql
-- Find entry points
SELECT * FROM entry_points WHERE entry_type = 'main';
-- Result: main.py has main() function at line 150
```

**Query 2: "What does main() do?"**
```sql
-- Find what main() calls
SELECT callee_function_name, callee_file 
FROM function_calls 
WHERE caller_function_id = 'main.py:main';
-- Result: Calls init_app(), setup_routes(), run_server()
```

**Query 3: "Where is setup_routes() defined?"**
```sql
-- Find the function
SELECT file_path, line_start 
FROM function_index 
WHERE name = 'setup_routes';
-- Result: routes.py line 45
```

**Query 4: "What does routes.py import?"**
```sql
-- Find dependencies
SELECT module_name, imported_names 
FROM imports 
WHERE file_path = 'routes.py';
-- Result: Imports auth, database, controllers
```

**Query 5: "Show me the call chain from main() to database_query()"**
```sql
-- Find path
SELECT path_json 
FROM call_paths 
WHERE from_function_id LIKE '%main%' 
  AND to_function_id LIKE '%database_query%';
-- Result: ["main", "init_app", "setup_database", "database_query"]
```

**Query 6: "Is anyone using old_function()?"**
```sql
-- Dead code detection
SELECT COUNT(*) 
FROM function_calls 
WHERE callee_function_name = 'old_function';
-- Result: 0 (dead code!)
```

---

## Visual: What Database Enables

With complete database, you can generate:

### 1. **File Dependency Graph**
```
main.py
  └─ imports auth.py
       └─ imports database.py
       └─ imports utils.py
  └─ imports routes.py
       └─ imports controllers.py
```

### 2. **Function Call Graph**
```
main()
  ├─ init_app()
  │   └─ setup_database()
  │       └─ database_query()
  └─ run_server()
      └─ handle_request()
          └─ auth.login()
```

### 3. **Class Hierarchy**
```
BaseController
  ├─ UserController
  │   └─ AdminController
  └─ ProductController
```

### 4. **Architecture Layers**
```
[Presentation Layer]
  routes.py, controllers.py

[Business Logic Layer]  
  services.py, business.py

[Data Layer]
  database.py, models.py

[Utilities]
  utils.py, helpers.py
```

---

## Implementation Priority

### Phase 1: Essential Navigation (Week 1)
1. Populate `imports` table
2. Populate `exports` table
3. Add `file_dependencies` table
4. Enhance `function_calls` with file resolution

### Phase 2: Deep Navigation (Week 2)
5. Add `entry_points` detection
6. Enhance `class_relationships`
7. Build `call_paths` table

### Phase 3: Polish (Week 3)
8. Add `architectural_layers` detection
9. Add `code_metadata` extraction
10. Add query/visualization tools

---

## Bottom Line

**To truly navigate an unknown codebase, you need:**

✅ **Files** → What files exist  
✅ **Functions** → What functions exist  
✅ **Imports** → What imports what  
✅ **Exports** → What's public API  
✅ **Dependencies** → File → File relationships  
✅ **Calls** → Function → Function relationships (WITH file paths)  
✅ **Entry Points** → Where to start  
✅ **Call Chains** → How to get from A to B  

**With these 8 things, someone can understand ANY codebase without reading a single line of code.**

Ready to implement?
