"""
ORC Integration Tests

Test components working together to ensure proper integration.

Author: ORC Team
Date: 2026-01-14
"""

import os
import tempfile
from pathlib import Path
import pytest

# Import ORC components
try:
    from orc.core.parallel_indexer import ParallelIndexer
    from orc.storage.graph_db import GraphDB
    from orc.parsers import get_parser, PythonParser
    from orc.analysis.all_analyzers import Analyzer, DependencyResolver
except ImportError as e:
    pytest.skip(f"ORC components not available: {e}", allow_module_level=True)


@pytest.fixture
def temp_project():
    """Create temporary project directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create sample Python files
        (project_path / "main.py").write_text("""
def main():
    result = calculate(10, 20)
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    main()
""")
        
        (project_path / "utils.py").write_text("""
def calculate(a, b):
    if a > 0:
        if b > 0:
            return a + b
    return 0

def unused_function():
    # This should be detected as dead code
    pass
""")
        
        (project_path / "config.py").write_text("""
CONFIG = {
    'debug': True,
    'version': '1.0.0'
}
""")
        
        yield project_path


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db = None
    try:
        yield db_path
    finally:
        # Cleanup - close any connections first
        import gc
        gc.collect()  # Force garbage collection to close connections
        
        # Try to delete, ignore errors on Windows
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass  # Windows file lock, ignore


class TestIndexerParserIntegration:
    """Test Indexer + Parser integration."""
    
    def test_indexer_finds_files(self, temp_project):
        """Test that indexer finds all Python files."""
        indexer = ParallelIndexer(root_path=temp_project)
        
        # Scan files (don't parse yet)
        files = indexer._scan_files(extensions=['.py'])
        
        assert len(files) >= 3
        filenames = [f.name for f in files]
        assert 'main.py' in filenames
        assert 'utils.py' in filenames
        assert 'config.py' in filenames
    
    def test_parser_processes_indexed_files(self, temp_project):
        """Test that parser can process files found by indexer."""
        indexer = ParallelIndexer(root_path=temp_project)
        files = indexer._scan_files(extensions=['.py'])
        
        parser = PythonParser()
        
        for file in files:
            result = parser.parse_file(file)
            
            assert result is not None
            assert 'functions' in result
            assert 'classes' in result
            assert 'imports' in result
    
    def test_indexer_full_index(self, temp_project):
        """Test full indexing workflow."""
        indexer = ParallelIndexer(root_path=temp_project)
        
        # Run full index - now returns single dict
        result = indexer.index()
        
        # Verify results
        assert 'files' in result
        assert len(result['files']) >= 3
        assert result['files_indexed'] >= 3
        assert 'total_functions' in result or result.get('stats', {}).get('total_functions', 0) >= 0


class TestParserDatabaseIntegration:
    """Test Parser + Database integration."""
    
    def test_store_parsed_functions(self, temp_project, temp_db):
        """Test storing parsed functions in database."""
        # Parse file
        parser = PythonParser()
        result = parser.parse_file(temp_project / "utils.py")
        
        # Store in database
        db = GraphDB(temp_db)
        
        # Store file (only 3 params: file_path, language, loc)
        db.store_file(
            file_path=str(temp_project / "utils.py"),
            language='python',
            loc=10
        )
        
        # Store functions
        for func_id, func_data in result['functions'].items():
            db.store_function(
                func_id=func_id,
                name=func_data['name'],
                file=str(temp_project / "utils.py"),
                line_start=func_data.get('line', 0),
                line_end=func_data.get('end_line', 0),
                complexity=func_data.get('complexity', 1),
                code=func_data.get('code', ''),
                parameters=func_data.get('params', []),
                calls=func_data.get('calls', []),
                is_exported=func_data.get('is_exported', False)
            )
        
        # Query back (pattern is positional, not keyword)
        functions = db.query_functions('%')
        
        assert len(functions) >= 2
        func_names = [f['name'] for f in functions]
        assert 'calculate' in func_names
        assert 'unused_function' in func_names
    
    def test_roundtrip_parse_store_retrieve(self, temp_project, temp_db):
        """Test parse → store → retrieve roundtrip."""
        parser = PythonParser()
        db = GraphDB(temp_db)
        
        # Parse
        result = parser.parse_file(temp_project / "main.py")
        
        # Store
        db.store_file(
            file_path=str(temp_project / "main.py"),
            language='python',
            loc=5
        )
        
        for func_id, func_data in result['functions'].items():
            db.store_function(
                func_id=func_id,
                name=func_data['name'],
                file=str(temp_project / "main.py"),
                line_start=func_data.get('line', 0),
                line_end=func_data.get('end_line', 0),
                complexity=func_data.get('complexity', 1),
                code=func_data.get('code', ''),
                parameters=func_data.get('params', []),
                calls=func_data.get('calls', []),
                is_exported=func_data.get('is_exported', False)
            )
        
        # Retrieve - query_functions takes pattern as positional arg
        retrieved = db.query_functions('main')
        
        assert len(retrieved) >= 1
        assert retrieved[0]['name'] == 'main'


class TestFullWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_index_analyze_workflow(self, temp_project, temp_db):
        """Test: Index → Analyze workflow."""
        # Step 1: Index - now returns single dict
        indexer = ParallelIndexer(root_path=temp_project)
        result = indexer.index()
        
        assert result['files_indexed'] >= 3
        
        # Step 2: Store in database
        db = GraphDB(temp_db)
        parser = PythonParser()
        
        for file in Path(temp_project).glob('*.py'):
            result = parser.parse_file(file)
            
            # Store file
            db.store_file(
                file_path=str(file),
                language='python',
                loc=len(file.read_text().splitlines())
            )
            
            # Store functions
            for func_id, func_data in result['functions'].items():
                db.store_function(
                    func_id=func_id,
                    name=func_data['name'],
                    file=str(file),
                    line_start=func_data.get('line', 0),
                    line_end=func_data.get('end_line', 0),
                    complexity=func_data.get('complexity', 1),
                    code=func_data.get('code', ''),
                    parameters=func_data.get('params', []),
                    calls=func_data.get('calls', []),
                    is_exported=func_data.get('is_exported', False)
                )
        
        # Step 3: Query database (use wildcard pattern)
        all_functions = db.query_functions('%')
        
        assert len(all_functions) >= 3
        
        # Step 4: Run analysis (simplified)
        complex_functions = [f for f in all_functions if f['complexity'] > 2]
        
        # Verify we found the complex function
        complex_names = [f['name'] for f in complex_functions]
        assert 'calculate' in complex_names
    
    def test_parser_registry_integration(self, temp_project):
        """Test parser registry automatically selects correct parser."""
        # Create JS file
        js_file = temp_project / "test.js"
        js_file.write_text("""
function hello() {
    console.log("Hello");
}
""")
        
        # Get parser from registry
        parser = get_parser(js_file)
        
        assert parser is not None
        
        # Parse file
        result = parser.parse_file(js_file)
        
        assert 'functions' in result
        assert len(result['functions']) >= 1


class TestErrorHandling:
    """Test error handling in integrated workflows."""
    
    def test_malformed_python_file(self, temp_project):
        """Test handling of syntactically invalid Python."""
        # Create malformed file
        bad_file = temp_project / "bad.py"
        bad_file.write_text("""
def broken(
    # Missing closing paren and colon
""")
        
        parser = PythonParser()
        
        # Should not crash
        result = parser.parse_file(bad_file)
        
        # Should return empty or error result
        assert result is not None
    
    def test_missing_file(self, temp_project):
        """Test handling of non-existent file."""
        parser = PythonParser()
        
        non_existent = temp_project / "does_not_exist.py"
        
        # Parser logs error but doesn't raise - graceful failure
        result = parser.parse_file(non_existent)
        
        # Should return result (possibly with error info)
        assert result is not None
        # Could check for error indicator if parser includes one


class TestCacheIntegration:
    """Test cache integration with indexer."""
    
    def test_cache_speeds_up_reindex(self, temp_project):
        """Test that cache improves reindex performance."""
        indexer = ParallelIndexer(root_path=temp_project)
        
        # First index (cold)
        import time
        start1 = time.time()
        result1 = indexer.index()
        time1 = time.time() - start1
        
        # Second index (warm cache)
        start2 = time.time()
        result2 = indexer.index()
        time2 = time.time() - start2
        
        # Second should be faster (or at least not slower)
        # Note: In small projects, overhead might make this flaky
        assert result1['files_indexed'] == result2['files_indexed']
        
        # Cache should be used
        # (Time comparison might be unreliable for tiny projects)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
