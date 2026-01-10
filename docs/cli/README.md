# ORC CLI Reference

Complete command-line reference for ORC.

## Global Options

```bash
orc [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--version` - Show version and exit
- `--help` - Show help message and exit
- `--verbose, -v` - Enable verbose output
- `--quiet, -q` - Suppress non-error output

## Commands

### `orc init`

Initialize ORC in the current directory.

```bash
orc init [OPTIONS]
```

**Options:**
- `--force, -f` - Overwrite existing configuration

**Example:**
```bash
cd /path/to/project
orc init
```

---

### `orc index`

Index the codebase and build dependency graphs.

```bash
orc index [OPTIONS] [PATH]
```

**Arguments:**
- `PATH` - Path to index (default: current directory)

**Options:**
- `--rebuild` - Force rebuild of entire index
- `--workers N` - Number of parallel workers (default: CPU count)
- `--exclude PATTERN` - Additional patterns to exclude

**Example:**
```bash
# Index current directory
orc index

# Index specific path
orc index /path/to/code

# Rebuild index from scratch
orc index --rebuild

# Use 4 workers
orc index --workers 4
```

---

### `orc analyze`

Run code analysis.

```bash
orc analyze [OPTIONS]
```

**Options:**
- `--dead-code` - Find unused functions and imports
- `--complexity` - Analyze code complexity
- `--security` - Check for security issues
- `--performance` - Find performance bottlenecks
- `--all` - Run all analyses (default)
- `--output FILE` - Save results to file
- `--format FORMAT` - Output format: text, json, html (default: text)

**Examples:**
```bash
# Run all analyses
orc analyze

# Find dead code only
orc analyze --dead-code

# Multiple analyses
orc analyze --dead-code --security

# Save results to JSON
orc analyze --output report.json --format json

# Generate HTML report
orc analyze --output report.html --format html
```

---

### `orc chat`

Interactive AI chat about your codebase.

```bash
orc chat [OPTIONS] [QUERY]
```

**Arguments:**
- `QUERY` - Optional query to run (starts interactive mode if omitted)

**Options:**
- `--model MODEL` - AI model to use (default: from config)
- `--provider PROVIDER` - AI provider: groq, openai, anthropic, deepseek
- `--context-size N` - Max context tokens (default: 8000)

**Examples:**
```bash
# Start interactive chat
orc chat

# One-off query
orc chat "Explain the authentication system"

# Use specific model
orc chat --model gpt-4 --provider openai

# Reduce context size
orc chat --context-size 4000
```

**Interactive Commands:**
- `/help` - Show help
- `/clear` - Clear conversation
- `/context` - Show current context
- `/exit` or `/quit` - Exit chat

---

### `orc query`

Query the codebase without AI.

```bash
orc query [OPTIONS] PATTERN
```

**Arguments:**
- `PATTERN` - Search pattern (supports regex)

**Options:**
- `--type TYPE` - Search type: function, class, import, file
- `--language LANG` - Filter by language: python, javascript, typescript
- `--limit N` - Max results (default: 50)

**Examples:**
```bash
# Find all functions matching pattern
orc query "authenticate" --type function

# Find Python classes
orc query ".*Model$" --type class --language python

# Search files
orc query "auth" --type file --limit 10
```

---

### `orc graph`

Generate and view dependency graphs.

```bash
orc graph [OPTIONS]
```

**Options:**
- `--output FILE` - Save graph to file (png, svg, pdf)
- `--focus MODULE` - Focus on specific module
- `--depth N` - Max dependency depth (default: 3)
- `--layout LAYOUT` - Graph layout: dot, neato, circo (default: dot)

**Examples:**
```bash
# Generate graph
orc graph --output deps.png

# Focus on auth module
orc graph --focus auth --output auth_deps.svg

# Simple graph (depth 2)
orc graph --depth 2 --output simple.pdf
```

---

### `orc web`

Start the web interface.

```bash
orc web [OPTIONS]
```

**Options:**
- `--host HOST` - Host to bind to (default: 127.0.0.1)
- `--port PORT` - Port to bind to (default: 5000)
- `--debug` - Enable debug mode
- `--no-browser` - Don't open browser automatically

**Examples:**
```bash
# Start web interface
orc web

# Custom port
orc web --port 8080

# Allow external connections
orc web --host 0.0.0.0

# Debug mode
orc web --debug
```

---

### `orc optimize`

Get optimization suggestions.

```bash
orc optimize [OPTIONS] [FILE]
```

**Arguments:**
- `FILE` - File to optimize (default: all files)

**Options:**
- `--apply` - Apply suggestions automatically (use with caution!)
- `--interactive` - Review each suggestion interactively
- `--type TYPE` - Optimization type: algorithm, complexity, readability

**Examples:**
```bash
# Get suggestions for all files
orc optimize

# Optimize specific file
orc optimize src/utils.py

# Interactive mode
orc optimize --interactive

# Apply suggestions automatically
orc optimize --apply src/utils.py
```

---

### `orc config`

Manage configuration.

```bash
orc config [OPTIONS] [KEY] [VALUE]
```

**Options:**
- `--list` - List all settings
- `--set KEY VALUE` - Set configuration value
- `--get KEY` - Get configuration value
- `--reset` - Reset to defaults

**Examples:**
```bash
# List all settings
orc config --list

# Set AI provider
orc config --set ai.provider groq

# Get setting
orc config --get ai.model

# Reset configuration
orc config --reset
```

---

### `orc version`

Show version information.

```bash
orc version [OPTIONS]
```

**Options:**
- `--verbose` - Show detailed version info

**Example:**
```bash
orc version
orc version --verbose
```

---

## Environment Variables

ORC reads configuration from environment variables:

```bash
# AI Provider API Keys
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key

# ORC Settings
ORC_SECRET_KEY=your_secret_key
ORC_LOG_LEVEL=INFO
ORC_DATABASE_PATH=/path/to/database
```

## Configuration File

ORC uses `.orc/config.yaml` for project-specific settings:

```yaml
# .orc/config.yaml
version: "2.0"

# Analysis settings
analysis:
  exclude_patterns:
    - "node_modules/**"
    - "*.min.js"
    - "dist/**"
  
  complexity:
    max_complexity: 10
    warn_threshold: 7
  
  dead_code:
    exclude_tests: true
    exclude_init: true

# AI settings
ai:
  provider: groq
  model: mixtral-8x7b-32768
  max_context_tokens: 8000
  temperature: 0.7

# Indexing settings
indexing:
  parallel_workers: 4
  batch_size: 100
  cache_enabled: true
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Configuration error
- `4` - Analysis found issues (can be configured)

## Tips

1. **Use tab completion** - Enable bash/zsh completion for easier command usage
2. **Alias common commands** - Create shell aliases for frequent operations
3. **Integrate with CI/CD** - Run `orc analyze` in your CI pipeline
4. **Use `.orcignore`** - Keep unnecessary files out of analysis
5. **Start small** - Index small projects first to understand ORC's behavior

## See Also

- [Getting Started](../getting_started.md)
- [Configuration](../configuration.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
