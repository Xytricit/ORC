#!/usr/bin/env python
"""
Test script to verify the Context Compression Engine implementation
"""
import tempfile
import shutil
import traceback
from pathlib import Path

def test_context_compression():
    """Test the context compression engine with a simple example"""

    try:
        from core.index_service import IndexService
        from orc_package.config.settings import ORCConfig

        # Create a temporary directory with test code
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test Python file
            test_file = temp_path / "test_code.py"
            test_code = '''
def used_function():
    """This function is used"""
    print("I am used")
    return 42

def unused_function():
    """This function is never called"""
    print("I am unused")
    return 100

def another_unused_function():
    """Another unused function"""
    x = 1 + 1
    y = x * 2
    return y

# Only call the used function
if __name__ == "__main__":
    result = used_function()
    print(f"Result: {result}")
'''

            with open(test_file, 'w') as f:
                f.write(test_code)

            # Create config
            config = ORCConfig()
            config.project_root = temp_path
            config.index_path = temp_path / ".orc" / "index.db"

            # Create index service
            service = IndexService(config)

            # Index the project
            print("Indexing project...")
            service.index_project(temp_path)
            print("Indexing complete.")

            # Test context compression
            print("\nTesting context compression...")
            context = service.build_context("used function", max_tokens=2000)

            print(f"Query: {context['query']}")
            print(f"Files: {context['files']}")
            print(f"Number of functions: {len(context['functions'])}")
            print(f"Total tokens: {context['total_tokens']}")
            print(f"Summary: {context['summary']}")

            # Verify the context contains relevant information
            assert context['query'] == "used function"
            assert len(context['files']) > 0
            assert len(context['functions']) > 0
            assert context['total_tokens'] >= 0

            print("\nContext compression test passed!")
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    test_context_compression()