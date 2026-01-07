"""
Context Builder for AI Integration
Assembles minimal relevant code for AI queries
"""
from typing import List, Dict, Optional
import numpy as np
from .embeddings import SemanticSearch, EmbeddingGenerator
from storage.vector_store import VectorStore
import math


class ContextBuilder:
    """Build compressed context for AI tools"""

    def __init__(self, vector_store: VectorStore = None):
        self.index = {}
        self.graph = None
        self.vector_store = vector_store
        self.semantic_search = SemanticSearch(vector_store) if vector_store else None
        self.embedding_gen = EmbeddingGenerator()

    def build_context(self, query: str, max_tokens: int = 8000) -> Dict:
        """
        Build minimal context for a query

        Args:
            query: Natural language query or keyword search
            max_tokens: Maximum tokens to return

        Returns:
            Compressed context with relevant code
        """
        # Prepare user context for relevance ranking
        user_context = {
            'recent_files': getattr(self, '_recent_files', []),
            'frequent_entities': getattr(self, '_frequent_entities', {})
        }

        # If we have a vector store, use semantic search
        if self.semantic_search:
            semantic_results = self.semantic_search.search(query, top_k=20)

            # Extract relevant functions based on semantic search
            function_ids = [result['entity_id'] for result in semantic_results
                           if result['metadata'].get('entity_type') == 'function']

            # Get function data from index
            functions = []
            files = set()
            total_tokens = 0

            for fid in function_ids:
                if fid in self.index.get("functions", {}):
                    func_data = self.index["functions"][fid]
                    # Add relevance score placeholder
                    func_data['relevance_score'] = 0.9  # High score for semantic matches
                    # Estimate token count (rough approximation: 1 token ≈ 4 characters)
                    code = func_data.get("code", "")
                    est_tokens = math.ceil(len(code) / 4) if code else 0

                    if total_tokens + est_tokens <= max_tokens:
                        functions.append(func_data)
                        files.add(func_data.get("file", ""))
                        total_tokens += est_tokens
                    else:
                        break  # Stop if we exceed token budget

            # If semantic search didn't return enough results, fall back to keyword search
            if len(functions) < 5:
                keyword_results = self._keyword_search(query)
                for func_data in keyword_results:
                    fid = f"{func_data.get('file', '')}::{func_data.get('name', '')}"
                    if fid not in [f.get('file', '') + '::' + f.get('name', '') for f in functions]:
                        code = func_data.get("code", "")
                        est_tokens = math.ceil(len(code) / 4) if code else 0

                        if total_tokens + est_tokens <= max_tokens:
                            functions.append(func_data)
                            files.add(func_data.get("file", ""))
                            total_tokens += est_tokens
                        else:
                            break
        else:
            # Fall back to keyword search only
            keyword_results = self._keyword_search(query)
            functions = []
            files = set()
            total_tokens = 0

            for func_data in keyword_results:
                code = func_data.get("code", "")
                est_tokens = math.ceil(len(code) / 4) if code else 0

                if total_tokens + est_tokens <= max_tokens:
                    functions.append(func_data)
                    files.add(func_data.get("file", ""))
                    total_tokens += est_tokens
                else:
                    break

        # Apply sophisticated relevance ranking to the results
        if functions:
            functions = self._rank_by_relevance(functions, query, user_context)
            # Re-calculate token usage after ranking
            functions_within_token_limit = []
            current_tokens = 0
            for func_data in functions:
                code = func_data.get("code", "")
                est_tokens = math.ceil(len(code) / 4) if code else 0
                if current_tokens + est_tokens <= max_tokens:
                    functions_within_token_limit.append(func_data)
                    current_tokens += est_tokens
                else:
                    break
            functions = functions_within_token_limit

        return {
            "query": query,
            "files": list(files),
            "functions": functions,
            "total_tokens": total_tokens,
            "summary": f"Context built for query: {query}"
        }

    def _keyword_search(self, query: str) -> List[Dict]:
        """Fallback keyword search when semantic search is not available."""
        keywords = query.lower().split()
        results = []

        # Search in functions
        for fid, fdata in self.index.get("functions", {}).items():
            name = fdata.get("name", "")
            docstring = fdata.get("docstring", "")
            code = fdata.get("code", "")

            # Check if any keyword appears in name, docstring, or code
            text_to_search = f"{name} {docstring} {code}".lower()
            if any(k in text_to_search for k in keywords):
                results.append(fdata)

        # Search in classes
        for cid, cdata in self.index.get("classes", {}).items():
            name = cdata.get("name", "")
            if any(k in name.lower() for k in keywords):
                # Add class methods if available
                results.extend(cdata.get("methods", []))

        return results[:20]  # Return top 20 matches

    def _rank_by_relevance(self, items: List[Dict], query: str, user_context: Dict = None) -> List[Dict]:
        """Rank items by relevance using the sophisticated relevance ranker."""
        from .relevance_ranker import rank_entities

        ranked_entities = rank_entities(items, query, user_context)

        # Convert back to the original format
        ranked_items = []
        for entity in ranked_entities:
            item = {
                'id': entity.id,
                'name': entity.name,
                'file': entity.file_path,
                'code': entity.content,
                'relevance_score': entity.relevance_score,
                'metadata': entity.metadata
            }
            # Add any additional fields that were in the original item
            if entity.type:
                item['type'] = entity.type
            ranked_items.append(item)

        return ranked_items

    def index_for_semantic_search(self):
        """Index the current codebase for semantic search."""
        if self.semantic_search:
            self.semantic_search.index_code_entities(self.index)
