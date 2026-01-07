"""
ORC Storage: SQLite Graph Database
"""
import sqlite3
import json
import pickle
from pathlib import Path
from typing import Dict, Tuple
from core.indexer import ModuleInfo

class GraphStorage:
    """SQLite database operations for storing indexed data and graphs"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for storing module information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                path TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                last_modified REAL,
                hash TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for storing graph data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graphs (
                id INTEGER PRIMARY KEY,
                graph_type TEXT NOT NULL,
                data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for storing analysis results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY,
                result_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Normalized multi-language index tables (v2)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_index (
                path TEXT PRIMARY KEY,
                language TEXT,
                framework TEXT,
                loc INTEGER,
                last_modified REAL,
                hash TEXT,
                metadata_json TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS function_index (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                name TEXT NOT NULL,
                language TEXT,
                line_start INTEGER,
                line_end INTEGER,
                complexity INTEGER,
                calls_json TEXT,
                extras_json TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class_index (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                name TEXT NOT NULL,
                language TEXT,
                bases_json TEXT,
                extras_json TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_index (
                file_path TEXT NOT NULL,
                module TEXT NOT NULL,
                count INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_index (
                file_path TEXT NOT NULL,
                symbol TEXT NOT NULL,
                kind TEXT
            )
        ''')

        # Manifest for incremental indexing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_manifest (
                path TEXT PRIMARY KEY,
                language TEXT,
                last_modified REAL,
                hash TEXT,
                last_indexed_at REAL
            )
        ''')

        conn.commit()
        conn.close()

    def save_modules(self, modules: Dict[str, ModuleInfo]):
        """Save module information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for path, module in modules.items():
            # Convert ModuleInfo to JSON-serializable format
            module_data = {
                'path': module.path,
                'lines': module.lines,
                'imports': module.imports,
                'exports': module.exports,
                'functions': {
                    name: {
                        'name': func.name,
                        'file_path': func.file_path,
                        'line_start': func.line_start,
                        'line_end': func.line_end,
                        'complexity': func.complexity,
                        'calls': func.calls,
                        'called_by': list(func.called_by),
                        'parameters': func.parameters,
                        'is_exported': func.is_exported,
                        'is_used': func.is_used,
                        'docstring': func.docstring
                    }
                    for name, func in module.functions.items()
                },
                'classes': module.classes,
                'last_modified': module.last_modified,
                'hash': module.hash
            }

            module_json = json.dumps(module_data)
            cursor.execute(
                '''INSERT OR REPLACE INTO modules (path, data, last_modified, hash)
                   VALUES (?, ?, ?, ?)''',
                (path, module_json, module.last_modified, module.hash)
            )

        conn.commit()
        conn.close()

    def load_modules(self) -> Dict[str, ModuleInfo]:
        """Load module information from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT path, data FROM modules')
        modules = {}
        for path, data_json in cursor.fetchall():
            data = json.loads(data_json)

            # Reconstruct ModuleInfo object
            functions = {}
            for name, func_data in data['functions'].items():
                from core.indexer import FunctionInfo
                functions[name] = FunctionInfo(
                    name=func_data['name'],
                    file_path=func_data['file_path'],
                    line_start=func_data['line_start'],
                    line_end=func_data['line_end'],
                    complexity=func_data['complexity'],
                    calls=func_data['calls'],
                    called_by=set(func_data['called_by']),
                    parameters=func_data['parameters'],
                    is_exported=func_data['is_exported'],
                    is_used=func_data['is_used'],
                    docstring=func_data['docstring']
                )

            modules[path] = ModuleInfo(
                path=data['path'],
                lines=data['lines'],
                imports=data['imports'],
                exports=data['exports'],
                functions=functions,
                classes=data['classes'],
                last_modified=data['last_modified'],
                hash=data['hash']
            )

        conn.close()
        return modules

    # --- v1 graph + analysis APIs ---------------------------------------

    def save_graph(self, graph_type: str, graph_data):
        """Save graph data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete existing graph of this type
        cursor.execute('DELETE FROM graphs WHERE graph_type = ?', (graph_type,))

        # Insert new graph data
        cursor.execute(
            'INSERT INTO graphs (graph_type, data) VALUES (?, ?)',
            (graph_type, pickle.dumps(graph_data))
        )

        conn.commit()
        conn.close()

    def load_graph(self, graph_type: str):
        """Load graph data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT data FROM graphs WHERE graph_type = ?', (graph_type,))
        row = cursor.fetchone()

        graph = pickle.loads(row[0]) if row else None

        conn.close()
        return graph

    def save_analysis_result(self, result_type: str, result_data: dict):
        """Save analysis results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO analysis_results (result_type, data) VALUES (?, ?)',
            (result_type, json.dumps(result_data))
        )

        conn.commit()
        conn.close()

    def load_analysis_results(self, result_type: str = None) -> list:
        """Load analysis results from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if result_type:
            cursor.execute(
                'SELECT data FROM analysis_results WHERE result_type = ? ORDER BY created_at DESC',
                (result_type,)
            )
        else:
            cursor.execute('SELECT data FROM analysis_results ORDER BY created_at DESC')

        results = [json.loads(row[0]) for row in cursor.fetchall()]

        conn.close()
        return results

    # --- v2 normalized index APIs ---------------------------------------

    def upsert_file_index(self, path: str, language: str, framework: str,
                          loc: int, last_modified: float, hash_value: str,
                          metadata: dict = None):
        """Insert or update a file_index row."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata or {})
        cursor.execute(
            '''INSERT OR REPLACE INTO file_index
               (path, language, framework, loc, last_modified, hash, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (path, language, framework, loc, last_modified, hash_value, metadata_json),
        )

        conn.commit()
        conn.close()

    def clear_file_index_for_path(self, path: str):
        """Remove index rows for a given file path (functions, classes, imports, exports)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM function_index WHERE file_path = ?', (path,))
        cursor.execute('DELETE FROM class_index WHERE file_path = ?', (path,))
        cursor.execute('DELETE FROM import_index WHERE file_path = ?', (path,))
        cursor.execute('DELETE FROM export_index WHERE file_path = ?', (path,))
        cursor.execute('DELETE FROM file_index WHERE path = ?', (path,))

        conn.commit()
        conn.close()

    def bulk_upsert_functions(self, functions: Dict[str, dict]):
        """Bulk upsert into function_index from a mapping id -> metadata dict."""
        if not functions:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        rows = []
        for fid, meta in functions.items():
            rows.append(
                (
                    fid,
                    meta.get('file', ''),
                    meta.get('name', ''),
                    meta.get('language', None),
                    meta.get('line_start', None),
                    meta.get('line_end', None),
                    meta.get('complexity', None),
                    json.dumps(meta.get('calls', [])),
                    json.dumps({k: v for k, v in meta.items()
                                if k not in {'id', 'file', 'name', 'language', 'line_start', 'line_end', 'complexity', 'calls'}}),
                )
            )

        cursor.executemany(
            '''INSERT OR REPLACE INTO function_index
               (id, file_path, name, language, line_start, line_end, complexity, calls_json, extras_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            rows,
        )
        conn.commit()
        conn.close()

    def bulk_upsert_classes(self, classes: Dict[str, dict]):
        """Bulk upsert into class_index from a mapping id -> metadata dict."""
        if not classes:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        rows = []
        for cid, meta in classes.items():
            rows.append(
                (
                    cid,
                    meta.get('file', ''),
                    meta.get('name', ''),
                    meta.get('language', None),
                    json.dumps(meta.get('bases', [])),
                    json.dumps({k: v for k, v in meta.items()
                                if k not in {'id', 'file', 'name', 'language', 'bases'}}),
                )
            )

        cursor.executemany(
            '''INSERT OR REPLACE INTO class_index
               (id, file_path, name, language, bases_json, extras_json)
               VALUES (?, ?, ?, ?, ?, ?)''',
            rows,
        )
        conn.commit()
        conn.close()

    def bulk_upsert_imports(self, file_path: str, imports: Dict[str, dict]):
        """Replace import_index rows for a file with the given mapping module -> meta."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM import_index WHERE file_path = ?', (file_path,))

        rows = []
        for mod, meta in imports.items():
            rows.append((file_path, mod, int(meta.get('count', 0))))

        if rows:
            cursor.executemany(
                'INSERT INTO import_index (file_path, module, count) VALUES (?, ?, ?)',
                rows,
            )

        conn.commit()
        conn.close()

    def bulk_upsert_exports(self, file_path: str, exports: Dict[str, dict]):
        """Replace export_index rows for a file with the given mapping symbol -> meta."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM export_index WHERE file_path = ?', (file_path,))

        rows = []
        for sym, meta in exports.items():
            rows.append((file_path, sym, meta.get('kind', None)))

        if rows:
            cursor.executemany(
                'INSERT INTO export_index (file_path, symbol, kind) VALUES (?, ?, ?)',
                rows,
            )

        conn.commit()
        conn.close()

    # Manifest helpers

    def get_manifest_entry(self, path: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT path, language, last_modified, hash, last_indexed_at FROM index_manifest WHERE path = ?', (path,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            'path': row[0],
            'language': row[1],
            'last_modified': row[2],
            'hash': row[3],
            'last_indexed_at': row[4],
        }

    def iter_manifest_paths(self):
        """Return a list of all paths currently tracked in the manifest."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM index_manifest')
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def upsert_manifest_entry(self, path: str, language: str, last_modified: float,
                              hash_value: str, last_indexed_at: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT OR REPLACE INTO index_manifest
               (path, language, last_modified, hash, last_indexed_at)
               VALUES (?, ?, ?, ?, ?)''',
            (path, language, last_modified, hash_value, last_indexed_at),
        )
        conn.commit()
        conn.close()

    def delete_manifest_entry(self, path: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM index_manifest WHERE path = ?', (path,))
        conn.commit()
        conn.close()

    # Search helpers -----------------------------------------------------

    def search_symbols(self, query: str, limit: int = 50) -> list:
        """Search functions, classes and files by name/path.

        Returns a list of dicts with keys: kind, name, file, language,
        line_start, line_end.
        """
        q = f"%{query.lower()}%"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = []

        # Functions
        cursor.execute(
            '''SELECT 'function' as kind, name, file_path, language, line_start, line_end
               FROM function_index
               WHERE lower(name) LIKE ?
               LIMIT ?''',
            (q, limit),
        )
        for kind, name, file_path, language, line_start, line_end in cursor.fetchall():
            results.append({
                'kind': kind,
                'name': name,
                'file': file_path,
                'language': language,
                'line_start': line_start,
                'line_end': line_end,
            })

        # Classes (append until limit, if needed)
        remaining = max(0, limit - len(results))
        if remaining:
            cursor.execute(
                '''SELECT 'class' as kind, name, file_path, language, NULL, NULL
                   FROM class_index
                   WHERE lower(name) LIKE ?
                   LIMIT ?''',
                (q, remaining),
            )
            for kind, name, file_path, language, line_start, line_end in cursor.fetchall():
                results.append({
                    'kind': kind,
                    'name': name,
                    'file': file_path,
                    'language': language,
                    'line_start': line_start,
                    'line_end': line_end,
                })

        # Files (by filename)
        remaining = max(0, limit - len(results))
        if remaining:
            cursor.execute(
                '''SELECT 'file' as kind, path, path, language, NULL, NULL
                   FROM file_index
                   WHERE lower(path) LIKE ?
                   LIMIT ?''',
                (q, remaining),
            )
            for kind, name, file_path, language, line_start, line_end in cursor.fetchall():
                results.append({
                    'kind': kind,
                    'name': name,
                    'file': file_path,
                    'language': language,
                    'line_start': line_start,
                    'line_end': line_end,
                })

        conn.close()
        return results
