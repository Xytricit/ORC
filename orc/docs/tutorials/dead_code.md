# Finding Dead Code with ORC

Learn how to identify and remove unused code from your codebase.

## What is Dead Code?

Dead code is code that exists in your codebase but is never executed or used:

- **Unused functions** - Functions that are never called
- **Unused imports** - Imported modules that aren't used
- **Unused variables** - Variables that are assigned but never read
- **Unreachable code** - Code after return statements or in impossible conditions
- **Unused classes** - Classes that are never instantiated

## Why Remove Dead Code?

1. **Improves maintainability** - Less code to understand and maintain
2. **Reduces bundle size** - Smaller deployments
3. **Faster builds** - Less code to compile/transpile
4. **Reduces confusion** - Developers won't wonder if code is used
5. **Easier refactoring** - Less code to update

## Running Dead Code Analysis

### Basic Detection

```bash
orc analyze --dead-code
```

**Output:**
```
🗑️  Dead Code Detection

Unused Functions (12 found):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. format_timestamp()
   📁 src/utils/date_helpers.py:45
   ❌ Never called anywhere in the codebase
   
2. calculate_tax()
   📁 src/billing/calculations.py:89
   ❌ Defined but never used
   
3. send_notification()
   📁 src/notifications/sender.py:23
   ⚠️  Only defined, no calls found

Unused Imports (34 found):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. import pandas as pd
   📁 src/analysis/reports.py:5
   🗑️  Imported but never used
   
2. from datetime import timezone
   📁 src/utils/time.py:3
   🗑️  Import never referenced

Unused Classes (3 found):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. UserValidator
   📁 src/validators/user.py:12
   ❌ Never instantiated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Summary: 49 pieces of dead code found
💡 Estimated cleanup: ~500 lines of code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Save Results to File

```bash
# JSON format
orc analyze --dead-code --output dead_code.json --format json

# HTML report
orc analyze --dead-code --output dead_code.html --format html
```

### Filter Results

```bash
# Only show unused functions
orc analyze --dead-code --type function

# Only Python files
orc analyze --dead-code --language python

# Specific directory
orc analyze --dead-code --path src/utils/
```

## Understanding Results

### Confidence Levels

ORC assigns confidence levels to dead code findings:

- **High (100%)** - Definitely unused, safe to remove
- **Medium (70-99%)** - Likely unused, review before removing
- **Low (<70%)** - Might be used indirectly, investigate carefully

### False Positives

Some code may appear dead but is actually used:

1. **Dynamic imports** - `importlib.import_module(module_name)`
2. **Reflection** - `getattr()`, `setattr()`, `exec()`
3. **External usage** - Code called from outside the project
4. **Framework hooks** - Methods called by frameworks (Django, Flask)
5. **Entry points** - CLI commands, API endpoints

### Exclusions

Configure what to exclude in `.orc/config.yaml`:

```yaml
analysis:
  dead_code:
    # Don't flag these as dead code
    exclude_tests: true        # Exclude test files
    exclude_init: true         # Exclude __init__.py files
    exclude_magic: true        # Exclude __str__, __repr__, etc.
    exclude_patterns:
      - "*/migrations/*"       # Django migrations
      - "*/fixtures/*"         # Test fixtures
      - "*/scripts/*"          # Utility scripts
```

## Step-by-Step Cleanup

### Step 1: Review Findings

Don't blindly delete everything. Review each finding:

```bash
# Get detailed report
orc analyze --dead-code --verbose
```

### Step 2: Verify Unused Functions

Check if function is truly unused:

```bash
# Search for function usage
orc query "function_name"

# Or use grep
grep -r "function_name" .
```

### Step 3: Check Git History

See if code was recently added or used:

```bash
# Check when function was last modified
git log -p --all -S "function_name"

# Check function history
git log --follow -- path/to/file.py
```

### Step 4: Remove Code

Start with high-confidence findings:

```python
# Before - src/utils/helpers.py
def format_date(date):
    return date.strftime("%Y-%m-%d")

def format_timestamp(timestamp):  # ← Dead code
    return timestamp.isoformat()

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")
```

```python
# After - Remove unused function
def format_date(date):
    return date.strftime("%Y-%m-%d")

# Removed format_timestamp() - never used

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")
```

### Step 5: Remove Unused Imports

```python
# Before
import os
import sys
import json
import pandas as pd  # ← Never used
from datetime import datetime, timezone  # ← timezone never used

def process_data(data):
    return json.loads(data)
```

```python
# After
import json
from datetime import datetime

def process_data(data):
    return json.loads(data)
```

### Step 6: Test After Removal

```bash
# Run tests
pytest

# Re-index
orc index

# Re-analyze
orc analyze --dead-code
```

## Advanced Techniques

### Using AI Chat

Ask ORC's AI for help:

```bash
orc chat
```

```
You: Is the format_timestamp function used anywhere?

🤖: I searched the entire codebase and found no calls to 
format_timestamp(). It was last modified 6 months ago in 
commit abc123f. It appears safe to remove.
```

### Batch Removal

For projects with lots of dead code:

```python
# create_cleanup_script.py
import json

# Load dead code report
with open('dead_code.json') as f:
    report = json.load(f)

# Generate cleanup commands
for item in report['unused_imports']:
    file = item['file']
    line = item['line']
    print(f"sed -i '{line}d' {file}")
```

### Gradual Cleanup

Don't remove everything at once:

```bash
# Week 1: Remove unused imports
orc analyze --dead-code --type import

# Week 2: Remove unused functions (high confidence)
orc analyze --dead-code --type function --confidence high

# Week 3: Review medium confidence findings
orc analyze --dead-code --confidence medium
```

## Common Patterns

### Pattern 1: Legacy Code

```python
# Old payment processing - replaced by new system
def process_payment_v1(amount):
    # Old Stripe integration
    pass

def process_payment_v2(amount):
    # New payment processor
    pass
```

**Action:** Remove v1 after confirming v2 works

### Pattern 2: Commented Code

```python
# def old_calculation():
#     return x * 2

def new_calculation():
    return x * 3
```

**Action:** Remove commented code (it's in Git history if needed)

### Pattern 3: TODO Functions

```python
def future_feature():
    # TODO: Implement later
    pass
```

**Action:** Remove if not planned soon, or create issue and remove

### Pattern 4: Copy-Paste Duplication

```python
def calculate_discount_basic(price):
    return price * 0.9

def calculate_discount_premium(price):  # ← Never used
    return price * 0.8
```

**Action:** Remove unused variant

## Framework-Specific Tips

### Django

Exclude Django-specific code:

```yaml
# .orc/config.yaml
analysis:
  dead_code:
    exclude_patterns:
      - "*/migrations/*"
      - "*/management/commands/*"
    exclude_magic: true  # Keep __str__, __repr__
```

### Flask

Entry points and view functions:

```python
@app.route('/api/users')
def get_users():
    # This looks unused but is called by Flask
    pass
```

**Solution:** Mark as used in config:

```yaml
dead_code:
  keep_decorators:
    - "app.route"
    - "api.route"
```

### React/JavaScript

```javascript
// May appear unused but called by React
function ComponentName() {
  return <div>Hello</div>;
}
```

**Solution:** ORC understands React components automatically

## Integration with CI/CD

### GitHub Actions

```yaml
# .github/workflows/dead-code.yml
name: Dead Code Check

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install ORC
        run: pip install orc-cli
      
      - name: Check for dead code
        run: |
          orc init
          orc index
          orc analyze --dead-code --output report.json
      
      - name: Fail if dead code found
        run: |
          dead_count=$(jq '.summary.total' report.json)
          if [ "$dead_count" -gt 0 ]; then
            echo "Found $dead_count dead code items"
            exit 1
          fi
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for new dead code
orc index
dead_code=$(orc analyze --dead-code --format json | jq '.summary.total')

if [ "$dead_code" -gt "0" ]; then
    echo "⚠️  Warning: Found $dead_code dead code items"
    echo "Run 'orc analyze --dead-code' for details"
fi
```

## Metrics & Tracking

### Track Progress

```bash
# Initial baseline
orc analyze --dead-code --output baseline.json

# After cleanup
orc analyze --dead-code --output after.json

# Compare
python compare_reports.py baseline.json after.json
```

### Set Goals

```yaml
# .orc/config.yaml
analysis:
  dead_code:
    fail_threshold: 10  # Fail if more than 10 items
    warn_threshold: 5   # Warn if more than 5 items
```

## Best Practices

1. **Start Small** - Begin with high-confidence findings
2. **Review Carefully** - Don't auto-delete without review
3. **Test Thoroughly** - Run full test suite after removal
4. **Check Git** - Look at history before removing
5. **Document** - Comment why code was removed in commit
6. **Gradual** - Clean up over time, not all at once
7. **Automate** - Add checks to CI/CD
8. **Regular Audits** - Check monthly for new dead code

## Troubleshooting

### "False positives for dynamic code"

**Solution:** Add exclusions:
```yaml
dead_code:
  exclude_patterns:
    - "*/plugins/*"
    - "*/extensions/*"
```

### "Missing externally called code"

**Solution:** Mark as used:
```yaml
dead_code:
  keep_functions:
    - "api_endpoint_*"
    - "handle_*"
```

### "Too many results"

**Solution:** Filter by confidence:
```bash
orc analyze --dead-code --confidence high
```

## Summary

You've learned to:
- ✅ Find dead code in your project
- ✅ Understand confidence levels
- ✅ Review findings carefully
- ✅ Remove code safely
- ✅ Configure exclusions
- ✅ Integrate with workflows
- ✅ Track cleanup progress

## Next Steps

- [Performance Optimization](performance.md) - Optimize remaining code
- [Configuration](../configuration.md) - Customize dead code detection
- [CLI Reference](../cli/README.md) - All CLI options

Happy cleaning! 🧹
