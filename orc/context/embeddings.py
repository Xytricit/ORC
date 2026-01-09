"""Embeddings module for ORC context compression.

Handles generation and management of vector embeddings for semantic search.
"""
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

from typing import List, Dict, Optional
from pathlib import Path
import hashlib
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    text: str
    embedding: List[float]
    entity_id: str
    entity_type: str  # function, class, file, etc.
    file_path: str


class EmbeddingGenerator:
    """Generates embeddings for code entities"""
    
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding for the given text"""
        # Create a more sophisticated embedding based on text characteristics
        # This is a simplified implementation - in production, you'd use
        # a proper model like OpenAI embeddings or Sentence Transformers
        
        # Create a hash of the text
        text_hash = hashlib.sha256(text.lower().encode()).hexdigest()
        
        # Convert hex to floats and normalize
        embedding = []
        for i in range(0, len(text_hash), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append(byte_val / 255.0)  # Normalize to 0-1
        
        # Pad or truncate to target dimension
        if len(embedding) < self.dimension:
            # Pad with zeros
            embedding.extend([0.0] * (self.dimension - len(embedding)))
        else:
            # Truncate
            embedding = embedding[:self.dimension]
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], entity_ids: List[str], 
                                 entity_types: List[str], file_paths: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for a batch of texts"""
        results = []
        for text, entity_id, entity_type, file_path in zip(texts, entity_ids, entity_types, file_paths):
            embedding = self.generate_embedding(text)
            results.append(EmbeddingResult(
                text=text,
                embedding=embedding,
                entity_id=entity_id,
                entity_type=entity_type,
                file_path=file_path
            ))
        return results


class SemanticSearch:
    """Performs semantic search using vector embeddings"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.embedding_gen = EmbeddingGenerator()
    
    def index_code_entities(self, index: Dict):
        """Index all code entities in the vector store"""
        # Extract functions, classes, and files from the index
        texts = []
        entity_ids = []
        entity_types = []
        file_paths = []
        
        # Process functions
        for func_id, func_data in index.get('functions', {}).items():
            if 'code' in func_data:
                texts.append(func_data['code'])
                entity_ids.append(func_id)
                entity_types.append('function')
                file_paths.append(func_data.get('file', 'unknown'))
        
        # Process classes
        for class_id, class_data in index.get('classes', {}).items():
            # Combine class definition with methods if available
            class_text = f"class {class_data.get('name', '')}:"
            if 'methods' in class_data:
                for method in class_data['methods']:
                    class_text += f"\n{method.get('code', '')}"
            texts.append(class_text)
            entity_ids.append(class_id)
            entity_types.append('class')
            file_paths.append(class_data.get('file', 'unknown'))
        
        # Process files
        for file_path, file_data in index.get('files', {}).items():
            # For files, we might want to include the file content or summary
            file_summary = f"File: {file_path}\nLanguage: {file_data.get('language', 'unknown')}"
            if 'imports' in file_data:
                file_summary += f"\nImports: {', '.join(file_data['imports'][:5])}"  # First 5 imports
            texts.append(file_summary)
            entity_ids.append(file_path)
            entity_types.append('file')
            file_paths.append(file_path)
        
        # Generate embeddings for all entities
        if texts:
            embedding_results = self.embedding_gen.generate_embeddings_batch(
                texts, entity_ids, entity_types, file_paths
            )
            
            # Store embeddings in vector store
            for result in embedding_results:
                self.vector_store.upsert(
                    id=result.entity_id,
                    vector=result.embedding,
                    metadata={
                        'entity_type': result.entity_type,
                        'file_path': result.file_path
                    },
                    content=result.text,
                    file_path=result.file_path,
                    entity_type=result.entity_type
                )
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Perform semantic search for the given query"""
        # Generate embedding for the query
        query_embedding = self.embedding_gen.generate_embedding(query)
        
        # Query the vector store
        results = self.vector_store.query(query_embedding, top_k=top_k, include_metadata=True)
        
        # Format results
        formatted_results = []
        for entity_id, similarity, metadata in results:
            formatted_results.append({
                'entity_id': entity_id,
                'similarity': similarity,
                'metadata': metadata or {}
            })
        
        return formatted_results