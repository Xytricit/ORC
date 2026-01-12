# Implementation Roadmap: Enhanced Database + AI Summaries

## Goal
Add complete code intelligence (structure + AI summaries) to ORC's backend.
No web dashboard needed yet - just make the data available for ORC AI to use.

---

## Phase 1: Enhanced Database Schema (Week 1)

### What We're Adding
New tables to store:
1. File dependencies (who imports who)
2. Imports/exports (populate existing empty tables)
3. Resolved function calls (with file paths, not just names)
4. Entry points (where to start reading)
5. AI summaries (for files, functions, classes)

### Implementation Steps

#### Step 1.1: Update Database Schema (Day 1)
**File:** `orc/storage/graph_db.py`

Add new tables:
```sql
-- File-to-file dependencies
CREATE TABLE file_dependencies (
    source_file TEXT,
    target_file TEXT,
    import_statement TEXT,
    line_number INTEGER
);

-- Resolved function calls (enhanced)
CREATE TABLE function_calls_resolved (
    caller_function_id TEXT,
    caller_file TEXT,
    caller_line INTEGER,
    callee_function_name TEXT,
    callee_function_id TEXT,
    callee_file TEXT,
    is_resolved BOOLEAN,
    is_external BOOLEAN
);

-- Entry points detection
CREATE TABLE entry_points (
    file_path TEXT,
    entry_type TEXT,
    function_name TEXT,
    line_number INTEGER,
    confidence REAL
);

-- AI summaries
CREATE TABLE code_summaries (
    target_type TEXT,
    target_id TEXT,
    summary_short TEXT,
    summary_detailed TEXT,
    purpose TEXT,
    inputs TEXT,
    outputs TEXT,
    business_rules TEXT,
    ai_model TEXT,
    confidence REAL,
    generated_at TIMESTAMP,
    code_hash TEXT
);
```

#### Step 1.2: Update Parsers to Extract More Data (Day 2-3)
**Files:** 
- `orc/parsers/python_parser.py`
- `orc/parsers/javascript_parser.py`
- `orc/parsers/typescript_parser.py`

Enhance parsers to extract:
- Import statements (with line numbers)
- Export statements
- Entry point detection (if __name__ == "__main__", etc.)

#### Step 1.3: Update Indexer to Store New Data (Day 4)
**File:** `orc/core/parallel_indexer.py`

Modify to:
- Store imports in `import_index` table (currently empty)
- Store exports in `export_index` table (currently empty)
- Store file dependencies in `file_dependencies` table
- Detect and store entry points

#### Step 1.4: Build Dependency Resolver (Day 5)
**New File:** `orc/core/dependency_resolver.py`

Create class to:
- Resolve function calls to actual files
- Build file dependency graph
- Identify circular dependencies

---

## Phase 2: AI Integration (Week 2)

### What We're Adding
AI client that:
1. Generates summaries during indexing
2. Batches requests for efficiency
3. Caches results (only regenerate if code changes)
4. Stores summaries in database

### Implementation Steps

#### Step 2.1: Create AI Summarization Client (Day 1)
**New File:** `orc/ai_summarizer.py`

```python
class AICodeSummarizer:
    """Generates AI summaries of code"""
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client or get_ai_client()
        self.batch = []
        self.batch_size = 10
    
    def summarize_function(self, code, name, context):
        """Generate summary for a function"""
        pass
    
    def summarize_class(self, code, name, methods):
        """Generate summary for a class"""
        pass
    
    def summarize_file(self, file_path, functions, classes):
        """Generate summary for entire file"""
        pass
    
    def _process_batch(self):
        """Send batch to AI and get summaries"""
        pass
```

#### Step 2.2: Add Summarization Prompts (Day 1)
**New File:** `orc/prompts/summarization.py`

Define prompts for:
- Function summarization
- Class summarization
- File summarization
- Code insight generation

#### Step 2.3: Integrate AI with Parsers (Day 2)
**File:** `orc/core/parallel_indexer.py`

Add optional AI summarization:
```python
def index_directory_parallel(directory, with_ai=False, ai_client=None):
    # Parse files (existing)
    result = parse_files(directory)
    
    # Generate AI summaries (new, optional)
    if with_ai:
        summarizer = AICodeSummarizer(ai_client)
        summaries = summarizer.generate_summaries(result)
        result['summaries'] = summaries
    
    return result
```

#### Step 2.4: Add Summary Storage (Day 3)
**File:** `orc/storage/graph_db.py`

Add methods:
```python
def store_summary(self, target_type, target_id, summary):
    """Store AI-generated summary"""
    pass

def get_summary(self, target_id):
    """Retrieve summary for code element"""
    pass

def summaries_need_refresh(self, code_hashes):
    """Check which summaries need regeneration"""
    pass
```

#### Step 2.5: Add Caching Logic (Day 4)
**File:** `orc/ai_summarizer.py`

Implement:
- Hash code to detect changes
- Only regenerate if code changed
- Store generation timestamp

---

## Phase 3: Update CLI Commands (Week 2-3)

### Make Data Available Through CLI

#### Step 3.1: Enhance `orc index` Command (Day 1)
**File:** `orc/cli_main.py`

Add flag:
```bash
orc index --with-ai          # Index with AI summaries
orc index --with-ai --model groq  # Specify AI provider
```

#### Step 3.2: Enhance `orc find` Command (Day 2)
**File:** `orc/cli_main.py`

Show summaries in results:
```bash
orc find login

# Shows:
# Function: login()
# File: auth.py:45
# Summary: "Authenticates user credentials..." (AI)
# Calls: database.get_user(), ...
```

#### Step 3.3: Enhance `orc explain` Command (Day 3)
**File:** `orc/cli_main.py`

Make it actually work (currently stub):
```bash
orc explain login

# Shows complete info:
# - Location
# - AI Summary
# - Business rules
# - Inputs/outputs
# - Dependencies
# - Code snippet
```

#### Step 3.4: Add `orc summarize` Command (Day 4)
**File:** `orc/cli_main.py`

New command:
```bash
orc summarize                # Generate summaries for all code
orc summarize --file auth.py # Summarize specific file
orc summarize --refresh      # Regenerate all summaries
```

---

## Phase 4: Integrate with ORC AI (Week 3)

### Make AI Chat Use Enhanced Database

#### Step 4.1: Update AI Tools (Day 1-2)
**File:** `orc/ai_tools.py`

Enhance existing tools to return summaries:

```python
def query_functions(pattern, limit=20):
    """Enhanced to include AI summaries"""
    results = db.query("""
        SELECT 
            f.name, 
            f.file_path, 
            f.line_start,
            f.complexity,
            s.summary_short,
            s.summary_detailed
        FROM function_index f
        LEFT JOIN code_summaries s ON f.id = s.target_id
        WHERE f.name LIKE ?
        LIMIT ?
    """, (pattern, limit))
    return results
```

#### Step 4.2: Add New AI Tools (Day 3)
**File:** `orc/ai_tools.py`

New tools for AI to call:
```python
def get_file_summary(file_path):
    """Get AI summary of entire file"""
    pass

def get_function_summary(function_name):
    """Get AI summary of function"""
    pass

def get_dependencies(file_path):
    """Get file dependencies (who imports who)"""
    pass

def find_entry_points():
    """Find main entry points in codebase"""
    pass

def trace_call_chain(from_func, to_func):
    """Show path from one function to another"""
    pass
```

#### Step 4.3: Update System Prompt (Day 4)
**File:** `orc/ai_guidelines.py`

Tell AI it has access to summaries:
```python
SYSTEM_PROMPT = """
You have access to a complete codebase index with:
- Structure: files, functions, classes, imports
- Relationships: dependencies, call graphs
- AI Summaries: human-readable explanations of code

When a user asks about code:
1. First query the database for structure
2. Then get AI summaries for context
3. Only show actual code if they specifically ask

Example:
User: "What does login() do?"
You: Query for function + summary, then explain based on summary
"""
```

---

## Implementation Priority & Timeline

### ✅ MUST HAVE (Week 1) - Core Foundation
1. Database schema updates
2. Enhanced parser data extraction
3. Store imports/exports (make tables work!)
4. File dependencies
5. Basic indexing updates

### ✅ SHOULD HAVE (Week 2) - AI Layer
6. AI summarization client
7. Prompts for summarization
8. Integration with indexing
9. Summary storage and caching

### ✅ NICE TO HAVE (Week 3) - Polish
10. Enhanced CLI commands
11. AI tools integration
12. Better error handling
13. Performance optimization

---

## File Structure After Implementation

```
orc/
├── storage/
│   ├── graph_db.py              [MODIFIED] Add new tables
│   └── summary_cache.py         [NEW] Cache management
│
├── core/
│   ├── parallel_indexer.py      [MODIFIED] Add AI integration
│   ├── dependency_resolver.py   [NEW] Resolve dependencies
│   └── entry_point_detector.py  [NEW] Find entry points
│
├── parsers/
│   ├── python_parser.py         [MODIFIED] Extract more data
│   ├── javascript_parser.py     [MODIFIED] Extract more data
│   └── base_parser.py           [MODIFIED] Add common methods
│
├── ai_summarizer.py             [NEW] AI summarization
├── prompts/
│   └── summarization.py         [NEW] AI prompts
│
├── ai_tools.py                  [MODIFIED] Add new tools
├── ai_guidelines.py             [MODIFIED] Update system prompt
│
└── cli_main.py                  [MODIFIED] Enhanced commands
```

---

## Testing Strategy

### Unit Tests
```python
# test_enhanced_parser.py
def test_parser_extracts_imports():
    result = parser.parse_file("test_file.py")
    assert 'imports' in result
    assert len(result['imports']) > 0

def test_parser_detects_entry_points():
    result = parser.parse_file("main.py")
    assert result['entry_points']

# test_ai_summarizer.py
def test_summarize_function():
    summary = summarizer.summarize_function(code, "login", {})
    assert summary['summary_short']
    assert len(summary['summary_short']) < 100

# test_dependency_resolver.py
def test_resolve_function_call():
    resolved = resolver.resolve_call("login", "auth.py")
    assert resolved['file_path']
    assert resolved['line_number']
```

### Integration Tests
```python
# test_full_indexing.py
def test_index_with_ai():
    result = index_directory_parallel(test_dir, with_ai=True)
    assert 'summaries' in result
    assert len(result['summaries']) > 0

# test_ai_tools.py  
def test_ai_can_get_summaries():
    tools = ORCTools(db_path)
    result = tools.get_function_summary("login")
    assert result['summary']
```

---

## Configuration

### Add to `.orcrc`
```yaml
# AI Summarization Settings
ai_summarization:
  enabled: false              # Off by default
  provider: groq              # Default provider (free)
  model: llama3-70b          # Default model
  batch_size: 10             # Functions per request
  cache_summaries: true      # Cache to avoid regeneration
  
# What to summarize
summarize:
  functions: true
  classes: true
  files: true
  
# Cost control
limits:
  max_cost_per_run: 5.0      # Max $5 per indexing
  max_tokens_per_request: 4000
```

---

## Usage After Implementation

### Developer Experience

#### 1. First Time Index (with AI)
```bash
$ orc init
$ orc index --with-ai

Indexing: /path/to/project
Database: .orc/index.db

[1/3] Parsing files...
  + Indexed 87 files
  + Found 155 functions
  + Found 85 classes
  + Extracted 234 imports

[2/3] Resolving dependencies...
  + Built dependency graph
  + Found 12 entry points
  + Detected 3 circular dependencies

[3/3] Generating AI summaries...
  + Summarized 155 functions
  + Summarized 85 classes
  + Summarized 87 files
  + Cost: $0.85

Complete! Database ready.
```

#### 2. ORC AI Uses Enhanced Data
```bash
$ orc

> What does the authentication system do?

[ORC AI queries database + summaries]

Based on the codebase:

auth.py handles authentication. Here's the summary:
"Manages user login, logout, and session handling. 
 Implements rate limiting (max 3 attempts) and 
 password validation with bcrypt."

Key functions:
- login() - Authenticates credentials, creates session
- logout() - Ends session and clears cookies
- validate_password() - Checks password strength
- reset_password() - Sends reset email with token

The auth module is imported by:
- api.py (for API endpoints)
- web_routes.py (for web pages)
- admin.py (for admin panel)

Entry point: api.py calls auth.login() on POST /login

Would you like to see the actual code or dive deeper?
```

#### 3. Enhanced `orc find`
```bash
$ orc find login

┌──────────────────────────────────────────────────────┐
│ Function: login()                                    │
│ File: auth.py:45-76                                  │
│ Complexity: 8                                        │
│                                                      │
│ Summary:                                             │
│ "Authenticates user credentials and creates session. │
│  Implements rate limiting (max 3 attempts per 10min).│
│  Returns session token on success."                  │
│                                                      │
│ Business Rules:                                      │
│   - Email must exist in database                     │
│   - Password verified with bcrypt                    │
│   - Account locked after 3 failed attempts           │
│                                                      │
│ Called by:                                           │
│   - api.login_endpoint() (api.py:123)                │
│   - web_routes.handle_login() (routes.py:45)         │
│                                                      │
│ Calls:                                               │
│   - database.get_user() (database.py:89)             │
│   - security.verify_password() (security.py:34)      │
└──────────────────────────────────────────────────────┘
```

---

## Rollout Strategy

### Phase 1: Foundation (Week 1)
✅ Core developers use: Enhanced database structure
✅ No AI yet: Just better structural data
✅ Benefits: Better navigation, accurate dead code detection

### Phase 2: AI Layer (Week 2)
✅ Optional AI: Use `--with-ai` flag
✅ Beta testers: Try AI summaries
✅ Feedback: Improve prompt quality

### Phase 3: Integration (Week 3)
✅ ORC AI: Uses summaries automatically
✅ CLI: Shows summaries in all commands
✅ Production: Ready for company use

---

## Success Metrics

### Before Implementation:
- Time to understand new code: 2-4 hours
- Queries return: Structure only
- Dead code detection: 70% accuracy

### After Implementation:
- Time to understand new code: 10-15 minutes (95% reduction)
- Queries return: Structure + summaries
- Dead code detection: 95% accuracy
- AI cost: $1-2 per 10k functions (one-time)

---

## Next Steps

1. ✅ Get approval for implementation plan
2. ✅ Start with Phase 1 (database schema)
3. ✅ Test with small codebase
4. ✅ Roll out Phase 2 (AI integration)
5. ✅ Polish and optimize
6. ✅ (Later) Build web dashboard if needed

---

Ready to start implementation?
