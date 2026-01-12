# ORC Command Reference - Complete Guide - Complete Guide

This document lists all **working** ORC CLI commands with examples and usage.

---

## Quick Reference

### ✅ Commands That Actually Work (Tested & Verified)

| Command | Purpose | Status |
|---------|---------|--------|
| `orc` | Interactive AI chat | ✅ WORKS |
| `orc init` | Initialize project | ✅ WORKS |
| `orc index` | Index codebase | ✅ WORKS |
| `orc scan` | Index + analyze in one go | ✅ WORKS |
| `orc report` | Comprehensive report | ✅ WORKS |
| `orc find <what>` | Smart search | ✅ WORKS |
| `orc check` | Quick health check | ✅ WORKS |
| `orc stats` | Show statistics | ✅ WORKS (deprecated) |
| `orc config` | Manage configuration | ✅ WORKS |
| `orc ignore` | Add ignore patterns | ✅ WORKS |

### ⚠️ Stub Commands (Don't Actually Work)

| Command | Status | Reason |
|---------|--------|--------|
| `orc delete` | ❌ STUB | Says "feature in development" |
| `orc explain` | ❌ STUB | Says "requires persistent IDs" |
| `orc optimize` | ❌ STUB | Says "in development" |

---

## Detailed Command Reference

### 1. `orc` - Interactive AI Chat ⭐ BEST FEATURE

**Description:** Chat with AI about your codebase. Ask questions, get explanations, find code.

**Usage:**
```bash
orc
```

**What It Does:**
- Starts an interactive chat session
- AI can query your indexed codebase
- Answer questions about code structure
- Explain complex functions
- Help find specific code patterns

**Example Session:**
```
$ orc

ORC Interactive Mode
Type 'exit' to quit, 'help' for commands

> What does the GraphStorage class do?
> Find all functions related to authentication
> How complex is the indexer.py file?
> exit
```

**Requirements:**
- Indexed codebase (run `orc index` first)
- AI API key configured (GROQ_API_KEY, OPENAI_API_KEY, etc.)

---

### 2. `orc init` - Initialize Project

**Description:** Initialize ORC in current directory. Creates configuration files.

**Usage:**
```bash
orc init
```

**What It Creates:**
1. `.orc/` directory - for database and cache
2. `.orcrc` file - YAML configuration
3. `.orcignore` file - patterns to exclude from analysis

**Example Output:**
```
+ Created .orc/ directory
+ Created .orcrc config file
+ Created .orcignore file

ORC initialized successfully!

Next steps:
  1. Run orc index to index your codebase
  2. Run orc analyze to get analysis results
  3. Edit .orcignore to customize ignored patterns
```

**Configuration Created (`.orcrc`):**
```yaml
version: 1.0.0
ignore:
  - node_modules/
  - __pycache__/
  - .git/
  - .venv/
  - venv/
  - dist/
  - build/
dynamic_patterns:
  - getattr
  - eval
  - __import__
  - exec
complexity_threshold: 10
confidence_threshold: 0.7
```

---

### 3. `orc index` - Index Codebase

**Description:** Parse and index your codebase into a searchable database.

**Usage:**
```bash
orc index                    # Index current directory
orc index /path/to/project   # Index specific directory
orc index --force            # Force re-index (overwrite existing)
```

**What It Does:**
- Scans for Python, JavaScript, TypeScript, React, etc.
- Extracts functions, classes, imports
- Calculates complexity metrics
- Stores everything in SQLite database (`.orc/index.db`)

**Example Output:**
```
Indexing: C:\Users\user\project
Database: .orc\index.db

Indexing files...
Indexed 10/87 files...
Indexed 20/87 files...
...
Indexed 80/87 files...
Saving to database...

+ Indexing complete!
  Files: 87
  Functions: 155
  Classes: 85

Run 'orc stats' to see detailed statistics.
```

**Supported Languages:**
- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)
- React components
- HTML, CSS, SCSS, SASS, LESS
- JSON, YAML, Markdown

**Performance:**
- Uses parallel processing
- Typical speed: 50-100 files/second
- Automatically skips: `node_modules`, `.git`, `__pycache__`, etc.

---

### 4. `orc scan` - Smart One-Step Scan ⭐ RECOMMENDED

**Description:** Index and analyze in one command. Best way to get started.

**Usage:**
```bash
orc scan                  # Scan current directory
orc scan /path/to/project # Scan specific directory
orc scan --quick          # Fast scan (skip analysis)
```

**What It Does:**
1. Indexes your entire codebase
2. Runs comprehensive analysis
3. Shows health score and summary
4. Provides next steps

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ ORC Smart Scan                                          │
│                                                         │
│ Path: C:\Users\user\project                             │
│ Database: .orc\index.db                                 │
│ Mode: Full                                              │
└─────────────────────────────────────────────────────────┘

⠋ Indexing files...
⠋ Saving to database...

+ Indexed 87 files
+ Found 155 functions
+ Found 85 classes

Running analysis...

┌─────────────────────────────────────────────────────────┐
│ Scan Complete!                                          │
│                                                         │
│ Statistics:                                             │
│    - Files: 87                                          │
│    - Functions: 155                                     │
│    - Classes: 85                                        │
│    - Total LOC: 12,456                                  │
│                                                         │
│ Top Complexity: 26                                      │
│ Average Complexity: 4.85                                │
└─────────────────────────────────────────────────────────┘

Tip: Run orc report for detailed analysis
Tip: Run orc find dead to find unused code
Tip: Run orc to chat with AI about your code
```

**When to Use:**
- First time analyzing a project
- After major code changes
- Weekly/monthly code health checks

---

### 5. `orc report` - Comprehensive Report

**Description:** Generate detailed analysis report with health score.

**Usage:**
```bash
orc report                      # Full interactive report
orc report --format summary     # Quick summary only
orc report --format json        # JSON output
orc report --save report.txt    # Save to file
```

**What It Shows:**
- Health score (0-100)
- Statistics (files, functions, classes, LOC)
- Language distribution
- Complexity hotspots (worst offenders)
- Largest files
- Highly coupled modules
- Next steps recommendations

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ ORC Codebase Report                                     │
│                                                         │
│ Health Score: 85/100                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Statistics                                              │
│                                                         │
│   Total Files        87                                 │
│   Functions          155                                │
│   Classes            85                                 │
│   Total LOC          12,456                             │
│   Avg Complexity     4.85                               │
│   Max Complexity     26                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Language Distribution                                   │
│                                                         │
│   Language    Files                                     │
│   python      87                                        │
└─────────────────────────────────────────────────────────┘

Complexity Hotspots
  1. delete() 
     Complexity: 26
     File: commands.py
     
  2. _search_multilanguage_index()
     Complexity: 24
     File: commands.py
     
  3. find()
     Complexity: 23
     File: cli_main.py

Largest Files
  1. commands.py
     Lines: 1,105
     Language: python
     
  2. codebase_mapper.py
     Lines: 661
     Language: python

┌─────────────────────────────────────────────────────────┐
│ Next Steps                                              │
│                                                         │
│ orc find dead - Find unused code                        │
│ orc find complex - Find complex functions               │
│ orc - Chat with AI about your code                      │
│ orc check - Quick health check                          │
└─────────────────────────────────────────────────────────┘
```

---

### 6. `orc find` - Smart Search ⭐ POWERFUL

**Description:** Natural language search for code issues and patterns.

**Usage:**
```bash
# Find specific issues
orc find dead              # Find dead/unused code
orc find complex           # Find complex functions
orc find large             # Find large files

# Search for code
orc find auth              # Find anything with "auth"
orc find UserController    # Find specific class/function
orc find login             # Search by pattern
```

**What It Does:**
- Understands natural language queries
- Searches functions, classes, files
- Analyzes code quality issues
- Shows results in beautiful tables

#### **6a. Find Dead Code**

```bash
orc find dead
orc find unused
orc find dead --min-confidence 0.9   # Higher confidence only
```

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ Searching for Dead Code                                 │
│                                                         │
│ Confidence threshold: 0.7                               │
└─────────────────────────────────────────────────────────┘

Analyzing function usage...

Analyzed 155 functions
Found 12 potentially unused

┌─────────────────────────────────────────────────────────┐
│ High Confidence (5 items)                               │
│ These are very likely safe to remove                    │
└─────────────────────────────────────────────────────────┘

 Function              File                Confidence 
 old_parser()          legacy.py           95%        
 unused_helper()       utils.py            92%        
 deprecated_func()     old_code.py         90%        

Tip: Use orc to chat with AI about specific functions
```

#### **6b. Find Complex Functions**

```bash
orc find complex
orc find complexity
```

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ Finding Complex Functions                               │
│                                                         │
│ Looking for functions with high cyclomatic complexity   │
└─────────────────────────────────────────────────────────┘

Summary
   Total Functions: 155
   Average Complexity: 4.85
   Critical (20+): 6
   High (10-19): 14

 Function                       Complexity  File         Lines   
 delete()                       26          commands.py  301-452 
 _search_multilanguage_index()  24          commands.py  785-901 
 find()                         23          cli_main.py  179-397 
 check()                        23          cli_main.py  815-976 

Tip: Consider refactoring functions with complexity > 20
```

#### **6c. Find Large Files**

```bash
orc find large
orc find big
```

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ Finding Large Files                                     │
└─────────────────────────────────────────────────────────┘

 File                Lines  Language 
 commands.py         1,105  python   
 codebase_mapper.py    661  python   
 graph_db.py           627  python   
 cli_main.py           588  python   

Tip: Consider splitting files larger than 500 lines
```

#### **6d. Search by Pattern**

```bash
orc find auth
orc find UserManager
orc find validate
```

**Example Output:**
```
┌─────────────────────────────────────────────────────────┐
│ Searching for: 'auth'                                   │
└─────────────────────────────────────────────────────────┘

Functions (3 found)
 Function         File             Complexity 
 authenticate()   auth.py          5          
 is_authorized()  auth_utils.py    3          
 auth_required()  decorators.py    2          

Classes (1 found)
  - AuthManager
    File: auth_manager.py
    Language: python
```

---

### 7. `orc check` - Quick Health Check

**Description:** Fast code health check with actionable recommendations.

**Usage:**
```bash
orc check              # Full health check
orc check --quick      # Skip dead code analysis (faster)
```

**What It Does:**
- Calculates health score (0-100)
- Identifies critical issues
- Provides recommendations
- Perfect for CI/CD pipelines

**Health Score Calculation:**
- 90-100: EXCELLENT
- 75-89: GOOD
- 60-74: FAIR
- 40-59: NEEDS WORK
- 0-39: CRITICAL

**Example Output:**
```
Running health check...

┌─────────────────────────── Codebase Health Check ───────┐
│ GOOD                                                    │
│                                                         │
│ Health Score: 80/100                                    │
└─────────────────────────────────────────────────────────┘

Quick Stats
   Files: 87
   Functions: 155
   Average Complexity: 4.85

Issues Found
   - 6 critical complexity functions (20+)
   - 14 high complexity functions (10-19)
   - 3 potentially unused functions

Recommendations
   orc find complex - Address critical complexity
   orc find dead - Clean up unused code
   orc report - Review full report
```

**CI/CD Integration:**
- Exits with code 1 if health < 50 (fails build)
- Exits with code 0 otherwise (passes build)

**Example CI/CD Usage:**
```yaml
# GitHub Actions
- name: Check Code Health
  run: orc check
  # Fails if health score < 50
```

---

### 8. `orc stats` - Show Statistics

**Description:** Display codebase statistics. **(Deprecated - use `orc report` instead)**

**Usage:**
```bash
orc stats
orc stats --json-output   # JSON format
```

**Example Output:**
```
Codebase Statistics
  Files: 87
  Functions: 155
  Classes: 85
  Average Complexity: 4.85
  Max Complexity: 26

Files by Language:
  python    87  

Tip: For detailed analysis, run orc report
```

---

### 9. `orc config` - Manage Configuration

**Description:** View and modify ORC configuration.

**Usage:**
```bash
orc config show                           # Show current config
orc config set complexity_threshold 15    # Set value
orc config add-ignore "test_*.py"         # Add ignore pattern
```

**Example Output:**
```bash
$ orc config show

ORC Configuration

version: 1.0.0
ignore:
- node_modules/
- __pycache__/
- .git/
- .venv/
- venv/
- dist/
- build/
dynamic_patterns:
- getattr
- eval
- __import__
- exec
complexity_threshold: 10
confidence_threshold: 0.7
```

**Configuration Options:**
- `complexity_threshold` - Minimum complexity to flag (default: 10)
- `confidence_threshold` - Minimum confidence for dead code (default: 0.7)
- `ignore` - List of patterns to ignore
- `dynamic_patterns` - Patterns that indicate dynamic code usage

---

### 10. `orc ignore` - Add Ignore Patterns

**Description:** Add patterns to `.orcignore` file to exclude from analysis.

**Usage:**
```bash
orc ignore "test_*.py"        # Ignore test files
orc ignore "legacy/"          # Ignore directory
orc ignore "*.min.js"         # Ignore minified files
```

**Example Output:**
```
+ Added 'test_*.py' to .orcignore
```

**Common Patterns:**
```bash
orc ignore "node_modules/"
orc ignore "__pycache__/"
orc ignore "*.pyc"
orc ignore ".git/"
orc ignore "dist/"
orc ignore "build/"
orc ignore "*.min.js"
orc ignore "*.bundle.js"
```

---

## Typical Workflows

### First Time Setup
```bash
cd /path/to/project
orc init              # Initialize
orc scan              # Index and analyze
orc report            # View detailed report
```

### Daily Usage
```bash
orc find dead         # Find unused code
orc find complex      # Find complex functions
orc check             # Quick health check
orc                   # Chat with AI
```

### CI/CD Pipeline
```bash
orc init
orc index
orc check             # Fails build if health < 50
```

### Code Review
```bash
orc scan              # Full scan
orc report            # Generate report
orc find complex      # Review complex code
orc find dead         # Identify dead code
```

---

## Performance Notes

### Indexing Speed
- Small projects (<100 files): 1-2 seconds
- Medium projects (100-1,000 files): 5-15 seconds
- Large projects (1,000-10,000 files): 30-60 seconds
- Very large projects (10,000+ files): 2-5 minutes

### Database Size
- Small projects: ~1-5 MB
- Medium projects: ~5-50 MB
- Large projects: ~50-500 MB

### AI Chat Response Time
- Depends on AI provider
- Typical: 1-5 seconds per query
- Uses local database for fast lookups

---

## Requirements

### Minimum Requirements
- Python 3.9+
- 100 MB free disk space
- 512 MB RAM

### Optional Requirements
- AI API key (for `orc` chat command)
  - GROQ_API_KEY (free, fast)
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - Or any other supported provider

---

## Troubleshooting

### "Database not found" Error
```bash
# Solution: Index your codebase first
orc index
# or
orc scan
```

### "No files found" Error
```bash
# Check .orcignore patterns
cat .orcignore

# Make sure you're in the right directory
pwd
ls
```

### Slow Indexing
```bash
# Use --quick mode
orc scan --quick

# Or ignore large directories
orc ignore "large_vendor_dir/"
```

### AI Not Working
```bash
# Check if API key is set
echo $GROQ_API_KEY

# Set API key
export GROQ_API_KEY="your-key-here"

# Or create .env file
echo "GROQ_API_KEY=your-key-here" > .env
```

---

## Summary

### ✅ Fully Working Commands (Use These!)
1. `orc` - AI chat
2. `orc init` - Initialize
3. `orc index` - Index codebase
4. `orc scan` - One-step index + analyze ⭐
5. `orc report` - Comprehensive report
6. `orc find <what>` - Smart search ⭐
7. `orc check` - Health check
8. `orc config` - Manage config
9. `orc ignore` - Add ignore patterns
10. `orc stats` - Statistics (deprecated)

### ⚠️ Stub Commands (Don't Use Yet)
1. `orc delete` - Not implemented
2. `orc explain` - Not implemented
3. `orc optimize` - Not implemented

---

**Ready to analyze your code? Start with:** `orc scan`
