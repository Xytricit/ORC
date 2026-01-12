# ORC Stub Commands - Design Document

This document explains what the 3 stub commands (`delete`, `explain`, `optimize`) should do when fully implemented.

---

## 1. `orc delete` - Safe Code Deletion

### **Purpose**
Safely delete dead/unused code with automatic backups and confirmation.

### **Current Status**
⚠️ STUB - Shows warning message only

### **What It Should Do**

#### **Basic Usage**
```bash
orc delete                    # Interactive mode - shows dead code and asks what to delete
orc delete path/to/file.py    # Delete specific file
orc delete --finding-id D-12  # Delete specific finding by ID
orc delete --all-dead         # Delete all high-confidence dead code
```

#### **Features Needed**

1. **Safety First**
   - Create backup in `.orc/backups/` with timestamp
   - Show what will be deleted before doing it
   - Require confirmation (unless `--yes` flag)
   - Support `--dry-run` to preview without deleting

2. **Smart Deletion**
   - Delete entire files if completely unused
   - Delete individual functions/classes if file has mixed usage
   - Update imports in other files if needed
   - Handle edge cases (decorators, inheritance, etc.)

3. **Rollback Capability**
   - Keep backups for 30 days
   - Provide `orc restore` command to undo deletions
   - Log all deletions with timestamps

#### **Example Flow**
```bash
$ orc delete

Found 12 potentially unused code items:

High Confidence (Safe to Delete):
  [1] old_utils.py (entire file) - 100% confidence
  [2] legacy_parser() in utils.py - 95% confidence
  [3] unused_helper() in helpers.py - 90% confidence

Medium Confidence (Review Recommended):
  [4] might_be_used() in lib.py - 75% confidence
  ...

Select items to delete (comma-separated): 1,2
Create backup? [Y/n]: y

✓ Backup created: .orc/backups/2026-01-12_18-45-23/
✓ Deleted old_utils.py
✓ Deleted legacy_parser() from utils.py

2 items deleted. Run 'orc restore' to undo.
```

#### **Implementation Requirements**

1. **Database Changes**
   - Add `findings` table to store dead code findings with persistent IDs
   - Add `deletions` table to track what was deleted and when
   - Schema:
     ```sql
     CREATE TABLE findings (
         id TEXT PRIMARY KEY,        -- e.g., "D-12"
         type TEXT,                  -- "dead_code", "unused_import", etc.
         target TEXT,                -- file path or function name
         confidence REAL,            -- 0.0 to 1.0
         reason TEXT,                -- why it's flagged
         discovered_at TIMESTAMP,
         status TEXT                 -- "open", "deleted", "ignored"
     );
     
     CREATE TABLE deletions (
         id INTEGER PRIMARY KEY,
         finding_id TEXT,
         backup_path TEXT,
         deleted_at TIMESTAMP,
         deleted_by TEXT,            -- user/system
         restored_at TIMESTAMP NULL
     );
     ```

2. **Code Changes Needed**
   - Implement file backup logic (copy to `.orc/backups/`)
   - Implement function deletion (parse file, remove function, update file)
   - Implement import cleanup (find and remove unused imports)
   - Add `--dry-run` simulation mode

3. **Safety Checks**
   - Verify code isn't used by other projects (monorepo awareness)
   - Check for dynamic usage (eval, getattr, etc.)
   - Warn about external dependencies

---

## 2. `orc explain` - Detailed Finding Explanation

### **Purpose**
Explain WHY something was flagged as dead code, complex, or problematic.

### **Current Status**
⚠️ STUB - Shows message about needing persistent IDs

### **What It Should Do**

#### **Basic Usage**
```bash
orc explain D-12              # Explain finding D-12
orc explain C-5               # Explain complexity finding C-5
orc explain file.py           # Explain all findings for a file
orc explain my_function       # Explain findings for a specific function
```

#### **Finding ID Prefixes**
- `D-###` = Dead code finding
- `C-###` = Complexity finding
- `S-###` = Security finding
- `P-###` = Performance finding

#### **Features Needed**

1. **Dead Code Explanation**
   - Show where function is defined
   - List all files that were scanned for usage
   - Show call graph (what calls what)
   - Explain why no usage was found
   - Show dynamic usage patterns checked

2. **Complexity Explanation**
   - Show cyclomatic complexity calculation
   - Highlight complex code paths
   - Suggest refactoring strategies
   - Show comparison with codebase average

3. **Interactive Mode**
   - Show code snippet with highlighting
   - Offer to open file in editor
   - Suggest next actions

#### **Example Output**
```bash
$ orc explain D-12

Finding: D-12 (Dead Code)
═══════════════════════════════════════════════════════════

Target:     old_parser() in src/utils/legacy.py
Confidence: 95%
Status:     Open

Why This Was Flagged:
────────────────────────────────────────────────────────────
✗ No direct calls found in 87 scanned files
✗ Not exported from module
✗ No dynamic usage patterns detected (eval, getattr, etc.)
✗ Not referenced in tests
✗ Last modified: 6 months ago

Call Graph Analysis:
────────────────────────────────────────────────────────────
old_parser() 
  ├─ Called by: (none)
  └─ Calls: json.loads(), validate_schema()

Files Scanned:
────────────────────────────────────────────────────────────
✓ 87 Python files in codebase
✓ 12 test files
✓ 5 configuration files

Potential False Positive Indicators:
────────────────────────────────────────────────────────────
! Function name contains 'legacy' (might be kept for compatibility)
! File is in 'utils' directory (might be utility function)

Suggested Actions:
────────────────────────────────────────────────────────────
1. orc delete D-12              Delete this code
2. orc ignore D-12              Keep this code (mark as intentional)
3. View code: src/utils/legacy.py:45-67

What would you like to do? [delete/ignore/view/cancel]:
```

#### **Implementation Requirements**

1. **Database Changes**
   - Store findings with detailed metadata
   - Track explanation history
   - Store user decisions (deleted, ignored, etc.)

2. **Code Changes Needed**
   - Generate detailed analysis for each finding type
   - Create call graph visualization (text-based)
   - Add file path resolution and line number tracking
   - Implement interactive prompt system

3. **AI Integration (Optional Enhancement)**
   - Use AI to provide natural language explanation
   - Suggest refactoring strategies
   - Explain code complexity in plain English

---

## 3. `orc optimize` - Optimization Suggestions

### **Purpose**
Analyze code and suggest performance, memory, and algorithmic optimizations.

### **Current Status**
⚠️ STUB - Shows message about feature being in development

### **What It Should Do**

#### **Basic Usage**
```bash
orc optimize                       # Scan entire codebase
orc optimize path/to/file.py       # Scan specific file
orc optimize --type performance    # Only performance issues
orc optimize --type memory         # Only memory issues
orc optimize --type algorithm      # Only algorithmic issues
```

#### **Optimization Types**

1. **Performance Optimizations**
   - Unnecessary loops
   - Inefficient string concatenation
   - Repeated function calls in loops
   - Missing caching opportunities
   - Slow I/O operations

2. **Memory Optimizations**
   - Large data structures kept in memory
   - Memory leaks (unclosed files, connections)
   - Unnecessary data copies
   - Generator vs list opportunities

3. **Algorithmic Optimizations**
   - O(n²) algorithms that could be O(n log n) or O(n)
   - Nested loops that could be optimized
   - Redundant computations
   - Better data structure choices

4. **Code Quality**
   - Duplicate code blocks
   - Overly complex conditionals
   - Long parameter lists
   - God classes/functions

#### **Example Output**
```bash
$ orc optimize

Optimization Analysis
═══════════════════════════════════════════════════════════

Found 8 optimization opportunities (estimated 40% speed improvement)

HIGH IMPACT (3 issues):
────────────────────────────────────────────────────────────

[P-1] Inefficient Loop in process_data() - data_processor.py:45
  Current:   O(n²) - nested loops
  Problem:   Iterating over same list twice
  Impact:    ~60% slower for large datasets
  
  Current Code:
    for item in items:
        for other in items:
            if item.matches(other):
                ...
  
  Suggested Fix:
    # Use set for O(1) lookup
    item_set = {item.id: item for item in items}
    for item in items:
        if item.id in item_set:
            ...
  
  Expected Improvement: 60% faster
  Estimated Time to Fix: 15 minutes
  
────────────────────────────────────────────────────────────

[P-2] Repeated Database Query - user_service.py:89
  Current:   Query executed in loop (N queries)
  Problem:   N+1 query problem
  Impact:    ~80% slower with database latency
  
  Current Code:
    for user_id in user_ids:
        user = db.get_user(user_id)  # Query per iteration!
        process(user)
  
  Suggested Fix:
    # Batch query
    users = db.get_users(user_ids)  # Single query
    for user in users:
        process(user)
  
  Expected Improvement: 80% faster
  Estimated Time to Fix: 5 minutes

────────────────────────────────────────────────────────────

[M-1] Memory Leak - file_handler.py:123
  Current:   File not closed in all code paths
  Problem:   File handle left open on exception
  Impact:    Memory leak over time
  
  Current Code:
    f = open(file_path)
    data = process(f.read())
    f.close()  # Not called if process() raises exception!
  
  Suggested Fix:
    with open(file_path) as f:
        data = process(f.read())
    # Automatically closed even on exception
  
  Expected Improvement: No memory leaks
  Estimated Time to Fix: 2 minutes


MEDIUM IMPACT (3 issues):
────────────────────────────────────────────────────────────
[A-1] Suboptimal Sort - report_generator.py:234
[P-3] String Concatenation in Loop - formatter.py:156
[M-2] Large List in Memory - data_loader.py:78

LOW IMPACT (2 issues):
────────────────────────────────────────────────────────────
[Q-1] Duplicate Code Block - utils.py:45,67
[Q-2] Complex Conditional - validator.py:123


Summary:
────────────────────────────────────────────────────────────
Total Issues: 8
Estimated Time to Fix All: 1.5 hours
Expected Performance Gain: 40-50%

Apply fixes? [y/N]:
```

#### **Implementation Requirements**

1. **Pattern Detection**
   - AST (Abstract Syntax Tree) analysis to detect patterns
   - Complexity analysis (already have this!)
   - Data flow analysis
   - Loop analysis

2. **Optimization Rules Database**
   - Store known anti-patterns and their fixes
   - Language-specific optimizations
   - Framework-specific optimizations

3. **Impact Estimation**
   - Heuristics for performance impact
   - Complexity reduction calculations
   - Memory usage estimates

4. **Code Changes Needed**
   - Add `optimization/detector.py` - pattern detection
   - Add `optimization/rules.py` - optimization rules
   - Add `optimization/suggester.py` - generate suggestions
   - Update database schema for optimization findings

5. **Database Schema**
   ```sql
   CREATE TABLE optimization_findings (
       id TEXT PRIMARY KEY,           -- e.g., "P-1", "M-1", "A-1"
       type TEXT,                     -- "performance", "memory", "algorithm", "quality"
       severity TEXT,                 -- "high", "medium", "low"
       title TEXT,                    -- short description
       description TEXT,              -- detailed explanation
       file_path TEXT,
       line_start INTEGER,
       line_end INTEGER,
       current_code TEXT,             -- code snippet
       suggested_fix TEXT,            -- improved code
       expected_improvement TEXT,     -- "60% faster"
       estimated_time_minutes INTEGER, -- time to fix
       status TEXT,                   -- "open", "fixed", "ignored"
       discovered_at TIMESTAMP
   );
   ```

---

## Implementation Priority

### **Phase 1: Foundation (Required for all commands)**
1. Add `findings` table to database
2. Implement persistent finding IDs
3. Update `orc find dead/complex` to store findings with IDs
4. Add backup/restore infrastructure

### **Phase 2: `orc explain` (Easiest to implement)**
1. Query findings from database by ID
2. Generate detailed explanation from stored data
3. Add call graph visualization
4. Add interactive prompts

### **Phase 3: `orc delete` (Medium difficulty)**
1. Implement backup logic
2. Implement file deletion
3. Implement function deletion (AST manipulation)
4. Add rollback capability
5. Add safety checks and confirmations

### **Phase 4: `orc optimize` (Most complex)**
1. Implement pattern detection engine
2. Build optimization rules database
3. Add AST-based code analysis
4. Implement suggestion generation
5. Add impact estimation
6. Add auto-fix capability (optional)

---

## Estimated Implementation Time

- **`orc explain`**: 4-6 hours (mostly data retrieval and formatting)
- **`orc delete`**: 8-12 hours (needs file manipulation and safety features)
- **`orc optimize`**: 20-30 hours (complex pattern detection and analysis)

**Total**: ~32-48 hours of focused development

---

## Testing Requirements

Each command needs:
1. Unit tests for core logic
2. Integration tests with real code
3. Safety tests (for delete command)
4. Edge case handling
5. Performance tests for large codebases

---

## Questions to Answer Before Implementation

1. **For `delete`**:
   - How long should backups be kept?
   - Should we support Git integration (create commits)?
   - What if deleted code is used by external projects?

2. **For `explain`**:
   - Should we use AI for natural language explanations?
   - How much detail is too much?
   - Should we support multiple output formats (JSON, Markdown)?

3. **For `optimize`**:
   - Should we auto-apply fixes or just suggest them?
   - How conservative should suggestions be?
   - Should we estimate $ cost savings for cloud deployments?

---

## Next Steps

Once you approve this design:
1. Implement database schema changes
2. Start with `orc explain` (simplest)
3. Then `orc delete` (most useful)
4. Finally `orc optimize` (most impressive)

Ready to begin implementation when you give the green light! 🚀
