"""
ORC Phase 6: Table of Contents (TOC) Generator
================================================

Generates a searchable index of the entire knowledge database for fast navigation.

WHY TOC IS NEEDED:
- 19-table database becomes HUGE for large codebases
- AI needs fast keyword-based navigation (not full scans)
- TOC acts as master index to 22 sections of knowledge
- Enables instant lookups instead of scanning millions of rows

ARCHITECTURE:
- Database = Encyclopedia (19 volumes)
- TOC = Master index to find topics instantly
- AI uses TOC to jump to relevant sections

Usage:
    from orc.storage.graph_db import GraphDB
    from orc.core.toc_generator import TOCGenerator
    
    db = GraphDB('orc.db')
    toc_gen = TOCGenerator(db)
    toc = toc_gen.generate_toc()
    toc_gen.save_toc(Path('.orc/toc.json'))
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TOCGenerator:
    """
    Generates Table of Contents from ORC knowledge database.
    
    Provides fast keyword-based navigation for AI queries.
    """
    
    def __init__(self, db):
        """
        Initialize TOC generator with database connection.
        
        Args:
            db: GraphDB instance
        """
        self.db = db
        self._toc_cache: Optional[Dict[str, Any]] = None
    
    def generate_toc(self) -> Dict[str, Any]:
        """
        Generate complete TOC from database.
        
        Returns:
            {
                'sections': {
                    'files': {'count': 100, 'languages': [...]},
                    'functions': {'count': 500, 'top_complex': [...]},
                    'classes': {'count': 50, 'names': [...]},
                    'api_endpoints': {'count': 20, 'routes': {...}},
                    'database_queries': {'count': 30, 'tables': [...]},
                    'error_handlers': {'count': 15, 'types': [...]},
                    'config_usage': {'count': 25, 'keys': [...]},
                    'side_effects': {'count': 10, 'targets': [...]},
                    'cross_cutting': {'count': 20, 'types': [...]},
                    'security_risks': {'count': 5, 'high_priority': [...]},
                    'data_models': {'count': 15, 'names': [...]},
                    'concurrency': {'count': 8, 'patterns': [...]},
                },
                'keywords': {
                    'user': ['functions.get_user', 'api_endpoints./users', 'classes.User'],
                    'payment': ['functions.process_payment', 'security_risks.stripe_call'],
                    'auth': ['functions.login', 'cross_cutting.login_required']
                },
                'statistics': {
                    'total_files': 100,
                    'total_functions': 500,
                    'total_lines': 15000,
                    'avg_complexity': 7.2,
                    'languages': ['python', 'javascript']
                }
            }
        """
        logger.info("Generating TOC from database...")
        
        toc = {
            'sections': {},
            'keywords': {},
            'statistics': {}
        }
        
        # Generate all section summaries
        toc['sections']['files'] = self._summarize_files()
        toc['sections']['functions'] = self._summarize_functions()
        toc['sections']['classes'] = self._summarize_classes()
        toc['sections']['api_endpoints'] = self._summarize_api_endpoints()
        toc['sections']['database_queries'] = self._summarize_database_queries()
        toc['sections']['error_handlers'] = self._summarize_error_handlers()
        toc['sections']['config_usage'] = self._summarize_config_usage()
        toc['sections']['side_effects'] = self._summarize_side_effects()
        toc['sections']['cross_cutting'] = self._summarize_cross_cutting()
        toc['sections']['security_risks'] = self._summarize_security_risks()
        toc['sections']['data_models'] = self._summarize_data_models()
        toc['sections']['concurrency'] = self._summarize_concurrency()
        
        # Generate keyword index
        toc['keywords'] = self.build_keyword_index()
        
        # Generate statistics
        toc['statistics'] = self._generate_statistics()
        
        # Cache the TOC
        self._toc_cache = toc
        
        logger.info(f"TOC generated: {toc['statistics']['total_files']} files, "
                   f"{toc['statistics']['total_functions']} functions, "
                   f"{len(toc['keywords'])} keywords")
        
        return toc
    
    def _summarize_files(self) -> Dict[str, Any]:
        """Summarize file_index table."""
        cursor = self.db.conn.cursor()
        
        # Get count and languages
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT language) FROM file_index")
        total, lang_count = cursor.fetchone()
        
        cursor.execute("SELECT DISTINCT language FROM file_index")
        languages = [row[0] for row in cursor.fetchall()]
        
        # Get total LOC
        cursor.execute("SELECT SUM(loc) FROM file_index")
        total_loc = cursor.fetchone()[0] or 0
        
        return {
            'count': total,
            'languages': languages,
            'language_count': lang_count,
            'total_loc': total_loc
        }
    
    def _summarize_functions(self) -> Dict[str, Any]:
        """Summarize function_index table."""
        cursor = self.db.conn.cursor()
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM function_index")
        total = cursor.fetchone()[0]
        
        # Get top 10 complex functions
        cursor.execute("""
            SELECT name, file, complexity, line_start 
            FROM function_index 
            ORDER BY complexity DESC 
            LIMIT 10
        """)
        top_complex = [
            {'name': row[0], 'file': row[1], 'complexity': row[2], 'line': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Get entry points
        cursor.execute("""
            SELECT name, file, line_start
            FROM function_index 
            WHERE name IN ('main', '__main__', 'run', 'start', 'app', 'serve')
        """)
        entry_points = [
            {'name': row[0], 'file': row[1], 'line': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get average complexity
        cursor.execute("SELECT AVG(complexity) FROM function_index")
        avg_complexity = cursor.fetchone()[0] or 0
        
        return {
            'count': total,
            'top_complex': top_complex,
            'entry_points': entry_points,
            'avg_complexity': round(avg_complexity, 2)
        }
    
    def _summarize_classes(self) -> Dict[str, Any]:
        """Summarize class_index table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM class_index")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT name, file, line_start FROM class_index ORDER BY name")
        all_classes = [
            {'name': row[0], 'file': row[1], 'line': row[2]}
            for row in cursor.fetchall()
        ]
        
        return {
            'count': total,
            'names': [c['name'] for c in all_classes],
            'details': all_classes
        }
    
    def _summarize_api_endpoints(self) -> Dict[str, Any]:
        """Summarize api_endpoints table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM api_endpoints")
        total = cursor.fetchone()[0]
        
        # Group routes by path
        cursor.execute("""
            SELECT route, method, handler, file, line 
            FROM api_endpoints 
            ORDER BY route, method
        """)
        
        routes = {}
        all_endpoints = []
        for row in cursor.fetchall():
            route, method, handler, file, line = row
            if route not in routes:
                routes[route] = []
            routes[route].append(method)
            all_endpoints.append({
                'route': route,
                'method': method,
                'handler': handler,
                'file': file,
                'line': line
            })
        
        return {
            'count': total,
            'routes': routes,
            'details': all_endpoints
        }
    
    def _summarize_database_queries(self) -> Dict[str, Any]:
        """Summarize database_queries table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM database_queries")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT table_name FROM database_queries WHERE table_name IS NOT NULL")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT orm_type FROM database_queries")
        orm_types = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'tables': tables,
            'orm_types': orm_types
        }
    
    def _summarize_error_handlers(self) -> Dict[str, Any]:
        """Summarize error_handlers table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM error_handlers")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT handler_type FROM error_handlers")
        types = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'handler_types': types
        }
    
    def _summarize_config_usage(self) -> Dict[str, Any]:
        """Summarize config_usage table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM config_usage")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT config_key, config_type, file, line FROM config_usage ORDER BY config_key")
        all_config = [
            {'key': row[0], 'type': row[1], 'file': row[2], 'line': row[3]}
            for row in cursor.fetchall()
        ]
        
        return {
            'count': total,
            'keys': [c['key'] for c in all_config],
            'details': all_config
        }
    
    def _summarize_side_effects(self) -> Dict[str, Any]:
        """Summarize side_effects table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM side_effects")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT target FROM side_effects WHERE target IS NOT NULL")
        targets = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT effect_type FROM side_effects")
        types = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'targets': targets,
            'types': types
        }
    
    def _summarize_cross_cutting(self) -> Dict[str, Any]:
        """Summarize cross_cutting_concerns table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cross_cutting_concerns")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT concern_type FROM cross_cutting_concerns")
        types = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'concern_types': types
        }
    
    def _summarize_security_risks(self) -> Dict[str, Any]:
        """Summarize security_risks table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM security_risks")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT risk_type, risk_level, reason, file, line 
            FROM security_risks 
            WHERE risk_level = 'high' 
            ORDER BY file, line
        """)
        high_priority = [
            {'type': row[0], 'level': row[1], 'reason': row[2], 'file': row[3], 'line': row[4]}
            for row in cursor.fetchall()
        ]
        
        cursor.execute("SELECT DISTINCT risk_type FROM security_risks")
        types = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'high_priority': high_priority,
            'risk_types': types
        }
    
    def _summarize_data_models(self) -> Dict[str, Any]:
        """Summarize data_models table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM data_models")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT model_name, model_type, file, line FROM data_models ORDER BY model_name")
        all_models = [
            {'name': row[0], 'type': row[1], 'file': row[2], 'line': row[3]}
            for row in cursor.fetchall()
        ]
        
        return {
            'count': total,
            'names': [m['name'] for m in all_models],
            'details': all_models
        }
    
    def _summarize_concurrency(self) -> Dict[str, Any]:
        """Summarize concurrency_patterns table."""
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM concurrency_patterns")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT pattern_type FROM concurrency_patterns")
        patterns = [row[0] for row in cursor.fetchall()]
        
        return {
            'count': total,
            'pattern_types': patterns
        }
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Generate overall statistics."""
        cursor = self.db.conn.cursor()
        
        # File count
        cursor.execute("SELECT COUNT(*) FROM file_index")
        total_files = cursor.fetchone()[0]
        
        # Function count
        cursor.execute("SELECT COUNT(*) FROM function_index")
        total_functions = cursor.fetchone()[0]
        
        # Class count
        cursor.execute("SELECT COUNT(*) FROM class_index")
        total_classes = cursor.fetchone()[0]
        
        # Total LOC
        cursor.execute("SELECT SUM(loc) FROM file_index")
        total_lines = cursor.fetchone()[0] or 0
        
        # Average complexity
        cursor.execute("SELECT AVG(complexity) FROM function_index")
        avg_complexity = cursor.fetchone()[0] or 0
        
        # Languages
        cursor.execute("SELECT DISTINCT language FROM file_index")
        languages = [row[0] for row in cursor.fetchall()]
        
        return {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_lines': total_lines,
            'avg_complexity': round(avg_complexity, 2),
            'languages': languages
        }
    
    def build_keyword_index(self) -> Dict[str, List[str]]:
        """
        Build keyword -> location mapping for fast search.
        
        Extracts keywords from:
        - Function names (split on underscore, camelCase)
        - API routes (/users -> 'users')
        - Config keys (DATABASE_URL -> 'database', 'url')
        - Class names
        - Table names
        
        Returns:
            {
                'user': ['functions.get_user', 'api_endpoints./users', 'classes.User'],
                'payment': ['functions.process_payment'],
                'auth': ['functions.login', 'cross_cutting.login_required']
            }
        """
        keyword_map: Dict[str, List[str]] = {}
        
        def add_keyword(keyword: str, location: str):
            """Add keyword -> location mapping."""
            keyword = keyword.lower()
            if len(keyword) < 3:  # Skip very short keywords
                return
            if keyword not in keyword_map:
                keyword_map[keyword] = []
            if location not in keyword_map[keyword]:
                keyword_map[keyword].append(location)
        
        def extract_keywords(text: str) -> List[str]:
            """Extract keywords from text (split on underscore, camelCase)."""
            # Split on underscore
            parts = text.split('_')
            keywords = []
            
            for part in parts:
                # Split camelCase
                camel_parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)', part)
                if camel_parts:
                    keywords.extend(camel_parts)
                else:
                    keywords.append(part)
            
            return [k.lower() for k in keywords if len(k) >= 3]
        
        cursor = self.db.conn.cursor()
        
        # Index functions
        cursor.execute("SELECT name, file, line_start FROM function_index")
        for row in cursor.fetchall():
            name, file, line = row
            location = f"functions.{name}@{file}:{line}"
            for keyword in extract_keywords(name):
                add_keyword(keyword, location)
        
        # Index classes
        cursor.execute("SELECT name, file, line_start FROM class_index")
        for row in cursor.fetchall():
            name, file, line = row
            location = f"classes.{name}@{file}:{line}"
            for keyword in extract_keywords(name):
                add_keyword(keyword, location)
        
        # Index API endpoints
        cursor.execute("SELECT route, method, handler, file, line FROM api_endpoints")
        for row in cursor.fetchall():
            route, method, handler, file, line = row
            location = f"api_endpoints.{method}:{route}@{file}:{line}"
            # Extract from route: /users/profile -> 'users', 'profile'
            route_parts = [p for p in route.split('/') if p]
            for part in route_parts:
                add_keyword(part, location)
        
        # Index config keys
        cursor.execute("SELECT config_key, file, line FROM config_usage")
        for row in cursor.fetchall():
            key, file, line = row
            location = f"config.{key}@{file}:{line}"
            for keyword in extract_keywords(key):
                add_keyword(keyword, location)
        
        # Index database tables
        cursor.execute("SELECT DISTINCT table_name, file FROM database_queries WHERE table_name IS NOT NULL")
        for row in cursor.fetchall():
            table, file = row
            location = f"database_queries.{table}@{file}"
            for keyword in extract_keywords(table):
                add_keyword(keyword, location)
        
        # Index security risks
        cursor.execute("SELECT risk_type, file, line FROM security_risks")
        for row in cursor.fetchall():
            risk_type, file, line = row
            location = f"security_risks.{risk_type}@{file}:{line}"
            for keyword in extract_keywords(risk_type):
                add_keyword(keyword, location)
        
        logger.debug(f"Built keyword index: {len(keyword_map)} keywords")
        return keyword_map
    
    def get_section_summary(self, section: str) -> Dict[str, Any]:
        """
        Get summary of a specific section.
        
        Args:
            section: Section name (e.g., 'functions', 'api_endpoints')
        
        Returns:
            Section summary dict or empty dict if not found
        """
        if self._toc_cache and section in self._toc_cache.get('sections', {}):
            return self._toc_cache['sections'][section]
        
        # Generate TOC if not cached
        if not self._toc_cache:
            self.generate_toc()
        
        return self._toc_cache.get('sections', {}).get(section, {})
    
    def search_toc(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search TOC by keyword, return matching locations.
        
        Args:
            keyword: Search keyword
        
        Returns:
            List of location dicts:
            [
                {'type': 'function', 'name': 'get_user', 'file': 'api.py', 'line': 42},
                {'type': 'api_endpoint', 'route': '/users', 'file': 'routes.py', 'line': 10}
            ]
        """
        if not self._toc_cache:
            self.generate_toc()
        
        keyword = keyword.lower()
        keywords = self._toc_cache.get('keywords', {})
        
        if keyword not in keywords:
            return []
        
        locations = keywords[keyword]
        results = []
        
        for loc in locations:
            # Parse location string: "type.name@file:line"
            parts = loc.split('@')
            type_name = parts[0]
            file_line = parts[1] if len(parts) > 1 else ''
            
            type_part, name = type_name.split('.', 1)
            
            file = ''
            line = 0
            if ':' in file_line:
                file, line_str = file_line.rsplit(':', 1)
                try:
                    line = int(line_str)
                except ValueError:
                    pass
            
            results.append({
                'type': type_part,
                'name': name,
                'file': file,
                'line': line,
                'location': loc
            })
        
        return results
    
    def save_toc(self, path: Path) -> None:
        """
        Save TOC to JSON file for fast loading.
        
        Args:
            path: Path to save TOC (e.g., Path('.orc/toc.json'))
        """
        if not self._toc_cache:
            self.generate_toc()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._toc_cache, f, indent=2)
        
        logger.info(f"TOC saved to {path}")
    
    def load_toc(self, path: Path) -> Dict[str, Any]:
        """
        Load pre-generated TOC from file.
        
        Args:
            path: Path to TOC file
        
        Returns:
            TOC dict
        """
        if not path.exists():
            raise FileNotFoundError(f"TOC file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self._toc_cache = json.load(f)
        
        logger.info(f"TOC loaded from {path}")
        return self._toc_cache


# ==================== STANDALONE TEST ====================

if __name__ == '__main__':
    """
    Test TOC generation with sample database.
    
    Run: python -m orc.core.toc_generator
    """
    import sys
    import tempfile
    from orc.storage.graph_db import GraphDB
    
    print("Testing TOC Generator...")
    print("=" * 70)
    
    # Create test database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = GraphDB(db_path)
        
        # Populate with test data
        print("\n1. Populating test database...")
        db.store_file('api.py', 'python', 100)
        db.store_file('models.py', 'python', 50)
        
        db.store_function('api.py:get_user', 'get_user', 'api.py', 10, 20, 5, 'def get_user():\n    pass', '', '', True)
        db.store_function('api.py:process_payment', 'process_payment', 'api.py', 30, 50, 15, 'def process_payment():\n    pass', '', '', True)
        
        db.store_class('models.py:User', 'User', 'models.py', 5, 15, 'save,delete', '')
        
        # Add semantic data
        db.store_api_endpoints([
            {'route': '/users', 'method': 'GET', 'handler': 'get_user', 'line': 10}
        ], 'api.py')
        
        db.store_config_usage({
            'env_vars': [{'key': 'DATABASE_URL', 'default': None, 'line': 1}]
        }, 'api.py')
        
        db.store_security_risks({
            'sql_injection_risks': [
                {'risk_level': 'high', 'reason': 'f-string in SQL', 'line': 40, 'query': 'SELECT * FROM users WHERE id = {user_id}'}
            ]
        }, 'api.py')
        
        print("   [OK] Test data populated")
        
        # Generate TOC
        print("\n2. Generating TOC...")
        toc_gen = TOCGenerator(db)
        toc = toc_gen.generate_toc()
        print(f"   [OK] TOC generated")
        
        # Verify sections
        print("\n3. Verifying sections...")
        assert 'sections' in toc
        assert 'keywords' in toc
        assert 'statistics' in toc
        assert toc['statistics']['total_files'] == 2
        assert toc['statistics']['total_functions'] == 2
        assert toc['statistics']['total_classes'] == 1
        print(f"   [OK] All sections present")
        
        # Test keyword search
        print("\n4. Testing keyword search...")
        results = toc_gen.search_toc('user')
        assert len(results) > 0
        print(f"   [OK] Found {len(results)} results for 'user'")
        
        # Test save/load
        print("\n5. Testing save/load...")
        toc_path = Path(tempfile.gettempdir()) / 'test_toc.json'
        toc_gen.save_toc(toc_path)
        assert toc_path.exists()
        
        loaded_toc = toc_gen.load_toc(toc_path)
        assert loaded_toc['statistics']['total_files'] == 2
        print(f"   [OK] TOC saved and loaded successfully")
        
        # Cleanup
        toc_path.unlink()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nTOC Generator is ready for integration!")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
