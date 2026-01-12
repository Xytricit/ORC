"""Pydantic schemas (skeleton)."""
from pydantic import BaseModel
from typing import List, Dict, Optional


class ContextQuery(BaseModel):
    query: str
    max_tokens: int = 8000


class ContextResponse(BaseModel):
    query: str
    files: List[str] = []
    functions: List[Dict] = []
    total_tokens: int = 0
    summary: str = ""


class SemanticSearchResponse(BaseModel):
    query: str
    results: List[Dict]
    count: int
