"""
ORC Tests: Indexer Module Tests
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import os

from orc.core.indexer import PythonIndexer, ModuleInfo, FunctionInfo
from orc.config.settings import ORCConfig

class TestPythonIndexer:
    def setup_method(self):
        """Set up test fixtures"""
        self.config = ORCConfig(project_root=Path('.'))
        self.indexer = PythonIndexer(self.config)

    def test_index_file_basic(self):
        """Test basic file indexing"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def simple_function():
    return 42

class SimpleClass:
    def method(self):
        if True:
            return "hello"
""")
            temp_file = f.name

        try:
            # Test indexing
            result = self.indexer.index_file(Path(temp_file))
            
            assert result is not None
            assert result.path == temp_file
            assert len(result.functions) == 1  # simple_function
            assert len(result.classes) == 1    # SimpleClass
            
            # Check function details
            func_info = result.functions['simple_function']
            assert func_info.name == 'simple_function'
            assert func_info.complexity == 1  # Simple function has complexity 1
            
        finally:
            # Clean up
            os.unlink(temp_file)

    def test_index_file_with_imports(self):
        """Test indexing file with imports"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
import os
from pathlib import Path
import json as js

def func():
    pass
""")
            temp_file = f.name

        try:
            result = self.indexer.index_file(Path(temp_file))
            
            assert 'os' in result.imports
            assert 'pathlib' in result.imports  # From "from pathlib import Path"
            assert 'json' in result.imports      # From "import json as js"
            
        finally:
            os.unlink(temp_file)

    def test_calculate_complexity(self):
        """Test complexity calculation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def complex_function():
    if True:
        for i in range(10):
            while i > 0:
                if i % 2 == 0:
                    pass
                else:
                    break
    return True
""")
            temp_file = f.name

        try:
            result = self.indexer.index_file(Path(temp_file))
            func_info = result.functions['complex_function']
            
            # Minimum complexity is 1, plus 3 control structures (if, for, while, another if) = 4+ or more
            assert func_info.complexity >= 4
            
        finally:
            os.unlink(temp_file)

    def test_extract_calls(self):
        """Test function call extraction"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def func1():
    return 42

def func2():
    result = func1()
    func1()
    return result
""")
            temp_file = f.name

        try:
            result = self.indexer.index_file(Path(temp_file))
            func2_info = result.functions['func2']
            
            # func2 calls func1 twice
            assert 'func1' in func2_info.calls
            
        finally:
            os.unlink(temp_file)

    def test_index_directory(self):
        """Test directory indexing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file in the temp directory
            py_file = Path(temp_dir) / "test_module.py"
            py_file.write_text("""
def sample_function():
    return "hello"
""")

            # Index the directory
            modules = self.indexer.index_directory(Path(temp_dir))
            
            # Check that our file was indexed
            assert str(py_file) in modules
            assert len(modules) == 1
            
            module = modules[str(py_file)]
            assert 'sample_function' in module.functions

    def test_private_functions_exported(self):
        """Test that private functions are not marked as exported"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def public_func():
    pass

def _private_func():
    pass
""")
            temp_file = f.name

        try:
            result = self.indexer.index_file(Path(temp_file))
            
            # Public function should be in exports
            assert 'public_func' in result.exports
            # Private function should not be in exports
            assert '_private_func' not in result.exports
            
        finally:
            os.unlink(temp_file)