# ORC API Documentation

This directory contains API reference documentation for ORC.

## Overview

ORC provides multiple APIs for different use cases:

1. **Python API** - Use ORC as a library in your Python code
2. **REST API** - HTTP endpoints for remote access
3. **CLI API** - Command-line interface

## Python API

### Core Components

#### Indexer
```python
from orc.core.indexer import Indexer

indexer = Indexer(root_path="./my-project")
result = indexer.index()
print(f"Indexed {result['total_files']} files")
```

#### Analyzer
```python
from orc.core.analyzer import Analyzer

analyzer = Analyzer(db_path=".orc/orc.db")
metrics = analyzer.analyze_metrics()
dead_code = analyzer.find_dead_code()
```

#### Graph Builder
```python
from orc.core.graph_builder import DependencyGraph

graph = DependencyGraph()
graph.build_from_db(".orc/orc.db")
dependencies = graph.get_dependencies("mymodule")
```

### Analysis Modules

#### Complexity Analysis
```python
from orc.analysis.complexity import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
report = analyzer.analyze_file("path/to/file.py")
print(f"Average complexity: {report['average_complexity']}")
```

#### Dead Code Detection
```python
from orc.orc_package.analysis.dead_code import DeadCodeDetector

detector = DeadCodeDetector(root_path=".")
unused = detector.find_unused_functions()
```

#### Security Analysis
```python
from orc.analysis.security import SecurityAnalyzer

analyzer = SecurityAnalyzer()
vulnerabilities = analyzer.scan_file("path/to/file.py")
```

### Parsers

ORC supports multiple languages through a plugin-based parser system:

```python
from orc.parsers.python_parser import PythonParser
from orc.parsers.javascript_parser import JavaScriptParser
from orc.parsers.react_parser import ReactParser

# Python
parser = PythonParser()
result = parser.parse_file("script.py")

# JavaScript
js_parser = JavaScriptParser()
result = js_parser.parse_file("app.js")

# React/JSX
react_parser = ReactParser()
result = react_parser.parse_file("Component.jsx")
```

## REST API

See [REST API Documentation](rest_api.md) for HTTP endpoint details.

### Quick Example

```bash
# Start the API server
orc serve --port 5000

# Make requests
curl http://localhost:5000/api/v1/analyze?path=./src
```

### Authentication

```python
import requests

# Generate API token via web dashboard
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("http://localhost:5000/api/v1/stats", headers=headers)
```

## CLI API

See [CLI Documentation](../cli/README.md) for command-line usage.

### Programmatic CLI Usage

```python
from orc.cli_main import cli
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(cli, ['stats'])
print(result.output)
```

## Data Models

### Project Structure
```python
{
    "name": "my-project",
    "path": "/path/to/project",
    "languages": ["Python", "JavaScript"],
    "total_files": 150,
    "total_lines": 15000,
    "modules": [...],
    "dependencies": [...]
}
```

### Complexity Report
```python
{
    "file": "path/to/file.py",
    "functions": [
        {
            "name": "complex_function",
            "complexity": 15,
            "line_number": 42,
            "severity": "high"
        }
    ],
    "average_complexity": 8.5
}
```

### Dead Code Report
```python
{
    "unused_functions": [
        {
            "name": "unused_func",
            "file": "module.py",
            "line": 100,
            "confidence": 0.95
        }
    ],
    "unused_classes": [...],
    "total_unused": 10
}
```

## Configuration

### Environment Variables
```python
import os

# Set configuration
os.environ['ORC_AI_PROVIDER'] = 'groq'
os.environ['ORC_MAX_TOKENS'] = '4000'

# Use in code
from orc.config import get_config

config = get_config()
print(config.ai_provider)
```

### Configuration File
```python
from orc.config import Config

config = Config.from_file(".orcrc")
config.complexity_threshold = 15
config.save(".orcrc")
```

## Advanced Usage

### Custom Parsers

Create your own parser for unsupported languages:

```python
from orc.parsers.base_parser import BaseParser

class MyCustomParser(BaseParser):
    def parse_file(self, file_path):
        # Your parsing logic
        return {
            "files": [file_path],
            "functions": [...],
            "classes": [...]
        }
```

### Custom Analysis Rules

```python
from orc.optimization.suggester import OptimizationSuggester

suggester = OptimizationSuggester()

# Add custom rule
suggester.add_rule({
    "name": "Custom Rule",
    "pattern": r"my_pattern",
    "severity": "medium",
    "suggestion": "Use better approach"
})

suggestions = suggester.analyze_file("file.py")
```

### Integration with CI/CD

```python
from orc.integrations.ci_cd import CIIntegration

ci = CIIntegration()
ci.set_threshold(complexity=15, coverage=80)

# Run analysis
report = ci.analyze_project(".")

# Exit with code 1 if thresholds exceeded
if report['failed']:
    exit(1)
```

## API Reference by Module

- [Core](core.md) - Indexing, analysis, graph building
- [Analysis](analysis.md) - Complexity, security, patterns
- [Parsers](parsers.md) - Language-specific parsers
- [Optimization](optimization.md) - Code suggestions and improvements
- [Context](context.md) - Smart context building for AI
- [Web](web.md) - Web dashboard API
- [Integrations](integrations.md) - Git, CI/CD integrations

## Examples

See the [examples/](../../examples/) directory for complete working examples.

## Support

- [GitHub Issues](https://github.com/xytricit/orc/issues)
- [Documentation](https://github.com/xytricit/orc)
- [Contributing](../../CONTRIBUTING.md)
