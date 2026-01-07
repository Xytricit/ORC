"""Sophisticated relevance ranking algorithm for context compression."""

from typing import Dict, List, Tuple, Any
import math
from dataclasses import dataclass
import re


@dataclass
class RankedEntity:
    """Represents an entity with its relevance score."""
    id: str
    type: str  # 'function', 'class', 'file', etc.
    name: str
    file_path: str
    content: str
    relevance_score: float
    metadata: Dict[str, Any]


class RelevanceRanker:
    """Ranks code entities by relevance to a query using multiple factors."""

    def __init__(self):
        self.weights = {
            'keyword_match': 0.3,
            'semantic_similarity': 0.25,
            'structural_context': 0.2,
            'usage_frequency': 0.15,
            'recency': 0.1
        }

    def rank_entities(self,
                     entities: List[Dict],
                     query: str,
                     user_context: Dict = None) -> List[RankedEntity]:
        """Rank entities by relevance to the query."""
        ranked_entities = []

        for entity in entities:
            relevance_score = self._calculate_relevance_score(entity, query, user_context)

            ranked_entity = RankedEntity(
                id=entity.get('id', ''),
                type=entity.get('type', 'unknown'),
                name=entity.get('name', ''),
                file_path=entity.get('file', ''),
                content=entity.get('code', entity.get('content', '')),
                relevance_score=relevance_score,
                metadata=entity.get('metadata', {})
            )

            ranked_entities.append(ranked_entity)

        # Sort by relevance score in descending order
        ranked_entities.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked_entities

    def _calculate_relevance_score(self,
                                 entity: Dict,
                                 query: str,
                                 user_context: Dict = None) -> float:
        """Calculate the relevance score for a single entity."""
        score = 0.0

        # Keyword matching score (0.0 to 1.0)
        keyword_score = self._calculate_keyword_score(entity, query)
        score += keyword_score * self.weights['keyword_match']

        # Semantic similarity score (0.0 to 1.0)
        semantic_score = self._calculate_semantic_score(entity, query)
        score += semantic_score * self.weights['semantic_similarity']

        # Structural context score (0.0 to 1.0)
        structural_score = self._calculate_structural_score(entity, query)
        score += structural_score * self.weights['structural_context']

        # Usage frequency score (0.0 to 1.0)
        usage_score = self._calculate_usage_score(entity)
        score += usage_score * self.weights['usage_frequency']

        # Recency score (0.0 to 1.0) - if user context includes recency info
        recency_score = self._calculate_recency_score(entity, user_context)
        score += recency_score * self.weights['recency']

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def _calculate_keyword_score(self, entity: Dict, query: str) -> float:
        """Calculate score based on keyword matching."""
        entity_text = f"{entity.get('name', '')} {entity.get('code', '')} {entity.get('docstring', '')}".lower()
        query_terms = query.lower().split()

        matches = 0
        total_terms = len(query_terms)

        for term in query_terms:
            if term in entity_text:
                matches += 1

        if total_terms == 0:
            return 0.0

        return matches / total_terms

    def _calculate_semantic_score(self, entity: Dict, query: str) -> float:
        """Calculate score based on semantic similarity."""
        # This is a simplified implementation
        # In a real system, this would use embeddings or more sophisticated NLP

        entity_text = f"{entity.get('name', '')} {entity.get('code', '')} {entity.get('docstring', '')}".lower()
        query_lower = query.lower()

        # Simple semantic indicators
        semantic_indicators = [
            ('authentication', 'auth', 'login', 'password', 'token', 'session'),
            ('database', 'db', 'sql', 'query', 'connection', 'model'),
            ('api', 'endpoint', 'route', 'request', 'response', 'http'),
            ('error', 'exception', 'raise', 'try', 'catch', 'handle'),
            ('cache', 'memory', 'store', 'retrieve', 'performance'),
            ('security', 'encrypt', 'decrypt', 'validate', 'permission', 'access')
        ]

        max_similarity = 0.0

        for indicator_group in semantic_indicators:
            query_has_indicator = any(ind in query_lower for ind in indicator_group)
            entity_has_indicator = any(ind in entity_text for ind in indicator_group)

            if query_has_indicator and entity_has_indicator:
                max_similarity = max(max_similarity, 0.8)
            elif query_has_indicator or entity_has_indicator:
                max_similarity = max(max_similarity, 0.4)

        return max_similarity

    def _calculate_structural_score(self, entity: Dict, query: str) -> float:
        """Calculate score based on structural context."""
        score = 0.0

        # Functions that are called by many others are more relevant
        callers_count = entity.get('callers_count', 0)
        if callers_count > 10:
            score += 0.3
        elif callers_count > 5:
            score += 0.2
        elif callers_count > 0:
            score += 0.1

        # Functions that call many others might be orchestrators
        callees_count = entity.get('callees_count', 0)
        if callees_count > 10:
            score += 0.2
        elif callees_count > 5:
            score += 0.1

        # Entry points are often more relevant
        name = entity.get('name', '').lower()
        if any(entry_point in name for entry_point in ['main', 'init', 'run', 'start', 'entry']):
            score += 0.3

        # Public APIs are often more relevant
        if not name.startswith('_'):
            score += 0.1

        return min(1.0, score)

    def _calculate_usage_score(self, entity: Dict) -> float:
        """Calculate score based on usage frequency."""
        # This would typically come from metrics about how often code is used
        usage_count = entity.get('usage_count', 0)

        if usage_count > 1000:
            return 1.0
        elif usage_count > 500:
            return 0.8
        elif usage_count > 100:
            return 0.6
        elif usage_count > 10:
            return 0.4
        elif usage_count > 0:
            return 0.2
        else:
            return 0.1  # Even unused code might be relevant for understanding

    def _calculate_recency_score(self, entity: Dict, user_context: Dict = None) -> float:
        """Calculate score based on recency of changes."""
        if not user_context or 'recent_files' not in user_context:
            return 0.1  # Default low score if no recency info

        recent_files = user_context.get('recent_files', [])
        file_path = entity.get('file', '')

        if file_path in recent_files:
            # More recent = higher score, with position in list indicating recency
            position = recent_files.index(file_path)
            # Score decreases as position increases (more recent = higher position)
            score = max(0.1, 1.0 - (position * 0.1))
            return score

        return 0.1

    def rerank_based_on_dependencies(self,
                                   ranked_entities: List[RankedEntity],
                                   dependency_graph: Dict) -> List[RankedEntity]:
        """Rerank entities based on their dependencies."""
        # Boost score of entities that are dependencies of highly-ranked items
        entity_map = {entity.id: entity for entity in ranked_entities}

        for entity in ranked_entities:
            # Find dependencies of this entity
            deps = dependency_graph.get(entity.id, {}).get('depends_on', [])

            for dep_id in deps:
                if dep_id in entity_map:
                    dep_entity = entity_map[dep_id]
                    # Boost dependency's score based on the score of the entity that depends on it
                    boost = entity.relevance_score * 0.1  # 10% boost from each dependent
                    dep_entity.relevance_score = min(1.0, dep_entity.relevance_score + boost)

        # Re-sort after boosting dependencies
        ranked_entities.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked_entities


def rank_entities(entities: List[Dict], query: str, user_context: Dict = None) -> List[RankedEntity]:
    """Public function to rank entities by relevance."""
    ranker = RelevanceRanker()
    return ranker.rank_entities(entities, query, user_context)


def rank_results(items: List[Dict], query: str) -> List[Dict]:
    """Legacy function for backward compatibility."""
    ranked_entities = rank_entities(items, query)
    # Convert back to original format for compatibility
    return [{
        'id': entity.id,
        'type': entity.type,
        'name': entity.name,
        'file': entity.file_path,
        'content': entity.content,
        'relevance_score': entity.relevance_score,
        'metadata': entity.metadata
    } for entity in ranked_entities]
