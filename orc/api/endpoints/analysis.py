"""Analysis endpoints for codebase insights."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json

from orc_package.analysis.dead_code import DeadCodeAnalyzer
from orc_package.analysis.metrics import MetricsAnalyzer
from orc_package.analysis.dependencies import DependencyAnalyzer
from storage.graph_db import GraphStorage
from orc_package.config.settings import load_config

router = APIRouter()


class DeadCodeResponse:
    def __init__(self, unused_functions: List[Dict], unused_files: List[str], estimated_lines_saved: int):
        self.unused_functions = unused_functions
        self.unused_files = unused_files
        self.estimated_lines_saved = estimated_lines_saved


@router.get("/deadcode")
def get_deadcode():
    """
    Get dead code analysis for the entire codebase.

    Returns unused functions, classes, and files that could be safely removed.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        analyzer = DeadCodeAnalyzer(cfg)
        report = analyzer.analyze(modules)

        # Format the results
        unused_functions = []
        for func in report.unused_functions:
            unused_functions.append({
                "id": func.get("id", ""),
                "function": func.get("function", ""),
                "file": func.get("file", ""),
                "line": func.get("line", 0),
                "complexity": func.get("complexity", 0)
            })

        return {
            "unused_functions": unused_functions,
            "unused_files": report.unused_files,
            "estimated_lines_saved": report.estimated_lines_saved
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dead code analysis: {str(e)}")


@router.get("/metrics")
def get_metrics():
    """
    Get comprehensive code metrics for the codebase.

    Returns statistics about code quality, complexity, and structure.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        analyzer = MetricsAnalyzer(cfg)
        report = analyzer.analyze(modules)

        return {
            "total_files": report.total_files,
            "total_functions": report.total_functions,
            "total_classes": report.total_classes,
            "total_lines": report.total_lines,
            "avg_complexity": report.avg_complexity,
            "max_complexity": report.max_complexity,
            "avg_loc_per_function": report.avg_loc_per_function,
            "duplicate_functions": report.duplicate_functions,
            "large_files": report.large_files,
            "complex_functions": report.complex_functions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/dependencies")
def get_dependencies():
    """
    Get dependency analysis for the codebase.

    Returns information about module and function dependencies.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        analyzer = DependencyAnalyzer(cfg)
        report = analyzer.analyze(modules)

        return {
            "circular_dependencies": report.circular_dependencies,
            "highly_coupled_modules": report.highly_coupled_modules,
            "dependency_chains": report.dependency_chains,
            "modules_with_most_outgoing_deps": report.modules_with_most_outgoing_deps,
            "modules_with_most_incoming_deps": report.modules_with_most_incoming_deps
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dependency analysis: {str(e)}")


@router.get("/impact")
def get_impact(file: str, function: str):
    """
    Analyze the impact of changing or removing a specific function.

    Returns information about what depends on the specified function.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        # Build dependency graph
        from core.graph_builder import DependencyGraph
        graph = storage.load_graph("dependency")
        if graph is None:
            # Rebuild from stored modules if needed
            graph = DependencyGraph()
            graph.build_from_modules(modules)

        # Get function ID
        func_id = f"{file}::{function}"

        # Get callers (who calls this function)
        callers = graph.get_function_callers(func_id) if hasattr(graph, 'get_function_callers') else []

        # Get dependencies (what this function calls)
        dependencies = graph.get_function_dependencies(func_id) if hasattr(graph, 'get_function_dependencies') else []

        return {
            "function": function,
            "file": file,
            "called_by": callers,
            "depends_on": dependencies,
            "impact_score": len(callers) * 10,  # Simple impact score based on number of callers
            "risk_level": "high" if len(callers) > 10 else "medium" if len(callers) > 3 else "low"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving impact analysis: {str(e)}")
