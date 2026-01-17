"""
ORC - AI-Powered Codebase Intelligence Platform

A comprehensive tool for analyzing, understanding, and optimizing codebases
using AI-powered insights and graph-based analysis.

Author: ORC Team
Date: 2026-01-14
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "ORC Team"
__license__ = "MIT"

# Core components (lazy imports to avoid circular dependencies)
try:
    from orc.core.parallel_indexer import ParallelIndexer
    from orc.core.index_service import IndexService
    from orc.storage.graph_db import GraphDB
    from orc.analysis.all_analyzers import Analyzer
    from orc.cli.cli_main import cli, main
except ImportError:
    # Allow partial imports during development
    pass

__all__ = [
    'ParallelIndexer',
    'IndexService',
    'GraphDB',
    'Analyzer',
    'cli',
    'main',
    '__version__',
]
