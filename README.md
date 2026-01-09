# ORC - Optimization & Refactoring Catalyst

<div align="center">

![ORC Logo](assets/orclogo.png)

**Your AI-Powered Code Intelligence Assistant**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## What is ORC?

ORC is an intelligent code analysis and refactoring assistant that combines powerful static analysis with AI to help you understand, optimize, and improve your codebase. Whether you're dealing with technical debt, trying to understand legacy code, or optimizing performance, ORC is your trusty companion.

### Why ORC?

- **AI-Powered Intelligence**: Chat with your codebase using natural language
- **Deep Analysis**: Find dead code, complexity hotspots, and performance issues
- **Beautiful Web Dashboard**: Visualize your code metrics and track improvements
- **Lightning Fast**: Efficiently indexes and analyzes large codebases
- **Modern UI**: Sleek black & green interface with real-time notifications
- **Privacy First**: All analysis runs locally, your code never leaves your machine

---

## Features

### AI-Powered Code Chat
```bash
orc
> "Show me the most complex functions"
> "Find unused code in the authentication module"
> "Explain what the UserService class does"
```

### Comprehensive Analysis
- **Dead Code Detection**: Find unused functions, classes, and imports
- **Complexity Analysis**: Identify functions that need refactoring
- **Dependency Mapping**: Visualize how your modules interact
- **Performance Hotspots**: Pinpoint optimization opportunities
- **Code Metrics**: Track LOC, cyclomatic complexity, and more

### Professional Web Interface
- **Interactive Dashboard**: Beautiful stats and visualizations
- **Project Management**: Handle multiple codebases effortlessly
- **AI Chat Interface**: Talk to your code through the web
- **Analysis History**: Track improvements over time
- **Smart Search**: Find documentation instantly with dropdown suggestions

### Developer-Friendly CLI
```bash
orc index              # Index your codebase
orc analyze            # Run full analysis
orc dead               # Find dead code
orc complexity         # Check complexity metrics
orc hotspots           # Find performance issues
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Option 1: Install from PyPI (Recommended)
```bash
# Install the latest stable release
pip install orc-cli

# Verify installation
orc --version
```

### Option 2: Install from TestPyPI (Beta/Testing)
```bash
# Install from TestPyPI for testing new features
pip install -i https://test.pypi.org/simple/ orc-cli==2.0.0

# Verify installation
orc --version
```

### Option 3: Install from GitHub (Latest Development)
```bash
# Install directly from GitHub main branch
pip install git+https://github.com/xytricit/orc.git

# Or clone and install in development mode
git clone https://github.com/xytricit/orc.git
cd orc
pip install -e .

# Verify installation
orc --version
```

### Optional: Install with Web Interface (Local Development)
```bash
# If you want to run the web interface locally
pip install orc-cli[web]

# Note: The production web app is deployed separately at [your-domain]
```

### Upgrading
```bash
# Upgrade to the latest version
pip install --upgrade orc-cli

# Or from TestPyPI
pip install --upgrade -i https://test.pypi.org/simple/ orc-cli
```

---

## Quick Start

### 1. Authenticate
```bash
orc login
```
This opens your browser to create an account and generate a CLI token.

### 2. Index Your Codebase
```bash
cd your-project
orc index
```

### 3. Start AI Chat
```bash
orc
```
Now chat with your codebase using natural language!

### 4. Access Web Dashboard
```bash
# Start the web server (runs automatically)
# Visit: http://127.0.0.1:5000
```

---

## Documentation

### User Guides
- [Getting Started](docs/getting_started.md) - First steps with ORC
- [CLI Reference](docs/cli/README.md) - Complete command documentation
- [Web Interface Guide](docs/web/README.md) - Using the dashboard
- [API Documentation](docs/api/README.md) - Integrate ORC into your tools

### Tutorials
- [Your First Analysis](docs/tutorials/first_analysis.md)
- [Using AI Chat](docs/tutorials/ai_chat.md)
- [Finding Dead Code](docs/tutorials/dead_code.md)
- [Performance Optimization](docs/tutorials/performance.md)

### Advanced Topics
- [Configuration](docs/configuration.md) - Customize ORC's behavior
- [Custom Parsers](docs/custom_parsers.md) - Add support for new languages
- [Deployment Guide](docs/DEPLOYMENT.md) - Production setup
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

---

## 🎨 Screenshots

### AI-Powered Chat
![CLI Chat](docs/screenshots/cli_chat.png)

### Web Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Analysis Results
![Analysis](docs/screenshots/analysis.png)

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Integration**: Multi-provider support (Groq, OpenAI, Anthropic, DeepSeek)
- **Code Analysis**: AST parsing, static analysis
- **Database**: SQLite (local), PostgreSQL (production)
- **CLI**: Click, Rich, Prompt Toolkit

---

## Contributing

We love contributions! Whether it's bug fixes, new features, or documentation improvements, all help is appreciated.

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📋 Roadmap

### Version 2.1 (Next Release)
- [ ] VS Code Extension
- [ ] GitHub Integration
- [ ] Multi-language support (Java, Go, Rust)
- [ ] Team collaboration features
- [ ] Advanced refactoring suggestions

### Future Plans
- [ ] JetBrains IDE Plugin
- [ ] CI/CD Integration
- [ ] Cloud-hosted option
- [ ] Enterprise features
- [ ] Real-time collaboration

---

## 🔒 Security

ORC takes security seriously:
- All code analysis runs **locally on your machine**
- API keys are **encrypted** and never exposed
- No code is sent to external servers (except AI API calls)
- Open source - audit the code yourself

See [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

---

## 📜 License

ORC is released under the [MIT License](LICENSE). Feel free to use it in your projects, both personal and commercial.

---

## 💖 Acknowledgments

- Built with love by the ORC team
- Inspired by the best code analysis tools
- Special thanks to all our contributors
- AI providers: Groq, OpenAI, Anthropic, DeepSeek

---

## Support & Community

- [Report a Bug](https://github.com/xytricit/orc/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/xytricit/orc/issues/new?template=feature_request.md)
- [Join Discord](https://discord.gg/orc-community) (Coming Soon)
- [Email Us](mailto:andohbempahnanaakwasi@gmail.com)

---

## 🌟 Star Us!

If you find ORC useful, please give us a star on GitHub! It helps us grow and improve.

[![GitHub stars](https://img.shields.io/github/stars/xytricit/orc?style=social)](https://github.com/xytricit/orc/stargazers)

---

<div align="center">

**Made with 💚 by developers, for developers**

[Website](https://orc-tool.dev) • [Documentation](https://docs.orc-tool.dev) • [Blog](https://blog.orc-tool.dev)

</div>
