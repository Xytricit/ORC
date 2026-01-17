"""
Test suite for parallel_indexer.py - Parallel Indexing System

Tests parallel processing, .orcignore pattern matching, file scanning, and performance.
"""
import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from orc.core.parallel_indexer import ParallelIndexer, _count_lines, _parse_file_worker


class TestParallelIndexerInitialization:
    """Test indexer initialization."""
    
    def test_indexer_initializes(self, sample_project):
        """Test that indexer initializes successfully."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        assert indexer.root_path == sample_project
        assert indexer.max_workers >= 1
        assert len(indexer.ignore_patterns) > 0
    
    def test_indexer_rejects_nonexistent_path(self, temp_dir):
        """Test that non-existent path raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            ParallelIndexer(root_path=temp_dir / "nonexistent")
    
    def test_indexer_rejects_file_path(self, temp_dir):
        """Test that file path raises ValueError."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("content")
        
        with pytest.raises(ValueError, match="not a directory"):
            ParallelIndexer(root_path=file_path)
    
    def test_indexer_accepts_custom_max_workers(self, sample_project):
        """Test custom max_workers setting."""
        indexer = ParallelIndexer(root_path=sample_project, max_workers=4)
        assert indexer.max_workers == 4
    
    def test_indexer_accepts_custom_ignore_patterns(self, sample_project):
        """Test custom ignore patterns."""
        custom_patterns = ['*.log', 'temp/']
        indexer = ParallelIndexer(root_path=sample_project, ignore_patterns=custom_patterns)
        
        assert indexer.ignore_patterns == custom_patterns


class TestOrcignorePatternMatching:
    """Test .orcignore pattern matching logic."""
    
    def test_indexer_loads_orcignore_file(self, sample_project, sample_orcignore):
        """Test loading patterns from .orcignore file."""
        # Copy .orcignore to project
        import shutil
        shutil.copy(sample_orcignore, sample_project / ".orcignore")
        
        indexer = ParallelIndexer(root_path=sample_project)
        
        # Should include both default and file patterns
        assert 'node_modules/' in indexer.ignore_patterns
        assert '*.pyc' in indexer.ignore_patterns
    
    def test_indexer_ignores_node_modules(self, sample_project):
        """Test that node_modules directory is ignored."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        node_modules_file = sample_project / "node_modules" / "package.js"
        assert indexer._should_ignore(node_modules_file) is True
    
    def test_indexer_ignores_git_directory(self, sample_project):
        """Test that .git directory is ignored."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        git_file = sample_project / ".git" / "config"
        assert indexer._should_ignore(git_file) is True
    
    def test_indexer_ignores_pycache(self, sample_project):
        """Test that __pycache__ is ignored."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        pycache_dir = sample_project / "__pycache__"
        pycache_dir.mkdir()
        pyc_file = pycache_dir / "module.pyc"
        pyc_file.write_text("compiled")
        
        assert indexer._should_ignore(pycache_dir) is True
        assert indexer._should_ignore(pyc_file) is True
    
    def test_indexer_does_not_ignore_regular_files(self, sample_project):
        """Test that regular files are not ignored."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        main_py = sample_project / "main.py"
        assert indexer._should_ignore(main_py) is False
    
    def test_indexer_pattern_matching_glob_style(self, sample_project):
        """Test glob-style pattern matching."""
        indexer = ParallelIndexer(
            root_path=sample_project,
            ignore_patterns=['test_*.py', 'tmp/']
        )
        
        test_file = sample_project / "test_something.py"
        test_file.write_text("test")
        
        assert indexer._should_ignore(test_file) is True


class TestFileScanning:
    """Test file scanning functionality."""
    
    def test_indexer_scans_python_files(self, sample_project):
        """Test scanning for Python files."""
        indexer = ParallelIndexer(root_path=sample_project)
        files = indexer._scan_files(extensions=['.py'])
        
        # Should find main.py, utils.py, tests/test_main.py
        file_names = [f.name for f in files]
        assert 'main.py' in file_names
        assert 'utils.py' in file_names
    
    def test_indexer_respects_ignore_patterns_during_scan(self, sample_project):
        """Test that ignored files are excluded from scan."""
        indexer = ParallelIndexer(root_path=sample_project)
        files = indexer._scan_files()
        
        # Should not find files in node_modules or .git
        file_paths = [str(f) for f in files]
        assert not any('node_modules' in p for p in file_paths)
        assert not any('.git' in p for p in file_paths)
    
    def test_indexer_scans_multiple_extensions(self, sample_project):
        """Test scanning for multiple file extensions."""
        # Create a JS file
        (sample_project / "app.js").write_text("console.log('hello');")
        
        indexer = ParallelIndexer(root_path=sample_project)
        files = indexer._scan_files(extensions=['.py', '.js'])
        
        extensions = [f.suffix for f in files]
        assert '.py' in extensions
        assert '.js' in extensions
    
    def test_indexer_handles_empty_directory(self, empty_project):
        """Test scanning empty directory."""
        indexer = ParallelIndexer(root_path=empty_project)
        files = indexer._scan_files()
        
        assert len(files) == 0


class TestParallelIndexing:
    """Test parallel indexing operations."""
    
    def test_indexer_indexes_project(self, sample_project):
        """Test basic project indexing."""
        indexer = ParallelIndexer(root_path=sample_project, max_workers=2)
        index, stats = indexer.index()
        
        assert 'files' in index
        assert 'functions' in index
        assert 'classes' in index
        assert len(index['files']) > 0
        assert stats['total_files'] > 0
    
    def test_indexer_returns_statistics(self, sample_project):
        """Test that statistics are returned."""
        indexer = ParallelIndexer(root_path=sample_project)
        index, stats = indexer.index()
        
        assert 'total_files' in stats
        assert 'indexing_time' in stats
        assert 'files_per_second' in stats
        assert 'workers_used' in stats
        assert stats['indexing_time'] > 0
    
    def test_indexer_handles_empty_project(self, empty_project):
        """Test indexing empty project."""
        indexer = ParallelIndexer(root_path=empty_project)
        index, stats = indexer.index()
        
        assert stats['total_files'] == 0
        assert len(index['files']) == 0
    
    def test_indexer_processes_files_in_parallel(self, large_project):
        """Test that parallel processing is faster than sequential."""
        # Sequential (1 worker)
        indexer_seq = ParallelIndexer(root_path=large_project, max_workers=1)
        start = time.time()
        index1, stats1 = indexer_seq.index()
        time_seq = time.time() - start
        
        # Parallel (2 workers)
        indexer_par = ParallelIndexer(root_path=large_project, max_workers=2)
        start = time.time()
        index2, stats2 = indexer_par.index()
        time_par = time.time() - start
        
        # Parallel should be faster (allow some variance)
        assert time_par < time_seq * 1.2  # At most 20% slower due to overhead
        
        # Results should be the same
        assert len(index1['files']) == len(index2['files'])


class TestWorkerFunction:
    """Test worker functions."""
    
    def test_parse_file_worker(self, sample_project):
        """Test _parse_file_worker function."""
        file_path = sample_project / "main.py"
        result = _parse_file_worker(str(file_path), 'python')
        
        assert 'files' in result
        assert str(file_path) in result['files']
        assert result['files'][str(file_path)]['language'] == 'python'
    
    def test_parse_file_worker_handles_errors(self, temp_dir):
        """Test that worker handles parsing errors gracefully."""
        bad_file = temp_dir / "bad.py"
        bad_file.write_text("def invalid syntax:")
        
        result = _parse_file_worker(str(bad_file), 'python')
        
        # Should return error structure, not raise
        assert 'files' in result
    
    def test_count_lines_function(self, temp_dir):
        """Test _count_lines helper function."""
        test_file = temp_dir / "test.py"
        test_file.write_text("line 1\nline 2\nline 3\n")
        
        count = _count_lines(test_file)
        assert count == 3
    
    def test_count_lines_handles_missing_file(self, temp_dir):
        """Test _count_lines handles missing files."""
        count = _count_lines(temp_dir / "nonexistent.py")
        assert count == 0


class TestIndexerRepr:
    """Test string representation."""
    
    def test_indexer_repr(self, sample_project):
        """Test indexer __repr__ for debugging."""
        indexer = ParallelIndexer(root_path=sample_project, max_workers=4)
        repr_str = repr(indexer)
        
        assert 'ParallelIndexer' in repr_str
        assert 'workers=4' in repr_str
    
    def test_indexer_get_ignore_patterns(self, sample_project):
        """Test get_ignore_patterns() returns a copy."""
        indexer = ParallelIndexer(root_path=sample_project)
        
        patterns1 = indexer.get_ignore_patterns()
        patterns2 = indexer.get_ignore_patterns()
        
        # Should be different objects
        assert patterns1 is not patterns2


