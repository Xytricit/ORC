#!/usr/bin/env python
"""
Simple test to check if ORC modules can be imported
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

print("Testing imports...")

try:
    from orc_package.config.settings import ORCConfig
    print("✓ ORCConfig imported successfully")
except Exception as e:
    print(f"✗ Failed to import ORCConfig: {e}")

try:
    from core.index_service import IndexService
    print("✓ IndexService imported successfully")
except Exception as e:
    print(f"✗ Failed to import IndexService: {e}")

try:
    from context.builder import ContextBuilder
    print("✓ ContextBuilder imported successfully")
except Exception as e:
    print(f"✗ Failed to import ContextBuilder: {e}")

print("Import test complete.")