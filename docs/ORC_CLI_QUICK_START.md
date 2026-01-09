# ORC CLI - Quick Start Guide

## Installation & Setup

```bash
# 1. Initialize ORC in your project
orc init

# 2. Index your codebase
orc index .

# 3. You're ready to analyze!
orc stats
```

---

## Most Common Commands

### Get Overview
```bash
# Show codebase statistics
orc stats

# Full analysis report
orc analyze
```

### Find Problems
```bash
# Find complex code (default threshold: 10)
orc complexity

# Find high-complexity functions (threshold: 15+)
orc complexity --threshold 15 --limit 10

# Find potentially unused code
orc dead --confidence 0.8 --limit 20

# Find all problem areas
orc hotspots
```

### Search Code
```bash
# Search for functions
orc query "auth" --type functions

# Search for classes
orc query "User" --type classes

# Search for files
orc query "config" --type files
```

---

## Configuration

### View & Modify Config
```bash
# Show current configuration
orc config show

# Set a value
orc config set complexity_threshold 15
orc config set confidence_threshold 0.8

# Add ignore patterns
orc ignore "*.tmp"
orc ignore "legacy/"
orc config add-ignore "test_*"
```

### Config File Location
- **Config**: `.orcrc` (YAML format)
- **Ignore**: `.orcignore` (gitignore-style patterns)
- **Database**: `.orc/index.db` (SQLite)

---

## Advanced Usage

### Re-index After Code Changes
```bash
# Force re-indexing
orc index . --force
```

### Web Interface
```bash
# Start web dashboard
orc serve --port 5000

# Then open: http://127.0.0.1:5000
```

### Custom Database Location
```bash
# Use different database
orc stats --db path/to/custom.db
orc query "pattern" --db path/to/custom.db
```

---

## Typical Workflows

### Daily Code Review
```bash
orc stats                    # Check overall health
orc complexity --threshold 10 # Find complex code
orc hotspots --limit 5       # Top issues
```

### Refactoring Session
```bash
orc complexity --threshold 15  # Find targets
orc query "function_name"      # Locate function
orc dead --confidence 0.9      # Find unused code
```

### New Project Setup
```bash
orc init                     # Initialize
orc index .                  # Index codebase
orc analyze                  # Get baseline
```

### Before Deployment
```bash
orc index . --force          # Re-index
orc dead --confidence 0.9    # Check for dead code
orc complexity --threshold 20 # Critical complexity
```

---

## Flags & Options

### Common Flags (Most Commands)
- `--db <path>` - Custom database location (default: `.orc/index.db`)
- `--limit <n>` - Maximum results to show
- `--help` - Show command help

### Index Command
- `--output, -o <path>` - Output database path
- `--force` - Force re-indexing

### Dead Code Command
- `--confidence <0.0-1.0>` - Confidence threshold (default: 0.7)
- `--timeout <seconds>` - Analysis timeout (default: 30)
- `--limit <n>` - Max results

### Complexity Command
- `--threshold <n>` - Complexity threshold (default: 10)
- `--limit <n>` - Max results

### Query Command
- `--type <functions|classes|files>` - Search type (default: functions)
- `--limit <n>` - Max results

### Serve Command
- `--port <n>` - Port number (default: 5000)
- `--host <ip>` - Host to bind (default: 127.0.0.1)

---

## Understanding Output

### Complexity Levels
- **Critical (20+)**: Immediate refactoring needed
- **High (10-19)**: Should be reviewed
- **Medium (5-9)**: Acceptable but monitor
- **Low (<5)**: Simple and maintainable

### Dead Code Confidence
- **0.9+**: Safe to delete (deprecated names, private unused)
- **0.7-0.9**: Review before delete (no calls found)
- **<0.7**: Likely safe but check (entry points, exports)

### Hotspots Categories
- **Complexity Hotspots**: High cyclomatic complexity functions
- **Large Files**: Files with many lines
- **Coupling Hotspots**: Heavily imported modules

---

## Tips & Best Practices

### Performance Tips
1. **Use --limit**: Limit results for faster output
2. **Timeout for dead code**: Use `--timeout` on large codebases
3. **Selective indexing**: Index specific directories if needed

### Workflow Tips
1. **Run init once**: `orc init` sets up config files
2. **Re-index regularly**: Use `orc index . --force` after major changes
3. **Start with stats**: `orc stats` gives quick overview
4. **Progressive analysis**: Start with high thresholds, lower gradually

### Configuration Tips
1. **Customize thresholds**: Adjust complexity_threshold in .orcrc
2. **Use .orcignore**: Exclude generated code, vendor libs
3. **Project-specific config**: Each project can have its own .orcrc

---

## Troubleshooting

### Database not found
```bash
# Error: Database not found
# Solution: Index first
orc index .
```

### Dead code analysis is slow
```bash
# Problem: Takes too long
# Solution 1: Reduce limit
orc dead --limit 10 --timeout 15

# Solution 2: Increase timeout
orc dead --timeout 60
```

### No results found
```bash
# Problem: Query returns nothing
# Solution 1: Check if indexed
orc stats

# Solution 2: Try broader pattern
orc query "auth"  # Instead of "authenticate_user"
```

### Config file not found
```bash
# Error: No .orcrc found
# Solution: Initialize
orc init
```

---

## Examples by Use Case

### Find Technical Debt
```bash
orc complexity --threshold 20  # Critical complexity
orc dead --confidence 0.9      # Definitely unused
orc hotspots --limit 10        # Worst offenders
```

### Optimize Codebase
```bash
orc analyze                    # Get baseline
orc complexity --threshold 15  # Find targets
orc dead --confidence 0.8      # Remove unused
orc index . --force            # Re-index
orc analyze                    # Compare results
```

### Code Review
```bash
orc query "new_feature" --type functions
orc complexity --threshold 10
orc dead --confidence 0.7
```

### Documentation
```bash
orc stats > docs/codebase_stats.txt
orc complexity --threshold 10 > docs/complexity_report.txt
orc hotspots > docs/hotspots.txt
```

---

## Integration with Other Tools

### Git Pre-commit Hook
```bash
# .git/hooks/pre-commit
orc complexity --threshold 20
if [ $? -ne 0 ]; then
    echo "Critical complexity found!"
    exit 1
fi
```

### CI/CD Pipeline
```bash
# In your CI script
orc index .
orc analyze
orc dead --confidence 0.9
orc complexity --threshold 15
```

### Editor Integration
```bash
# VS Code task.json
{
    "label": "ORC Analyze",
    "type": "shell",
    "command": "orc analyze"
}
```

---

## Getting Help

### Command Help
```bash
orc --help              # List all commands
orc <command> --help    # Command-specific help
```

### Show Version
```bash
orc --version
```

### Configuration Help
```bash
orc config show         # See current config
orc init                # Create default config
```

---

## Cheat Sheet

```bash
# Setup
orc init                           # Initialize
orc index .                        # Index codebase

# Analysis
orc stats                          # Statistics
orc analyze                        # Full analysis
orc complexity                     # Complexity report
orc hotspots                       # Problem areas
orc dead                           # Dead code

# Search
orc query "pattern"                # Search functions
orc query "Class" --type classes   # Search classes
orc query "file" --type files      # Search files

# Config
orc config show                    # Show config
orc config set key value           # Set value
orc ignore "pattern"               # Add ignore

# Advanced
orc serve                          # Web interface
orc index . --force                # Re-index
orc dead --timeout 60              # Long timeout
```

---

## Next Steps

After mastering the basics:

1. **Customize**: Edit `.orcrc` and `.orcignore` for your project
2. **Automate**: Add ORC to your CI/CD pipeline
3. **Monitor**: Run regularly to track code health
4. **Web UI**: Use `orc serve` for interactive exploration
5. **Integrate**: Add to git hooks, editor workflows

---

**Happy Analyzing! 🔍**

For more details, see:
- `CLI_IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `CLI_IMPLEMENTATION_GUIDE.md` - Original specification
- `orc --help` - Built-in help
