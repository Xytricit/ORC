# ORC Configuration Guide

Complete guide to configuring ORC for your project.

## Configuration Files

ORC uses multiple configuration sources:

1. **`.orc/config.yaml`** - Project-specific settings
2. **`.env`** - Environment variables (API keys, secrets)
3. **`.orcignore`** - Files/directories to exclude

## Creating Configuration

### Initialize Default Config

```bash
orc init
```

This creates `.orc/config.yaml` with defaults:

```yaml
# .orc/config.yaml
version: "2.0"

# Project information
project:
  name: "My Project"
  description: "Project description"
  languages:
    - python
    - javascript
    - typescript

# Indexing settings
indexing:
  parallel_workers: 4        # Number of parallel workers (default: CPU count)
  batch_size: 100           # Files processed per batch
  cache_enabled: true       # Enable caching for faster re-indexing
  max_file_size: 1048576   # Max file size in bytes (1MB)

# Analysis settings
analysis:
  # Patterns to exclude from analysis
  exclude_patterns:
    - "node_modules/**"
    - "venv/**"
    - ".git/**"
    - "dist/**"
    - "build/**"
    - "*.min.js"
    - "__pycache__/**"
    - "*.pyc"
  
  # Complexity analysis
  complexity:
    max_complexity: 10       # Maximum cyclomatic complexity
    warn_threshold: 7        # Warning threshold
    fail_on_high: false      # Fail if high complexity found
  
  # Dead code detection
  dead_code:
    exclude_tests: true      # Exclude test files
    exclude_init: true       # Exclude __init__.py
    exclude_magic: true      # Exclude __str__, __repr__, etc.
    confidence_threshold: 70 # Minimum confidence to report (0-100)
    exclude_patterns:
      - "*/migrations/*"
      - "*/fixtures/*"
  
  # Security analysis
  security:
    check_sql_injection: true
    check_xss: true
    check_hardcoded_secrets: true
    check_insecure_crypto: true
    severity_threshold: "medium"  # low, medium, high, critical
  
  # Performance analysis
  performance:
    check_nested_loops: true
    check_string_concat: true
    check_repeated_calls: true
    max_function_lines: 200
    warn_function_lines: 100

# AI settings
ai:
  # Provider configuration
  provider: "groq"           # groq, openai, anthropic, deepseek, gemini
  model: "mixtral-8x7b-32768"
  
  # API key (use environment variable)
  api_key: "${GROQ_API_KEY}"
  
  # Context settings
  max_context_tokens: 8000
  max_context_files: 50
  
  # Generation settings
  temperature: 0.7
  max_tokens: 2000
  
  # Provider-specific models
  models:
    groq:
      - mixtral-8x7b-32768
      - llama-3.1-70b-versatile
      - gemma-7b-it
    openai:
      - gpt-4
      - gpt-3.5-turbo
    anthropic:
      - claude-3-opus
      - claude-3-sonnet

# Web interface settings
web:
  host: "127.0.0.1"
  port: 5000
  debug: false
  secret_key: "${ORC_SECRET_KEY}"
  
  # Database
  database_uri: "sqlite:///orc_web.db"
  
  # Session
  session_lifetime: 86400    # 24 hours in seconds

# Output settings
output:
  format: "text"             # text, json, html
  verbose: false
  color: true
  show_progress: true

# Logging
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: ".orc/orc.log"
  max_size: 10485760        # 10MB
  backup_count: 3
```

## Environment Variables

Create `.env` file for sensitive data:

```bash
# .env

# AI Provider API Keys
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
DEEPSEEK_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# ORC Settings
ORC_SECRET_KEY=your_secret_key_here
ORC_LOG_LEVEL=INFO
ORC_DATABASE_PATH=/path/to/database

# Optional: Custom paths
ORC_CONFIG_PATH=/custom/path/to/config.yaml
ORC_CACHE_DIR=/custom/cache/directory
```

**⚠️ Important:** Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

## Ignore Patterns

Create `.orcignore` file to exclude files/directories:

```bash
# .orcignore

# Dependencies
node_modules/
venv/
env/
.venv/
vendor/

# Build outputs
dist/
build/
out/
.next/
*.min.js
*.min.css

# Version control
.git/
.svn/
.hg/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
coverage/
.pytest_cache/
.coverage

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Secrets
.env
*.pem
*.key
secrets/
```

## Configuration Sections

### Project Settings

```yaml
project:
  name: "My Awesome Project"
  description: "E-commerce platform"
  version: "1.0.0"
  languages:
    - python
    - javascript
    - typescript
    - react
  
  # Project metadata
  author: "Your Name"
  repository: "https://github.com/username/repo"
```

### Indexing Settings

```yaml
indexing:
  # Performance tuning
  parallel_workers: 8        # Use more workers for faster indexing
  batch_size: 200           # Process more files at once
  
  # Caching
  cache_enabled: true
  cache_ttl: 3600           # Cache validity in seconds
  
  # File handling
  max_file_size: 5242880    # 5MB max file size
  encoding: "utf-8"
  
  # Include/exclude
  include_patterns:
    - "src/**/*.py"
    - "src/**/*.js"
  
  exclude_patterns:
    - "**/*.test.js"
    - "**/*.spec.py"
```

### Analysis Settings

#### Complexity

```yaml
analysis:
  complexity:
    max_complexity: 15       # Stricter = lower number
    warn_threshold: 10
    fail_on_high: true       # CI/CD will fail
    
    # Custom rules
    ignore_tests: true       # Don't check test files
    ignore_init: true        # Don't check __init__
    
    # Per-language settings
    languages:
      python:
        max_complexity: 10
      javascript:
        max_complexity: 15
```

#### Dead Code

```yaml
analysis:
  dead_code:
    # Exclusions
    exclude_tests: true
    exclude_init: true
    exclude_magic: true      # __str__, __repr__, etc.
    exclude_decorators:      # Don't flag decorated functions
      - "app.route"
      - "api.route"
      - "celery.task"
    
    # Patterns
    exclude_patterns:
      - "*/migrations/*"
      - "*/management/commands/*"
    
    # Keep specific functions
    keep_functions:
      - "main"
      - "cli_*"
      - "handle_*"
    
    # Confidence
    confidence_threshold: 80  # Only show 80%+ confidence
```

#### Security

```yaml
analysis:
  security:
    # Enable checks
    check_sql_injection: true
    check_xss: true
    check_hardcoded_secrets: true
    check_insecure_crypto: true
    check_path_traversal: true
    check_command_injection: true
    
    # Severity
    severity_threshold: "high"  # Only show high+ severity
    
    # Secret detection
    secret_patterns:
      - "password\\s*=\\s*['\"]\\w+"
      - "api_key\\s*=\\s*['\"]\\w+"
    
    # Allowed patterns (false positive reduction)
    allowed_patterns:
      - "password = 'test'"     # Test data
      - "API_KEY = os.getenv"   # Environment variables
```

#### Performance

```yaml
analysis:
  performance:
    # Detection
    check_nested_loops: true
    check_string_concat: true
    check_repeated_calls: true
    check_n_plus_one: true
    
    # Thresholds
    max_function_lines: 150
    warn_function_lines: 80
    max_loop_depth: 3
    
    # Database
    db_query_threshold: 100   # Warn if >100 queries
```

### AI Settings

```yaml
ai:
  # Default provider
  provider: "groq"
  model: "mixtral-8x7b-32768"
  
  # Fallback providers
  fallback_providers:
    - provider: "openai"
      model: "gpt-3.5-turbo"
    - provider: "anthropic"
      model: "claude-3-haiku"
  
  # Context configuration
  max_context_tokens: 16000
  max_context_files: 100
  context_strategy: "smart"   # smart, full, minimal
  
  # Generation
  temperature: 0.7
  max_tokens: 4000
  top_p: 0.9
  
  # Prompts
  system_prompt: |
    You are an expert code assistant analyzing a codebase.
    Provide clear, actionable suggestions.
  
  # Rate limiting
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 100000
```

### Web Interface

```yaml
web:
  # Server
  host: "0.0.0.0"           # Allow external access
  port: 8080                # Custom port
  debug: false              # Never enable in production
  
  # Security
  secret_key: "${ORC_SECRET_KEY}"
  csrf_enabled: true
  session_cookie_secure: true  # HTTPS only
  session_cookie_httponly: true
  
  # Database
  database_uri: "postgresql://user:pass@localhost/orc"
  
  # Session
  session_lifetime: 43200   # 12 hours
  permanent_session: false
  
  # Upload limits
  max_content_length: 16777216  # 16MB
  
  # CORS (if needed)
  cors_origins:
    - "https://yourdomain.com"
```

## Per-Language Configuration

```yaml
languages:
  python:
    # Parser settings
    parser: "ast"
    version: "3.9"
    
    # Analysis
    complexity:
      max_complexity: 10
    
    # Style
    line_length: 88
    
  javascript:
    parser: "babel"
    ecma_version: 2022
    
    complexity:
      max_complexity: 15
    
    # Frameworks
    frameworks:
      - react
      - vue
  
  typescript:
    parser: "typescript"
    strict: true
    
    complexity:
      max_complexity: 12
```

## Output Configuration

```yaml
output:
  # Format
  format: "html"             # text, json, html, markdown
  
  # Console output
  color: true
  show_progress: true
  verbose: false
  
  # File output
  save_to_file: true
  output_dir: "reports/"
  filename_template: "orc_report_{date}.html"
  
  # Report sections
  include:
    - summary
    - complexity
    - dead_code
    - security
    - recommendations
  
  # Formatting
  max_line_length: 100
  truncate_paths: true
```

## Logging Configuration

```yaml
logging:
  # Level
  level: "INFO"              # DEBUG for troubleshooting
  
  # File logging
  file: ".orc/logs/orc.log"
  max_size: 10485760        # 10MB
  backup_count: 5
  
  # Format
  format: "[%(asctime)s] %(levelname)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  # Console logging
  console_enabled: true
  console_level: "WARNING"
```

## Command-Line Overrides

Override config from CLI:

```bash
# Override provider
orc chat --provider openai --model gpt-4

# Override workers
orc index --workers 8

# Override output format
orc analyze --format json --output report.json

# Override log level
orc --verbose analyze

# Multiple overrides
orc analyze --complexity-max 15 --fail-on-high
```

## Environment-Specific Configs

### Development

```yaml
# .orc/config.dev.yaml
ai:
  provider: "groq"          # Free tier
  model: "mixtral-8x7b-32768"

web:
  debug: true
  host: "127.0.0.1"

logging:
  level: "DEBUG"
```

### Production

```yaml
# .orc/config.prod.yaml
ai:
  provider: "openai"        # Paid tier
  model: "gpt-4"

web:
  debug: false
  host: "0.0.0.0"
  session_cookie_secure: true

logging:
  level: "WARNING"
  file: "/var/log/orc/orc.log"
```

### Load Config

```bash
# Use specific config
ORC_CONFIG=.orc/config.prod.yaml orc web

# Or in code
orc web --config .orc/config.prod.yaml
```

## Validation

Validate your configuration:

```bash
# Check config is valid
orc config --validate

# Show current config
orc config --show

# Show specific setting
orc config --get ai.provider
```

## Best Practices

1. **Use environment variables** for secrets
2. **Version control** `.orc/config.yaml`
3. **Don't commit** `.env` file
4. **Document** custom settings
5. **Test** config changes before deploying
6. **Use** per-environment configs
7. **Validate** before running in CI/CD

## Troubleshooting

### Config not loading

```bash
# Check config path
orc config --show-path

# Validate config
orc config --validate
```

### API keys not working

```bash
# Check environment variables
env | grep API_KEY

# Test API key
orc chat --test-connection
```

### Performance issues

```yaml
# Increase workers
indexing:
  parallel_workers: 16

# Reduce batch size
indexing:
  batch_size: 50

# Disable cache
indexing:
  cache_enabled: false
```

## Examples

See example configs:
- [Minimal Config](../examples/config.minimal.yaml)
- [Full Config](../examples/config.full.yaml)
- [Django Project](../examples/config.django.yaml)
- [React Project](../examples/config.react.yaml)

## See Also

- [Getting Started](getting_started.md)
- [CLI Reference](cli/README.md)
- [Custom Parsers](custom_parsers.md)
