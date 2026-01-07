"""
ORC Tests: Analyzer Module Tests
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from orc.core.analyzer import Analyzer
from orc.core.indexer import ModuleInfo, FunctionInfo
from orc.config.settings import ORCConfig

class TestAnalyzer:
    def setup_method(self):
        """Set up test fixtures"""
        self.config = ORCConfig(project_root=Path('.'))
        self.analyzer = Analyzer(self.config)

    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        assert self.analyzer.config == self.config
        assert self.analyzer.dead_code_analyzer is not None
        assert self.analyzer.dependency_analyzer is not None
        assert self.analyzer.metrics_analyzer is not None
        assert self.analyzer.pattern_analyzer is not None

    def test_run_all_with_empty_modules(self):
        """Test running analysis with empty modules"""
        modules = {}
        result = self.analyzer.run_all(modules)
        
        assert 'dead_code' in result
        assert 'dependencies' in result
        assert 'metrics' in result
        assert 'patterns' in result
        assert 'summary' in result
        
        # Check summary for empty modules
        summary = result['summary']
        assert summary['total_files'] == 0
        assert summary['total_functions'] == 0
        assert summary['total_lines'] == 0

    def test_run_all_with_sample_modules(self):
        """Test running analysis with sample modules"""
        # Create sample modules
        modules = {
            'module1.py': ModuleInfo(
                path='module1.py',
                lines=50,
                imports=['os', 'sys'],
                exports=['func1'],
                functions={
                    'func1': FunctionInfo(
                        name='func1',
                        file_path='module1.py',
                        line_start=5,
                        line_end=10,
                        complexity=3,
                        calls=['func2'],
                        called_by=set(),
                        parameters=['x', 'y'],
                        is_exported=True,
                        is_used=True,
                        docstring='Sample function'
                    )
                },
                classes=['MyClass'],
                last_modified=0.0,
                hash='abc123'
            )
        }
        
        result = self.analyzer.run_all(modules)
        
        # Check that all analysis types returned results
        assert 'dead_code' in result
        assert 'dependencies' in result
        assert 'metrics' in result
        assert 'patterns' in result
        assert 'summary' in result
        
        # Check summary values
        summary = result['summary']
        assert summary['total_files'] == 1
        assert summary['total_functions'] == 1
        assert summary['total_lines'] == 50

    def test_generate_summary(self):
        """Test summary generation"""
        modules = {
            'file1.py': ModuleInfo(
                path='file1.py',
                lines=100,
                imports=[],
                exports=[],
                functions={
                    'func1': FunctionInfo(
                        name='func1', file_path='file1.py', line_start=1, line_end=5,
                        complexity=2, calls=[], called_by=set(), parameters=[],
                        is_exported=False, is_used=True, docstring=None
                    ),
                    'func2': FunctionInfo(
                        name='func2', file_path='file1.py', line_start=7, line_end=12,
                        complexity=4, calls=[], called_by=set(), parameters=[],
                        is_exported=False, is_used=True, docstring=None
                    )
                },
                classes=[],
                last_modified=0.0,
                hash='hash1'
            ),
            'file2.py': ModuleInfo(
                path='file2.py',
                lines=75,
                imports=[],
                exports=[],
                functions={
                    'func3': FunctionInfo(
                        name='func3', file_path='file2.py', line_start=1, line_end=3,
                        complexity=1, calls=[], called_by=set(), parameters=[],
                        is_exported=False, is_used=True, docstring=None
                    )
                },
                classes=[],
                last_modified=0.0,
                hash='hash2'
            )
        }
        
        summary = self.analyzer._generate_summary(modules)
        
        assert summary['total_files'] == 2
        assert summary['total_functions'] == 3
        assert summary['total_lines'] == 175  # 100 + 75
        assert summary['avg_functions_per_file'] == 1.5  # 3/2
        assert summary['avg_lines_per_file'] == 87.5  # 175/2