"""
Tests for CLI functionality
"""
import pytest
import tempfile
import os
from pathlib import Path
import subprocess
import sys


def test_cli_index_command():
    """Test the index command functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test_cli.py"
        test_code = '''
def used_function():
    """This function is used"""
    return 42

def unused_function():
    """This function is never called"""
    return 100

if __name__ == "__main__":
    result = used_function()
    print(result)
'''
        test_file.write_text(test_code)

        # Test that we can run the index command
        # We'll test this by importing and calling the function directly
        # since running the CLI as a subprocess would be complex
        from orc_package.config.settings import ORCConfig
        from core.index_service import IndexService
        
        config = ORCConfig(project_root=Path(temp_dir))
        service = IndexService(config)
        
        # This should run without errors
        service.index_project(Path(temp_dir))
        
        # Check that the index database was created
        assert config.index_path.exists()


def test_cli_dead_command():
    """Test the dead code detection command"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file with dead code
        test_file = Path(temp_dir) / "test_dead_cli.py"
        test_code = '''
def used_function():
    """This function is used"""
    return 42

def unused_function():
    """This function is never called"""
    return 100

if __name__ == "__main__":
    result = used_function()
    print(result)
'''
        test_file.write_text(test_code)

        # Index the project first
        from orc_package.config.settings import ORCConfig
        from core.index_service import IndexService
        
        config = ORCConfig(project_root=Path(temp_dir))
        service = IndexService(config)
        service.index_project(Path(temp_dir))

        # Now test dead code analysis
        from storage.graph_db import GraphStorage
        from orc_package.analysis.dead_code import DeadCodeAnalyzer
        
        storage = GraphStorage(config.index_path)
        modules = storage.load_modules()
        
        analyzer = DeadCodeAnalyzer(config)
        report = analyzer.analyze(modules)
        
        # Should find the unused function
        dead_functions = [f['function'] for f in report.unused_functions]
        assert 'unused_function' in dead_functions


def test_cli_analyze_command():
    """Test the analyze command functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test_analyze_cli.py"
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

        # Index the project
        from orc_package.config.settings import ORCConfig
        from core.index_service import IndexService
        
        config = ORCConfig(project_root=Path(temp_dir))
        service = IndexService(config)
        service.index_project(Path(temp_dir))

        # Test analysis
        from storage.graph_db import GraphStorage
        from core.analyzer import Analyzer
        
        storage = GraphStorage(config.index_path)
        modules = storage.load_modules()
        
        analyzer = Analyzer(config)
        report = analyzer.run_all(modules)
        
        # Check that all analysis components ran
        assert 'dead_code' in report
        assert 'dependencies' in report
        assert 'metrics' in report
        assert 'patterns' in report
        assert 'summary' in report


def test_cli_query_command():
    """Test the query command functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test Python file
        test_file = Path(temp_dir) / "test_query_cli.py"
        test_code = '''
def authenticate_user(username, password):
    """Authenticate a user"""
    return True

def get_user_data(user_id):
    """Get user data"""
    return {"id": user_id, "name": "test"}
'''
        test_file.write_text(test_code)

        # Index the project
        from orc_package.config.settings import ORCConfig
        from core.index_service import IndexService
        
        config = ORCConfig(project_root=Path(temp_dir))
        service = IndexService(config)
        service.index_project(Path(temp_dir))

        # Test query functionality
        from storage.graph_db import GraphStorage
        from orc_package.agent.query_engine import QueryEngine
        from core.graph_builder import DependencyGraph
        
        storage = GraphStorage(config.index_path)
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')
        
        if graph is None:
            graph = DependencyGraph()
            graph.build_from_modules(modules)

        engine = QueryEngine(config, modules, graph)
        
        # Test a query about functions
        result = engine.process_query("Show functions")
        assert result.result_type in ['list', 'help']
        
        # Test a query about complexity
        result = engine.process_query("Show complex functions")
        assert result.result_type in ['list', 'help']


def test_cli_config_commands():
    """Test configuration-related CLI commands"""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Test init command (create config)
        from orc_package.config.settings import ORCConfig
        from orc_package.cli.commands import init
        
        # This should create a .orcrc file
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            init()
        
        # Check that .orcrc was created
        assert os.path.exists(".orcrc")
        
        # Test config show command
        from orc_package.cli.commands import config
        f = io.StringIO()
        with redirect_stdout(f):
            config('show', None, None)
        
        output = f.getvalue()
        assert "Current ORC Configuration" in output


def test_cli_ignore_command():
    """Test the ignore command functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Test adding to ignore list
        from orc_package.cli.commands import ignore
        import io
        from contextlib import redirect_stdout
        
        # Add something to ignore
        f = io.StringIO()
        with redirect_stdout(f):
            ignore("test_pattern")
        
        # Check that .orcrc was created and has the pattern
        assert os.path.exists(".orcrc")
        
        import yaml
        with open(".orcrc", 'r') as f:
            config = yaml.safe_load(f)
        
        assert "test_pattern" in config['ignore']


def test_cli_complexity_integration():
    """Test integration of complexity analysis through CLI"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file with complex code
        test_file = Path(temp_dir) / "complex_test.py"
        test_code = '''
def very_complex_function():
    """A function with high complexity"""
    result = 0
    for i in range(10):
        for j in range(10):
            for k in range(10):
                result += i * j * k
    return result

def simple_function():
    """Simple function"""
    return 1
'''
        test_file.write_text(test_code)

        # Index the project
        from orc_package.config.settings import ORCConfig
        from core.index_service import IndexService
        
        config = ORCConfig(project_root=Path(temp_dir))
        service = IndexService(config)
        service.index_project(Path(temp_dir))

        # Test that the complexity analyzer can process this
        from storage.graph_db import GraphStorage
        from analysis.complexity import ComplexityAnalyzer
        from core.graph_builder import DependencyGraph
        
        storage = GraphStorage(config.index_path)
        modules = storage.load_modules()
        graph = storage.load_graph('dependency')
        
        if graph is None:
            graph = DependencyGraph()
            graph.build_from_modules(modules)

        # Create index structure for complexity analyzer
        index = {
            "functions": {}
        }
        
        # Convert modules to the format expected by complexity analyzer
        for path, module in modules.items():
            for func_name, func_info in module.functions.items():
                func_id = f"{path}::{func_name}"
                index["functions"][func_id] = {
                    "complexity": func_info.complexity,
                    "code": func_info.docstring or ""
                }

        analyzer = ComplexityAnalyzer(index, graph)
        reports = analyzer.analyze_all()
        
        # Should have found the complex function
        complex_reports = [r for r in reports if r.complexity_score > 10]
        assert len(complex_reports) >= 1


if __name__ == "__main__":
    pytest.main([__file__])