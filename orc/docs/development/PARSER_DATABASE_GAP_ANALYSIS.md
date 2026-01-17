# Parser vs Database Gap Analysis

**Date:** 2026-01-16
**Issue:** Parsers collect basic data, but 22-section vision needs much more

---

## Current Parser Output

### What Parsers Currently Extract:
```python
{
    'files': {path: {language, loc, path}},
    'functions': {
        func_id: {
            name, file, line_start, line_end,
            complexity, parameters, calls, code,
            is_exported, decorators, docstring, is_async
        }
    },
    'classes': {
        class_id: {
            name, file, line_start, line_end,
            methods, base_classes
        }
    },
    'imports_detailed': [(statement, line_number, what_imported)],
    'exports': {export_id: {name, kind, file}},
    'entry_points': [(type, line_number)]
}
```

**Covers:** ~4 of 22 sections (18%)

---

## Current Database Schema

### What Database Can Store (10 Tables):
1. ✅ file_index - Files
2. ✅ function_index - Functions
3. ✅ class_index - Classes
4. ✅ import_index - Imports
5. ✅ export_index - Exports
6. ✅ file_dependencies - Dependencies
7. ✅ function_calls_resolved - Call graph
8. ✅ entry_points - Entry points
9. ✅ code_summaries - AI summaries (for AI Backend)
10. ✅ ai_insights - AI insights (for AI Backend)

**Covers:** ~6 of 22 sections (27%)

---

## The 22-Section Vision vs Reality

### Section 1: File Registry ✅ (COVERED)
**Current:** file_index table has path, language, loc
**Missing:** Purpose/description (needs AI Backend)

---

### Section 2: Symbol Index ✅ (COVERED)
**Current:** function_index, class_index
**Missing:** 
- Brief descriptions (needs AI Backend)
- Return value descriptions (parsers don't extract)
- Throws/errors (parsers don't extract)
- Constants/config (no table for this)
- Enums (TypeScript parser extracts but no storage)

---

### Section 3: Data Models & Schemas ❌ (MISSING)
**Current:** Nothing
**Needed:**
- Detect data structures (classes that are just data)
- Field types and requirements
- Purpose of each model
- Database table mappings
- Example structures

**This needs NEW parser logic + NEW database table**

---

### Section 4: Entry Points & Execution Flow ⚠️ (PARTIAL)
**Current:** entry_points table (only __main__ detection)
**Missing:**
- API endpoints (FastAPI/Flask routes)
- Event listeners
- Scheduled jobs/cron
- CLI commands
- Execution flow/sequences

**This needs ENHANCED parser logic (detect decorators like @app.route)**

---

### Section 5: State Management & Persistence ❌ (MISSING)
**Current:** Nothing
**Needed:**
- Database queries (detect SQL, ORM calls)
- Cache usage (detect Redis, Memcached)
- File storage patterns
- State read/write tracking

**This needs NEW parser logic to detect database/cache patterns**

---

### Section 6: Dependencies & Relationships ⚠️ (PARTIAL)
**Current:** file_dependencies, function_calls_resolved
**Missing:**
- External library purposes (just names, not "why")
- Data flow tracking
- Module coupling metrics

**Database adequate, parsers need enhancement**

---

### Section 7: Error Handling & Failure Modes ❌ (MISSING)
**Current:** Nothing
**Needed:**
- Try/except blocks
- Error types raised
- Error handling patterns
- Recovery mechanisms

**This needs NEW parser logic + NEW table**

---

### Section 8: Configuration & Environment ❌ (MISSING)
**Current:** Nothing
**Needed:**
- Env var usage (os.getenv, process.env)
- Config file detection
- Default values
- Feature flags

**This needs NEW parser logic + NEW table**

---

### Section 9: Cross-Cutting Concerns ❌ (MISSING)
**Current:** Nothing
**Needed:**
- Auth decorators (@login_required)
- Logging calls (logger.info, console.log)
- Cache decorators (@cache)
- Rate limiting
- Validation

**This needs NEW parser logic + NEW table**

---

### Section 10: Metadata & Context ❌ (MISSING - AI BACKEND JOB)
**Current:** code_summaries, ai_insights tables exist
**Needed:** AI Backend to populate these
- Module purpose
- Gotchas
- Performance notes
- Tech debt markers

**Database ready, need AI Backend implementation**

---

### Sections 11-22: All Missing ❌
These are completely missing:
- 11. Testing & Coverage
- 12. Documentation Links
- 13. Request/Response Contracts
- 14. Side Effects & External Actions
- 15. Concurrency & Threading
- 16. Performance Characteristics
- 17. Security & Vulnerabilities
- 18. Integration Points
- 19. Backwards Compatibility
- 20. Resource Usage & Limits
- 21. Deployment & Infrastructure
- 22. Metrics & Monitoring

---

## Gap Summary

### Parsers Collect (Current):
- ✅ Basic structure (functions, classes)
- ✅ Complexity scores
- ✅ Imports/exports
- ✅ Entry points (basic)
- ❌ Everything else

### Database Can Store (Current):
- ✅ 10 tables for basic data
- ✅ 2 tables for AI insights
- ❌ Need ~12 more tables for 22 sections

### AI Backend (Current):
- ❌ Not implemented
- ❌ Should add "meaning" to raw parser data

---

## Decision Point: Two Approaches

### Approach A: Pragmatic (Recommended)
**Start with what we have, enhance incrementally**

**Phase 1: Wire Current Parsers (Now)**
- Connect existing parsers to database
- Store the 4 sections we already collect
- Get basic system working

**Phase 2: Enhance Parsers (Next)**
- Add detection for:
  - API endpoints (Section 4)
  - Error handling (Section 7)
  - Config usage (Section 8)
  - Side effects (Section 14)

**Phase 3: Add AI Backend (Later)**
- Implement intelligence layer
- Add context/purpose/risk (Section 10)

**Phase 4: Complete Vision (Eventually)**
- Add remaining 12 sections
- Full 22-section database

**Timeline:** 
- Phase 1: 1 session (get something working)
- Phase 2: 2-3 sessions (enhance)
- Phase 3: 2-3 sessions (AI Backend)
- Phase 4: 5-10 sessions (complete)

---

### Approach B: All-or-Nothing (Not Recommended)
**Build everything before connecting anything**

- Enhance parsers for all 22 sections first
- Build all database tables
- Implement AI Backend
- Then connect everything

**Timeline:** 15+ sessions before anything works

**Risk:** High (might miss requirements, lots of unused code)

---

## Recommendation: Approach A

**Why:**
1. Get value quickly (working system in 1 session)
2. Learn what's actually needed (user feedback)
3. Iterate based on real usage
4. Less waste (don't build unused features)

**Minimum Viable ORC (Phase 1):**
- Parse: Functions, classes, imports, complexity
- Store: In existing 10 tables
- Query: Find dead code, complex functions
- Chat: Basic queries on actual data

**This solves 80% of use cases with 20% of work**

---

## Implementation Plan (Phase 1 - Next Session)

### Task 1: Parser Registry (15 min)
```python
# orc/parsers/__init__.py
PARSER_REGISTRY = {
    '.py': PythonParser,
    '.js': JavaScriptParser,
    '.ts': TypeScriptParser,
}

def get_parser_for_file(file_path):
    ext = Path(file_path).suffix
    parser_class = PARSER_REGISTRY.get(ext)
    return parser_class() if parser_class else None
```

### Task 2: Wire Index Command (30 min)
```python
# In orc/cli/cli_main.py index() command

from orc.parsers import get_parser_for_file
from orc.storage.graph_db import GraphDB

# After indexer runs:
db = GraphDB(".orc/graph.db")

for file_path in indexed_files:
    parser = get_parser_for_file(file_path)
    if parser:
        result = parser.parse_file(file_path)
        
        # Store file
        file_info = result['files'][str(file_path)]
        db.store_file(str(file_path), file_info['language'], file_info['loc'])
        
        # Store functions
        for func_id, func_data in result['functions'].items():
            db.store_function(
                func_id=func_id,
                name=func_data['name'],
                file=func_data['file'],
                line_start=func_data['line_start'],
                line_end=func_data['line_end'],
                complexity=func_data['complexity'],
                code=func_data['code'],
                params=','.join(func_data['parameters']),
                calls=','.join(func_data['calls']),
                is_exported=func_data['is_exported']
            )
        
        # Store classes
        for class_id, class_data in result['classes'].items():
            db.store_class(
                class_id=class_id,
                name=class_data['name'],
                file=class_data['file'],
                line_start=class_data['line_start'],
                line_end=class_data['line_end'],
                methods=','.join(class_data['methods']),
                base_classes=','.join(class_data['base_classes'])
            )
        
        # Store imports
        for idx, (statement, line_num, what) in enumerate(result['imports_detailed']):
            import_id = f"{file_path}:{idx}"
            db.store_import(
                import_id=import_id,
                source_file=str(file_path),
                import_statement=statement,
                line_number=line_num
            )
        
        # Store exports
        for export_id, export_data in result['exports'].items():
            db.store_export(
                export_id=export_id,
                name=export_data['name'],
                kind=export_data['kind'],
                file=export_data['file']
            )
        
        # Store entry points
        entry_points_list = [
            {
                'file_path': str(file_path),
                'entry_type': entry_type,
                'line_number': line_num
            }
            for entry_type, line_num in result['entry_points']
        ]
        if entry_points_list:
            db.store_entry_points(entry_points_list)
```

### Task 3: Test on Real Project (15 min)
```bash
cd test_project
orc init
orc index
# Check database has data:
sqlite3 .orc/graph.db "SELECT COUNT(*) FROM function_index"
```

### Task 4: Verify CLI Commands Work (15 min)
```bash
orc find dead
orc find complex
orc report
```

---

## Future Enhancements (Phase 2+)

### Parser Enhancements Needed:
1. **API Endpoint Detection**
   - FastAPI: `@app.get("/path")`
   - Flask: `@app.route("/path")`
   - Django: url patterns

2. **Error Handling**
   - Try/except blocks
   - Raised exceptions
   - Error types

3. **Config Usage**
   - os.getenv()
   - config.get()
   - process.env

4. **Database Queries**
   - SQL strings
   - ORM methods
   - Query builders

5. **Side Effects**
   - HTTP requests
   - File I/O
   - Email sends

### Database Tables Needed:
```sql
-- Section 4: API Endpoints
CREATE TABLE api_endpoints (
    id INTEGER PRIMARY KEY,
    route TEXT,
    method TEXT,
    handler_function TEXT,
    file TEXT,
    line_number INTEGER
);

-- Section 7: Error Handling
CREATE TABLE error_handlers (
    id INTEGER PRIMARY KEY,
    exception_type TEXT,
    handler_function TEXT,
    file TEXT,
    line_number INTEGER
);

-- Section 8: Configuration
CREATE TABLE config_usage (
    id INTEGER PRIMARY KEY,
    config_key TEXT,
    default_value TEXT,
    used_in_file TEXT,
    line_number INTEGER
);

-- Section 14: Side Effects
CREATE TABLE side_effects (
    id INTEGER PRIMARY KEY,
    effect_type TEXT,  -- 'http', 'db', 'email', 'file'
    function TEXT,
    target TEXT,
    file TEXT,
    line_number INTEGER
);
```

---

## Bottom Line

**Current Reality:**
- Parsers: 18% of vision
- Database: 27% of vision
- AI Backend: 0% of vision
- **Total: ~15% complete**

**Recommendation:**
- Wire what we have (Phase 1) → Get working system
- Enhance incrementally (Phase 2-4) → Add features based on real usage
- Don't try to build all 22 sections at once

**Next Session:**
Focus on Phase 1 only. Get `orc index` storing data in database. Test with real project. Then we can see what's actually needed for Phase 2.

---

**Question:** Do you want to proceed with Approach A (pragmatic incremental), or build more before connecting?
