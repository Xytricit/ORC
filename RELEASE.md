# ORC Release Notes

## Version 1.0.0 - Initial Release (2026-01-09)

### Overview

ORC (Optimization & Refactoring Catalyst) is an AI-powered codebase intelligence platform that helps developers analyze, optimize, and improve their code.

### Key Features

#### Core Functionality
- Multi-language code analysis (Python, JavaScript, TypeScript, React, HTML/CSS)
- AI-powered codebase querying and exploration
- Complexity analysis and dead code detection
- Dependency graph visualization
- Security vulnerability scanning

#### AI Chat Interface
- Interactive CLI with natural language queries
- Context-aware responses using codebase knowledge
- Tool-based analysis integration
- Multiple AI provider support (Groq, OpenAI, Anthropic, Gemini, Ollama)

#### SubAgents System
- Create specialized AI agents for different tasks
- Custom training and expertise per agent
- Persistent memory files (orc_<name>.md)
- Agent switching and @ mentions
- Independent context per agent

#### Memory & Context
- Persistent project memory (ORC.md)
- Auto-updates when analyzing codebase
- Context persists across sessions
- Smart context compression

#### Web Dashboard (Optional)
- Project management interface
- Analysis history tracking
- User authentication
- API configuration

### Installation

```bash
pip install orc-cli
```

### Quick Start

```bash
# Start ORC
orc

# Initialize project memory
/init

# Create a specialized agent
/create-agent

# Ask questions
analyze my codebase for security issues
```

### Requirements

- Python 3.9+
- At least one AI provider API key (Groq, OpenAI, etc.)

### Documentation

- User Guide: docs/ORC_CLI_QUICK_START.md
- SubAgents Guide: docs/SUBAGENTS_GUIDE.md
- API Documentation: docs/api/README.md

### Support

- Issues: https://github.com/xytricit/orc/issues
- Discussions: https://github.com/xytricit/orc/discussions

### License

MIT License - See LICENSE file

### Credits

Built with Rich, Click, NetworkX, and support for multiple AI providers.

---

For detailed changelog, see CHANGELOG.md
