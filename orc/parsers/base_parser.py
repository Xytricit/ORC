"""
ORC Base Parser

Abstract base class for all language parsers.
"""

import ast
import re
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for all language parsers.
    
    All parsers must implement parse_file() and return consistent structure.
    
    Enhanced parsers should also implement semantic extraction methods for
    building the complete 22-section knowledge base.
    """
    
    @abstractmethod
    def parse_file(self, path: Path) -> Dict[str, Any]:
        """
        Parse a single file and extract code structure.
        
        Args:
            path: Path to source file
            
        Returns:
            dict with keys:
            
            BASIC STRUCTURE (Existing):
            - 'files': {file_path: {language, loc, file_type, module, purpose}}
            - 'functions': {func_id: {name, line_start, line_end, complexity, 
                                      parameters, calls, code, return_type, raises,
                                      side_effects, is_exported, decorators}}
            - 'classes': {class_id: {name, line_start, line_end, methods, 
                                     base_classes, properties, is_data_model}}
            - 'imports_detailed': [{statement, line, what, is_external, library_name, purpose}]
            - 'exports': {export_id: {name, kind}}
            
            SEMANTIC SECTIONS (New):
            - 'entry_points': {main, api_endpoints, event_listeners, cron_jobs, cli_commands}
            - 'data_models': {model_id: {name, fields, purpose, db_table}}
            - 'state_management': {database_queries, cache_usage, file_operations}
            - 'error_handling': {try_except_blocks, raises}
            - 'configuration': {env_vars, config_keys, feature_flags}
            - 'cross_cutting': {auth_checks, logging, caching, validation}
            - 'side_effects': {external_apis, email_sends, message_queue, background_jobs}
            - 'concurrency': {async_functions, locks, thread_usage}
            - 'security': {sql_injection_risks, xss_risks, secrets}
        """
        pass
    
    # ==================== SEMANTIC EXTRACTION METHODS ====================
    # These methods enable building the complete 22-section knowledge base.
    # Concrete parsers should implement these to extract semantic information.
    # Default implementations return empty structures for backwards compatibility.
    
    def extract_api_endpoints(self, tree: Any, source: str, path: Path) -> List[Dict[str, Any]]:
        """
        Extract API endpoint definitions (routes).
        
        Detects patterns like:
        - Python FastAPI: @app.get("/path"), @app.post("/path")
        - Python Flask: @app.route("/path", methods=["GET"])
        - Python Django: url patterns in urls.py
        - JavaScript Express: app.get('/path', handler)
        - JavaScript Fastify: fastify.get('/path', handler)
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            List of endpoint dicts with keys:
            - route: str (URL pattern like "/users/{id}")
            - method: str (GET, POST, PUT, DELETE, etc.)
            - handler: str (function name)
            - line: int
            - auth_required: bool
            - middleware: List[str]
        """
        return []
    
    def extract_database_queries(self, tree: Any, source: str, path: Path) -> List[Dict[str, Any]]:
        """
        Extract database query patterns.
        
        Detects patterns like:
        - Python SQLAlchemy: User.query.filter_by(...), db.session.add(...)
        - Python Django ORM: User.objects.get(...), User.objects.filter(...)
        - Python Raw SQL: cursor.execute("SELECT ...", params)
        - JavaScript Sequelize: User.findOne({...}), User.create({...})
        - JavaScript TypeORM: repository.find({...})
        - JavaScript Raw SQL: db.query("SELECT ...", [params])
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            List of query dicts with keys:
            - query_type: str (SELECT, INSERT, UPDATE, DELETE, or ORM method)
            - table: str (table/model name)
            - function: str (function making the query)
            - line: int
            - is_parameterized: bool (safe from SQL injection)
            - orm_type: str (sqlalchemy, django, sequelize, typeorm, raw)
        """
        return []
    
    def extract_error_handling(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract error handling patterns.
        
        Detects patterns like:
        - Python: try/except blocks, raise statements
        - JavaScript: try/catch blocks, throw statements
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict with keys:
            - 'try_blocks': List of dicts with:
                - exceptions: List[str] (exception types caught)
                - function: str (containing function)
                - line: int
                - has_recovery: bool (not just re-raise)
            - 'raises': List of dicts with:
                - exception_type: str
                - function: str
                - line: int
                - condition: str (why raised)
        """
        return {'try_blocks': [], 'raises': []}
    
    def extract_config_usage(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract configuration and environment variable usage.
        
        Detects patterns like:
        - Python: os.getenv("KEY"), os.environ["KEY"], config.get("key")
        - JavaScript: process.env.KEY, config.get('key')
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict with keys:
            - 'env_vars': List of dicts with:
                - key: str (env var name)
                - default: Any (default value if provided)
                - used_in: str (function name)
                - line: int
            - 'config_keys': List of dicts with:
                - key: str
                - source: str (config file, .env, etc.)
                - used_in: str
                - line: int
            - 'feature_flags': List of dicts with similar structure
        """
        return {'env_vars': [], 'config_keys': [], 'feature_flags': []}
    
    def extract_side_effects(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract side effects (external interactions).
        
        Detects patterns like:
        - HTTP: requests.get/post, fetch(), axios.get/post
        - Email: smtplib, nodemailer
        - Message Queues: pika (RabbitMQ), redis pub/sub, AWS SQS
        - Background Jobs: celery, bull, rq
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict with keys:
            - 'external_apis': List of dicts with:
                - url: str
                - method: str (GET, POST, etc.)
                - function: str
                - line: int
                - library: str (requests, fetch, axios)
            - 'email_sends': List of dicts
            - 'message_queue': List of dicts
            - 'background_jobs': List of dicts
        """
        return {
            'external_apis': [],
            'email_sends': [],
            'message_queue': [],
            'background_jobs': []
        }
    
    def extract_cross_cutting_concerns(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract cross-cutting concerns (patterns used throughout code).
        
        Detects patterns like:
        - Auth: @login_required, @require_permission, auth checks
        - Logging: logger.info(), console.log(), print()
        - Caching: @cache, redis.get/set
        - Validation: schema validation, input checks
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict with keys:
            - 'auth_checks': List of dicts with:
                - type: str (decorator, conditional)
                - function: str
                - line: int
                - permission: str (if applicable)
            - 'logging': List of dicts with:
                - level: str (info, debug, error, etc.)
                - function: str
                - line: int
            - 'caching': List of dicts
            - 'validation': List of dicts
        """
        return {
            'auth_checks': [],
            'logging': [],
            'caching': [],
            'validation': []
        }
    
    def extract_security_risks(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract potential security risks.
        
        Detects patterns like:
        - SQL Injection: String interpolation in SQL queries
        - XSS: Unescaped user input in HTML
        - Hardcoded Secrets: API keys, passwords in code
        - Weak Crypto: MD5, SHA1 for passwords
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict with keys:
            - 'sql_injection_risks': List of dicts with:
                - query: str
                - function: str
                - line: int
                - risk_level: str (high, medium, low)
                - reason: str
            - 'xss_risks': List of dicts
            - 'secrets': List of dicts with:
                - type: str (api_key, password, token)
                - value: str (partially redacted)
                - line: int
            - 'weak_crypto': List of dicts
        """
        return {
            'sql_injection_risks': [],
            'xss_risks': [],
            'secrets': [],
            'weak_crypto': []
        }
    
    def extract_data_models(self, tree: Any, source: str, path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Extract data model/schema definitions.
        
        Detects patterns like:
        - Python: dataclass, Pydantic models, SQLAlchemy models
        - TypeScript: interfaces, types
        - JSON Schema definitions
        
        Args:
            tree: Parsed AST or source representation
            source: Raw source code string
            path: File path
            
        Returns:
            Dict of model_id -> dict with keys:
            - name: str
            - fields: List of dicts with:
                - name: str
                - type: str
                - required: bool
                - default: Any
                - description: str
            - purpose: str
            - db_table: str (if mapped to database)
            - line: int
        """
        return {}
    
    def extract_concurrency_patterns(self, tree: Any, source: str, path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract concurrency and threading patterns.
        
        Detects patterns like:
        - Async functions (already tracked in functions)
        - Locks: threading.Lock(), asyncio.Lock()
        - Thread creation: threading.Thread(), multiprocessing.Process()
        - Async context managers: async with
        
        Args:
            tree: Parsed AST or source representation
            source: str
            path: File path
            
        Returns:
            Dict with keys:
            - 'locks': List of dicts with:
                - type: str (threading.Lock, asyncio.Lock)
                - resource: str (what's being protected)
                - function: str
                - line: int
            - 'thread_usage': List of dicts
            - 'async_contexts': List of dicts
        """
        return {
            'locks': [],
            'thread_usage': [],
            'async_contexts': []
        }



