"""
Pytest fixtures for ORC Component 1 tests.

Provides reusable test fixtures for configuration, cache, and file structures.
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for tests.
    
    Automatically cleaned up after test completes.
    
    Yields:
        Path: Temporary directory path
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project(temp_dir):
    """
    Create a sample project structure for testing.
    
    Structure:
        project/
            main.py
            utils.py
            tests/
                test_main.py
            node_modules/
                package.js
            .git/
                config
    
    Yields:
        Path: Project root directory
    """
    project_root = temp_dir / "project"
    project_root.mkdir()
    
    # Create Python files
    (project_root / "main.py").write_text(
        "def main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()\n"
    )
    
    (project_root / "utils.py").write_text(
        "def helper():\n    return 42\n\nclass Helper:\n    pass\n"
    )
    
    # Create test directory
    test_dir = project_root / "tests"
    test_dir.mkdir()
    (test_dir / "test_main.py").write_text(
        "def test_main():\n    assert True\n"
    )
    
    # Create directories that should be ignored
    node_modules = project_root / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text("console.log('package');")
    
    git_dir = project_root / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n")
    
    return project_root


@pytest.fixture
def sample_config_yaml(temp_dir):
    """
    Create a sample configuration YAML file.
    
    Yields:
        Path: Config file path
    """
    config_file = temp_dir / "test_config.yaml"
    config_content = """
project_root: .
cache_dir: .test_cache
cache_ttl: 1800
max_workers: 2
file_extensions:
  - .py
  - .js
ignore_patterns:
  - __pycache__/
  - node_modules/
log_level: DEBUG
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_orcignore(temp_dir):
    """
    Create a sample .orcignore file.
    
    Yields:
        Path: .orcignore file path
    """
    ignore_file = temp_dir / ".orcignore"
    ignore_content = """
# Test ignore patterns
node_modules/
__pycache__/
*.pyc
.git/
*.log
"""
    ignore_file.write_text(ignore_content)
    return ignore_file


@pytest.fixture
def large_project(temp_dir):
    """
    Create a large project for performance testing.
    
    Creates 100 Python files for performance benchmarks.
    
    Yields:
        Path: Project root directory
    """
    project_root = temp_dir / "large_project"
    project_root.mkdir()
    
    # Create 100 Python files
    for i in range(100):
        file_path = project_root / f"module_{i}.py"
        content = f"""
def function_{i}_1():
    '''Function {i}-1 docstring'''
    return {i}

def function_{i}_2():
    '''Function {i}-2 docstring'''
    return {i} * 2

class Class_{i}:
    '''Class {i} docstring'''
    
    def method_{i}(self):
        return {i}
"""
        file_path.write_text(content)
    
    return project_root


@pytest.fixture
def malformed_yaml(temp_dir):
    """
    Create a malformed YAML file for error testing.
    
    Yields:
        Path: Malformed YAML file path
    """
    bad_yaml = temp_dir / "bad_config.yaml"
    bad_yaml.write_text("project_root: [\ninvalid: yaml: content\n")
    return bad_yaml


@pytest.fixture
def empty_project(temp_dir):
    """
    Create an empty project directory.
    
    Yields:
        Path: Empty project directory
    """
    empty = temp_dir / "empty_project"
    empty.mkdir()
    return empty
