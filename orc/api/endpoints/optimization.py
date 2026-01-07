"""Optimization endpoints for suggesting code improvements."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

from orc_package.optimization.suggester import suggest_optimizations, OptimizationSuggestion
from orc_package.analysis.complexity import ComplexityAnalyzer, ComplexityReport
from storage.graph_db import GraphStorage
from orc_package.config.settings import load_config

router = APIRouter()


class OptimizationRequest(BaseModel):
    file: str
    function: Optional[str] = None
    code: Optional[str] = None
    complexity_report: Optional[Dict[str, Any]] = None


class OptimizationResponse(BaseModel):
    current_complexity: str
    suggested_complexity: str
    suggestion: str
    optimized_code: Optional[str] = None
    estimated_improvement: float
    implementation_example: Optional[str] = None


@router.post("/optimize", response_model=OptimizationResponse)
def optimize_code(request: OptimizationRequest):
    """
    Get optimization suggestions for code.

    This endpoint analyzes the provided code and suggests optimizations
    based on algorithmic complexity and common patterns.
    """
    try:
        # If code is provided directly, analyze it
        if request.code and request.function:
            # Create a mock complexity report if not provided
            complexity_report = None
            if request.complexity_report:
                complexity_report = ComplexityReport(
                    function=request.function,
                    file=request.file,
                    time_complexity=request.complexity_report.get('time_complexity', 'O(n)'),
                    space_complexity=request.complexity_report.get('space_complexity', 'O(1)'),
                    hotspot=request.complexity_report.get('hotspot', False),
                    suggestion=request.complexity_report.get('suggestion', ''),
                    estimated_improvement=request.complexity_report.get('estimated_improvement', 0.1),
                    complexity_score=request.complexity_report.get('complexity_score', 1)
                )

            # Get optimization suggestions
            suggestions = suggest_optimizations(
                function_code=request.code,
                function_name=request.function,
                file_path=request.file,
                complexity_report=complexity_report
            )

            if suggestions:
                best_suggestion = suggestions[0]  # Return the first/most relevant suggestion
                return OptimizationResponse(
                    current_complexity=best_suggestion.current_algorithm,
                    suggested_complexity=best_suggestion.suggested_algorithm,
                    suggestion=best_suggestion.suggestion_details,
                    estimated_improvement=best_suggestion.estimated_performance_gain,
                    implementation_example=best_suggestion.implementation_example
                )

        # If no specific code provided, analyze the file from the indexed codebase
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        # Find the function in the indexed modules
        for module_path, module_info in modules.items():
            if module_path.endswith(request.file):
                if request.function and request.function in module_info.functions:
                    func_info = module_info.functions[request.function]

                    # Extract function code
                    with open(module_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    start_line = func_info.line_start - 1  # Convert to 0-based index
                    end_line = func_info.line_end

                    # Extract the function code
                    func_lines = lines[start_line:end_line]
                    code = "".join(func_lines).strip()

                    # Create complexity report
                    complexity_report = ComplexityReport(
                        function=request.function,
                        file=request.file,
                        time_complexity=getattr(func_info, 'time_complexity', 'O(n)'),
                        space_complexity=getattr(func_info, 'space_complexity', 'O(1)'),
                        hotspot=False,  # Would need graph to determine this properly
                        suggestion="",
                        estimated_improvement=0.1,
                        complexity_score=func_info.complexity
                    )

                    # Get optimization suggestions
                    suggestions = suggest_optimizations(
                        function_code=code,
                        function_name=request.function,
                        file_path=request.file,
                        complexity_report=complexity_report
                    )

                    if suggestions:
                        best_suggestion = suggestions[0]
                        return OptimizationResponse(
                            current_complexity=best_suggestion.current_algorithm,
                            suggested_complexity=best_suggestion.suggested_algorithm,
                            suggestion=best_suggestion.suggestion_details,
                            estimated_improvement=best_suggestion.estimated_performance_gain,
                            implementation_example=best_suggestion.implementation_example
                        )

                # If no specific function requested, analyze all functions in the file
                elif not request.function:
                    # For now, return a general response - in a full implementation
                    # we might want to analyze all functions in the file
                    raise HTTPException(status_code=400, detail="Function name required when analyzing file")

        # If we get here, the file/function wasn't found in the index
        raise HTTPException(status_code=404, detail=f"Function {request.function} not found in {request.file}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing optimization request: {str(e)}")


@router.get("/complexity")
def get_complexity_overview():
    """
    Get an overview of complexity in the codebase.

    Returns functions with high complexity that could benefit from optimization.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        # Create a simple index for the analyzer
        index = {}
        for module_path, module_info in modules.items():
            for func_name, func_info in module_info.functions.items():
                func_id = f"{module_path}::{func_name}"
                index[func_id] = {
                    'name': func_name,
                    'file': module_path,
                    'complexity': func_info.complexity,
                    'code': _extract_function_code(module_path, func_info)
                }

        analyzer = ComplexityAnalyzer(index, None)
        complex_functions = analyzer.get_complex_functions(threshold=10)  # Threshold of 10

        # Format the results
        results = []
        for report in complex_functions:
            results.append({
                "function": report.function,
                "file": report.file,
                "time_complexity": report.time_complexity,
                "space_complexity": report.space_complexity,
                "complexity_score": report.complexity_score,
                "hotspot": report.hotspot,
                "suggestion": report.suggestion,
                "estimated_improvement": report.estimated_improvement
            })

        return {"complex_functions": results[:50]}  # Return top 50

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving complexity overview: {str(e)}")


def _extract_function_code(file_path: str, func_info) -> str:
    """Extract the code for a specific function from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_line = func_info.line_start - 1  # Convert to 0-based index
        end_line = func_info.line_end

        # Extract the function code
        func_lines = lines[start_line:end_line]
        return "".join(func_lines).strip()
    except Exception:
        return ""
