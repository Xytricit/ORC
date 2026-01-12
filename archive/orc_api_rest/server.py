"""FastAPI server providing ORC context to external AI tools.

Exposes a simple `/api/context` endpoint that lets any AI client ask
for a compressed view of the codebase for a natural-language query.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path

from orc.api.schemas import ContextQuery, ContextResponse, SemanticSearchResponse
from orc.core.index_service import IndexService
from orc_package.config.settings import load_config

# Import API endpoints
from orc.api.endpoints import context, optimization, analysis, query

app = FastAPI(title="ORC API", version="2.0")

# Allow local tools / IDEs to call this API easily.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(optimization.router, prefix="/api", tags=["optimization"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(query.router, prefix="/api", tags=["query"])

# Global IndexService instance (lazy index on first use if needed)
_cfg = load_config("config.yaml")
_index_service = IndexService(_cfg)


@app.get("/health")
def health():
    return {"status": "healthy", "version": app.version}


@app.post("/api/context", response_model=ContextResponse)
def get_context(query: ContextQuery):
    """Return minimal code context for a natural-language query.

    This is designed for external AIs: they call this endpoint with a
    user query and max token budget, and ORC returns a set of relevant
    snippets across all indexed languages.
    """
    # Assume `orc index`/`orc analyse` have been run; if not, callers
    # should trigger indexing separately. We *could* do lazy indexing
    # here, but that is usually too heavy for a single request.
    context = _index_service.build_context(query.query, max_tokens=query.max_tokens)
    return ContextResponse(**context)


@app.get("/api/search", response_model=SemanticSearchResponse)
def semantic_search(query: str, top_k: int = 10):
    """Perform semantic search across the indexed codebase.

    This endpoint uses vector embeddings to find semantically similar
    code entities to the provided query.
    """
    try:
        # Use the context builder's semantic search functionality
        from context.builder import ContextBuilder
        from storage.vector_store import VectorStore

        # Create a temporary context builder with the vector store
        vector_store = _index_service.vector_store
        context_builder = ContextBuilder(vector_store=vector_store)

        # Perform semantic search
        results = vector_store.search_by_content(query, top_k=top_k)

        return SemanticSearchResponse(
            query=query,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index")
def trigger_indexing(path: str = None):
    """Trigger indexing of a codebase.

    This endpoint allows triggering a re-index of the codebase,
    which will also update the vector embeddings for semantic search.
    """
    try:
        from pathlib import Path
        import os

        # Use the project root if no path is provided
        if path is None:
            index_path = _cfg.project_root
        else:
            index_path = Path(path)
            if not os.path.exists(index_path):
                raise HTTPException(status_code=404, detail=f"Path {path} does not exist")

        # Trigger indexing
        _index_service.index_project(index_path)

        return {
            "status": "success",
            "message": f"Indexing completed for {index_path}",
            "path": str(index_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
