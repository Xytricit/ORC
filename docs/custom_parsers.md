# Custom Parsers for ORC

Learn how to add support for new programming languages and file formats.

## Overview

ORC uses parsers to extract information from source code:
- Functions/methods
- Classes
- Imports/dependencies
- Variables
- Comments

Built-in parsers support:
- Python
- JavaScript
- TypeScript
- React (JSX/TSX)
- HTML/CSS
- JSON/YAML
- Markdown

## When to Create a Custom Parser

Create a custom parser when you need to:
- Support a new programming language
- Parse domain-specific languages (DSL)
- Extract custom metadata
- Handle proprietary file formats
- Improve parsing accuracy for specific frameworks

## Parser Architecture

### Base Parser Class

All parsers inherit from `BaseParser`:

```python
from orc.parsers.base_parser import BaseParser

class MyCustomParser(BaseParser):
    """Parser for MyLanguage files"""
    
    def __init__(self):
        super().__init__()
        self.language = "mylanguage"
        self.extensions = [".myl", ".mylang"]
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the file"""
        return file_path.endswith(tuple(self.extensions))
    
    def parse(self, file_path: str, content: str) -> dict:
        """Parse file and extract information"""
        # Your parsing logic here
        return {
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'metadata': {}
        }
```

## Creating a Simple Parser

### Example: Go Language Parser

```python
# orc/parsers/go_parser.py

import re
from orc.parsers.base_parser import BaseParser

class GoParser(BaseParser):
    """Parser for Go language files"""
    
    def __init__(self):
        super().__init__()
        self.language = "go"
        self.extensions = [".go"]
    
    def can_parse(self, file_path: str) -> bool:
        return file_path.endswith(".go")
    
    def parse(self, file_path: str, content: str) -> dict:
        """Parse Go source code"""
        result = {
            'file_path': file_path,
            'language': 'go',
            'functions': self._extract_functions(content),
            'classes': [],  # Go doesn't have classes
            'imports': self._extract_imports(content),
            'variables': self._extract_variables(content),
            'metadata': {
                'package': self._extract_package(content),
                'line_count': len(content.split('\n'))
            }
        }
        return result
    
    def _extract_package(self, content: str) -> str:
        """Extract package name"""
        match = re.search(r'^package\s+(\w+)', content, re.MULTILINE)
        return match.group(1) if match else None
    
    def _extract_imports(self, content: str) -> list:
        """Extract import statements"""
        imports = []
        
        # Single import: import "fmt"
        single = re.finditer(r'import\s+"([^"]+)"', content)
        for match in single:
            imports.append({
                'name': match.group(1),
                'type': 'import',
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Multiple imports: import ( ... )
        multi = re.search(r'import\s*\((.*?)\)', content, re.DOTALL)
        if multi:
            for line in multi.group(1).split('\n'):
                match = re.search(r'"([^"]+)"', line)
                if match:
                    imports.append({
                        'name': match.group(1),
                        'type': 'import',
                        'line': content[:multi.start()].count('\n') + 1
                    })
        
        return imports
    
    def _extract_functions(self, content: str) -> list:
        """Extract function definitions"""
        functions = []
        
        # Pattern: func functionName(args) returnType { ... }
        pattern = r'func\s+(\w+)\s*\((.*?)\)\s*([^{]*)\s*\{'
        
        for match in re.finditer(pattern, content):
            name = match.group(1)
            params = match.group(2)
            return_type = match.group(3).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            # Find function end (simplified - doesn't handle nested braces)
            start = match.end()
            brace_count = 1
            end = start
            
            for i, char in enumerate(content[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break
            
            body = content[start:end]
            
            functions.append({
                'name': name,
                'type': 'function',
                'line': line_num,
                'params': self._parse_params(params),
                'return_type': return_type,
                'complexity': self._calculate_complexity(body),
                'line_count': body.count('\n') + 1
            })
        
        return functions
    
    def _parse_params(self, params_str: str) -> list:
        """Parse function parameters"""
        if not params_str.strip():
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if param:
                # Go params: name type
                parts = param.split()
                if len(parts) >= 2:
                    params.append({
                        'name': parts[0],
                        'type': ' '.join(parts[1:])
                    })
        
        return params
    
    def _extract_variables(self, content: str) -> list:
        """Extract variable declarations"""
        variables = []
        
        # var varName type = value
        var_pattern = r'var\s+(\w+)\s+(\w+)'
        for match in re.finditer(var_pattern, content):
            variables.append({
                'name': match.group(1),
                'type': match.group(2),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return variables
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        # Count decision points
        keywords = ['if', 'for', 'switch', 'case', '&&', '||']
        for keyword in keywords:
            complexity += code.count(keyword)
        
        return complexity
```

### Register the Parser

```python
# orc/parsers/__init__.py

from orc.parsers.python_parser import PythonParser
from orc.parsers.javascript_parser import JavaScriptParser
from orc.parsers.go_parser import GoParser  # Add your parser

PARSERS = {
    'python': PythonParser,
    'javascript': JavaScriptParser,
    'go': GoParser,  # Register it
}

def get_parser(file_path: str):
    """Get appropriate parser for file"""
    for name, parser_class in PARSERS.items():
        parser = parser_class()
        if parser.can_parse(file_path):
            return parser
    return None
```

## Using AST-based Parsing

For better accuracy, use language-specific AST parsers:

### Example: Ruby Parser with AST

```python
# Requires: pip install parser

import parser
from orc.parsers.base_parser import BaseParser

class RubyParser(BaseParser):
    """Parser for Ruby using AST"""
    
    def __init__(self):
        super().__init__()
        self.language = "ruby"
        self.extensions = [".rb"]
    
    def parse(self, file_path: str, content: str) -> dict:
        try:
            # Parse Ruby code to AST
            tree = parser.parse(content)
            
            return {
                'file_path': file_path,
                'language': 'ruby',
                'functions': self._extract_functions_ast(tree),
                'classes': self._extract_classes_ast(tree),
                'imports': self._extract_imports_ast(tree),
                'variables': [],
                'metadata': {}
            }
        except SyntaxError as e:
            return self._handle_parse_error(file_path, str(e))
    
    def _extract_functions_ast(self, tree) -> list:
        """Extract functions from AST"""
        functions = []
        
        # Walk AST and find function definitions
        for node in tree.walk():
            if node.type == 'def':
                functions.append({
                    'name': node.name,
                    'type': 'function',
                    'line': node.line,
                    'params': [p.name for p in node.params],
                    'complexity': self._calculate_complexity_ast(node)
                })
        
        return functions
```

## Advanced Parser Features

### 1. Dependency Analysis

```python
def _extract_dependencies(self, imports: list) -> list:
    """Analyze import dependencies"""
    dependencies = []
    
    for imp in imports:
        dep = {
            'module': imp['name'],
            'type': self._classify_import(imp['name']),
            'line': imp['line']
        }
        dependencies.append(dep)
    
    return dependencies

def _classify_import(self, module_name: str) -> str:
    """Classify import as local, stdlib, or third-party"""
    if module_name.startswith('.'):
        return 'local'
    elif module_name in STDLIB_MODULES:
        return 'stdlib'
    else:
        return 'third-party'
```

### 2. Framework Detection

```python
def _detect_framework(self, content: str, imports: list) -> str:
    """Detect framework being used"""
    import_names = [imp['name'] for imp in imports]
    
    if 'django' in import_names:
        return 'django'
    elif 'flask' in import_names:
        return 'flask'
    elif 'fastapi' in import_names:
        return 'fastapi'
    
    return None
```

### 3. Documentation Extraction

```python
def _extract_docstrings(self, functions: list, content: str) -> dict:
    """Extract documentation for functions"""
    docs = {}
    
    for func in functions:
        # Find docstring after function definition
        pattern = rf'func {func["name"]}.*?\{{[\s\n]*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            docs[func['name']] = match.group(1).strip()
    
    return docs
```

### 4. Type Hint Extraction

```python
def _extract_type_hints(self, func_node) -> dict:
    """Extract type hints from function"""
    hints = {
        'params': {},
        'return': None
    }
    
    # Extract parameter types
    for param in func_node.params:
        if param.type_annotation:
            hints['params'][param.name] = param.type_annotation
    
    # Extract return type
    if func_node.return_type:
        hints['return'] = func_node.return_type
    
    return hints
```

## Testing Your Parser

### Unit Tests

```python
# tests/test_go_parser.py

import pytest
from orc.parsers.go_parser import GoParser

def test_parse_simple_function():
    """Test parsing a simple Go function"""
    content = '''
    package main
    
    func add(a int, b int) int {
        return a + b
    }
    '''
    
    parser = GoParser()
    result = parser.parse("test.go", content)
    
    assert len(result['functions']) == 1
    assert result['functions'][0]['name'] == 'add'
    assert len(result['functions'][0]['params']) == 2

def test_parse_imports():
    """Test import extraction"""
    content = '''
    package main
    
    import (
        "fmt"
        "os"
    )
    '''
    
    parser = GoParser()
    result = parser.parse("test.go", content)
    
    assert len(result['imports']) == 2
    assert 'fmt' in [i['name'] for i in result['imports']]
```

### Integration Test

```bash
# Create test file
cat > test.go << EOF
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
EOF

# Test with ORC
orc init
orc index
orc query "main" --type function
```

## Configuration

Add parser configuration to `.orc/config.yaml`:

```yaml
parsers:
  go:
    enabled: true
    extensions:
      - .go
    options:
      extract_comments: true
      extract_types: true
      max_complexity: 15
```

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache

class OptimizedParser(BaseParser):
    
    @lru_cache(maxsize=1000)
    def parse(self, file_path: str, content: str) -> dict:
        # Parsing logic
        pass
```

### 2. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def parse_multiple_files(file_paths: list) -> list:
    """Parse multiple files in parallel"""
    parser = MyParser()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(parser.parse_file, file_paths))
    
    return results
```

### 3. Incremental Parsing

```python
class IncrementalParser(BaseParser):
    
    def parse_changes(self, old_content: str, new_content: str) -> dict:
        """Only parse changed sections"""
        diff = self._compute_diff(old_content, new_content)
        
        # Only re-parse changed functions
        changed_functions = self._parse_diff(diff)
        
        return changed_functions
```

## Best Practices

1. **Handle Errors Gracefully** - Don't crash on malformed code
2. **Use AST When Possible** - More accurate than regex
3. **Extract Metadata** - Line numbers, file paths, etc.
4. **Calculate Complexity** - Cyclomatic complexity is useful
5. **Test Thoroughly** - Test edge cases and malformed code
6. **Document** - Explain what your parser extracts
7. **Optimize** - Cache results, parse incrementally
8. **Follow Conventions** - Match ORC's data format

## Parser Registry

Register parsers dynamically:

```python
# orc/parsers/registry.py

class ParserRegistry:
    def __init__(self):
        self._parsers = {}
    
    def register(self, language: str, parser_class):
        """Register a parser"""
        self._parsers[language] = parser_class
    
    def get_parser(self, file_path: str):
        """Get parser for file"""
        for parser_class in self._parsers.values():
            parser = parser_class()
            if parser.can_parse(file_path):
                return parser
        return None

# Global registry
registry = ParserRegistry()

# Register parsers
registry.register('python', PythonParser)
registry.register('go', GoParser)
```

## Example Parsers

### Minimal Parser

```python
class MinimalParser(BaseParser):
    """Simplest possible parser"""
    
    def __init__(self):
        super().__init__()
        self.language = "text"
        self.extensions = [".txt"]
    
    def parse(self, file_path: str, content: str) -> dict:
        return {
            'file_path': file_path,
            'language': 'text',
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'metadata': {
                'line_count': len(content.split('\n')),
                'char_count': len(content)
            }
        }
```

### SQL Parser

```python
class SQLParser(BaseParser):
    """Parser for SQL files"""
    
    def parse(self, file_path: str, content: str) -> dict:
        return {
            'file_path': file_path,
            'language': 'sql',
            'functions': self._extract_procedures(content),
            'classes': self._extract_tables(content),
            'imports': [],
            'variables': [],
            'metadata': {
                'queries': self._extract_queries(content)
            }
        }
    
    def _extract_procedures(self, content: str) -> list:
        """Extract stored procedures"""
        pattern = r'CREATE\s+PROCEDURE\s+(\w+)'
        procedures = []
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            procedures.append({
                'name': match.group(1),
                'type': 'procedure',
                'line': content[:match.start()].count('\n') + 1
            })
        
        return procedures
```

## Contributing Parsers

To contribute a parser to ORC:

1. Create parser in `orc/parsers/`
2. Add tests in `tests/`
3. Update documentation
4. Submit pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## See Also

- [Getting Started](getting_started.md)
- [Configuration](configuration.md)
- [API Documentation](api/README.md)

## Summary

You've learned to:
- ✅ Create custom parsers
- ✅ Use AST-based parsing
- ✅ Extract language-specific features
- ✅ Test parsers thoroughly
- ✅ Register parsers with ORC
- ✅ Optimize parser performance

Happy parsing! 🎯
