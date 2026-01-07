"""
ORC Scripts: Database Migration Utilities
"""
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple

def run_migration(db_path: str = ".orc/index.db"):
    """Run database migrations"""
    print(f"Running migrations on database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Check current schema version
        current_version = get_schema_version(conn)
        print(f"Current schema version: {current_version}")
        
        # Apply migrations sequentially
        migrations = get_migrations()
        for version, description, migration_func in migrations:
            if version > current_version:
                print(f"Applying migration {version}: {description}")
                migration_func(conn)
                update_schema_version(conn, version)
                print(f"Migration {version} completed")
    
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("All migrations completed successfully!")

def get_schema_version(conn) -> int:
    """Get the current schema version from the database"""
    try:
        # Check if version table exists
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        
        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        # Table doesn't exist, return version 0
        return 0

def update_schema_version(conn, version: int):
    """Update the schema version in the database"""
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
    conn.commit()

def get_migrations() -> List[Tuple[int, str, callable]]:
    """Get list of available migrations"""
    return [
        (1, "Initial schema", create_initial_schema),
        (2, "Add analysis results table", add_analysis_results_table),
        (3, "Add hash column to modules", add_hash_column_to_modules),
    ]

def create_initial_schema(conn):
    """Create the initial database schema"""
    cursor = conn.cursor()
    
    # Create modules table
    cursor.execute("""
        CREATE TABLE modules (
            path TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            last_modified REAL,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create graphs table
    cursor.execute("""
        CREATE TABLE graphs (
            id INTEGER PRIMARY KEY,
            graph_type TEXT NOT NULL,
            data BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()

def add_analysis_results_table(conn):
    """Add analysis results table"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE analysis_results (
            id INTEGER PRIMARY KEY,
            result_type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()

def add_hash_column_to_modules(conn):
    """Add hash column to modules table"""
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(modules)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'hash' not in columns:
        cursor.execute("ALTER TABLE modules ADD COLUMN hash TEXT")
    
    conn.commit()

def rollback_migration(db_path: str, to_version: int):
    """Rollback migrations to a specific version"""
    print(f"Rolling back migrations to version {to_version}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        current_version = get_schema_version(conn)
        
        if to_version >= current_version:
            print("Target version is not less than current version")
            return
        
        # For now, we'll just print what would be done
        # In a real system, you'd have rollback functions for each migration
        print(f"Would rollback from version {current_version} to {to_version}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else ".orc/index.db"
    run_migration(db_path)