"""
ORC Storage: SQLite Graph Database
"""
import sqlite3
import json
import pickle
from pathlib import Path
from typing import Dict, Tuple

try:
    from core.indexer import ModuleInfo
except ImportError:
    from orc.core.indexer import ModuleInfo

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

        # ============================================
        # NEW TABLES FOR ENHANCED CODE INTELLIGENCE
        # ============================================
        
        # File-to-file dependencies (who imports who)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_dependencies (
                source_file TEXT NOT NULL,
                target_file TEXT NOT NULL,
                import_statement TEXT,
                line_number INTEGER,
                import_type TEXT
            )
        ''')
        
        # Resolved function calls (with file paths, not just names)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS function_calls_resolved (
                caller_function_id TEXT NOT NULL,
                caller_file TEXT NOT NULL,
                caller_line INTEGER,
                callee_function_name TEXT NOT NULL,
                callee_function_id TEXT,
                callee_file TEXT,
                is_resolved BOOLEAN DEFAULT 0,
                is_external BOOLEAN DEFAULT 0,
                call_type TEXT
            )
        ''')
        
        # Entry points detection (where code starts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_points (
                file_path TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                function_name TEXT,
                line_number INTEGER,
                confidence REAL DEFAULT 1.0
            )
        ''')
        
        # AI-generated code summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_summaries (
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                summary_short TEXT,
                summary_detailed TEXT,
                purpose TEXT,
                inputs TEXT,
                outputs TEXT,
                side_effects TEXT,
                business_rules TEXT,
                complexity_explanation TEXT,
                edge_cases TEXT,
                assumptions TEXT,
                ai_model TEXT,
                confidence REAL DEFAULT 1.0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER,
                code_hash TEXT,
                needs_refresh BOOLEAN DEFAULT 0,
                PRIMARY KEY (target_type, target_id)
            )
        ''')
        
        # AI insights (code smells, suggestions, warnings)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                severity TEXT,
                suggested_fix TEXT,
                code_example TEXT,
                ai_model TEXT,
                confidence REAL DEFAULT 1.0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ============================================
        # PERFORMANCE INDEXES for large databases
        # ============================================
        
        # Indexes for function_index (most queried table)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_file_path 
            ON function_index(file_path)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_name 
            ON function_index(name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_complexity 
            ON function_index(complexity DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_language 
            ON function_index(language)
        ''')
        
        # Indexes for class_index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_class_file_path 
            ON class_index(file_path)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_class_name 
            ON class_index(name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_class_language 
            ON class_index(language)
        ''')
        
        # Indexes for import_index (for dependency analysis)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_import_file_path 
            ON import_index(file_path)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_import_module 
            ON import_index(module)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_import_composite 
            ON import_index(module, file_path)
        ''')
        
        # Indexes for export_index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_export_file_path 
            ON export_index(file_path)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_export_symbol 
            ON export_index(symbol)
        ''')
        
        # Indexes for file_index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_language 
            ON file_index(language)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_loc 
            ON file_index(loc DESC)
        ''')
        
        # NEW INDEXES for enhanced tables
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_deps_source 
            ON file_dependencies(source_file)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_deps_target 
            ON file_dependencies(target_file)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_calls_caller 
            ON function_calls_resolved(caller_function_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_function_calls_callee 
            ON function_calls_resolved(callee_function_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_summaries_target 
            ON code_summaries(target_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_insights_target 
            ON ai_insights(target_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entry_points_file 
            ON entry_points(file_path)
        ''')
        
        # ============================================
        # PRAGMA optimizations for SQLite performance
        # ============================================
        
        # Use Write-Ahead Logging for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')
        
        # Increase cache size (10MB default -> 50MB for large codebases)
        cursor.execute('PRAGMA cache_size=-51200')  # Negative = KB
        
        # Store temp tables in memory for speed
        cursor.execute('PRAGMA temp_store=MEMORY')
        
        # Synchronous=NORMAL provides good balance of safety and speed
        cursor.execute('PRAGMA synchronous=NORMAL')
        
        # Optimize for read-heavy workloads
        cursor.execute('PRAGMA query_only=OFF')
        
        # Enable memory-mapped I/O for large databases (256MB)
        cursor.execute('PRAGMA mmap_size=268435456')

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
                try:
                    from core.indexer import FunctionInfo
                except ImportError:
                    from orc.core.indexer import FunctionInfo
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
    # ============================================
    # NEW METHODS FOR ENHANCED CODE INTELLIGENCE
    # ============================================
    
    def store_file_dependencies(self, dependencies):
        """Store file-to-file dependencies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dep in dependencies:
            cursor.execute('''
                INSERT INTO file_dependencies 
                (source_file, target_file, import_statement, line_number, import_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                dep.get('source_file'),
                dep.get('target_file'),
                dep.get('import_statement'),
                dep.get('line_number'),
                dep.get('import_type')
            ))
        
        conn.commit()
        conn.close()
    
    def store_resolved_function_calls(self, calls):
        """Store resolved function calls"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for call in calls:
            cursor.execute('''
                INSERT INTO function_calls_resolved 
                (caller_function_id, caller_file, caller_line, callee_function_name,
                 callee_function_id, callee_file, is_resolved, is_external, call_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                call.get('caller_function_id'),
                call.get('caller_file'),
                call.get('caller_line'),
                call.get('callee_function_name'),
                call.get('callee_function_id'),
                call.get('callee_file'),
                call.get('is_resolved', False),
                call.get('is_external', False),
                call.get('call_type', 'direct')
            ))
        
        conn.commit()
        conn.close()
    
    def store_entry_points(self, entry_points):
        """Store detected entry points"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ep in entry_points:
            cursor.execute('''
                INSERT INTO entry_points 
                (file_path, entry_type, function_name, line_number, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ep.get('file_path'),
                ep.get('entry_type'),
                ep.get('function_name'),
                ep.get('line_number'),
                ep.get('confidence', 1.0)
            ))
        
        conn.commit()
        conn.close()
    
    def store_summary(self, target_type, target_id, summary):
        """Store AI-generated code summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO code_summaries 
            (target_type, target_id, summary_short, summary_detailed, purpose,
             inputs, outputs, side_effects, business_rules, complexity_explanation,
             edge_cases, assumptions, ai_model, confidence, tokens_used, code_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            target_type,
            target_id,
            summary.get('summary_short'),
            summary.get('summary_detailed'),
            summary.get('purpose'),
            summary.get('inputs'),
            summary.get('outputs'),
            summary.get('side_effects'),
            summary.get('business_rules'),
            summary.get('complexity_explanation'),
            summary.get('edge_cases'),
            summary.get('assumptions'),
            summary.get('ai_model'),
            summary.get('confidence', 1.0),
            summary.get('tokens_used'),
            summary.get('code_hash')
        ))
        
        conn.commit()
        conn.close()
    
    def get_function_with_summary(self, function_name):
        """Get function details with AI summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                f.name, f.file_path, f.line_start, f.line_end, f.complexity,
                f.calls_json, s.summary_short, s.summary_detailed, s.purpose,
                s.inputs, s.outputs, s.business_rules, s.edge_cases
            FROM function_index f
            LEFT JOIN code_summaries s ON f.id = s.target_id
            WHERE f.name LIKE ?
        ''', (f'%{function_name}%',))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'name': result[0],
            'file_path': result[1],
            'line_start': result[2],
            'line_end': result[3],
            'complexity': result[4],
            'calls': result[5],
            'summary': result[6],
            'details': result[7],
            'purpose': result[8],
            'inputs': result[9],
            'outputs': result[10],
            'business_rules': result[11],
            'edge_cases': result[12]
        }
    
    def get_file_dependencies(self, file_path):
        """Get dependencies for a file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # What this file imports
        cursor.execute('''
            SELECT target_file, import_statement, line_number
            FROM file_dependencies
            WHERE source_file = ?
        ''', (file_path,))
        imports = cursor.fetchall()
        
        # Who imports this file
        cursor.execute('''
            SELECT source_file, import_statement, line_number
            FROM file_dependencies
            WHERE target_file = ?
        ''', (file_path,))
        imported_by = cursor.fetchall()
        
        conn.close()
        
        return {
            'imports': [{'file': i[0], 'statement': i[1], 'line': i[2]} for i in imports],
            'imported_by': [{'file': i[0], 'statement': i[1], 'line': i[2]} for i in imported_by]
        }
    
    def get_entry_points(self):
        """Get all entry points"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, entry_type, function_name, line_number, confidence
            FROM entry_points
            ORDER BY confidence DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'file_path': r[0],
                'entry_type': r[1],
                'function_name': r[2],
                'line_number': r[3],
                'confidence': r[4]
            }
            for r in results
        ]
