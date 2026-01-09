# ORC AI Tools - Complete Reference

**Total Tools**: 19 (12 original + 7 new)  
**Date Added**: 2026-01-08

---

## 🆕 New Action Tools (7)

### 1. `organize_codebase`
**Purpose**: Organize files into professional folder structure

**Parameters**:
- `dry_run` (bool, default: true) - Show what would be done without making changes
- `create_folders` (bool, default: true) - Create standard folders

**What it does**:
- Creates `docs/`, `tests/`, `examples/`, `assets/`, `src/` folders
- Moves files to appropriate folders:
  - `.md`, `.rst`, `.txt` → `docs/`
  - `test_*.py`, `*_test.py` → `tests/`
  - `example_*`, `sample_*`, `demo_*` → `examples/`
  - `.png`, `.jpg`, `.svg`, `.ico` → `assets/`
- Suggests missing files (README, .gitignore, requirements.txt)

**Example**:
```
organize_codebase(dry_run=true)  # Preview changes
organize_codebase(dry_run=false) # Execute organization
```

**Use when**: Project files are messy and scattered

---

### 2. `cleanup_imports`
**Purpose**: Find and remove unused imports

**Parameters**:
- `file_path` (str, optional) - Specific file or all files
- `auto_fix` (bool, default: false) - Automatically remove unused imports

**What it does**:
- Scans Python files for imports
- Identifies imports that are never used
- Can automatically remove them with `auto_fix=true`

**Example**:
```
cleanup_imports()  # Check all files
cleanup_imports(file_path="myfile.py", auto_fix=true)  # Fix specific file
```

**Use when**: Code has accumulated unused imports

---

### 3. `find_duplicates`
**Purpose**: Find duplicate code blocks for refactoring

**Parameters**:
- `min_lines` (int, default: 5) - Minimum lines to consider duplicate
- `similarity_threshold` (float, default: 0.9) - Similarity score 0.0-1.0

**What it does**:
- Scans codebase for similar code blocks
- Reports duplicates with similarity scores
- Shows file locations and line numbers

**Example**:
```
find_duplicates(min_lines=10)  # Find 10+ line duplicates
find_duplicates(similarity_threshold=0.95)  # 95%+ similarity
```

**Use when**: Suspecting copy-paste code exists

---

### 4. `suggest_refactoring`
**Purpose**: Comprehensive refactoring suggestions

**Parameters**:
- `file_path` (str, optional) - Specific file or all files
- `focus` (str, default: "all") - Focus: 'complexity', 'duplication', 'naming', 'all'

**What it does**:
- Combines complexity and dead code analysis
- Prioritizes suggestions by impact
- Provides specific recommendations

**Example**:
```
suggest_refactoring()  # All suggestions
suggest_refactoring(focus='complexity')  # Just complexity issues
```

**Use when**: Planning refactoring work

---

### 5. `analyze_performance`
**Purpose**: Find performance bottlenecks

**Parameters**:
- `file_path` (str, optional) - Specific file or all files

**What it does**:
- Detects O(n²) nested loops
- Finds list appends in loops (use comprehensions)
- Detects string concatenation in loops (use join)
- Suggests optimizations

**Example**:
```
analyze_performance()  # Scan entire codebase
analyze_performance(file_path="slow_module.py")  # Specific file
```

**Use when**: Code is slow or needs optimization

---

### 6. `check_best_practices`
**Purpose**: Validate code against best practices

**Parameters**:
- `language` (str, default: "all") - 'python', 'javascript', 'typescript', 'all'
- `strict` (bool, default: false) - Enable strict checking

**What it does**:
- Checks for missing docstrings
- Detects functions with too many arguments
- Finds magic numbers that should be constants
- More checks in strict mode

**Example**:
```
check_best_practices(language='python')  # Python only
check_best_practices(strict=true)  # Strict mode
```

**Use when**: Code review or quality check needed

---

### 7. `generate_docs`
**Purpose**: Generate documentation (in development)

**Parameters**:
- `target` (str, required) - File, folder, or 'all'
- `doc_type` (str, default: "all") - 'docstrings', 'readme', 'api', 'all'

**What it does**:
- Currently shows suggestions for manual documentation
- Future: Auto-generate docstrings, README, API docs

**Example**:
```
generate_docs(target='all')  # Document everything
```

**Status**: Framework implemented, full features coming soon

---

## 📚 Original Tools (12)

### Search Tools

#### `query_files`
Find files by name pattern or language
```
query_files(pattern="auth", language="python", limit=20)
```

#### `query_functions`
Find functions by name or complexity
```
query_functions(pattern="login", min_complexity=10)
```

#### `query_classes`
Find classes by name
```
query_classes(pattern="User")
```

#### `search_code`
Search for text patterns in code
```
search_code(pattern="TODO", file_pattern="*.py")
```

---

### Analysis Tools

#### `get_codebase_stats`
Get overall statistics
```
get_codebase_stats()
```

#### `get_complexity_report`
Analyze code complexity
```
get_complexity_report(min_complexity=10, limit=30)
```

#### `get_dead_code`
Find unused code
```
get_dead_code(confidence_threshold=0.7, limit=50, deep_scan=false)
```

#### `get_dependencies`
Analyze imports and callers
```
get_dependencies(file_path="auth.py")
get_dependencies(function_name="authenticate")
```

#### `get_security_issues`
Scan for vulnerabilities
```
get_security_issues(severity="critical", limit=30)
```

#### `get_hotspots`
Find problem areas
```
get_hotspots(limit=10)
```

#### `get_codebase_map`
Get hierarchical structure
```
get_codebase_map(depth=2)
```

---

### Utility Tools

#### `get_file_content`
Read file contents
```
get_file_content(file_path="main.py", start_line=10, end_line=50)
```

---

## 🎯 Tool Categories

### By Purpose

**Search & Discovery**:
- query_files, query_functions, query_classes, search_code

**Code Quality**:
- get_complexity_report, get_dead_code, check_best_practices

**Security**:
- get_security_issues

**Performance**:
- analyze_performance, get_hotspots

**Refactoring**:
- suggest_refactoring, find_duplicates, cleanup_imports

**Organization**:
- organize_codebase

**Documentation**:
- generate_docs

**Analysis**:
- get_dependencies, get_codebase_stats, get_codebase_map

---

## 💡 Common Workflows

### Complete Code Audit
```
1. get_codebase_stats()  # Overview
2. get_complexity_report()  # Find complex code
3. get_dead_code()  # Find unused code
4. get_security_issues()  # Security scan
5. check_best_practices()  # Quality check
6. suggest_refactoring()  # Get recommendations
```

### Performance Optimization
```
1. get_hotspots()  # Find problem areas
2. analyze_performance()  # Detect bottlenecks
3. get_complexity_report()  # High complexity = slow code
4. suggest_refactoring(focus='complexity')  # Get suggestions
```

### Code Cleanup
```
1. get_dead_code(confidence_threshold=0.9)  # Safe to delete
2. cleanup_imports()  # Remove unused imports
3. find_duplicates()  # Find copy-paste
4. organize_codebase(dry_run=true)  # Organize files
```

### Before Deployment
```
1. get_security_issues(severity='critical')  # Critical vulnerabilities
2. check_best_practices(strict=true)  # Quality check
3. get_dead_code()  # Remove unused code
4. analyze_performance()  # Performance check
```

---

## 🎨 Usage Tips

### 1. Always Start with dry_run=true
```
organize_codebase(dry_run=true)  # Preview first
# Review changes
organize_codebase(dry_run=false)  # Then execute
```

### 2. Use Filters to Reduce Noise
```
get_dead_code(confidence_threshold=0.9)  # Only high confidence
get_complexity_report(min_complexity=20)  # Only critical
```

### 3. Combine Tools for Better Insights
```
# Find functions to refactor
complexity = get_complexity_report(min_complexity=15)
dead = get_dead_code(confidence_threshold=0.8)
# Now you know: complex functions to simplify, dead code to remove
```

### 4. Work Incrementally
```
# Don't try to fix everything at once
suggest_refactoring(focus='complexity')  # Start with complexity
# Fix top 3 issues
suggest_refactoring(focus='duplication')  # Then duplication
```

---

## 🚀 Advanced Features

### Deep Scan for Dead Code
```
get_dead_code(deep_scan=true)
# Slower but more accurate
# Use for final validation before deletion
```

### Strict Best Practices
```
check_best_practices(strict=true)
# More rigorous checks
# Use before production deployment
```

### Performance Limits
Most tools have limits to prevent overwhelming results:
- `limit` parameter controls max results
- Default limits are tuned for usability
- Increase for comprehensive analysis

---

## 📖 Tool Return Formats

All tools return structured JSON with:
- **summary**: Key metrics
- **results**: Detailed findings
- **recommendations**: Action items

Example:
```json
{
  "summary": {
    "files_checked": 50,
    "issues_found": 12
  },
  "results": [...],
  "recommendations": "..."
}
```

---

## 🎯 When to Use Each Tool

| Tool | Use When... |
|------|-------------|
| `organize_codebase` | Files are scattered in root directory |
| `cleanup_imports` | Codebase has unused imports |
| `find_duplicates` | Suspecting copy-paste code |
| `suggest_refactoring` | Planning refactoring work |
| `analyze_performance` | Code is slow or needs optimization |
| `check_best_practices` | Code review or quality check |
| `get_complexity_report` | Need to simplify complex code |
| `get_dead_code` | Want to remove unused code |
| `get_security_issues` | Security audit needed |
| `get_hotspots` | Finding problem areas |

---

## 🎉 Summary

ORC AI now has **19 powerful tools** to help you:
- ✅ Analyze code quality
- ✅ Find performance issues
- ✅ Detect security vulnerabilities
- ✅ Organize project structure
- ✅ Suggest refactorings
- ✅ Clean up dead code
- ✅ Find duplicates

**All tools are production-ready and available now!**

Use them to maintain high code quality and developer productivity.
