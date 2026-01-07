"""Query endpoints for natural language codebase search."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from orc_package.agent.query_engine import QueryEngine
from storage.graph_db import GraphStorage
from orc_package.config.settings import load_config
from core.index_service import IndexService

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    include_context: bool = True


class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int


@router.post("/query", response_model=QueryResponse)
def query_codebase(request: QueryRequest):
    """
    Query the codebase using natural language.

    This endpoint allows users to ask questions about the codebase in plain English
    and returns relevant code snippets, functions, or files.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        # Load modules and graph for the query engine
        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        # Load dependency graph
        from core.graph_builder import DependencyGraph
        graph = storage.load_graph('dependency')
        if graph is None:
            # Rebuild from stored modules if needed
            graph = DependencyGraph()
            graph.build_from_modules(modules)

        # Initialize query engine
        engine = QueryEngine(cfg, modules, graph)
        result = engine.process_query(request.query)

        # Format results based on the result type
        formatted_results = []
        if result.result_type == 'list':
            for item in result.data[:request.top_k]:
                if isinstance(item, dict):
                    formatted_results.append(item)
                else:
                    formatted_results.append({"result": str(item)})
        elif result.result_type == 'metric':
            formatted_results = [{"metric": k, "value": v} for k, v in result.data.items()]
        else:
            formatted_results = [{"result": result.data}]

        return QueryResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/search")
def search_codebase(query: str, top_k: int = 10):
    """
    Search the codebase for specific terms or patterns.

    This endpoint performs keyword-based search across function names,
    class names, file paths, and code content.
    """
    try:
        cfg = load_config("config.yaml")
        index_service = IndexService(cfg)

        # Use the index service to search
        # For now, we'll simulate a search by looking at the loaded modules
        storage = GraphStorage(cfg.index_path)
        modules = storage.load_modules()

        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        # Perform a simple keyword search
        results = []
        search_term = query.lower()

        for file_path, module_info in modules.items():
            # Search in file path
            if search_term in file_path.lower():
                results.append({
                    "type": "file",
                    "name": file_path,
                    "path": file_path,
                    "match_type": "path"
                })

            # Search in function names
            for func_name, func_info in module_info.functions.items():
                if search_term in func_name.lower():
                    results.append({
                        "type": "function",
                        "name": func_name,
                        "path": file_path,
                        "line_start": func_info.line_start,
                        "complexity": func_info.complexity,
                        "match_type": "function_name"
                    })

                # Search in function docstrings
                if func_info.docstring and search_term in func_info.docstring.lower():
                    results.append({
                        "type": "function",
                        "name": func_name,
                        "path": file_path,
                        "line_start": func_info.line_start,
                        "complexity": func_info.complexity,
                        "match_type": "docstring"
                    })

        # Limit results
        results = results[:top_k]

        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@router.get("/symbols")
def get_symbols(prefix: str = "", limit: int = 50):
    """
    Get symbols (functions, classes, variables) from the codebase.

    This endpoint returns a list of symbols that match the given prefix,
    useful for autocomplete or symbol navigation.
    """
    try:
        cfg = load_config("config.yaml")
        storage = GraphStorage(cfg.index_path)

        modules = storage.load_modules()
        if not modules:
            raise HTTPException(status_code=404, detail="No indexed modules found")

        symbols = []
        prefix_lower = prefix.lower()

        for file_path, module_info in modules.items():
            # Add functions
            for func_name, func_info in module_info.functions.items():
                if not prefix or prefix_lower in func_name.lower():
                    symbols.append({
                        "name": func_name,
                        "type": "function",
                        "file": file_path,
                        "line": func_info.line_start,
                        "complexity": func_info.complexity
                    })

            # Add classes (if available)
            for class_name, class_info in module_info.classes.items():
                if not prefix or prefix_lower in class_name.lower():
                    symbols.append({
                        "name": class_name,
                        "type": "class",
                        "file": file_path,
                        "line": class_info.line_start
                    })

        # Sort and limit results
        symbols.sort(key=lambda x: x["name"])
        symbols = symbols[:limit]

        return {
            "prefix": prefix,
            "symbols": symbols,
            "total_found": len(symbols)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symbols: {str(e)}")
