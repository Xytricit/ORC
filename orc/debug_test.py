#!/usr/bin/env python
"""
Debug test to check if ORC is working
"""
import sys
import traceback

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Python path:", sys.path[:3])  # Just first 3 entries

try:
    import orc_package
    print("orc_package imported successfully")
    print("orc_package location:", orc_package.__file__)
except ImportError as e:
    print(f"Failed to import orc_package: {e}")
    traceback.print_exc()

try:
    from orc_package.cli.commands import cli
    print("CLI imported successfully")
    print("CLI type:", type(cli))
except ImportError as e:
    print(f"Failed to import CLI: {e}")
    traceback.print_exc()

try:
    from core.indexer import PythonIndexer
    print("PythonIndexer imported successfully")
except ImportError as e:
    print(f"Failed to import PythonIndexer: {e}")
    traceback.print_exc()

try:
    from analysis.complexity import ComplexityAnalyzer
    print("ComplexityAnalyzer imported successfully")
except ImportError as e:
    print(f"Failed to import ComplexityAnalyzer: {e}")
    traceback.print_exc()

print("Debug test completed")