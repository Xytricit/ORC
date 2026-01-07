"""Context endpoints for compressed code context."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional

from api.schemas import ContextQuery, ContextResponse
from core.index_service import IndexService
from orc_package.config.settings import load_config

router = APIRouter()


@router.post("/context", response_model=ContextResponse)
def get_context_endpoint(query: ContextQuery):
    """
    Get compressed context for a natural language query.

    This endpoint returns a minimal, relevant subset of the codebase
    that addresses the user's query, staying within the token budget.
    """
    # Get the global index service instance
    cfg = load_config("config.yaml")
    index_service = IndexService(cfg)

    # Build context based on the query
    context = index_service.build_context(query.query, max_tokens=query.max_tokens)

    return ContextResponse(**context)


class ContextByFileRequest(BaseModel):
    file_path: str
    include_dependencies: bool = True
    max_tokens: int = 8000


@router.post("/context-by-file")
def get_context_by_file(request: ContextByFileRequest):
    """
    Get context for a specific file and its dependencies.

    This endpoint returns the content of a specific file along with
    any files or functions it depends on, useful for focused analysis.
    """
    cfg = load_config("config.yaml")
    index_service = IndexService(cfg)

    # For now, return the file content directly
    # In a full implementation, we'd extract dependencies from the graph
    try:
        with open(request.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple token estimation (1 token ~ 4 chars)
        estimated_tokens = len(content) // 4

        result = {
            "file_path": request.file_path,
            "content": content[:request.max_tokens * 4] if estimated_tokens > request.max_tokens else content,
            "estimated_tokens": min(estimated_tokens, request.max_tokens),
            "truncated": estimated_tokens > request.max_tokens
        }

        return result
    except FileNotFoundError:
        return {"error": f"File not found: {request.file_path}"}
    except Exception as e:
        return {"error": str(e)}
