"""IndexService: façade over indexers, parsers, and storage.

This is a first-pass skeleton that wires MultiLanguageIndexer +
PythonIndexer into GraphStorage's normalized tables so that *all*
parsers are represented in the database-backed map.

Future work (per plan):
- Add real incremental logic using index_manifest.
- Add parallelism and batching.
- Add compressed context chunks and vector search.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional
import time
import hashlib

from .indexer import PythonIndexer, MultiLanguageIndexer
from .graph_builder import DependencyGraph
from orc.storage.graph_db import GraphStorage
from orc.storage.vector_store import VectorStore
from orc.context.builder import ContextBuilder
from orc_package.config.settings import ORCConfig


class IndexService:
    """High-level indexing API used by CLI and agents.

    This implementation focuses on wiring all language parsers into the
    normalized tables; it intentionally keeps logic simple and
    conservative, to be iterated on.
    """

    def __init__(self, config: ORCConfig):
        self.config = config
        self.storage = GraphStorage(config.index_path)
        # Initialize vector store for semantic search
        self.vector_store = VectorStore(config.index_path.parent / "vectors.db")
        # Initialize context builder with vector store
        self.context_builder = ContextBuilder(vector_store=self.vector_store)

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index_project(self, root_path: Optional[Path] = None, full: bool = True) -> None:
        """Index the entire project root.

        For now this always does a full walk and does very shallow
        incremental checks via manifest; later we can optimize further.
        """
        root = Path(root_path or self.config.project_root).resolve()

        # 1) Python AST index feeding v1 analyzers & module graph
        py_indexer = PythonIndexer(self.config)
        modules = py_indexer.index_directory(root)

        graph = DependencyGraph()
        graph.build_from_modules(modules)

        # Persist Python modules + graph using existing APIs
        self.storage.save_modules(modules)
        self.storage.save_graph("dependency", graph)

        # 2) Multi-language index from all parsers into normalized tables
        ml_indexer = MultiLanguageIndexer(self.config)
        index = ml_indexer.index_codebase(root)
        self._persist_multi_language_index(index)

        # 3) Index for semantic search using vector embeddings
        self._index_for_semantic_search(index)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_multi_language_index(self, index: Dict) -> None:
        """Write the multi-language index into normalized DB tables.

        The input `index` is the aggregate from MultiLanguageIndexer,
        containing the union of outputs from all parsers.
        """
        files = index.get("files", {}) or {}
        functions = index.get("functions", {}) or {}
        classes = index.get("classes", {}) or {}
        imports = index.get("imports", {}) or {}
        exports = index.get("exports", {}) or {}

        now = time.time()

        # Track which file paths are present in this index so we can clean
        # up anything that disappeared since the last run.
        current_paths = {str(p) for p in files.keys()}

        # Files
        for path_str, meta in files.items():
            path = str(path_str)
            language = meta.get("language", None)
            framework = meta.get("framework", None)
            loc = int(meta.get("loc", 0))

            # Try to infer mtime/hash cheaply; if file is missing, skip
            p = Path(path)
            if p.exists():
                stat = p.stat()
                last_modified = stat.st_mtime
                # Use a light hash based on size + mtime; callers that
                # need stronger guarantees can replace this later.
                hash_value = hashlib.md5(f"{stat.st_size}-{stat.st_mtime}".encode("utf-8")).hexdigest()
            else:
                last_modified = 0.0
                hash_value = ""

            # Persist file row + manifest
            self.storage.upsert_file_index(
                path=path,
                language=language,
                framework=framework,
                loc=loc,
                last_modified=last_modified,
                hash_value=hash_value,
                metadata={k: v for k, v in meta.items() if k not in {"language", "framework", "loc"}},
            )
            self.storage.upsert_manifest_entry(
                path=path,
                language=str(language or ""),
                last_modified=last_modified,
                hash_value=hash_value,
                last_indexed_at=now,
            )

        # Functions & classes store language from their own meta where
        # available; we do a best-effort lookup from file_index otherwise.
        self.storage.bulk_upsert_functions(functions)
        self.storage.bulk_upsert_classes(classes)

        # Imports/exports: currently MultiLanguageIndexer aggregates
        # imports/exports globally; we attach them per module when
        # possible.
        for file_path in files.keys():
            # For now, we do not attempt to reconstruct per-file imports
            # from global imports mapping; this can be refined by
            # teaching MultiLanguageIndexer to emit per-file imports.
            # To keep a consistent shape, we simply clear existing
            # per-file rows.
            self.storage.bulk_upsert_imports(str(file_path), {})
            self.storage.bulk_upsert_exports(str(file_path), {})

        # Clean up any manifest + index rows for files that no longer
        # exist in the latest multi-language index.
        try:
            existing_paths = set(self.storage.iter_manifest_paths())
        except Exception:
            existing_paths = set()
        removed_paths = existing_paths - current_paths
        for path in removed_paths:
            self.storage.clear_file_index_for_path(path)
            self.storage.delete_manifest_entry(path)

    def _index_for_semantic_search(self, index: Dict) -> None:
        """Index the multi-language index for semantic search using vector embeddings."""
        # For now, we'll use the vector store directly to index the code entities
        # The context builder will use this for semantic search
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

        # Generate embeddings for all entities using the embeddings module
        if texts:
            from context.embeddings import EmbeddingGenerator
            embedding_gen = EmbeddingGenerator()
            embedding_results = embedding_gen.generate_embeddings_batch(
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

    # ------------------------------------------------------------------
    # Query helpers (light-weight skeletons)
    # ------------------------------------------------------------------

    def get_dependency_graph(self) -> DependencyGraph:
        graph = self.storage.load_graph("dependency")
        if graph is None:
            # Rebuild from stored modules if needed
            modules = self.storage.load_modules()
            graph = DependencyGraph()
            graph.build_from_modules(modules)
        return graph

    def build_context(self, query: str, max_tokens: int = 8000) -> Dict:
        """Build a minimal context for a natural-language query.

        This implementation uses DB-backed symbol search to find
        relevant functions/classes/files, then slices the underlying
        source files into snippets until the approximate token budget is
        reached.
        """
        # Use the context builder which now supports both keyword and semantic search
        self.context_builder.index = self._get_current_index()
        return self.context_builder.build_context(query, max_tokens)

    def _get_current_index(self) -> Dict:
        """Get the current index from storage."""
        # This is a simplified implementation - in a real system, you'd want to
        # retrieve the full index from the database
        index = {
            'functions': {},
            'classes': {},
            'files': {}
        }

        # For now, we'll reconstruct a basic index from the stored data
        # In a real implementation, you'd want to store the full index in the DB
        modules = self.storage.load_modules()
        for path, module in modules.items():
            index['files'][path] = {
                'path': path,
                'language': 'python'  # Default for Python modules
            }
            for func_name, func_info in module.functions.items():
                func_id = f"{path}::{func_name}"
                index['functions'][func_id] = {
                    'name': func_name,
                    'file': path,
                    'code': self._get_function_code(path, func_info),
                    'docstring': func_info.docstring,
                    'complexity': func_info.complexity
                }

        return index

    def _get_function_code(self, file_path: str, func_info) -> str:
        """Extract function code from file."""
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
