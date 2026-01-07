"""
Basic tests for ORC functionality
"""
import pytest
import tempfile
import os
from pathlib import Path

from orc_package.config.settings import ORCConfig
from core.indexer import PythonIndexer
from storage.graph_db import GraphStorage
from orc_package.analysis.dead_code import DeadCodeAnalyzer
from orc_package.analysis.metrics import MetricsAnalyzer
from orc_package.analysis.dependencies import DependencyAnalyzer
from orc_package.analysis.patterns import PatternAnalyzer
from analysis.complexity import ComplexityAnalyzer
from analysis.optimizer import Optimizer


def test_config_creation():
    """Test that ORC configuration can be created"""
    config = ORCConfig(project_root=Path("."))
    assert config.project_root == Path(".")
    assert config.index_path == Path(".orc/index.db")


def test_python_indexer():
    """Test Python indexer with a simple code sample"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test.py"
        test_code = '''
def used_function():
    """This function is used"""
    return 42

def unused_function():
    """This function is never called"""
    return 100

def another_used_function():
    """This function calls another function"""
    return used_function()

if __name__ == "__main__":
    result = another_used_function()
    print(result)
'''
        test_file.write_text(test_code)

        # Create config
        config = ORCConfig(project_root=Path(temp_dir))

        # Index the file
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(Path(temp_dir))

        # Verify that the file was indexed
        assert str(test_file) in modules
        module = modules[str(test_file)]
        
        # Check that functions were found
        assert 'used_function' in module.functions
        assert 'unused_function' in module.functions
        assert 'another_used_function' in module.functions


def test_dead_code_detection():
    """Test dead code detection"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file with some dead code
        test_file = Path(temp_dir) / "test_dead.py"
        test_code = '''
def used_function():
    """This function is used"""
    return 42

def unused_function():
    """This function is never called"""
    return 100

def another_used_function():
    """This function calls another function"""
    return used_function()

if __name__ == "__main__":
    result = another_used_function()
    print(result)
'''
        test_file.write_text(test_code)

        # Create config
        config = ORCConfig(project_root=Path(temp_dir))

        # Index the file
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(Path(temp_dir))

        # Run dead code analysis
        analyzer = DeadCodeAnalyzer(config)
        report = analyzer.analyze(modules)

        # Check that unused_function is detected as dead code
        dead_functions = [f['function'] for f in report.unused_functions]
        assert 'unused_function' in dead_functions
        assert 'used_function' not in dead_functions
        assert 'another_used_function' not in dead_functions


def test_metrics_analysis():
    """Test metrics analysis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test_metrics.py"
        test_code = '''
def simple_function():
    """Simple function"""
    return 1

def complex_function():
    """More complex function with loops"""
    result = 0
    for i in range(10):
        for j in range(10):
            result += i * j
    return result
'''
        test_file.write_text(test_code)

        # Create config
        config = ORCConfig(project_root=Path(temp_dir))

        # Index the file
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(Path(temp_dir))

        # Run metrics analysis
        analyzer = MetricsAnalyzer(config)
        report = analyzer.analyze(modules)

        # Check metrics
        assert 'overall' in report
        assert 'modules' in report
        assert 'functions' in report

        # Check that our functions are in the function metrics
        func_metrics = report['functions']
        func_ids = list(func_metrics.keys())
        assert any('simple_function' in fid for fid in func_ids)
        assert any('complex_function' in fid for fid in func_ids)


def test_dependency_analysis():
    """Test dependency analysis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test Python files with dependencies
        file1 = Path(temp_dir) / "module1.py"
        file1_code = '''
def utility_function():
    return "hello"

def another_utility():
    return utility_function()
'''
        file1.write_text(file1_code)

        file2 = Path(temp_dir) / "module2.py"
        file2_code = '''
from module1 import utility_function

def main_function():
    return utility_function()
'''
        file2.write_text(file2_code)

        # Create config
        config = ORCConfig(project_root=Path(temp_dir))

        # Index the files
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(Path(temp_dir))

        # Run dependency analysis
        analyzer = DependencyAnalyzer(config)
        report = analyzer.analyze(modules)

        # Check that dependencies were found
        assert 'circular_dependencies' in report
        assert 'coupling_metrics' in report
        assert 'dependency_issues' in report


def test_pattern_analysis():
    """Test pattern analysis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test_patterns.py"
        test_code = '''
def simple_function():
    """Simple function"""
    return 1

def create_user():
    """Factory pattern function"""
    return {}

def notify_observer():
    """Observer pattern function"""
    pass

def very_complex_function():
    """A function with high complexity"""
    result = 0
    for i in range(10):
        for j in range(10):
            for k in range(10):
                result += i * j * k
    return result
'''
        test_file.write_text(test_code)

        # Create config
        config = ORCConfig(project_root=Path(temp_dir))

        # Index the file
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(Path(temp_dir))

        # Run pattern analysis
        analyzer = PatternAnalyzer(config)
        report = analyzer.analyze(modules)

        # Check that patterns were detected
        assert 'antipatterns' in report
        assert 'duplication' in report
        assert 'good_patterns' in report


def test_storage_functionality():
    """Test storage functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test database path
        db_path = Path(temp_dir) / "test.db"
        
        # Create storage instance
        storage = GraphStorage(db_path)
        
        # Verify database was created
        assert db_path.exists()
        
        # Test loading modules (should be empty initially)
        modules = storage.load_modules()
        assert isinstance(modules, dict)
        assert len(modules) == 0


if __name__ == "__main__":
    pytest.main([__file__])