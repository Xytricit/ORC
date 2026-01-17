# Enhanced Parser Design - Full 22-Section Vision

**Date:** 2026-01-16
**Status:** Design Phase - Risk It For The Biscuit! 🍪
**Goal:** Make parsers collect ALL data needed for complete 22-section knowledge base

---

## Philosophy

**Current parsers are "syntax parsers" - they extract structure.**
**Enhanced parsers will be "semantic parsers" - they extract meaning.**

---

## Enhanced Parser Output Structure

```python
{
    # Section 1: File Registry
    'files': {
        path: {
            'language': str,
            'loc': int,
            'file_type': str,  # NEW: 'source', 'config', 'test', 'doc'
            'module': str,  # NEW: which module/package
            'purpose': str  # NEW: brief description (AI Backend will enhance)
        }
    },
    
    # Section 2: Symbol Index (Enhanced)
    'functions': {
        func_id: {
            # Existing
            'name': str,
            'line_start': int,
            'line_end': int,
            'complexity': int,
            'parameters': list,
            'calls': list,
            'code': str,
            'is_exported': bool,
            'decorators': list,
            'docstring': str,
            'is_async': bool,
            
            # NEW: Enhanced metadata
            'return_type': str,  # Type annotation
            'raises': list,  # Exceptions raised
            'side_effects': list,  # DB calls, HTTP, files, etc.
            'purpose': str,  # Brief description
            'is_public': bool,  # Public API vs internal
            'is_tested': bool,  # Has test coverage
        }
    },
    
    'classes': {
        class_id: {
            # Existing
            'name': str,
            'line_start': int,
            'line_end': int,
            'methods': list,
            'base_classes': list,
            
            # NEW
            'properties': list,  # Class properties
            'is_data_model': bool,  # Is this just data?
            'is_abstract': bool,
            'purpose': str
        }
    },
    
    'constants': {},  # NEW: Global constants/config
    'enums': {},      # NEW: Enumerations
    'types': {},      # NEW: Type aliases
    
    # Section 3: Data Models & Schemas (NEW)
    'data_models': {
        model_id: {
            'name': str,
            'fields': [
                {
                    'name': str,
                    'type': str,
                    'required': bool,
                    'default': any,
                    'description': str
                }
            ],
            'purpose': str,
            'db_table': str,  # Mapped database table
        }
    },
    
    # Section 4: Entry Points & Execution Flow (Enhanced)
    'entry_points': {
        'main': [(type, line)],  # __main__, main()
        'api_endpoints': [
            {
                'route': str,
                'method': str,  # GET, POST, etc.
                'handler': str,  # Function name
                'line': int,
                'auth_required': bool
            }
        ],
        'event_listeners': [],
        'cron_jobs': [],
        'cli_commands': []
    },
    
    # Section 5: State Management (NEW)
    'state_management': {
        'database_queries': [
            {
                'query_type': str,  # SELECT, INSERT, etc.
                'table': str,
                'function': str,
                'line': int
            }
        ],
        'cache_usage': [
            {
                'operation': str,  # get, set, delete
                'key': str,
                'function': str,
                'line': int
            }
        ],
        'file_operations': [
            {
                'operation': str,  # read, write
                'path': str,
                'function': str,
                'line': int
            }
        ]
    },
    
    # Section 6: Dependencies (Enhanced)
    'imports_detailed': [
        {
            'statement': str,
            'line': int,
            'what': str,
            'is_external': bool,  # NEW
            'library_name': str,  # NEW
            'purpose': str  # NEW: Why this import?
        }
    ],
    
    # Section 7: Error Handling (NEW)
    'error_handling': {
        'try_except_blocks': [
            {
                'exceptions': list,  # Types caught
                'function': str,
                'line': int,
                'has_recovery': bool
            }
        ],
        'raises': [
            {
                'exception_type': str,
                'function': str,
                'line': int,
                'condition': str  # Why raised
            }
        ]
    },
    
    # Section 8: Configuration (NEW)
    'configuration': {
        'env_vars': [
            {
                'key': str,
                'default': any,
                'used_in': str,  # Function
                'line': int
            }
        ],
        'config_keys': [
            {
                'key': str,
                'source': str,  # config.yaml, .env, etc.
                'used_in': str,
                'line': int
            }
        ],
        'feature_flags': []
    },
    
    # Section 9: Cross-Cutting Concerns (NEW)
    'cross_cutting': {
        'auth_checks': [
            {
                'type': str,  # decorator, call
                'function': str,
                'line': int
            }
        ],
        'logging': [
            {
                'level': str,  # info, error, etc.
                'function': str,
                'line': int
            }
        ],
        'caching': [
            {
                'decorator': str,
                'function': str,
                'line': int
            }
        ],
        'validation': []
    },
    
    # Section 14: Side Effects (NEW)
    'side_effects': {
        'external_apis': [
            {
                'url': str,
                'method': str,
                'function': str,
                'line': int
            }
        ],
        'email_sends': [],
        'message_queue': [],
        'background_jobs': []
    },
    
    # Section 15: Concurrency (NEW)
    'concurrency': {
        'async_functions': list,  # Already have this
        'locks': [
            {
                'type': str,
                'resource': str,
                'function': str,
                'line': int
            }
        ],
        'thread_usage': []
    },
    
    # Section 17: Security (NEW)
    'security': {
        'sql_injection_risks': [
            {
                'query': str,
                'function': str,
                'line': int,
                'risk_level': str
            }
        ],
        'xss_risks': [],
        'secrets': [
            {
                'type': str,  # hardcoded password, etc.
                'location': str,
                'line': int
            }
        ]
    },
    
    # Sections 10-13, 16, 18-22: Handled by AI Backend
    # These need intelligence, not just parsing
}
```

---

## Detection Strategies by Section

### Section 4: API Endpoints
**Python (FastAPI/Flask/Django):**
```python
# FastAPI
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    pass

# Flask
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    pass

# Django
# In urls.py: path('users/<int:user_id>/', views.get_user)
```

**Detection Strategy:**
1. Find decorators: `@app.get`, `@app.post`, `@app.route`
2. Extract route pattern from decorator argument
3. Extract HTTP method
4. Link to handler function
5. Check for auth decorators (`@login_required`)

**JavaScript (Express/Fastify):**
```javascript
app.get('/users/:userId', async (req, res) => {
    // ...
});

router.post('/users', authMiddleware, createUser);
```

**Detection Strategy:**
1. Find `app.get`, `app.post`, `router.*` patterns
2. Extract route and handler
3. Check for middleware (auth)

---

### Section 5: State Management - Database
**Python (SQLAlchemy/Django ORM):**
```python
# SQLAlchemy
User.query.filter_by(id=user_id).first()
db.session.add(user)
db.session.commit()

# Django ORM
User.objects.get(id=user_id)
User.objects.filter(status='active')

# Raw SQL
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Detection Strategy:**
1. Find patterns: `.query`, `.objects`, `cursor.execute`
2. Identify table name
3. Determine operation type (SELECT, INSERT, UPDATE, DELETE)
4. Track which function makes the query

**JavaScript (Sequelize/TypeORM/Raw):**
```javascript
await User.findOne({ where: { id: userId } });
await db.query("SELECT * FROM users WHERE id = $1", [userId]);
```

---

### Section 7: Error Handling
**Python:**
```python
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Failed: {e}")
    return default_value
except Exception:
    raise CustomError("Operation failed")
```

**Detection Strategy:**
1. Find all `try` blocks
2. Extract exception types from `except`
3. Check if there's recovery logic (not just re-raise)
4. Track `raise` statements

**JavaScript:**
```javascript
try {
    await riskyOperation();
} catch (error) {
    if (error instanceof ValidationError) {
        return { error: error.message };
    }
    throw error;
}
```

---

### Section 8: Configuration
**Python:**
```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")
API_KEY = os.environ["API_KEY"]
DEBUG = config.get("debug", False)
```

**Detection Strategy:**
1. Find `os.getenv`, `os.environ[]`, `config.get`
2. Extract key name
3. Extract default value if present
4. Track usage location

**JavaScript:**
```javascript
const DATABASE_URL = process.env.DATABASE_URL || 'default';
const config = require('./config');
```

---

### Section 9: Auth Checks
**Python:**
```python
@login_required
@require_permission("admin")
def admin_view():
    pass

if not current_user.is_authenticated:
    raise Unauthorized()
```

**Detection Strategy:**
1. Find auth decorators
2. Find auth check conditionals
3. Track permission requirements

---

### Section 14: Side Effects - External APIs
**Python:**
```python
import requests
response = requests.post("https://api.stripe.com/charges", json=data)
```

**Detection Strategy:**
1. Find HTTP library imports (`requests`, `httpx`, `aiohttp`)
2. Track all `.get`, `.post`, etc. calls
3. Extract URLs
4. Note which function makes the call

**JavaScript:**
```javascript
await fetch('https://api.stripe.com/charges', { method: 'POST' });
await axios.post('https://api.stripe.com/charges', data);
```

---

### Section 17: Security - SQL Injection
**Python:**
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"  # BAD!
cursor.execute(query)

# SAFE
query = "SELECT * FROM users WHERE id = ?"  # GOOD
cursor.execute(query, (user_id,))
```

**Detection Strategy:**
1. Find SQL query strings
2. Check if using f-strings or string concatenation
3. Flag as high risk if variables embedded directly
4. Mark safe if using parameterized queries

---

## Implementation Plan

### Phase 1: Extend Base Parser (1 session)
Add new methods to `BaseParser`:
```python
class BaseParser(ABC):
    # Existing
    @abstractmethod
    def parse_file(self, path: Path) -> Dict[str, Any]:
        pass
    
    # NEW: Semantic extraction methods
    def extract_api_endpoints(self, tree, source) -> List[Dict]:
        """Extract API route definitions."""
        pass
    
    def extract_database_queries(self, tree, source) -> List[Dict]:
        """Extract database queries and ORM calls."""
        pass
    
    def extract_error_handling(self, tree, source) -> Dict:
        """Extract try/except blocks and raises."""
        pass
    
    def extract_config_usage(self, tree, source) -> Dict:
        """Extract env var and config usage."""
        pass
    
    def extract_side_effects(self, tree, source) -> Dict:
        """Extract external API calls, emails, etc."""
        pass
    
    def extract_security_risks(self, tree, source) -> Dict:
        """Detect SQL injection, XSS risks, hardcoded secrets."""
        pass
```

---

### Phase 2: Enhance Python Parser (2 sessions)
Implement all extraction methods for Python:
1. API endpoints (FastAPI, Flask, Django patterns)
2. Database queries (SQLAlchemy, Django ORM, raw SQL)
3. Error handling (try/except, raises)
4. Config usage (os.getenv, config files)
5. Side effects (requests, email, queues)
6. Security (SQL injection, secrets)

---

### Phase 3: Enhance JS/TS Parser (2 sessions)
Implement extraction for JavaScript/TypeScript:
1. API endpoints (Express, Fastify patterns)
2. Database queries (Sequelize, TypeORM, raw)
3. Error handling (try/catch, throws)
4. Config usage (process.env, config files)
5. Side effects (fetch, axios)
6. Security checks

---

### Phase 4: Extend Database Schema (1 session)
Add new tables for new sections:
```sql
CREATE TABLE api_endpoints (...);
CREATE TABLE database_queries (...);
CREATE TABLE error_handlers (...);
CREATE TABLE config_usage (...);
CREATE TABLE side_effects (...);
CREATE TABLE security_risks (...);
CREATE TABLE data_models (...);
-- etc.
```

---

### Phase 5: Implement AI Backend (2-3 sessions)
Build intelligence layer that:
1. Reads raw parser output
2. Adds semantic understanding:
   - Purpose of functions/modules
   - Business logic descriptions
   - Risk assessment
   - Performance implications
3. Stores in `code_summaries` and `ai_insights` tables

---

### Phase 6: Build TOC System (1 session)
Generate Table of Contents for fast navigation:
1. Index all sections
2. Create keyword map
3. Enable fast section jumping
4. Optimize for AI Frontend queries

---

### Phase 7: Wire Everything (1 session)
Connect all pieces:
1. Parser registry
2. `orc index` calls parsers → stores in extended DB
3. AI Backend runs after parsing
4. TOC generated after AI Backend
5. CLI commands query extended DB
6. Chat uses TOC for navigation

---

## Total Timeline

**Estimated Sessions:**
- Phase 1: 1 session
- Phase 2: 2 sessions
- Phase 3: 2 sessions
- Phase 4: 1 session
- Phase 5: 2-3 sessions
- Phase 6: 1 session
- Phase 7: 1 session

**Total: 10-11 focused sessions**

---

## Risk Mitigation

**Risk 1: Too complex, takes forever**
**Mitigation:** Build one section at a time, test incrementally

**Risk 2: Parsers miss patterns**
**Mitigation:** Start with major frameworks (FastAPI, Flask, Express), expand later

**Risk 3: AI Backend is hard**
**Mitigation:** Use simple prompts first, enhance later

**Risk 4: Database gets huge**
**Mitigation:** Add indexes, use efficient storage, test with large codebases

---

## Success Metrics

**Phase 1 Success:**
- BaseParser has all method signatures
- Clear contract for implementations

**Phase 2-3 Success:**
- Python parser extracts 15+ sections
- JS/TS parser extracts 15+ sections
- Test coverage >80%

**Phase 4 Success:**
- All tables created
- Can store all extracted data
- Efficient queries

**Phase 5 Success:**
- AI Backend adds meaningful context
- No hallucination (only facts from code)
- Performance acceptable (<5s per file)

**Phase 6 Success:**
- TOC generated in <10s
- Fast keyword lookup (<100ms)
- Efficient section navigation

**Phase 7 Success:**
- `orc index` populates full database
- All 22 sections have data
- CLI commands return rich results
- Chat answers complex questions accurately

---

## Next Session Start

**Goal:** Implement Phase 1 - Extend Base Parser

**Tasks:**
1. Add new abstract methods to BaseParser
2. Update method signatures
3. Document expected return structures
4. Create test stubs

**Files to modify:**
- `orc/parsers/base_parser.py`
- `orc/parsers/all_parsers.py`

**Ready to build? 🚀**
