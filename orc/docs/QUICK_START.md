# ORC Quick Start Guide

Get started with ORC in 5 minutes!

---

## 📦 Step 1: Install ORC

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Navigate to the ORC directory
cd orc

# Install in development mode
pip install -e .
```

**Expected Output:**
```
Successfully installed orc-codebase-1.0.0
```

### Verify Installation

```bash
# Check if orc command works
python -m orc.cli.cli_main --help
```

or if installed globally:
```bash
orc --help
```

---

## 🚀 Step 2: Initialize Your First Project

### Navigate to a Project

```bash
# Go to any Python/JavaScript project
cd /path/to/your/project
```

### Initialize ORC

```bash
orc init
```

**Output:**
```
› Initializing ORC
  ✓ Created directory: .orc
  ✓ Created cache and sessions directories
  ✓ Created orc_config.yaml
  ✓ Created .orcignore
  ✓ ORC initialized successfully!
```

**What was created:**
- `.orc/` - Directory for database and cache
- `orc_config.yaml` - Configuration file
- `.orcignore` - Pattern file (like .gitignore)

---

## 📊 Step 3: Index Your Code

### Run Indexing

```bash
orc index
```

**Output:**
```
› Indexing Project
  ✓ Files indexed: 42
  ✓ Functions found: 128
  ✓ Classes found: 18
  ✓ Imports found: 95
  • Completed in 3.87s
```

**What happened:**
- Scanned all Python/JavaScript/TypeScript files
- Parsed code structure (functions, classes, imports)
- Stored in SQLite database (`.orc/graph.db`)
- Created cache for faster subsequent runs

---

## 🔍 Step 4: Analyze Your Code

### Quick Health Scan

```bash
orc scan
```

**Output:**
```
› Running Quick Scan
  ✓ Files: 42
  ✓ Functions: 128
  ✓ Classes: 18
  ✓ No overly complex functions detected
  ✓ Scan complete!
```

### Find Complex Code

```bash
orc find complex
```

**Output:**
```
› Searching for: complex
  • calculate_metrics - src/analyzer.py:45 (complexity: 15)
  • process_data - src/utils.py:120 (complexity: 12)
```

### Find Large Functions

```bash
orc find large
```

**Output:**
```
› Searching for: large
  • generate_report - src/reporter.py:80 (250 lines)
```

---

## 📄 Step 5: Generate Report

### Create Analysis Report

```bash
orc report --output analysis.md
```

**Output:**
```
› Generating Report
  ✓ Report saved to: analysis.md
```

### View Report

```bash
cat analysis.md
```

**Report Contents:**
- File statistics
- Function count
- Complexity analysis
- High-complexity functions
- Recommendations

---

## ⚙️ Step 6: Configure ORC (Optional)

### View Configuration

```bash
orc config list
```

**Output:**
```yaml
project_root: .
db_path: .orc/graph.db
cache_dir: .orc/cache
analysis:
  max_complexity_threshold: 10
  max_coupling_threshold: 0.7
```

### Edit Configuration

Edit `orc_config.yaml`:

```yaml
analysis:
  max_complexity_threshold: 15  # Change threshold
  dead_code_confidence: 0.8
```

---

## 🎯 Common Use Cases

### Use Case 1: Find All Issues

```bash
orc init
orc index
orc scan
orc find complex
orc find dead
orc report --output issues.md
```

### Use Case 2: Quick Check Before Commit

```bash
orc index --quiet
orc check
```

### Use Case 3: Analyze Single Directory

Add to `.orcignore`:
```
# Ignore everything except src/
*
!src/
```

Then run:
```bash
orc index --force
```

### Use Case 4: Export Analysis

```bash
orc report --output analysis.md
orc report --output analysis.txt
```

---

## 📋 All Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `orc init` | Initialize ORC | `orc init` |
| `orc index` | Index project files | `orc index --force` |
| `orc scan` | Quick health scan | `orc scan` |
| `orc report` | Generate report | `orc report -o report.md` |
| `orc find` | Find code patterns | `orc find complex` |
| `orc check` | Health check | `orc check` |
| `orc ignore` | Add ignore pattern | `orc ignore "*.test.js"` |
| `orc config` | Manage config | `orc config list` |

---

## 🔧 Troubleshooting

### Issue: `orc: command not found`

**Solution 1:** Use Python module:
```bash
python -m orc.cli.cli_main --help
```

**Solution 2:** Add to PATH or use pip install location.

### Issue: No files indexed

**Check `.orcignore`:** Make sure you're not ignoring everything.

```bash
cat .orcignore
```

**Force re-index:**
```bash
orc index --force
```

### Issue: Database errors

**Reset database:**
```bash
rm .orc/graph.db
orc index --force
```

---

## 📚 Next Steps

1. **Read Full Documentation**: See `README.md`
2. **Explore Configuration**: Edit `orc_config.yaml`
3. **Run Tests**: `pytest` (if dev dependencies installed)
4. **Check Examples**: See `docs/` directory

---

## 💡 Tips & Tricks

### Tip 1: Use `.orcignore` Effectively

```
# Ignore test files
*test*.py
*_test.js

# Ignore generated code
dist/
build/
__pycache__/
```

### Tip 2: Set Complexity Threshold

In `orc_config.yaml`:
```yaml
analysis:
  max_complexity_threshold: 15  # Adjust based on project
```

### Tip 3: Regular Health Checks

Add to pre-commit hook:
```bash
#!/bin/bash
orc index --quiet
orc check
```

### Tip 4: CI/CD Integration

In your CI pipeline:
```yaml
- name: Run ORC Analysis
  run: |
    pip install -e .
    orc init
    orc index
    orc report --output analysis.md
```

---

## 🎓 Learning Path

1. ✅ **Install ORC** (you're here!)
2. ✅ **Initialize project** with `orc init`
3. ✅ **Index code** with `orc index`
4. ✅ **Run analysis** with `orc scan`
5. 📖 **Read reports** and understand metrics
6. ⚙️ **Configure** for your project needs
7. 🔄 **Integrate** into workflow
8. 🚀 **Advanced usage** - custom parsers, API usage

---

## 📞 Get Help

- **Command help**: `orc [command] --help`
- **Documentation**: `README.md`
- **Issues**: GitHub Issues
- **Examples**: Check `docs/tutorials/`

---

**Ready to analyze? Let's go! 🚀**

```bash
orc init
orc index
orc scan
```
