"""Vector store for embeddings (optional).

Provides semantic search capabilities using vector embeddings.
"""
import sqlite3
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pickle
import hashlib


class VectorStore:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path:
            self.db_path = db_path
            self.use_sqlite = True
            self._init_db()
        else:
            self.store: Dict[str, List[float]] = {}
            self.use_sqlite = False

    def _init_db(self):
        """Initialize SQLite database for vector storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for storing vectors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create table for storing text content associated with vectors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_content (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                file_path TEXT,
                entity_type TEXT,  -- function, class, file, etc.
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict] = None, content: Optional[str] = None, file_path: Optional[str] = None, entity_type: Optional[str] = None):
        """Upsert a vector with optional metadata and content"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Serialize the vector as binary data
            vector_blob = pickle.dumps(vector)
            metadata_json = pickle.dumps(metadata) if metadata else None

            # Insert/update vector
            cursor.execute(
                '''INSERT OR REPLACE INTO vectors (id, embedding, metadata_json)
                   VALUES (?, ?, ?)''',
                (id, vector_blob, metadata_json)
            )

            # Insert/update content if provided
            if content:
                cursor.execute(
                    '''INSERT OR REPLACE INTO vector_content (id, content, file_path, entity_type)
                       VALUES (?, ?, ?, ?)''',
                    (id, content, file_path, entity_type)
                )

            conn.commit()
            conn.close()
        else:
            self.store[id] = vector

    def query(self, query_vector: List[float], top_k: int = 10, include_metadata: bool = False) -> List[Tuple[str, float, Optional[Dict]]]:
        """Query for similar vectors using cosine similarity"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Retrieve all vectors from database
            cursor.execute('SELECT id, embedding FROM vectors')
            results = []

            for row_id, embedding_blob in cursor.fetchall():
                stored_vector = pickle.loads(embedding_blob)
                similarity = self._cosine_similarity(query_vector, stored_vector)
                results.append((row_id, similarity, None))  # Will add metadata if requested

            conn.close()

            # Sort by similarity (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            # Get top_k results
            top_results = results[:top_k]

            # If metadata is requested, fetch it
            if include_metadata:
                final_results = []
                for item_id, similarity, _ in top_results:
                    # Fetch metadata
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('SELECT metadata_json FROM vectors WHERE id = ?', (item_id,))
                    row = cursor.fetchone()

                    metadata = None
                    if row and row[0]:
                        metadata = pickle.loads(row[0])

                    # Also fetch content info
                    cursor.execute('SELECT content, file_path, entity_type FROM vector_content WHERE id = ?', (item_id,))
                    content_row = cursor.fetchone()

                    if content_row:
                        content_info = {
                            'content': content_row[0],
                            'file_path': content_row[1],
                            'entity_type': content_row[2]
                        }
                        if metadata is None:
                            metadata = content_info
                        else:
                            metadata.update(content_info)

                    conn.close()
                    final_results.append((item_id, similarity, metadata))

                return final_results
            else:
                return top_results
        else:
            # In-memory implementation
            similarities = []
            for item_id, stored_vector in self.store.items():
                similarity = self._cosine_similarity(query_vector, stored_vector)
                similarities.append((item_id, similarity))

            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [(item_id, sim, None) for item_id, sim in similarities[:top_k]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)

    def delete(self, id: str):
        """Delete a vector by ID"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM vectors WHERE id = ?', (id,))
            cursor.execute('DELETE FROM vector_content WHERE id = ?', (id,))

            conn.commit()
            conn.close()
        else:
            if id in self.store:
                del self.store[id]

    def get_content(self, id: str) -> Optional[Dict]:
        """Get content associated with a vector ID"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT content, file_path, entity_type FROM vector_content WHERE id = ?', (id,))
            row = cursor.fetchone()

            conn.close()

            if row:
                return {
                    'content': row[0],
                    'file_path': row[1],
                    'entity_type': row[2]
                }
            return None
        else:
            return None

    def search_by_content(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Optional[Dict]]]:
        """Semantic search by content using vector similarity"""
        # This would typically use an embedding model to convert the query to a vector
        # For now, we'll use a simple approach - in a real implementation,
        # you'd use something like OpenAI embeddings or Sentence Transformers
        query_vector = self._simple_text_to_vector(query)
        return self.query(query_vector, top_k=top_k, include_metadata=True)

    def _simple_text_to_vector(self, text: str) -> List[float]:
        """Simple text to vector conversion for demonstration purposes"""
        # This is a very basic implementation - in reality, you'd use
        # a proper embedding model like OpenAI's embeddings or Sentence Transformers
        import hashlib

        # Create a simple hash-based vector representation
        text_hash = hashlib.md5(text.lower().encode()).hexdigest()

        # Convert hex to floats
        vector = []
        for i in range(0, len(text_hash), 2):
            byte_val = int(text_hash[i:i+2], 16)
            vector.append(byte_val / 255.0)  # Normalize to 0-1

        # Pad or truncate to a fixed size (e.g., 128 dimensions)
        target_size = 128
        if len(vector) < target_size:
            vector.extend([0.0] * (target_size - len(vector)))
        else:
            vector = vector[:target_size]

        return vector
