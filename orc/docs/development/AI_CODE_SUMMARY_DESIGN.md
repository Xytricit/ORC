# AI-Powered Code Summaries - Design Document

## The Problem We're Solving

**Current State:**
- Database tells you WHERE the code is ✅
- Database tells you WHAT it calls ✅
- But you still need to READ the code to understand WHAT IT DOES ❌

**New Idea:**
- Store AI-generated summaries of code
- Developer reads summary instead of code
- Only read actual code when implementing changes

---

## The Vision

### Before (With Database Only):
```
Developer: "What does calculate_discount() do?"
Database: "It's in pricing.py line 234, calls validate_coupon() and apply_rules()"
Developer: *Opens file, reads 50 lines of code to understand logic*
Time: 5-10 minutes
```

### After (With Database + AI Summaries):
```
Developer: "What does calculate_discount() do?"
Database + AI: 
  Location: pricing.py:234
  Summary: "Validates coupon code, checks expiration date, applies percentage 
           or fixed discount based on coupon type, handles min purchase amount,
           returns discounted price or error if invalid"
  Inputs: cart_total (float), coupon_code (string)
  Outputs: discounted_price (float) or raises InvalidCouponError
  Business Rules: 
    - Expired coupons rejected
    - Min purchase $50 for percentage discounts
    - Max discount $100 for fixed discounts
Developer: *Understands without reading code!*
Time: 30 seconds
```

**Time savings: 90%+ for understanding code!**

---

## Architecture: Parser + AI Integration

### Current Flow (Without AI):
```
1. Parser reads file
   ↓
2. Extracts functions/classes/imports
   ↓
3. Stores in database
   ↓
4. DONE
```

### New Flow (With AI):
```
1. Parser reads file
   ↓
2. Extracts functions/classes/imports
   ↓
3. For each function/class:
   → Send code to AI
   → AI generates summary
   → Store summary in database
   ↓
4. DONE (with summaries!)
```

---

## Database Schema Changes

### New Tables:

#### 1. Code Summaries
```sql
CREATE TABLE code_summaries (
    target_type TEXT,              -- 'function', 'class', 'file', 'module'
    target_id TEXT,                -- Function ID, class ID, etc.
    
    -- AI Generated Content
    summary_short TEXT,            -- One-line: "Validates user credentials"
    summary_detailed TEXT,         -- Paragraph: Full explanation
    purpose TEXT,                  -- "Why this exists"
    inputs TEXT,                   -- "What it takes"
    outputs TEXT,                  -- "What it returns"
    side_effects TEXT,             -- "What it changes"
    business_rules TEXT,           -- "Important logic/rules"
    
    -- Code characteristics
    complexity_explanation TEXT,   -- "Why this is complex"
    edge_cases TEXT,              -- "Special cases handled"
    assumptions TEXT,              -- "What it assumes"
    
    -- Metadata
    ai_model TEXT,                 -- "gpt-4", "claude-3", etc.
    confidence REAL,               -- 0.0-1.0
    generated_at TIMESTAMP,
    tokens_used INTEGER,
    
    -- Versioning
    code_hash TEXT,                -- Hash of the code summarized
    needs_refresh BOOLEAN          -- True if code changed
);
```

#### 2. AI Insights
```sql
CREATE TABLE ai_insights (
    target_id TEXT,
    insight_type TEXT,             -- 'smell', 'pattern', 'suggestion', 'warning'
    
    title TEXT,                    -- "Potential N+1 Query Problem"
    description TEXT,              -- Detailed explanation
    severity TEXT,                 -- 'critical', 'high', 'medium', 'low'
    
    suggested_fix TEXT,            -- How to improve
    code_example TEXT,             -- Example of better code
    
    ai_model TEXT,
    confidence REAL,
    generated_at TIMESTAMP
);
```

#### 3. Cross-References (AI-Generated)
```sql
CREATE TABLE ai_cross_references (
    source_id TEXT,
    target_id TEXT,
    relationship_type TEXT,        -- 'similar_to', 'duplicates', 'related_to'
    
    explanation TEXT,              -- "Both implement sorting algorithms"
    similarity_score REAL,         -- 0.0-1.0
    
    ai_model TEXT,
    generated_at TIMESTAMP
);
```

---

## What AI Summarizes

### 1. **Functions**

#### Input to AI:
```python
def calculate_discount(cart_total, coupon_code):
    """Apply discount coupon to cart total."""
    coupon = Coupon.get_by_code(coupon_code)
    
    if not coupon or coupon.expired:
        raise InvalidCouponError("Coupon invalid or expired")
    
    if coupon.min_purchase and cart_total < coupon.min_purchase:
        raise InvalidCouponError(f"Minimum purchase ${coupon.min_purchase} required")
    
    if coupon.discount_type == 'percentage':
        discount = cart_total * (coupon.value / 100)
        discount = min(discount, coupon.max_discount or float('inf'))
    else:
        discount = coupon.value
    
    return max(0, cart_total - discount)
```

#### AI Generates:
```json
{
  "summary_short": "Applies discount coupon to shopping cart total",
  
  "summary_detailed": "Validates coupon code, checks expiration and minimum purchase requirements, calculates discount based on percentage or fixed amount type, applies max discount cap for percentage coupons, returns final discounted price",
  
  "purpose": "Handles coupon-based discounts during checkout",
  
  "inputs": "cart_total (float) - Current cart value, coupon_code (str) - Discount code entered by user",
  
  "outputs": "float - Discounted cart total, never negative",
  
  "side_effects": "None - pure calculation function",
  
  "business_rules": [
    "Expired coupons are rejected",
    "Minimum purchase amount enforced if set",
    "Percentage discounts capped at max_discount value",
    "Final price cannot go below zero"
  ],
  
  "edge_cases": [
    "Handles missing max_discount (treats as unlimited)",
    "Ensures result never negative",
    "Raises InvalidCouponError for invalid/expired coupons"
  ],
  
  "complexity_explanation": "Low complexity (4) - straightforward validation and calculation logic",
  
  "assumptions": [
    "Coupon.get_by_code() returns None if not found",
    "Coupon object has expired, min_purchase, discount_type, value, max_discount attributes"
  ]
}
```

---

### 2. **Classes**

#### Input to AI:
```python
class UserManager:
    """Manages user accounts and authentication."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = {}
    
    def create_user(self, email, password):
        # Hash password, create user, send welcome email
        ...
    
    def authenticate(self, email, password):
        # Verify credentials, return user or None
        ...
    
    def get_user(self, user_id):
        # Get user by ID with caching
        ...
```

#### AI Generates:
```json
{
  "summary_short": "Manages user account creation, authentication, and retrieval",
  
  "summary_detailed": "Central class for user management operations. Handles user creation with password hashing, authenticates login attempts, retrieves user data with caching layer. Uses database connection for persistence and in-memory cache for performance.",
  
  "purpose": "Provide a single interface for all user-related operations across the application",
  
  "key_methods": [
    "create_user() - Creates new user account with hashed password",
    "authenticate() - Validates login credentials",
    "get_user() - Retrieves user with caching"
  ],
  
  "design_pattern": "Manager/Service pattern - encapsulates business logic",
  
  "dependencies": "Requires database connection, uses internal cache dictionary",
  
  "state": "Maintains database connection and user cache",
  
  "thread_safety": "NOT thread-safe - cache not synchronized"
}
```

---

### 3. **Files/Modules**

#### Input to AI:
```python
# File: auth.py
"""Authentication and authorization module."""

def login(email, password):
    ...

def logout(session_id):
    ...

def check_permission(user, action):
    ...

class SessionManager:
    ...
```

#### AI Generates:
```json
{
  "summary_short": "Authentication and authorization utilities",
  
  "summary_detailed": "Core authentication module providing login/logout functionality and permission checking. Manages user sessions and access control. Used throughout application for securing endpoints and features.",
  
  "purpose": "Centralize all authentication and authorization logic",
  
  "main_components": [
    "login/logout functions - Session management",
    "check_permission() - Access control",
    "SessionManager class - Session lifecycle"
  ],
  
  "public_api": [
    "login(email, password)",
    "logout(session_id)",
    "check_permission(user, action)"
  ],
  
  "used_by": "All API endpoints, web routes, background jobs",
  
  "architecture_role": "Core security layer - business logic tier"
}
```

---

## Integration with Parsers

### Modified Parser Flow:

```python
class EnhancedPythonParser(PythonParser):
    def __init__(self, ai_client=None):
        super().__init__()
        self.ai_client = ai_client
    
    def parse_file(self, file_path):
        # Step 1: Normal parsing
        result = super().parse_file(file_path)
        
        # Step 2: AI summarization (if AI enabled)
        if self.ai_client:
            result['summaries'] = self._generate_summaries(result)
            result['insights'] = self._generate_insights(result)
        
        return result
    
    def _generate_summaries(self, parse_result):
        summaries = {}
        
        # Summarize each function
        for func_id, func_data in parse_result['functions'].items():
            summary = self.ai_client.summarize_function(
                code=func_data['code'],
                name=func_data['name'],
                context=func_data
            )
            summaries[func_id] = summary
        
        # Summarize each class
        for class_id, class_data in parse_result['classes'].items():
            summary = self.ai_client.summarize_class(
                code=class_data['code'],
                name=class_data['name'],
                methods=class_data['methods']
            )
            summaries[class_id] = summary
        
        # Summarize the file
        summaries['file'] = self.ai_client.summarize_file(
            file_path=parse_result['file_path'],
            functions=parse_result['functions'],
            classes=parse_result['classes']
        )
        
        return summaries
    
    def _generate_insights(self, parse_result):
        """Let AI find code smells, patterns, suggestions"""
        insights = []
        
        for func_id, func_data in parse_result['functions'].items():
            if func_data['complexity'] > 15:
                insight = self.ai_client.analyze_complexity(
                    code=func_data['code'],
                    complexity=func_data['complexity']
                )
                insights.append(insight)
        
        return insights
```

---

## AI Client Design

### Smart Batching System:

```python
class AICodeSummarizer:
    def __init__(self, provider='groq'):  # Fast and cheap
        self.client = get_ai_client(provider)
        self.batch = []
        self.batch_size = 10  # Process 10 functions at once
    
    def summarize_function(self, code, name, context):
        """Add to batch, process when batch is full"""
        self.batch.append({
            'type': 'function',
            'code': code,
            'name': name,
            'context': context
        })
        
        if len(self.batch) >= self.batch_size:
            return self._process_batch()
    
    def _process_batch(self):
        """Send entire batch to AI in one request (faster + cheaper)"""
        prompt = self._build_batch_prompt(self.batch)
        
        response = self.client.chat(
            messages=[
                {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Consistent summaries
        )
        
        summaries = self._parse_batch_response(response)
        self.batch = []
        return summaries
```

### Cost-Effective Strategy:

1. **Use cheap/fast AI for summaries** (Groq with Llama 3, ~free)
2. **Batch multiple functions per request** (10x faster, 10x cheaper)
3. **Cache summaries** (only regenerate if code changes)
4. **Progressive summarization** (summarize incrementally as you index)

---

## Prompts for AI

### Function Summary Prompt:
```
You are a code documentation expert. Analyze this function and provide:

1. One-line summary (max 80 chars)
2. Detailed explanation (2-3 sentences)
3. Purpose (why it exists)
4. Inputs (parameters and types)
5. Outputs (return value and type)
6. Side effects (database writes, API calls, file I/O, etc.)
7. Business rules (important logic)
8. Edge cases handled
9. Assumptions made

Function:
```python
{code}
```

Respond in JSON format:
{
  "summary_short": "...",
  "summary_detailed": "...",
  ...
}
```

### Class Summary Prompt:
```
Analyze this class and provide:

1. One-line summary
2. Detailed explanation
3. Purpose (design intent)
4. Key methods (list with brief descriptions)
5. Design pattern used (if any)
6. Dependencies
7. State management
8. Thread safety notes

Class:
```python
{code}
```
```

### Code Insight Prompt:
```
You are a senior code reviewer. Analyze this code for:

1. Code smells
2. Performance issues
3. Security vulnerabilities
4. Best practice violations
5. Suggested improvements

For each issue found, provide:
- Severity (critical/high/medium/low)
- Description
- Suggested fix
- Example of better code

Code:
```python
{code}
```
```

---

## Performance & Cost

### Indexing 1000 Functions:

#### Without AI:
- Time: ~10 seconds (parsing only)
- Cost: $0

#### With AI (Naive approach - one request per function):
- Time: ~1000 seconds (1 sec per function)
- Cost: ~$5 (at $0.005 per function)
- **TOO SLOW!**

#### With AI (Smart batching - 10 functions per request):
- Time: ~100 seconds (0.1 sec per function)
- Cost: ~$1 (bulk discount)
- **ACCEPTABLE!**

#### With AI (Progressive + caching):
- Initial index: 100 seconds, $1
- Subsequent indexes: Only new/changed functions
- Daily incremental: ~5 seconds, $0.05
- **PERFECT!**

---

## Storage Impact

### Per Function Summary:
- Summary text: ~500 bytes
- Total metadata: ~1 KB

### For 10,000 Functions:
- Summaries: ~10 MB
- Indexes: ~5 MB
- **Total: ~15 MB (trivial!)**

---

## Usage Examples

### Example 1: Understanding Function

```python
# Developer query
result = db.query("""
    SELECT 
        f.name, 
        f.file_path, 
        f.line_start,
        s.summary_short,
        s.summary_detailed,
        s.inputs,
        s.outputs,
        s.business_rules
    FROM function_index f
    LEFT JOIN code_summaries s ON f.id = s.target_id
    WHERE f.name = 'calculate_discount'
""")

# Output:
{
    "name": "calculate_discount",
    "file": "pricing.py",
    "line": 234,
    "summary": "Applies discount coupon to shopping cart total",
    "details": "Validates coupon code, checks expiration...",
    "inputs": "cart_total (float), coupon_code (str)",
    "outputs": "float - discounted price",
    "rules": [
        "Expired coupons rejected",
        "Min purchase enforced",
        ...
    ]
}
```

**Developer now understands without reading code!**

---

### Example 2: Finding Similar Code

```python
# Find functions similar to current one
result = db.query("""
    SELECT 
        cr.target_id,
        fi.name,
        fi.file_path,
        cr.explanation,
        cr.similarity_score
    FROM ai_cross_references cr
    JOIN function_index fi ON cr.target_id = fi.id
    WHERE cr.source_id = 'pricing.py:calculate_discount'
      AND cr.relationship_type = 'similar_to'
    ORDER BY cr.similarity_score DESC
    LIMIT 5
""")

# Output: "These 5 functions do similar discount calculations"
```

**Helps identify duplication and opportunities for refactoring!**

---

### Example 3: AI-Powered Code Search

```python
# Natural language search
query = "Find functions that validate email addresses"

# AI converts to database query + semantic search
results = ai_search_engine.search(query)

# Returns:
[
    {
        "function": "validate_email()",
        "file": "validators.py",
        "summary": "Checks email format using regex",
        "relevance": 0.95
    },
    {
        "function": "check_user_email()",
        "file": "user_service.py",
        "summary": "Validates email and checks if unique",
        "relevance": 0.87
    }
]
```

---

## Implementation Plan

### Phase 1: Basic Summaries (Week 1)
1. Add `code_summaries` table
2. Integrate AI client with parsers
3. Generate summaries during indexing
4. Add `orc summarize` command

### Phase 2: Smart Features (Week 2)
5. Add batching for performance
6. Add caching (only summarize changed code)
7. Add `ai_insights` table
8. Generate code smell warnings

### Phase 3: Advanced Features (Week 3)
9. Add `ai_cross_references` table
10. Find duplicate/similar code
11. Natural language code search
12. AI-powered recommendations

---

## CLI Commands

### Generate Summaries:
```bash
orc summarize                    # Summarize all indexed code
orc summarize --file auth.py     # Summarize specific file
orc summarize --refresh          # Regenerate all summaries
```

### View Summaries:
```bash
orc explain calculate_discount   # Show AI summary + database info
orc search "email validation"    # Natural language search
orc insights                     # Show AI-detected issues
```

### Enhanced Existing Commands:
```bash
orc find complex --with-explanations   # Show WHY it's complex
orc report --with-insights             # Include AI insights
```

---

## Cost Analysis

### One-Time Indexing (10,000 functions):
- Using Groq (Llama 3): **FREE** (generous limits)
- Using OpenAI (GPT-3.5): ~$2
- Using Claude (Haiku): ~$1

### Incremental Updates (daily):
- Typically 50-100 functions change
- Cost: $0.01-0.10 per day
- **Trivial cost for huge value!**

---

## The Value Proposition

### Before (Database Only):
- Find code location: **30 seconds** ✅
- Understand what it does: **5-10 minutes** reading ❌
- Total: ~10 minutes per function

### After (Database + AI Summaries):
- Find code location: **30 seconds** ✅
- Understand what it does: **30 seconds** reading summary ✅
- Total: ~1 minute per function

### **Time Savings: 90%!**

For a team of 10 developers:
- Each dev saves: 2-3 hours/day
- Team saves: 20-30 hours/day
- Cost: ~$1/day for AI
- **ROI: 1000x!**

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ORC with AI                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Parser extracts code structure                      │
│           ↓                                             │
│  2. AI generates summaries (batched)                    │
│           ↓                                             │
│  3. Store in database                                   │
│           ↓                                             │
│  4. Developer queries                                   │
│           ↓                                             │
│  5. Get instant understanding                           │
│                                                         │
│  Database gives you:  WHERE + WHAT CONNECTS             │
│  AI gives you:        WHAT IT DOES + WHY                │
│                                                         │
│  Result: Understand million-line codebases WITHOUT      │
│          reading most of the code!                      │
└─────────────────────────────────────────────────────────┘
```

---

## VERDICT

### 🔥 **THIS IS THE KILLER FEATURE!**

**Database alone:** 90% time savings on navigation
**Database + AI summaries:** 95%+ time savings on EVERYTHING

**This makes ORC:**
- ✅ Better than GitHub Copilot for understanding code
- ✅ Better than Sourcegraph for navigation
- ✅ Competitive with Google's internal tools
- ✅ A product companies will PAY for

---

## Ready to Implement?

**Priority:**
1. **First:** Implement enhanced database schema (dependencies, imports, exports)
2. **Then:** Add AI summarization layer
3. **Result:** Complete code intelligence platform

**Want to start?**
