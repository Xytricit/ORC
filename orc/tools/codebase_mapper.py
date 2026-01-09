"""
Advanced Codebase Mapper for efficiently navigating and understanding large codebases.

Handles 500k+ LOC efficiently using:
- Database indexes
- Query optimization
- Smart caching with TTL
- Hierarchical structure
- Pagination for large result sets
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
import time
import hashlib
import json


class CodebaseMapper:
    """Efficiently map and navigate large codebases"""
    
    def __init__(self, db_path: Path, cache_ttl: int = 300):
        """
        Initialize mapper with performance optimizations.
        
        Args:
            db_path: Path to SQLite database
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.db_path = db_path
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = cache_ttl
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Generate cache key from method name and arguments"""
        args_str = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(f"{method_name}:{args_str}".encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached result if still valid"""
        if cache_key not in self._cache:
            return None
        
        # Check if cache expired
        if time.time() - self._cache_timestamps[cache_key] > self._cache_ttl:
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
            return None
        
        return self._cache[cache_key]
    
    def _set_cached(self, cache_key: str, value: Any):
        """Store value in cache with timestamp"""
        self._cache[cache_key] = value
        self._cache_timestamps[cache_key] = time.time()
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get optimized database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Set connection-level optimizations
        conn.execute('PRAGMA temp_store=MEMORY')
        conn.execute('PRAGMA cache_size=-10000')  # 10MB cache per connection
        
        return conn
    
    def get_codebase_map(self, depth: int = 2) -> Dict[str, Any]:
        """
        Get hierarchical map of codebase structure.
        
        Args:
            depth: How deep to go in directory tree (1-3 recommended)
        
        Returns:
            Hierarchical structure with stats at each level
        """
        # Check cache first
        cache_key = self._get_cache_key('get_codebase_map', depth=depth)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all files grouped by directory
        cursor.execute("""
            SELECT 
                path,
                language,
                loc
            FROM file_index
            ORDER BY path
        """)
        
        files = cursor.fetchall()
        
        # Build hierarchical structure
        structure = {}
        for file in files:
            path_parts = Path(file['path']).parts
            
            # Navigate/create hierarchy
            current = structure
            for i, part in enumerate(path_parts[:-1]):
                if i >= depth:
                    break
                    
                if part not in current:
                    current[part] = {
                        '_stats': {'files': 0, 'loc': 0, 'functions': 0, 'classes': 0},
                        '_subdirs': {}
                    }
                
                # Update stats
                current[part]['_stats']['files'] += 1
                current[part]['_stats']['loc'] += file['loc'] or 0
                
                current = current[part]['_subdirs']
            
            # Add file to leaf
            filename = path_parts[-1]
            current[filename] = {
                'type': 'file',
                'language': file['language'],
                'loc': file['loc']
            }
        
        conn.close()
        
        # Cache the result
        self._set_cached(cache_key, structure)
        return structure
    
    def get_hotspots(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """
        Find codebase hotspots - areas needing attention.
        
        Returns:
            Dict with complexity_hotspots, large_files, dense_dependencies
        """
        # Check cache first
        cache_key = self._get_cache_key('get_hotspots', limit=limit)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Import filter utility
        from orc.utils.module_filter import should_ignore
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Complexity hotspots
        cursor.execute("""
            SELECT 
                file_path,
                COUNT(*) as complex_functions,
                AVG(complexity) as avg_complexity,
                MAX(complexity) as max_complexity
            FROM function_index
            WHERE complexity >= 10
            GROUP BY file_path
            ORDER BY complex_functions DESC, avg_complexity DESC
            LIMIT ?
        """, (limit * 3,))  # Get more, then filter
        
        complexity_hotspots = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            if not should_ignore(row_dict['file_path']):
                complexity_hotspots.append(row_dict)
                if len(complexity_hotspots) >= limit:
                    break
        
        # Large files
        cursor.execute("""
            SELECT path, language, loc
            FROM file_index
            WHERE loc > 300
            ORDER BY loc DESC
            LIMIT ?
        """, (limit * 3,))  # Get more, then filter
        
        large_files = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            if not should_ignore(row_dict['path']):
                large_files.append(row_dict)
                if len(large_files) >= limit:
                    break
        
        # Most imported modules (coupling hotspots)
        cursor.execute("""
            SELECT 
                module,
                COUNT(DISTINCT file_path) as imported_by_count
            FROM import_index
            GROUP BY module
            HAVING imported_by_count > 5
            ORDER BY imported_by_count DESC
            LIMIT ?
        """, (limit * 2,))  # Get more, then filter
        
        coupling_hotspots = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # Filter module names that look like they're from ignored paths
            if not any(ignored in row_dict['module'] for ignored in ['.venv', 'site-packages', 'node_modules']):
                coupling_hotspots.append(row_dict)
                if len(coupling_hotspots) >= limit:
                    break
        
        conn.close()
        
        result = {
            'complexity_hotspots': complexity_hotspots,
            'large_files': large_files,
            'coupling_hotspots': coupling_hotspots
        }
        
        # Cache the result
        self._set_cached(cache_key, result)
        return result
    
    def get_module_overview(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive overview of a specific module/file.
        
        Returns:
            Functions, classes, imports, exports, callers, callees
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # File info
        cursor.execute("SELECT * FROM file_index WHERE path = ?", (file_path,))
        file_info = dict(cursor.fetchone() or {})
        
        # Functions
        cursor.execute("""
            SELECT name, complexity
            FROM function_index
            WHERE file_path = ?
        """, (file_path,))
        functions = [dict(row) for row in cursor.fetchall()]
        
        # Classes
        cursor.execute("""
            SELECT name
            FROM class_index
            WHERE file_path = ?
        """, (file_path,))
        classes = [dict(row) for row in cursor.fetchall()]
        
        # Imports
        cursor.execute("""
            SELECT module
            FROM import_index
            WHERE file_path = ?
        """, (file_path,))
        imports = [{'module': row['module']} for row in cursor.fetchall()]
        
        # Exports
        cursor.execute("""
            SELECT symbol, kind
            FROM export_index
            WHERE file_path = ?
        """, (file_path,))
        exports = [dict(row) for row in cursor.fetchall()]
        
        # Who imports this file (simplified - just count for now)
        file_module = Path(file_path).stem
        imported_by = []  # Simplified for compatibility
        
        conn.close()
        
        return {
            'file': file_info,
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'exports': exports,
            'imported_by': imported_by
        }
    
    def search_similar_code(self, function_name: str, limit: int = 10) -> List[Dict]:
        """
        Find functions with similar names or complexity patterns.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the target function first
        cursor.execute("""
            SELECT complexity
            FROM function_index
            WHERE name = ?
            LIMIT 1
        """, (function_name,))
        
        target = cursor.fetchone()
        if not target:
            conn.close()
            return []
        
        target_complexity = target['complexity']
        
        # Find similar functions
        cursor.execute("""
            SELECT 
                name,
                file_path,
                line_start,
                complexity,
                ABS(complexity - ?) as complexity_diff
            FROM function_index
            WHERE name != ?
            AND complexity BETWEEN ? AND ?
            ORDER BY complexity_diff, name
            LIMIT ?
        """, (target_complexity, function_name, 
              max(1, target_complexity - 3), 
              target_complexity + 3,
              limit))
        
        similar = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return similar
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive codebase statistics efficiently"""
        # Check cache first
        cache_key = self._get_cache_key('get_statistics')
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # File stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_files,
                SUM(loc) as total_loc,
                AVG(loc) as avg_loc_per_file
            FROM file_index
        """)
        file_stats = dict(cursor.fetchone())
        
        # Get function and class counts separately
        cursor.execute("SELECT COUNT(*) as total_functions FROM function_index")
        file_stats['total_functions'] = cursor.fetchone()['total_functions']
        
        cursor.execute("SELECT COUNT(*) as total_classes FROM class_index")
        file_stats['total_classes'] = cursor.fetchone()['total_classes']
        
        # Language breakdown
        cursor.execute("""
            SELECT 
                language,
                COUNT(*) as files,
                SUM(loc) as loc
            FROM file_index
            GROUP BY language
            ORDER BY loc DESC
        """)
        languages = [dict(row) for row in cursor.fetchall()]
        
        # Complexity stats
        cursor.execute("""
            SELECT 
                AVG(complexity) as avg_complexity,
                MAX(complexity) as max_complexity,
                COUNT(CASE WHEN complexity > 10 THEN 1 END) as high_complexity_count
            FROM function_index
        """)
        complexity_stats = dict(cursor.fetchone())
        
        conn.close()
        
        stats = {
            **file_stats,
            'languages': languages,
            'complexity': complexity_stats
        }
        
        # Cache the result
        self._set_cached(cache_key, stats)
        return stats
    
    def get_functions_paginated(
        self, 
        page: int = 1, 
        page_size: int = 100,
        min_complexity: int = 0,
        file_pattern: str = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of functions for large codebases.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of results per page
            min_complexity: Minimum complexity filter
            file_pattern: Filter by file path pattern
        
        Returns:
            Dict with functions, total_count, page, page_size, total_pages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        where_clauses = []
        params = []
        
        if min_complexity > 0:
            where_clauses.append("complexity >= ?")
            params.append(min_complexity)
        
        if file_pattern:
            where_clauses.append("file_path LIKE ?")
            params.append(f"%{file_pattern}%")
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM function_index {where_sql}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        # Get paginated results
        query = f"""
            SELECT name, file_path, line_start, line_end, complexity
            FROM function_index
            {where_sql}
            ORDER BY complexity DESC, name
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [page_size, offset])
        functions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'functions': functions,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    def get_files_paginated(
        self,
        page: int = 1,
        page_size: int = 100,
        language: str = None,
        min_loc: int = 0
    ) -> Dict[str, Any]:
        """
        Get paginated list of files for large codebases.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of results per page
            language: Filter by language
            min_loc: Minimum lines of code
        
        Returns:
            Dict with files, total_count, page, page_size, total_pages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        where_clauses = []
        params = []
        
        if language:
            where_clauses.append("language = ?")
            params.append(language)
        
        if min_loc > 0:
            where_clauses.append("loc >= ?")
            params.append(min_loc)
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM file_index {where_sql}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Calculate pagination
        total_pages = (total_count + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        # Get paginated results
        query = f"""
            SELECT path, language, loc
            FROM file_index
            {where_sql}
            ORDER BY loc DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [page_size, offset])
        files = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'files': files,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    def stream_large_query(
        self,
        query: str,
        params: tuple = (),
        batch_size: int = 1000
    ):
        """
        Stream results from large queries in batches to avoid memory issues.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            batch_size: Number of rows to fetch at a time
        
        Yields:
            Batches of rows as list of dicts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield [dict(row) for row in rows]
        
        conn.close()
    
    def get_dependency_graph_data(
        self,
        max_nodes: int = 500,
        min_connections: int = 2
    ) -> Dict[str, Any]:
        """
        Get dependency graph data optimized for visualization.
        Limits nodes and edges for performance on large codebases.
        
        Args:
            max_nodes: Maximum number of nodes to include
            min_connections: Minimum connections for a module to be included
        
        Returns:
            Dict with nodes and edges for graph visualization
        """
        cache_key = self._get_cache_key(
            'get_dependency_graph_data',
            max_nodes=max_nodes,
            min_connections=min_connections
        )
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get most connected modules
        cursor.execute("""
            SELECT 
                module,
                COUNT(DISTINCT file_path) as connection_count
            FROM import_index
            GROUP BY module
            HAVING connection_count >= ?
            ORDER BY connection_count DESC
            LIMIT ?
        """, (min_connections, max_nodes))
        
        top_modules = [row['module'] for row in cursor.fetchall()]
        
        # Build nodes
        nodes = []
        for module in top_modules:
            cursor.execute("""
                SELECT COUNT(DISTINCT file_path) as importers
                FROM import_index
                WHERE module = ?
            """, (module,))
            
            importers = cursor.fetchone()['importers']
            nodes.append({
                'id': module,
                'label': module,
                'size': importers,
                'connections': importers
            })
        
        # Build edges (who imports whom)
        edges = []
        for module in top_modules:
            cursor.execute("""
                SELECT DISTINCT file_path
                FROM import_index
                WHERE module = ?
            """, (module,))
            
            importers = [row['file_path'] for row in cursor.fetchall()]
            
            for importer in importers[:50]:  # Limit edges per node
                # Convert file path to module name
                importer_module = importer.replace('/', '.').replace('\\', '.').replace('.py', '')
                if importer_module in top_modules:
                    edges.append({
                        'source': importer_module,
                        'target': module,
                        'type': 'imports'
                    })
        
        conn.close()
        
        result = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'max_nodes_limit': max_nodes,
                'min_connections_filter': min_connections
            }
        }
        
        self._set_cached(cache_key, result)
        return result
