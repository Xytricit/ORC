# Getting Started with ORC

Welcome to ORC (Optimization & Refactoring Catalyst)! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Basic familiarity with command line

## Installation

Install ORC via pip:

```bash
pip install orc-cli
```

Verify the installation:

```bash
orc --version
```

## First Steps

### 1. Initialize ORC in Your Project

Navigate to your project directory and initialize ORC:

```bash
cd /path/to/your/project
orc init
```

This creates a `.orc` configuration file in your project.

### 2. Index Your Codebase

Index your codebase to build the dependency graph:

```bash
orc index
```

ORC will:
- Scan all supported files (Python, JavaScript, TypeScript, React, etc.)
- Build a dependency graph
- Extract functions, classes, and imports
- Store everything in a local database

### 3. Run Your First Analysis

Analyze your codebase for issues:

```bash
orc analyze
```

This will show you:
- Code complexity metrics
- Dead code detection
- Security vulnerabilities
- Performance bottlenecks
- Code smells

### 4. Use AI Chat (Optional)

If you have an AI API key configured, you can chat with your codebase:

```bash
orc chat
```

Ask questions like:
- "What does the authentication system do?"
- "Find all database queries"
- "How can I optimize this function?"

## Configuration

### API Keys

To use AI features, set up your API keys:

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys
# GROQ_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### Custom Ignore Patterns

Create a `.orcignore` file to exclude directories:

```
node_modules/
.git/
dist/
build/
__pycache__/
*.min.js
```

## Web Interface

Launch the web dashboard for a visual interface:

```bash
orc web
```

Then open http://localhost:5000 in your browser.

Features include:
- Visual dependency graphs
- Interactive analysis results
- Project management
- AI chat interface
- Statistics dashboard

## Common Commands

```bash
# Index your codebase
orc index

# Analyze code quality
orc analyze

# Find dead code
orc analyze --dead-code

# Check security issues
orc analyze --security

# Run complexity analysis
orc analyze --complexity

# Chat with AI about your code
orc chat

# Start web interface
orc web

# Show help
orc --help
```

## Next Steps

- [CLI Reference](cli/README.md) - Complete command documentation
- [Your First Analysis](tutorials/first_analysis.md) - Detailed walkthrough
- [Using AI Chat](tutorials/ai_chat.md) - AI-powered code assistance
- [Configuration](configuration.md) - Customize ORC's behavior

## Getting Help

- Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
- Report bugs on [GitHub Issues](https://github.com/xytricit/orc/issues)
- Email: andohbempahnanaakwasi@gmail.com

## Quick Tips

✅ **Do:**
- Run `orc index` after adding new files
- Use `.orcignore` to exclude large directories
- Keep your API keys in `.env` (never commit them!)
- Run analyses regularly to catch issues early

❌ **Don't:**
- Don't index `node_modules` or similar large directories
- Don't commit your `.env` file with API keys
- Don't run ORC on non-code files (PDFs, images, etc.)

Happy coding! 🚀
