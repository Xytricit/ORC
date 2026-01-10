# Your First Analysis with ORC

This tutorial walks you through running your first code analysis with ORC.

## Prerequisites

- ORC installed (`pip install orc-cli`)
- A Python, JavaScript, or TypeScript project to analyze
- 5-10 minutes

## Step 1: Navigate to Your Project

Open a terminal and navigate to your project directory:

```bash
cd /path/to/your/project
```

**Example:**
```bash
cd ~/projects/my-web-app
```

## Step 2: Initialize ORC

Initialize ORC in your project:

```bash
orc init
```

**What this does:**
- Creates `.orc/` directory for ORC data
- Creates `.orc/config.yaml` with default settings
- Adds `.orc/` to `.gitignore` (if it exists)

**Output:**
```
✅ ORC initialized successfully!
📁 Configuration saved to .orc/config.yaml
```

## Step 3: Configure Ignore Patterns (Optional)

Create a `.orcignore` file to exclude unnecessary files:

```bash
# .orcignore
node_modules/
venv/
.git/
dist/
build/
*.min.js
*.pyc
__pycache__/
.env
```

**Why?** This speeds up indexing and keeps results relevant.

## Step 4: Index Your Codebase

Index your project to build the dependency graph:

```bash
orc index
```

**What happens:**
1. ORC scans all files in your project
2. Parses Python, JavaScript, TypeScript, React files
3. Extracts functions, classes, imports
4. Builds dependency relationships
5. Stores data in local database

**Output:**
```
🔍 Indexing codebase...
📊 Found 127 files
⚙️  Processing...
████████████████████ 100% | 127/127 files

✅ Indexing complete!
📈 Indexed:
   - 127 files
   - 543 functions
   - 89 classes
   - 1,234 lines of code
⏱️  Time: 3.2s
```

## Step 5: Run Your First Analysis

Run a complete analysis:

```bash
orc analyze
```

**What it checks:**
- Code complexity
- Dead code (unused functions/imports)
- Security vulnerabilities
- Performance issues
- Code smells

**Output:**
```
🔍 Analyzing codebase...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Analysis Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Complexity Analysis:
  ⚠️  High complexity functions: 7
  ✅ Low complexity functions: 536
  
Dead Code Detection:
  🗑️  Unused functions: 12
  🗑️  Unused imports: 34
  
Security Analysis:
  ⚠️  Potential SQL injection: 2
  ⚠️  Hardcoded secrets: 1
  ✅ No XSS vulnerabilities found
  
Performance Analysis:
  ⚠️  Inefficient algorithms: 3
  ⚠️  Large functions (>200 lines): 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Summary: 57 issues found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 6: Review Detailed Results

### View Complexity Issues

```bash
orc analyze --complexity
```

**Example output:**
```
High Complexity Functions:

1. process_user_data() - Complexity: 15
   📁 File: src/utils/data_processor.py:45
   ⚠️  Recommendation: Break into smaller functions
   
2. validate_input() - Complexity: 12
   📁 File: src/validators.py:89
   ⚠️  Recommendation: Reduce nested if statements
```

### Find Dead Code

```bash
orc analyze --dead-code
```

**Example output:**
```
Unused Functions:

1. format_date()
   📁 File: src/helpers/date_utils.py:23
   🗑️  Never called in the codebase
   
2. calculate_discount()
   📁 File: src/utils/pricing.py:156
   🗑️  Defined but never used

Unused Imports:

1. import pandas as pd
   📁 File: src/analysis/reports.py:5
   🗑️  Import never used
```

### Check Security

```bash
orc analyze --security
```

**Example output:**
```
Security Issues:

1. Potential SQL Injection
   📁 File: src/database/queries.py:45
   ⚠️  Risk: High
   💡 Fix: Use parameterized queries
   
   Code:
   query = f"SELECT * FROM users WHERE id = {user_id}"
   
   Should be:
   query = "SELECT * FROM users WHERE id = ?"
   cursor.execute(query, (user_id,))
```

## Step 7: Save Results

Save results to a file:

```bash
# JSON format
orc analyze --output report.json --format json

# HTML report
orc analyze --output report.html --format html
```

## Step 8: Fix Issues

Work through the issues found:

### Example: Fix High Complexity

**Before:**
```python
def process_user_data(user):
    if user.is_active:
        if user.has_subscription:
            if user.subscription_type == 'premium':
                if user.payment_valid:
                    # ... more nested logic
                    return process_premium(user)
    return None
```

**After:**
```python
def process_user_data(user):
    if not user.is_active:
        return None
    
    if not user.has_subscription:
        return None
        
    if user.subscription_type == 'premium' and user.payment_valid:
        return process_premium(user)
    
    return None
```

### Example: Remove Dead Code

**Before:**
```python
# Unused function
def calculate_discount(price, percentage):
    return price * (percentage / 100)

def get_final_price(price):
    return price * 0.9  # 10% discount hardcoded
```

**After:**
```python
# Removed unused function
# Updated to use it if needed, or deleted if truly unnecessary

def get_final_price(price, discount=0.1):
    return price * (1 - discount)
```

## Step 9: Re-index and Re-analyze

After making changes:

```bash
# Re-index to pick up changes
orc index

# Re-analyze to verify fixes
orc analyze
```

## Step 10: Use the Web Interface

For a visual experience:

```bash
orc web
```

1. Sign up / Sign in
2. Create a project
3. View results in the dashboard
4. Explore dependency graphs
5. Use AI chat for questions

## Common Patterns

### Daily Workflow

```bash
# Morning: Check codebase health
orc analyze --dead-code

# Before commit: Quick security check
orc analyze --security

# Weekly: Full analysis
orc analyze --all --output weekly_report.html
```

### CI/CD Integration

Add to your CI pipeline (`.github/workflows/orc.yml`):

```yaml
name: ORC Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install ORC
        run: pip install orc-cli
      
      - name: Run Analysis
        run: |
          orc init
          orc index
          orc analyze --output results.json --format json
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: orc-results
          path: results.json
```

## Tips for Better Results

1. **Keep .orcignore updated** - Exclude test files, vendors, builds
2. **Run after refactoring** - Verify improvements
3. **Set complexity thresholds** - Configure in `.orc/config.yaml`
4. **Use incrementally** - Start with one analysis type
5. **Automate** - Add to pre-commit hooks or CI

## Troubleshooting

### "No files found"

**Solution:** Check your `.orcignore` isn't too restrictive

### "Indexing takes too long"

**Solution:** 
- Exclude large directories (node_modules, etc.)
- Use `--workers 8` to increase parallelization

### "Analysis shows too many issues"

**Solution:**
- Start with one type: `orc analyze --complexity`
- Adjust thresholds in config
- Focus on high-priority issues first

## Next Steps

- [Using AI Chat](ai_chat.md) - Ask questions about your code
- [Finding Dead Code](dead_code.md) - Deep dive into dead code detection
- [Performance Optimization](performance.md) - Optimize your code
- [Configuration](../configuration.md) - Customize ORC settings

## Summary

You've learned to:
- ✅ Initialize ORC in a project
- ✅ Index your codebase
- ✅ Run comprehensive analysis
- ✅ Review and fix issues
- ✅ Save reports
- ✅ Integrate with workflows

Happy analyzing! 🚀
