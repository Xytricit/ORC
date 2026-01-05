"""
Graph Storage with SQLite Backend
"""
import sqlite3
import json
import pickle
from pathlib import Path
from typing import Dict, Tuple

class GraphStorage:
    """Persist and load graph data"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                path TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_data (
                id INTEGER PRIMARY KEY,
                graph_type TEXT NOT NULL,
                data BLOB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save(self, modules: Dict, graph: 'DependencyGraph'):
        """Save modules and graph to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save modules
        for path, module in modules.items():
            module_json = json.dumps(module, default=lambda o: o.__dict__)
            cursor.execute(
                'INSERT OR REPLACE INTO modules (path, data) VALUES (?, ?)',
                (path, module_json)
            )
        
        # Save graphs
        cursor.execute('DELETE FROM graph_data')
        cursor.execute(
            'INSERT INTO graph_data (graph_type, data) VALUES (?, ?)',
            ('dependency', pickle.dumps(graph))
        )
        
        conn.commit()
        conn.close()
    
    def load(self) -> Tuple[Dict, 'DependencyGraph']:
        """Load modules and graph from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load modules
        cursor.execute('SELECT path, data FROM modules')
        modules = {}
        for path, data in cursor.fetchall():
            modules[path] = json.loads(data)
        
        # Load graph
        cursor.execute('SELECT data FROM graph_data WHERE graph_type = ?', ('dependency',))
        row = cursor.fetchone()
        graph = pickle.loads(row[0]) if row else None
        
        conn.close()
        return modules, graph
