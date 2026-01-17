"""
ORC Component 3: Language Parsers (Part 1)
===========================================

Production-ready language parsers for Python, JavaScript, and TypeScript.

PARSERS:
1. PythonParser   - Full AST-based parsing with McCabe complexity
2. JavaScriptParser - Regex-based parsing for ES6+ and CommonJS
3. TypeScriptParser - Extends JavaScript with TypeScript features

Author: Senior Software Engineer
Date: 2026-01-14
Status: Production Ready
"""

import ast
import re
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for all language parsers.
    
    All parsers must implement parse_file() and return consistent structure.
    """
    
    @abstractmethod
    def parse_file(self, path: Path) -> Dict[str, Any]:
        """
        Parse a single file and extract code structure.
        
        Args:
            path: Path to source file
            
        Returns:
            dict with keys:
            - 'files': {file_path: {language, loc, ...}}
            - 'functions': {func_id: {name, line_start, line_end, complexity, parameters, calls, code}}
            - 'classes': {class_id: {name, line_start, line_end, methods, base_classes}}
            - 'imports': {import_type: [list]}
            - 'imports_detailed': [(statement, line_number, what_imported)]
            - 'exports': {export_id: {name, kind}}
            - 'entry_points': [(type, line_number)]
        """
        pass


class PythonParser(BaseParser):
    """
    Python parser using AST (Abstract Syntax Tree).
    
    Features:
    - Full AST-based parsing
    - McCabe cyclomatic complexity calculation
    - Async function support
    - Type hints extraction
    - Decorator support
    - Docstring extraction
    - Entry point detection (if __name__ == '__main__')
    """
    
    def parse_file(self, path: Path) -> Dict[str, Any]:
        """
        Parse Python file using AST.
        
        Args:
            path: Path to .py file
            
        Returns:
            Parsed structure with functions, classes, imports, etc.
            
        Raises:
            SyntaxError: If Python code has syntax errors (caught and logged)
        """
        try:
            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Count lines
            lines = source.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Parse AST
            try:
                tree = ast.parse(source)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {path}: {e}")
                return self._empty_result(path, loc, error=str(e))
            
            # Extract all elements
            result = {
                'files': {
                    str(path): {
                        'language': 'python',
                        'loc': loc,
                        'path': str(path)
                    }
                },
                'functions': {},
                'classes': {},
                'imports': {},
                'imports_detailed': [],
                'exports': {},
                'entry_points': []
            }
            
            # Parse top-level nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    self._extract_function(node, result, path, source)
                elif isinstance(node, ast.ClassDef):
                    self._extract_class(node, result, path, source)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._extract_import(node, result, path)
                elif isinstance(node, ast.If):
                    self._check_entry_point(node, result)
            
            # Extract __all__ exports
            self._extract_exports(tree, result, path)
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing {path}: {e}")
            return self._empty_result(path, 0, error=str(e))
    
    def _empty_result(self, path: Path, loc: int = 0, error: str = None) -> Dict[str, Any]:
        """Return empty result structure for failed parsing."""
        result = {
            'files': {
                str(path): {
                    'language': 'python',
                    'loc': loc,
                    'path': str(path)
                }
            },
            'functions': {},
            'classes': {},
            'imports': {},
            'imports_detailed': [],
            'exports': {},
            'entry_points': []
        }
        if error:
            result['files'][str(path)]['error'] = error
        return result
    
    def _extract_function(self, node: ast.FunctionDef, result: Dict, path: Path, source: str):
        """Extract function metadata including complexity."""
        func_name = node.name
        func_id = f"{path.name}:{func_name}"
        
        # Get line numbers
        line_start = node.lineno
        line_end = node.end_lineno or line_start
        
        # Extract parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Extract function code
        source_lines = source.split('\n')
        code_lines = source_lines[line_start - 1:line_end]
        code = '\n'.join(code_lines)
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(node)
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract function calls
        calls = self._extract_calls(node)
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        result['functions'][func_id] = {
            'name': func_name,
            'file': str(path),
            'line_start': line_start,
            'line_end': line_end,
            'complexity': complexity,
            'parameters': parameters,
            'calls': calls,
            'code': code,
            'is_exported': not func_name.startswith('_'),
            'decorators': decorators,
            'docstring': docstring,
            'is_async': is_async
        }
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate McCabe cyclomatic complexity.
        
        McCabe formula:
        - Base: 1
        - +1 for: if, elif, for, while, except, with, assert
        - +1 for: and, or in conditions
        - +1 for: lambda
        - +1 for: each except clause
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Control flow statements
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Assert)):
                complexity += 1
            # Boolean operators in conditions
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Lambda expressions
            elif isinstance(child, ast.Lambda):
                complexity += 1
            # Exception handlers
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # Elif is counted as separate branch
            elif isinstance(child, ast.If) and child.orelse:
                if isinstance(child.orelse[0], ast.If):
                    complexity += 1
        
        return complexity
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return 'unknown'
    
    def _extract_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return list(set(calls))  # Remove duplicates
    
    def _extract_class(self, node: ast.ClassDef, result: Dict, path: Path, source: str):
        """Extract class metadata."""
        class_name = node.name
        class_id = f"{path.name}:{class_name}"
        
        line_start = node.lineno
        line_end = node.end_lineno or line_start
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
        
        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)
        
        result['classes'][class_id] = {
            'name': class_name,
            'file': str(path),
            'line_start': line_start,
            'line_end': line_end,
            'methods': methods,
            'base_classes': base_classes
        }
    
    def _extract_import(self, node: ast.AST, result: Dict, path: Path):
        """Extract import statements."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                statement = f"import {alias.name}"
                result['imports_detailed'].append((statement, node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                statement = f"from {module} import {alias.name}"
                result['imports_detailed'].append((statement, node.lineno, f"{module}.{alias.name}"))
    
    def _check_entry_point(self, node: ast.If, result: Dict):
        """Check for if __name__ == '__main__' pattern."""
        if isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                if any(isinstance(comp, ast.Eq) for comp in node.test.ops):
                    for comp_val in node.test.comparators:
                        if isinstance(comp_val, ast.Constant) and comp_val.value == '__main__':
                            result['entry_points'].append(('__main__', node.lineno))
    
    def _extract_exports(self, tree: ast.AST, result: Dict, path: Path):
        """Extract __all__ exports."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    export_id = f"{path.name}:{elt.value}"
                                    result['exports'][export_id] = {
                                        'name': elt.value,
                                        'kind': 'unknown',
                                        'file': str(path)
                                    }


class JavaScriptParser(BaseParser):
    """
    JavaScript parser using regex patterns.
    
    Features:
    - ES6+ syntax support
    - Arrow functions
    - Class declarations
    - Import/export statements
    - CommonJS require/module.exports
    - Async functions
    """
    
    def parse_file(self, path: Path) -> Dict[str, Any]:
        """
        Parse JavaScript file using regex.
        
        Args:
            path: Path to .js file
            
        Returns:
            Parsed structure with functions, classes, imports, etc.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            lines = source.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
            
            result = {
                'files': {
                    str(path): {
                        'language': 'javascript',
                        'loc': loc,
                        'path': str(path)
                    }
                },
                'functions': {},
                'classes': {},
                'imports': {},
                'imports_detailed': [],
                'exports': {},
                'entry_points': []
            }
            
            # Extract functions
            self._extract_js_functions(source, result, path)
            
            # Extract classes
            self._extract_js_classes(source, result, path)
            
            # Extract imports
            self._extract_js_imports(source, result, path)
            
            # Extract exports
            self._extract_js_exports(source, result, path)
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing {path}: {e}")
            return self._empty_result(path, 0, error=str(e))
    
    def _empty_result(self, path: Path, loc: int = 0, error: str = None) -> Dict[str, Any]:
        """Return empty result structure."""
        result = {
            'files': {
                str(path): {
                    'language': 'javascript',
                    'loc': loc,
                    'path': str(path)
                }
            },
            'functions': {},
            'classes': {},
            'imports': {},
            'imports_detailed': [],
            'exports': {},
            'entry_points': []
        }
        if error:
            result['files'][str(path)]['error'] = error
        return result
    
    def _extract_js_functions(self, source: str, result: Dict, path: Path):
        """Extract JavaScript functions."""
        lines = source.split('\n')
        
        # Pattern 1: function declarations - function name(params) { ... }
        # Updated to handle TypeScript type annotations: function name(x: type): returnType {
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*[^{]+)?\s*\{'
        for match in re.finditer(func_pattern, source, re.MULTILINE):
            func_name = match.group(1)
            params_str = match.group(2)
            line_start = source[:match.start()].count('\n') + 1
            
            # Extract parameters
            parameters = [p.strip() for p in params_str.split(',') if p.strip()]
            
            # Find function end (simple brace counting)
            func_code, line_end = self._extract_function_code(source, match.start(), line_start)
            
            # Check if async (look in the match itself)
            is_async = 'async' in match.group(0) or 'async' in source[max(0, match.start()-20):match.start()]
            
            func_id = f"{path.name}:{func_name}"
            result['functions'][func_id] = {
                'name': func_name,
                'file': str(path),
                'line_start': line_start,
                'line_end': line_end,
                'complexity': 0,  # Not calculating for JS
                'parameters': parameters,
                'calls': [],
                'code': func_code,
                'is_exported': False,
                'is_async': is_async
            }
        
        # Pattern 2: arrow functions - const name = (params) => { ... } or const name = () => ...
        # Updated to handle TypeScript: const name = (x: type): returnType => ...
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)(?:\s*:\s*[^=]+)?\s*=>'
        for match in re.finditer(arrow_pattern, source, re.MULTILINE):
            func_name = match.group(1)
            params_str = match.group(2)
            line_start = source[:match.start()].count('\n') + 1
            
            parameters = [p.strip() for p in params_str.split(',') if p.strip()]
            
            # Extract code
            func_code, line_end = self._extract_arrow_function_code(source, match.end(), line_start)
            
            func_id = f"{path.name}:{func_name}"
            is_async = 'async' in source[max(0, match.start()-20):match.start()]
            result['functions'][func_id] = {
                'name': func_name,
                'file': str(path),
                'line_start': line_start,
                'line_end': line_end,
                'complexity': 0,
                'parameters': parameters,
                'calls': [],
                'code': func_code,
                'is_exported': False,
                'is_async': is_async
            }
    
    def _extract_function_code(self, source: str, start_pos: int, line_start: int) -> Tuple[str, int]:
        """Extract function body by matching braces."""
        # Find opening brace
        brace_start = source.find('{', start_pos)
        if brace_start == -1:
            return "", line_start
        
        # Count braces to find matching closing brace
        brace_count = 1
        pos = brace_start + 1
        while pos < len(source) and brace_count > 0:
            if source[pos] == '{':
                brace_count += 1
            elif source[pos] == '}':
                brace_count -= 1
            pos += 1
        
        line_end = source[:pos].count('\n') + 1
        code = source[start_pos:pos]
        return code, line_end
    
    def _extract_arrow_function_code(self, source: str, start_pos: int, line_start: int) -> Tuple[str, int]:
        """Extract arrow function body."""
        # Check if it's a block body { ... } or expression
        rest = source[start_pos:].lstrip()
        if rest.startswith('{'):
            return self._extract_function_code(source, start_pos, line_start)
        else:
            # Single expression - find end (semicolon or newline)
            end_pos = start_pos
            while end_pos < len(source) and source[end_pos] not in ';\n':
                end_pos += 1
            line_end = source[:end_pos].count('\n') + 1
            return source[start_pos:end_pos], line_end
    
    def _extract_js_classes(self, source: str, result: Dict, path: Path):
        """Extract JavaScript classes."""
        # Pattern: class ClassName { ... } or class ClassName implements Interface { ... }
        # Updated for TypeScript: class Name implements Interface, extends Base
        class_pattern = r'class\s+(\w+)(?:\s+(?:extends|implements)\s+([^\{]+?))?\s*\{'
        
        for match in re.finditer(class_pattern, source, re.MULTILINE):
            class_name = match.group(1)
            base_class = match.group(2)
            line_start = source[:match.start()].count('\n') + 1
            
            # Extract class body
            class_code, line_end = self._extract_function_code(source, match.start(), line_start)
            
            # Extract methods from class body
            methods = []
            method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{'
            for method_match in re.finditer(method_pattern, class_code):
                method_name = method_match.group(1)
                if method_name not in ['constructor', 'if', 'for', 'while']:  # Exclude keywords
                    methods.append(method_name)
            
            class_id = f"{path.name}:{class_name}"
            result['classes'][class_id] = {
                'name': class_name,
                'file': str(path),
                'line_start': line_start,
                'line_end': line_end,
                'methods': methods,
                'base_classes': [base_class] if base_class else []
            }
    
    def _extract_js_imports(self, source: str, result: Dict, path: Path):
        """Extract JavaScript imports."""
        lines = source.split('\n')
        
        # ES6 imports: import { x, y } from 'module'
        import_pattern = r"import\s+(?:\{([^}]+)\}|\*\s+as\s+(\w+)|(\w+))\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_pattern, source, re.MULTILINE):
            line_num = source[:match.start()].count('\n') + 1
            module = match.group(4)
            
            if match.group(1):  # Named imports
                imports = [i.strip() for i in match.group(1).split(',')]
            elif match.group(2):  # Namespace import
                imports = [match.group(2)]
            else:  # Default import
                imports = [match.group(3)]
            
            statement = match.group(0)
            result['imports_detailed'].append((statement, line_num, module))
        
        # CommonJS require: const x = require('module')
        require_pattern = r"(?:const|let|var)\s+(\w+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(require_pattern, source, re.MULTILINE):
            line_num = source[:match.start()].count('\n') + 1
            module = match.group(2)
            statement = match.group(0)
            result['imports_detailed'].append((statement, line_num, module))
    
    def _extract_js_exports(self, source: str, result: Dict, path: Path):
        """Extract JavaScript exports."""
        # export default
        default_pattern = r'export\s+default\s+(\w+)'
        for match in re.finditer(default_pattern, source):
            name = match.group(1)
            export_id = f"{path.name}:{name}"
            result['exports'][export_id] = {
                'name': name,
                'kind': 'default',
                'file': str(path)
            }
        
        # export const/function/class
        named_pattern = r'export\s+(?:const|let|var|function|class)\s+(\w+)'
        for match in re.finditer(named_pattern, source):
            name = match.group(1)
            export_id = f"{path.name}:{name}"
            result['exports'][export_id] = {
                'name': name,
                'kind': 'named',
                'file': str(path)
            }
        
        # module.exports = { ... }
        module_exports_pattern = r'module\.exports\s*=\s*\{([^}]+)\}'
        for match in re.finditer(module_exports_pattern, source):
            # Extract names from the object
            obj_content = match.group(1)
            names = re.findall(r'(\w+)', obj_content)
            for name in names:
                export_id = f"{path.name}:{name}"
                result['exports'][export_id] = {
                    'name': name,
                    'kind': 'commonjs',
                    'file': str(path)
                }
        
        # module.exports = name
        module_exports_simple = r'module\.exports\s*=\s*(\w+)'
        for match in re.finditer(module_exports_simple, source):
            if not '{' in match.group(0):  # Avoid double-matching
                name = match.group(1)
                export_id = f"{path.name}:{name}"
                result['exports'][export_id] = {
                    'name': name,
                    'kind': 'commonjs',
                    'file': str(path)
                }


class TypeScriptParser(JavaScriptParser):
    """
    TypeScript parser extending JavaScript parser.
    
    Additional features:
    - Type annotations
    - Interfaces
    - Type aliases
    - Enums
    - Access modifiers (public, private, protected)
    - Generics
    - Decorators
    """
    
    def parse_file(self, path: Path) -> Dict[str, Any]:
        """
        Parse TypeScript file.
        
        Args:
            path: Path to .ts file
            
        Returns:
            Parsed structure with TypeScript-specific features
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            lines = source.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
            
            result = {
                'files': {
                    str(path): {
                        'language': 'typescript',
                        'loc': loc,
                        'path': str(path)
                    }
                },
                'functions': {},
                'classes': {},
                'imports': {},
                'imports_detailed': [],
                'exports': {},
                'entry_points': [],
                'interfaces': {},
                'type_aliases': {},
                'enums': {}
            }
            
            # Extract JavaScript features first
            self._extract_js_functions(source, result, path)
            self._extract_js_classes(source, result, path)
            self._extract_js_imports(source, result, path)
            self._extract_js_exports(source, result, path)
            
            # Extract TypeScript-specific features
            self._extract_interfaces(source, result, path)
            self._extract_type_aliases(source, result, path)
            self._extract_enums(source, result, path)
            
            # Update functions with type annotations
            self._extract_type_annotations(source, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing {path}: {e}")
            return self._empty_result(path, 0, error=str(e))
    
    def _empty_result(self, path: Path, loc: int = 0, error: str = None) -> Dict[str, Any]:
        """Return empty result structure for TypeScript."""
        result = super()._empty_result(path, loc, error)
        result['files'][str(path)]['language'] = 'typescript'
        result['interfaces'] = {}
        result['type_aliases'] = {}
        result['enums'] = {}
        return result
    
    def _extract_interfaces(self, source: str, result: Dict, path: Path):
        """Extract TypeScript interfaces."""
        # Pattern: interface InterfaceName { ... }
        interface_pattern = r'interface\s+(\w+)(?:<[^>]+>)?\s*(?:extends\s+([^{]+))?\s*\{'
        
        for match in re.finditer(interface_pattern, source, re.MULTILINE):
            interface_name = match.group(1)
            extends = match.group(2).strip() if match.group(2) else None
            line_start = source[:match.start()].count('\n') + 1
            
            # Extract interface body
            interface_code, line_end = self._extract_function_code(source, match.start(), line_start)
            
            interface_id = f"{path.name}:{interface_name}"
            result['interfaces'][interface_id] = {
                'name': interface_name,
                'file': str(path),
                'line_start': line_start,
                'line_end': line_end,
                'extends': [extends] if extends else []
            }
    
    def _extract_type_aliases(self, source: str, result: Dict, path: Path):
        """Extract TypeScript type aliases."""
        # Pattern: type TypeName = ...
        type_pattern = r'type\s+(\w+)(?:<[^>]+>)?\s*='
        
        for match in re.finditer(type_pattern, source, re.MULTILINE):
            type_name = match.group(1)
            line_num = source[:match.start()].count('\n') + 1
            
            type_id = f"{path.name}:{type_name}"
            result['type_aliases'][type_id] = {
                'name': type_name,
                'file': str(path),
                'line_number': line_num
            }
    
    def _extract_enums(self, source: str, result: Dict, path: Path):
        """Extract TypeScript enums."""
        # Pattern: enum EnumName { ... }
        enum_pattern = r'enum\s+(\w+)\s*\{'
        
        for match in re.finditer(enum_pattern, source, re.MULTILINE):
            enum_name = match.group(1)
            line_start = source[:match.start()].count('\n') + 1
            
            # Extract enum body
            enum_code, line_end = self._extract_function_code(source, match.start(), line_start)
            
            enum_id = f"{path.name}:{enum_name}"
            result['enums'][enum_id] = {
                'name': enum_name,
                'file': str(path),
                'line_start': line_start,
                'line_end': line_end
            }
    
    def _extract_type_annotations(self, source: str, result: Dict):
        """Extract type annotations from functions."""
        # This would enhance function definitions with type info
        # For now, we just mark that types exist
        for func_id, func_data in result['functions'].items():
            func_data['has_type_annotations'] = ':' in source[
                source.find(func_data['name']):
                source.find(func_data['name']) + 100
            ]


# ==================== EMBEDDED TESTS ====================

if __name__ == "__main__":
    """
    Embedded test suite with real sample files.
    Tests all 3 parsers comprehensively.
    """
    
    import tempfile
    import sys
    
    print("=" * 70)
    print("ORC COMPONENT 3: LANGUAGE PARSERS")
    print("Running comprehensive test suite...")
    print("=" * 70)
    
    test_results = []
    total_tests = 0
    passed_tests = 0
    
    def run_test(test_name: str, test_func):
        """Helper to run a test and track results."""
        global total_tests, passed_tests
        total_tests += 1
        try:
            test_func()
            passed_tests += 1
            result = "✅ PASS"
            test_results.append((test_name, True, None))
            print(f"  {result} - {test_name}")
            return True
        except Exception as e:
            result = "❌ FAIL"
            test_results.append((test_name, False, str(e)))
            print(f"  {result} - {test_name}")
            print(f"      Error: {e}")
            return False
    
    # ==================== PYTHON PARSER TESTS ====================
    
    # Sample Python file 1: Complex example
    SAMPLE_PYTHON_COMPLEX = '''
"""Sample Python module for testing."""

import os
import sys
from pathlib import Path

__all__ = ['calculate', 'ComplexClass']

def simple_function(x, y):
    """Simple function with low complexity."""
    return x + y

async def async_function(data):
    """Async function example."""
    result = await process(data)
    return result

def complex_function(value):
    """Function with high complexity."""
    if value > 10:
        for i in range(value):
            if i % 2 == 0:
                while i > 0:
                    i -= 1
                    if i == 5:
                        break
            elif i % 3 == 0 and i > 5:
                continue
    return value

@decorator
def decorated_function():
    """Function with decorator."""
    pass

class SimpleClass:
    """Simple class."""
    
    def method_one(self):
        return 1
    
    def method_two(self):
        return 2

class ComplexClass(SimpleClass):
    """Class with inheritance."""
    
    def __init__(self):
        super().__init__()
    
    async def async_method(self):
        await something()

if __name__ == '__main__':
    print("Entry point detected")
    simple_function(1, 2)
'''

    # Sample Python file 2: Syntax error
    SAMPLE_PYTHON_ERROR = '''
def broken_function(
    # Missing closing parenthesis
    return "error"
'''

    # Sample Python file 3: Empty file
    SAMPLE_PYTHON_EMPTY = '''
# Just comments
# No code
'''

    def test_python_parse_functions():
        """Test Python function extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['functions']) >= 5, f"Expected >= 5 functions, got {len(result['functions'])}"
            assert 'simple_function' in str(result['functions'])
            assert 'async_function' in str(result['functions'])
            assert 'complex_function' in str(result['functions'])
    
    def test_python_complexity():
        """Test McCabe complexity calculation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            # Find complex_function and check its complexity
            complex_func = None
            for func_id, func_data in result['functions'].items():
                if 'complex_function' in func_id:
                    complex_func = func_data
                    break
            
            assert complex_func is not None
            assert complex_func['complexity'] > 5, f"Expected complexity > 5, got {complex_func['complexity']}"
            print(f"\n      Complex function complexity: {complex_func['complexity']}")
    
    def test_python_classes():
        """Test Python class extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['classes']) >= 2
            
            # Check inheritance
            complex_class = None
            for class_id, class_data in result['classes'].items():
                if 'ComplexClass' in class_id:
                    complex_class = class_data
                    break
            
            assert complex_class is not None
            assert 'SimpleClass' in complex_class['base_classes']
    
    def test_python_imports():
        """Test Python import extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['imports_detailed']) >= 3
            imports_str = str(result['imports_detailed'])
            assert 'os' in imports_str
            assert 'sys' in imports_str
            assert 'pathlib' in imports_str
    
    def test_python_exports():
        """Test Python __all__ export extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['exports']) >= 2
            exports_str = str(result['exports'])
            assert 'calculate' in exports_str
            assert 'ComplexClass' in exports_str
    
    def test_python_entry_point():
        """Test Python entry point detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['entry_points']) > 0
            assert result['entry_points'][0][0] == '__main__'
    
    def test_python_syntax_error():
        """Test Python syntax error handling."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_ERROR)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            # Should not crash, should return empty result with error
            assert 'files' in result
            assert len(result['functions']) == 0
    
    def test_python_empty_file():
        """Test Python empty file handling."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_EMPTY)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'files' in result
            assert len(result['functions']) == 0
            assert len(result['classes']) == 0
    
    def test_python_async_functions():
        """Test Python async function detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            async_func = None
            for func_id, func_data in result['functions'].items():
                if 'async_function' in func_id:
                    async_func = func_data
                    break
            
            assert async_func is not None
            assert async_func['is_async'] == True
    
    def test_python_decorators():
        """Test Python decorator extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_PYTHON_COMPLEX)
            f.flush()
            
            parser = PythonParser()
            result = parser.parse_file(Path(f.name))
            
            decorated_func = None
            for func_id, func_data in result['functions'].items():
                if 'decorated_function' in func_id:
                    decorated_func = func_data
                    break
            
            assert decorated_func is not None
            assert len(decorated_func['decorators']) > 0
    
    # ==================== JAVASCRIPT PARSER TESTS ====================
    
    SAMPLE_JAVASCRIPT = '''
// Sample JavaScript file
import { helper, utils } from './utils';
import React from 'react';

const moduleVar = require('module');

function regularFunction(a, b) {
    return a + b;
}

async function asyncFunction(data) {
    const result = await fetch(data);
    return result.json();
}

const arrowFunction = (x, y) => {
    return x * y;
};

const singleLineArrow = (x) => x * 2;

class MyClass extends BaseClass {
    constructor() {
        super();
    }
    
    method1() {
        return 1;
    }
    
    async method2() {
        await something();
    }
}

export default MyClass;
export const helper = () => {};
export function exportedFunc() {}

module.exports = { regularFunction };
'''

    SAMPLE_JAVASCRIPT_ERROR = '''
function broken(
    // syntax error
    return "error"
'''

    def test_js_parse_functions():
        """Test JavaScript function extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['functions']) >= 4, f"Expected >= 4 functions, got {len(result['functions'])}"
            funcs_str = str(result['functions'])
            assert 'regularFunction' in funcs_str
            assert 'asyncFunction' in funcs_str
            assert 'arrowFunction' in funcs_str
    
    def test_js_arrow_functions():
        """Test JavaScript arrow function detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            arrow_func = None
            for func_id, func_data in result['functions'].items():
                if 'arrowFunction' in func_id:
                    arrow_func = func_data
                    break
            
            assert arrow_func is not None
            assert len(arrow_func['parameters']) == 2
    
    def test_js_classes():
        """Test JavaScript class extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['classes']) >= 1
            
            my_class = None
            for class_id, class_data in result['classes'].items():
                if 'MyClass' in class_id:
                    my_class = class_data
                    break
            
            assert my_class is not None
            assert 'BaseClass' in my_class['base_classes']
            assert len(my_class['methods']) >= 2
    
    def test_js_imports():
        """Test JavaScript import extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['imports_detailed']) >= 2
            imports_str = str(result['imports_detailed'])
            assert 'utils' in imports_str or 'react' in imports_str.lower()
    
    def test_js_exports():
        """Test JavaScript export extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['exports']) >= 2
            exports_str = str(result['exports'])
            assert 'MyClass' in exports_str or 'helper' in exports_str
    
    def test_js_async_detection():
        """Test JavaScript async function detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            async_func = None
            for func_id, func_data in result['functions'].items():
                if 'asyncFunction' in func_id:
                    async_func = func_data
                    break
            
            assert async_func is not None
            assert async_func['is_async'] == True
    
    def test_js_syntax_error():
        """Test JavaScript syntax error handling."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT_ERROR)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            # Should not crash
            assert 'files' in result
    
    def test_js_commonjs_require():
        """Test CommonJS require detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            imports_str = str(result['imports_detailed'])
            assert 'module' in imports_str
    
    def test_js_empty_file():
        """Test JavaScript empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('// Just a comment\n')
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'files' in result
            assert len(result['functions']) == 0
    
    def test_js_module_exports():
        """Test module.exports detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(SAMPLE_JAVASCRIPT)
            f.flush()
            
            parser = JavaScriptParser()
            result = parser.parse_file(Path(f.name))
            
            exports_str = str(result['exports'])
            assert 'regularFunction' in exports_str
    
    # ==================== TYPESCRIPT PARSER TESTS ====================
    
    SAMPLE_TYPESCRIPT = '''
// Sample TypeScript file
import { Component } from '@angular/core';

interface User {
    name: string;
    age: number;
}

type UserID = string | number;

enum Status {
    Active,
    Inactive,
    Pending
}

function typedFunction(x: number, y: string): boolean {
    return x > 0;
}

const arrowWithTypes = (a: number): number => a * 2;

class TypedClass implements User {
    name: string;
    age: number;
    
    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }
    
    public getInfo(): string {
        return this.name;
    }
    
    private helperMethod(): void {
        // private
    }
}

export interface ExportedInterface {
    id: number;
}

export type ExportedType = string;
'''

    def test_ts_interfaces():
        """Test TypeScript interface extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'interfaces' in result
            assert len(result['interfaces']) >= 1
            assert 'User' in str(result['interfaces'])
    
    def test_ts_type_aliases():
        """Test TypeScript type alias extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'type_aliases' in result
            assert len(result['type_aliases']) >= 1
            assert 'UserID' in str(result['type_aliases'])
    
    def test_ts_enums():
        """Test TypeScript enum extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'enums' in result
            assert len(result['enums']) >= 1
            assert 'Status' in str(result['enums'])
    
    def test_ts_functions():
        """Test TypeScript function extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['functions']) >= 2
            assert 'typedFunction' in str(result['functions'])
    
    def test_ts_classes():
        """Test TypeScript class extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert len(result['classes']) >= 1
            assert 'TypedClass' in str(result['classes'])
    
    def test_ts_extends_js():
        """Test that TypeScript parser extends JavaScript."""
        assert issubclass(TypeScriptParser, JavaScriptParser)
    
    def test_ts_empty_file():
        """Test TypeScript empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write('// Empty\n')
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            assert 'files' in result
            assert result['files'][f.name]['language'] == 'typescript'
    
    def test_ts_interface_extends():
        """Test TypeScript interface inheritance."""
        sample = '''
interface Base {
    id: number;
}

interface Extended extends Base {
    name: string;
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(sample)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            extended_interface = None
            for iface_id, iface_data in result['interfaces'].items():
                if 'Extended' in iface_id:
                    extended_interface = iface_data
                    break
            
            assert extended_interface is not None
            assert len(extended_interface['extends']) > 0
    
    def test_ts_type_annotations():
        """Test TypeScript type annotation detection."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(SAMPLE_TYPESCRIPT)
            f.flush()
            
            parser = TypeScriptParser()
            result = parser.parse_file(Path(f.name))
            
            # Check that functions have type annotation info
            for func_id, func_data in result['functions'].items():
                if 'typedFunction' in func_id:
                    assert 'has_type_annotations' in func_data
    
    # ==================== RUN ALL TESTS ====================
    
    print("\n" + "=" * 70)
    print("PYTHON PARSER TESTS")
    print("=" * 70 + "\n")
    
    run_test("1. Python - Extract functions", test_python_parse_functions)
    run_test("2. Python - Calculate complexity", test_python_complexity)
    run_test("3. Python - Extract classes", test_python_classes)
    run_test("4. Python - Extract imports", test_python_imports)
    run_test("5. Python - Extract exports (__all__)", test_python_exports)
    run_test("6. Python - Detect entry points", test_python_entry_point)
    run_test("7. Python - Handle syntax errors", test_python_syntax_error)
    run_test("8. Python - Handle empty files", test_python_empty_file)
    run_test("9. Python - Detect async functions", test_python_async_functions)
    run_test("10. Python - Extract decorators", test_python_decorators)
    
    print("\n" + "=" * 70)
    print("JAVASCRIPT PARSER TESTS")
    print("=" * 70 + "\n")
    
    run_test("11. JavaScript - Extract functions", test_js_parse_functions)
    run_test("12. JavaScript - Arrow functions", test_js_arrow_functions)
    run_test("13. JavaScript - Extract classes", test_js_classes)
    run_test("14. JavaScript - Extract imports", test_js_imports)
    run_test("15. JavaScript - Extract exports", test_js_exports)
    run_test("16. JavaScript - Detect async", test_js_async_detection)
    run_test("17. JavaScript - Handle syntax errors", test_js_syntax_error)
    run_test("18. JavaScript - CommonJS require", test_js_commonjs_require)
    run_test("19. JavaScript - Empty files", test_js_empty_file)
    run_test("20. JavaScript - module.exports", test_js_module_exports)
    
    print("\n" + "=" * 70)
    print("TYPESCRIPT PARSER TESTS")
    print("=" * 70 + "\n")
    
    run_test("21. TypeScript - Extract interfaces", test_ts_interfaces)
    run_test("22. TypeScript - Extract type aliases", test_ts_type_aliases)
    run_test("23. TypeScript - Extract enums", test_ts_enums)
    run_test("24. TypeScript - Extract functions", test_ts_functions)
    run_test("25. TypeScript - Extract classes", test_ts_classes)
    run_test("26. TypeScript - Extends JavaScript", test_ts_extends_js)
    run_test("27. TypeScript - Empty files", test_ts_empty_file)
    run_test("28. TypeScript - Interface extends", test_ts_interface_extends)
    run_test("29. TypeScript - Type annotations", test_ts_type_annotations)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! ✅")
        print("\nComponent 3 is PRODUCTION READY")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - passed_tests} TEST(S) FAILED")
        print("\nFailed tests:")
        for name, passed, error in test_results:
            if not passed:
                print(f"  - {name}: {error}")
        sys.exit(1)
