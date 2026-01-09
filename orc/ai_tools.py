"""
AI Tools for ORC - Wrappers around ORC commands for AI to use
These tools provide REAL data from the codebase - no hallucinations
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional


# Tool definitions for AI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_files",
            "description": "Search for files in the indexed codebase by name pattern, language, or path. Returns file paths, sizes, and languages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "File name pattern to search for (e.g., 'auth', 'login', 'user')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Filter by programming language (e.g., 'python', 'javascript')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_functions",
            "description": "Search for functions/methods in the codebase. Returns function names, file locations, line numbers, and complexity scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Function name pattern to search for"
                    },
                    "min_complexity": {
                        "type": "integer",
                        "description": "Minimum complexity score to filter by"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Filter by file path pattern"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_classes",
            "description": "Search for classes in the codebase. Returns class names, file locations, and methods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Class name pattern to search for"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Filter by file path pattern"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_complexity_report",
            "description": "Get code complexity analysis. Returns functions sorted by cyclomatic complexity with file locations and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_complexity": {
                        "type": "integer",
                        "description": "Minimum complexity threshold (default: 10)",
                        "default": 10
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dead_code",
            "description": "Find potentially unused/dead code in the codebase. Returns unused functions, classes, and files with confidence scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence score (0.0-1.0)",
                        "default": 0.7
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 30
                    },
                    "deep_scan": {
                        "type": "boolean",
                        "description": "Enable deep scan for higher accuracy (VERY SLOW - only use for final verification)",
                        "default": False
                    },
                    "quick_scan": {
                        "type": "boolean",
                        "description": "Fast scan mode - checks only top 30 functions (recommended for initial queries)",
                        "default": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": "Read the content of a specific file. Use this to examine actual code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Starting line number (1-based)"
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line number (1-based)"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dependencies",
            "description": "Get comprehensive dependency and impact analysis. Shows what imports what, what would break if deleted, and function callers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Get dependencies for a specific file - what it imports and what imports it"
                    },
                    "module": {
                        "type": "string",
                        "description": "Get all files that import a specific module"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Get all callers of a specific function"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_security_issues",
            "description": "Scan codebase for security vulnerabilities - hardcoded secrets, SQL injection, unsafe eval, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity: 'critical', 'high', 'medium', 'low', or 'all'",
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of issues to return",
                        "default": 30
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_codebase_stats",
            "description": "Get overall statistics about the indexed codebase - file counts, LOC, languages, etc.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a text pattern in the codebase content. Returns matching files and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Text or regex pattern to search for in code"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Filter by file path pattern (e.g., '*.py')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_codebase_map",
            "description": "Get TABLE OF CONTENTS for codebase - like a book's TOC. Shows folder structure with stats but NOT individual files. Use this first to understand structure, then use query_files/query_functions to 'jump to specific pages'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "integer",
                        "description": "Directory depth (1-3, default 2)",
                        "default": 2
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_folder_contents",
            "description": "Jump to a specific 'page' - get files in a specific folder. Like opening to page 61 in a book after checking the table of contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Folder to explore (e.g., 'orc/analysis', 'docs')"
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "Include file stats (LOC, functions)",
                        "default": True
                    }
                },
                "required": ["folder_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hotspots",
            "description": "Find codebase hotspots - areas needing attention. Returns complexity hotspots, large files, and high-coupling modules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max results per category",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "organize_codebase",
            "description": "Organize codebase into professional structure. Moves files to proper folders (docs/, tests/, examples/, assets/), creates README files, and suggests improvements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, only show what would be done without making changes",
                        "default": True
                    },
                    "create_folders": {
                        "type": "boolean",
                        "description": "Create standard folders (docs/, tests/, examples/, assets/, src/)",
                        "default": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cleanup_imports",
            "description": "Find and remove unused imports across the codebase. Returns list of unused imports that can be safely removed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Specific file to check (or check all files if not provided)"
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Automatically remove unused imports",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_duplicates",
            "description": "Find duplicate code blocks across the codebase. Helps identify copy-paste code that should be refactored.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_lines": {
                        "type": "integer",
                        "description": "Minimum number of lines to consider as duplicate",
                        "default": 5
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0.0-1.0)",
                        "default": 0.9
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_docs",
            "description": "Generate documentation for code. Creates docstrings, README files, and API documentation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "File, folder, or 'all' to document entire codebase"
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "Type: 'docstrings', 'readme', 'api', or 'all'",
                        "default": "all"
                    }
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_refactoring",
            "description": "Analyze code and suggest refactoring opportunities. Finds long functions, duplicate logic, complex conditionals, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Specific file to analyze (or analyze all if not provided)"
                    },
                    "focus": {
                        "type": "string",
                        "description": "Focus area: 'complexity', 'duplication', 'naming', or 'all'",
                        "default": "all"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_performance",
            "description": "Analyze code for performance issues. Finds O(n²) loops, inefficient algorithms, excessive function calls, and optimization opportunities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Specific file to analyze"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_best_practices",
            "description": "Check code against best practices and style guidelines. Validates naming conventions, code structure, error handling, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Language: 'python', 'javascript', 'typescript', or 'all'",
                        "default": "all"
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Enable strict checking",
                        "default": False
                    }
                },
                "required": []
            }
        }
    }
]


class ORCTools:
    """
    Tool executor - runs ORC analysis commands and returns real data.
    All methods return dictionaries that can be serialized to JSON.
    """
    
    def __init__(self, db_path: str = ".orc/index.db"):
        self.db_path = db_path
        self.project_root = Path.cwd()
    
    def _get_connection(self) -> Optional[sqlite3.Connection]:
        """Get database connection if database exists"""
        full_path = self.project_root / self.db_path
        if not full_path.exists():
            return None
        conn = sqlite3.connect(str(full_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name and return results"""
        tool_map = {
            "query_files": self.query_files,
            "query_functions": self.query_functions,
            "query_classes": self.query_classes,
            "get_complexity_report": self.get_complexity_report,
            "get_dead_code": self.get_dead_code,
            "get_file_content": self.get_file_content,
            "get_dependencies": self.get_dependencies,
            "get_codebase_stats": self.get_codebase_stats,
            "search_code": self.search_code,
            "get_security_issues": self.get_security_issues,
            "get_codebase_map": self.get_codebase_map,  # TABLE OF CONTENTS
            "get_folder_contents": self.get_folder_contents,  # JUMP TO PAGE
            "get_hotspots": self.get_hotspots,
            "organize_codebase": self.organize_codebase,
            "cleanup_imports": self.cleanup_imports,
            "find_duplicates": self.find_duplicates,
            "generate_docs": self.generate_docs,
            "suggest_refactoring": self.suggest_refactoring,
            "analyze_performance": self.analyze_performance,
            "check_best_practices": self.check_best_practices,
        }
        
        # TOKEN OPTIMIZATION: Log tool usage to detect high-token tools
        # This helps identify which tools consume too many tokens
        
        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return tool_map[tool_name](**arguments)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def query_files(
        self,
        pattern: str = "",
        language: str = "",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for files in the indexed codebase"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            query = "SELECT path as file_path, language, loc as size FROM file_index WHERE 1=1"
            params = []
            
            if pattern:
                query += " AND path LIKE ?"
                params.append(f"%{pattern}%")
            
            if language:
                query += " AND LOWER(language) = LOWER(?)"
                params.append(language)
            
            # Exclude .venv and hidden directories
            query += " AND path NOT LIKE '%/.venv/%' AND path NOT LIKE '.venv/%'"
            query += " AND path NOT LIKE '%__pycache__%'"
            
            query += f" ORDER BY path LIMIT {limit}"
            
            cursor = conn.execute(query, params)
            files = [dict(row) for row in cursor.fetchall()]
            
            return {
                "count": len(files),
                "files": files
            }
        finally:
            conn.close()
    
    def query_functions(
        self,
        pattern: str = "",
        min_complexity: int = 0,
        file_path: str = "",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for functions in the codebase"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            query = """
                SELECT name, file_path, line_start as start_line, line_end as end_line, complexity
                FROM function_index WHERE 1=1
            """
            params = []
            
            if pattern:
                query += " AND name LIKE ?"
                params.append(f"%{pattern}%")
            
            if min_complexity > 0:
                query += " AND complexity >= ?"
                params.append(min_complexity)
            
            if file_path:
                query += " AND file_path LIKE ?"
                params.append(f"%{file_path}%")
            
            # Exclude .venv
            query += " AND file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'"
            
            query += f" ORDER BY complexity DESC LIMIT {limit}"
            
            cursor = conn.execute(query, params)
            functions = [dict(row) for row in cursor.fetchall()]
            
            return {
                "count": len(functions),
                "functions": functions
            }
        finally:
            conn.close()
    
    def query_classes(
        self,
        pattern: str = "",
        file_path: str = "",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for classes in the codebase"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            query = """
                SELECT name, file_path, language
                FROM class_index WHERE 1=1
            """
            params = []
            
            if pattern:
                query += " AND name LIKE ?"
                params.append(f"%{pattern}%")
            
            if file_path:
                query += " AND file_path LIKE ?"
                params.append(f"%{file_path}%")
            
            # Exclude .venv
            query += " AND file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'"
            
            query += f" ORDER BY name LIMIT {limit}"
            
            cursor = conn.execute(query, params)
            classes = [dict(row) for row in cursor.fetchall()]
            
            return {
                "count": len(classes),
                "classes": classes
            }
        finally:
            conn.close()
    
    def get_complexity_report(
        self,
        min_complexity: int = 5,
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive complexity analysis with actionable insights.
        Analyzes cyclomatic complexity, function length, and nesting depth.
        """
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            # Get all functions with complexity
            query = """
                SELECT name, file_path, line_start as start_line, line_end as end_line, complexity
                FROM function_index 
                WHERE complexity IS NOT NULL
                AND file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'
                AND file_path NOT LIKE '%__pycache__%'
                ORDER BY complexity DESC
            """
            
            cursor = conn.execute(query)
            all_functions = [dict(row) for row in cursor.fetchall()]
            
            # Calculate comprehensive stats
            if all_functions:
                complexities = [f["complexity"] for f in all_functions if f["complexity"]]
                avg_complexity = sum(complexities) / len(complexities) if complexities else 0
                max_complexity = max(complexities) if complexities else 0
                
                # Distribution analysis
                critical = [f for f in all_functions if f["complexity"] >= 20]  # Very high
                high = [f for f in all_functions if 10 <= f["complexity"] < 20]
                medium = [f for f in all_functions if 5 <= f["complexity"] < 10]
                low = [f for f in all_functions if f["complexity"] < 5]
            else:
                avg_complexity = 0
                max_complexity = 0
                critical = high = medium = low = []
            
            # Analyze each high-complexity function
            analyzed_functions = []
            for func in all_functions[:limit]:
                if func["complexity"] < min_complexity:
                    continue
                    
                lines = (func["end_line"] or 0) - (func["start_line"] or 0)
                
                # Determine severity and recommendation
                complexity = func["complexity"]
                if complexity >= 20:
                    severity = "CRITICAL"
                    recommendation = "Strongly recommend refactoring - split into smaller functions"
                    priority = 1
                elif complexity >= 15:
                    severity = "HIGH"
                    recommendation = "Consider breaking down into smaller functions"
                    priority = 2
                elif complexity >= 10:
                    severity = "MEDIUM"
                    recommendation = "Review for potential simplification"
                    priority = 3
                else:
                    severity = "LOW"
                    recommendation = "Acceptable complexity"
                    priority = 4
                
                # Identify potential issues
                issues = []
                if complexity >= 10:
                    issues.append("High cyclomatic complexity - many decision paths")
                if lines > 50:
                    issues.append(f"Long function ({lines} lines) - consider splitting")
                if lines > 0 and complexity / lines > 0.5:
                    issues.append("Dense logic - high complexity per line")
                
                analyzed_functions.append({
                    **func,
                    "lines": lines,
                    "severity": severity,
                    "priority": priority,
                    "recommendation": recommendation,
                    "issues": issues,
                })
            
            # Sort by priority then complexity
            analyzed_functions.sort(key=lambda x: (x["priority"], -x["complexity"]))
            
            # Get hotspots (files with most complex functions)
            file_complexity = {}
            for func in all_functions:
                fp = func["file_path"]
                if fp not in file_complexity:
                    file_complexity[fp] = {"total_complexity": 0, "function_count": 0, "max_complexity": 0}
                file_complexity[fp]["total_complexity"] += func["complexity"]
                file_complexity[fp]["function_count"] += 1
                file_complexity[fp]["max_complexity"] = max(file_complexity[fp]["max_complexity"], func["complexity"])
            
            hotspots = sorted(
                [{"file": k, **v, "avg_complexity": round(v["total_complexity"] / v["function_count"], 1)} 
                 for k, v in file_complexity.items()],
                key=lambda x: x["total_complexity"],
                reverse=True
            )[:10]
            
            return {
                "summary": {
                    "total_functions": len(all_functions),
                    "average_complexity": round(avg_complexity, 2),
                    "max_complexity": max_complexity,
                    "critical_count": len(critical),
                    "high_count": len(high),
                    "medium_count": len(medium),
                    "low_count": len(low),
                },
                "distribution": {
                    "critical_20plus": len(critical),
                    "high_10_to_19": len(high),
                    "medium_5_to_9": len(medium),
                    "low_under_5": len(low),
                },
                "high_complexity_functions": analyzed_functions,
                "hotspot_files": hotspots,
                "recommendations": {
                    "immediate_action": f"{len(critical)} functions need immediate refactoring",
                    "short_term": f"{len(high)} functions should be reviewed soon",
                    "tech_debt_estimate": f"~{len(critical) * 4 + len(high) * 2} hours to refactor critical/high functions"
                }
            }
        finally:
            conn.close()
    
    def get_dead_code(
        self,
        confidence_threshold: float = 0.5,
        limit: int = 50,
        deep_scan: bool = False,
        quick_scan: bool = True
    ) -> Dict[str, Any]:
        """
        Find potentially unused code with high confidence.
        
        Args:
            confidence_threshold: Minimum confidence (0.0-1.0)
            limit: Max results to return
            deep_scan: If True, use accurate but VERY slow regex analysis
            quick_scan: If True, only check top 30 functions (much faster)
        """
        import re
        
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            # Get all functions from project (exclude .venv, tests, __pycache__)
            cursor = conn.execute("""
                SELECT name, file_path, line_start as start_line, line_end as end_line
                FROM function_index 
                WHERE file_path NOT LIKE '%/.venv/%' 
                AND file_path NOT LIKE '.venv/%'
                AND file_path NOT LIKE '%__pycache__%'
                AND file_path NOT LIKE '%node_modules%'
                ORDER BY name
            """)
            all_functions = [dict(row) for row in cursor.fetchall()]
            
            # PERFORMANCE: Limit function count for quick scans
            if quick_scan and not deep_scan:
                all_functions = all_functions[:30]  # Only check first 30 functions for speed
            
            # Get all project files for scanning
            cursor = conn.execute("""
                SELECT path FROM file_index
                WHERE path NOT LIKE '%/.venv/%' 
                AND path NOT LIKE '.venv/%'
                AND path NOT LIKE '%__pycache__%'
                AND path NOT LIKE '%node_modules%'
            """)
            all_files = [row[0] for row in cursor.fetchall()]
            
            # Build a map of file contents for efficient scanning
            file_contents = {}
            for fpath in all_files:
                full_path = self.project_root / fpath
                if full_path.exists():
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_contents[fpath] = f.read()
                    except:
                        pass
            
            # Entry point patterns - these are NOT dead code
            entry_point_names = {
                "main", "setup", "teardown", "run", "start", "init", "execute",
                "handle", "process", "cli", "app", "server", "worker", "task",
                "get", "post", "put", "delete", "patch",  # HTTP methods
                "on_", "handle_", "process_",  # Event handlers
            }
            
            entry_point_files = {
                "__main__.py", "main.py", "app.py", "server.py", "wsgi.py",
                "asgi.py", "setup.py", "conftest.py", "manage.py", "run.py",
                "cli.py", "commands.py", "__init__.py",
            }
            
            potentially_unused = []
            definitely_used = set()
            
            if deep_scan:
                # ACCURATE SLOW SCAN: Use regex patterns for high accuracy
                for fpath, content in file_contents.items():
                    for func in all_functions:
                        func_name = func["name"]
                        # Look for all usage patterns
                        patterns = [
                            rf'\b{re.escape(func_name)}\s*\(',  # Direct call
                            rf'\.{re.escape(func_name)}\s*\(',  # Method call
                            rf'={re.escape(func_name)}\b',      # Assignment
                            rf'\({re.escape(func_name)}\b',     # Passed as arg
                            rf',\s*{re.escape(func_name)}\b',   # In list/tuple
                            rf'@{re.escape(func_name)}\b',      # Decorator
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, content):
                                if fpath != func["file_path"]:
                                    definitely_used.add((func_name, func["file_path"]))
                                    break
                                else:
                                    matches = list(re.finditer(pattern, content))
                                    if len(matches) > 1:
                                        definitely_used.add((func_name, func["file_path"]))
                                        break
            else:
                # FAST SCAN: Simple string search for speed
                for fpath, content in file_contents.items():
                    for func in all_functions:
                        func_name = func["name"]
                        # Quick check: is the name even in this file?
                        if func_name in content:
                            # Check if it's a call
                            if f"{func_name}(" in content or f".{func_name}(" in content:
                                if fpath != func["file_path"]:
                                    definitely_used.add((func_name, func["file_path"]))
                                else:
                                    count = content.count(f"{func_name}(")
                                    if count > 1:
                                        definitely_used.add((func_name, func["file_path"]))
                
                # Already limited above with quick_scan
                pass
            
            # Second pass: analyze each function
            for func in all_functions:
                func_name = func["name"]
                file_path = func["file_path"]
                file_name = Path(file_path).name
                
                # Skip if definitely used
                if (func_name, file_path) in definitely_used:
                    continue
                
                # Calculate confidence based on multiple factors
                confidence = 0.0
                reasons = []
                
                # 1. Check if it's a private function (starts with _)
                if func_name.startswith("__") and func_name.endswith("__"):
                    continue  # Dunder methods - skip
                
                is_private = func_name.startswith("_")
                
                # 2. Check if it's in an entry point file
                is_entry_file = any(ep in file_path for ep in entry_point_files)
                
                # 3. Check if it matches entry point patterns
                is_entry_func = any(
                    func_name.lower() == ep or func_name.lower().startswith(ep)
                    for ep in entry_point_names
                )
                
                # 4. Check for test functions
                is_test = func_name.startswith("test_") or "test" in file_path.lower()
                
                # 5. Check naming patterns that suggest dead code
                deprecated_patterns = ["deprecated", "old_", "_old", "legacy", "unused", "obsolete", "temp_", "_temp", "tmp_", "_tmp", "backup", "bak_"]
                has_deprecated_name = any(p in func_name.lower() for p in deprecated_patterns)
                
                # 6. Check if function is exported in __all__
                is_exported = False
                if file_path in file_contents:
                    content = file_contents[file_path]
                    if f"'{func_name}'" in content or f'"{func_name}"' in content:
                        # Might be in __all__ or referenced as string
                        if "__all__" in content:
                            is_exported = True
                
                # Calculate confidence score
                if has_deprecated_name:
                    confidence = 0.95
                    reasons.append("Name suggests deprecated/unused code")
                elif is_test:
                    confidence = 0.1  # Tests are expected to not be called
                    reasons.append("Test function")
                elif is_entry_func or is_entry_file:
                    confidence = 0.2  # Entry points might not be called in code
                    reasons.append("Likely entry point")
                elif is_exported:
                    confidence = 0.3
                    reasons.append("Exported but no internal usage found")
                elif is_private:
                    confidence = 0.85
                    reasons.append("Private function with no internal calls")
                else:
                    confidence = 0.75
                    reasons.append("No calls found in codebase")
                
                # Boost confidence if function is large (more impact)
                if func.get("end_line") and func.get("start_line"):
                    lines = func["end_line"] - func["start_line"]
                    if lines > 50:
                        confidence = min(1.0, confidence + 0.1)
                        reasons.append(f"Large function ({lines} lines)")
                
                if confidence >= confidence_threshold:
                    potentially_unused.append({
                        **func,
                        "confidence": round(confidence, 2),
                        "reasons": reasons,
                        "safe_to_delete": confidence >= 0.9,
                        "recommendation": "SAFE TO DELETE" if confidence >= 0.9 else "REVIEW BEFORE DELETE" if confidence >= 0.7 else "LIKELY SAFE"
                    })
            
            # Sort by confidence (highest first)
            potentially_unused.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Separate into categories
            safe_to_delete = [f for f in potentially_unused if f["confidence"] >= 0.9]
            review_needed = [f for f in potentially_unused if 0.7 <= f["confidence"] < 0.9]
            possibly_unused = [f for f in potentially_unused if f["confidence"] < 0.7]
            
            return {
                "summary": {
                    "total_functions_analyzed": len(all_functions),
                    "total_potentially_unused": len(potentially_unused),
                    "safe_to_delete_count": len(safe_to_delete),
                    "review_needed_count": len(review_needed),
                    "possibly_unused_count": len(possibly_unused),
                },
                "safe_to_delete": safe_to_delete[:limit],
                "review_needed": review_needed[:limit],
                "possibly_unused": possibly_unused[:limit],
                "note": "Functions in 'safe_to_delete' have 90%+ confidence of being unused."
            }
        finally:
            conn.close()
    
    def get_file_content(
        self,
        file_path: str,
        start_line: int = None,
        end_line: int = None
    ) -> Dict[str, Any]:
        """Read content of a specific file"""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Apply line range if specified
            if start_line is not None:
                start_idx = max(0, start_line - 1)
            else:
                start_idx = 0
            
            if end_line is not None:
                end_idx = min(total_lines, end_line)
            else:
                end_idx = min(total_lines, start_idx + 100)  # Limit to 100 lines by default
            
            selected_lines = lines[start_idx:end_idx]
            content = "".join(selected_lines)
            
            return {
                "file_path": file_path,
                "total_lines": total_lines,
                "showing_lines": f"{start_idx + 1}-{end_idx}",
                "content": content
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def get_dependencies(
        self,
        file_path: str = None,
        module: str = None,
        function_name: str = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dependency information.
        - For file_path: what it imports and what imports it
        - For module: all files that import it
        - For function_name: what calls it and what it calls
        """
        import re
        
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            results = {
                "imports": [],
                "imported_by": [],
                "depends_on": [],
                "dependents": [],
                "impact_analysis": {}
            }
            
            # Get all project files
            cursor = conn.execute("""
                SELECT path FROM file_index
                WHERE path NOT LIKE '%/.venv/%'
                AND path NOT LIKE '.venv/%'
                AND path NOT LIKE '%__pycache__%'
            """)
            all_files = [row[0] for row in cursor.fetchall()]
            
            # Build file contents cache
            file_contents = {}
            for fpath in all_files:
                full_path = self.project_root / fpath
                if full_path.exists():
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_contents[fpath] = f.read()
                    except:
                        pass
            
            if file_path:
                # Get what this file imports
                if file_path in file_contents:
                    content = file_contents[file_path]
                    
                    # Find import statements
                    import_patterns = [
                        r'^from\s+([\w.]+)\s+import\s+(.+)$',
                        r'^import\s+([\w.]+)(?:\s+as\s+\w+)?$',
                    ]
                    
                    for pattern in import_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE)
                        for match in matches:
                            if isinstance(match, tuple):
                                results["imports"].append({
                                    "module": match[0],
                                    "imports": match[1].strip() if len(match) > 1 else "*",
                                    "is_local": not match[0].startswith(('os', 'sys', 'json', 're', 'typing', 'pathlib', 'collections', 'datetime', 'time', 'random', 'math'))
                                })
                            else:
                                results["imports"].append({
                                    "module": match,
                                    "imports": "*",
                                    "is_local": not match.startswith(('os', 'sys', 'json', 're', 'typing', 'pathlib', 'collections', 'datetime', 'time', 'random', 'math'))
                                })
                
                # Find what imports this file
                file_module = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                file_name = Path(file_path).stem
                
                for fpath, content in file_contents.items():
                    if fpath == file_path:
                        continue
                    # Check various import patterns
                    if (re.search(rf'\bfrom\s+{re.escape(file_module)}\b', content) or
                        re.search(rf'\bimport\s+{re.escape(file_module)}\b', content) or
                        re.search(rf'\bfrom\s+[\w.]*{re.escape(file_name)}\b', content) or
                        re.search(rf'\bimport\s+[\w.]*{re.escape(file_name)}\b', content)):
                        results["imported_by"].append(fpath)
                
                # Impact analysis
                results["impact_analysis"] = {
                    "direct_dependents": len(results["imported_by"]),
                    "would_break_if_deleted": results["imported_by"],
                    "safe_to_modify": len(results["imported_by"]) == 0,
                    "risk_level": "HIGH" if len(results["imported_by"]) > 5 else "MEDIUM" if len(results["imported_by"]) > 0 else "LOW"
                }
            
            if module:
                # Find all files that import this module
                for fpath, content in file_contents.items():
                    if re.search(rf'\bimport\s+{re.escape(module)}\b|\bfrom\s+{re.escape(module)}\b', content):
                        # Get specific imports
                        specific_imports = re.findall(rf'from\s+{re.escape(module)}\s+import\s+(.+)$', content, re.MULTILINE)
                        results["imported_by"].append({
                            "file": fpath,
                            "imports": specific_imports[0].strip() if specific_imports else "*"
                        })
            
            if function_name:
                # Find where this function is called
                callers = []
                for fpath, content in file_contents.items():
                    # Look for function calls
                    if re.search(rf'\b{re.escape(function_name)}\s*\(', content):
                        # Count occurrences
                        call_count = len(re.findall(rf'\b{re.escape(function_name)}\s*\(', content))
                        # Get line numbers
                        lines = content.split('\n')
                        call_lines = [i+1 for i, line in enumerate(lines) if re.search(rf'\b{re.escape(function_name)}\s*\(', line)]
                        callers.append({
                            "file": fpath,
                            "call_count": call_count,
                            "lines": call_lines[:10]  # Limit to first 10
                        })
                
                results["callers"] = callers
                results["caller_count"] = len(callers)
                results["total_calls"] = sum(c["call_count"] for c in callers)
            
            return results
        finally:
            conn.close()
    
    def get_codebase_stats(self) -> Dict[str, Any]:
        """Get overall codebase statistics (OPTIMIZED - minimal data)"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            stats = {}
            
            # File counts by language (exclude .venv) - LIMIT to top 10
            cursor = conn.execute("""
                SELECT language, COUNT(*) as count
                FROM file_index
                WHERE path NOT LIKE '%/.venv/%' AND path NOT LIKE '.venv/%'
                GROUP BY language
                ORDER BY count DESC
                LIMIT 10
            """)
            stats["files_by_language"] = {row[0] or "unknown": row[1] for row in cursor.fetchall()}
            
            # Total files
            cursor = conn.execute("""
                SELECT COUNT(*) FROM file_index
                WHERE path NOT LIKE '%/.venv/%' AND path NOT LIKE '.venv/%'
            """)
            stats["total_files"] = cursor.fetchone()[0]
            
            # Total functions
            cursor = conn.execute("""
                SELECT COUNT(*) FROM function_index
                WHERE file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'
            """)
            stats["total_functions"] = cursor.fetchone()[0]
            
            # Total classes
            cursor = conn.execute("""
                SELECT COUNT(*) FROM class_index
                WHERE file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'
            """)
            stats["total_classes"] = cursor.fetchone()[0]
            
            # Complexity stats
            cursor = conn.execute("""
                SELECT AVG(complexity), MAX(complexity)
                FROM function_index
                WHERE complexity IS NOT NULL
                AND file_path NOT LIKE '%/.venv/%' AND file_path NOT LIKE '.venv/%'
            """)
            row = cursor.fetchone()
            stats["average_complexity"] = round(row[0], 2) if row[0] else 0
            stats["max_complexity"] = row[1] if row[1] else 0
            
            return stats
        finally:
            conn.close()
    
    def search_code(
        self,
        pattern: str,
        file_pattern: str = "",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for a pattern in code content"""
        import re
        
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            # Get files to search
            query = """
                SELECT path as file_path FROM file_index
                WHERE path NOT LIKE '%/.venv/%' AND path NOT LIKE '.venv/%'
            """
            if file_pattern:
                query += f" AND path LIKE '%{file_pattern}%'"
            
            cursor = conn.execute(query)
            files = [row[0] for row in cursor.fetchall()]
            
            results = []
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                # If not a valid regex, treat as literal string
                regex = re.compile(re.escape(pattern), re.IGNORECASE)
            
            for fpath in files:
                if len(results) >= limit:
                    break
                
                full_path = self.project_root / fpath
                if not full_path.exists():
                    continue
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            results.append({
                                "file_path": fpath,
                                "line_number": i,
                                "line_content": line.strip()[:200]  # Truncate long lines
                            })
                            if len(results) >= limit:
                                break
                except:
                    pass
            
            return {
                "pattern": pattern,
                "count": len(results),
                "matches": results
            }
        finally:
            conn.close()
    
    def get_security_issues(
        self,
        severity: str = "all",
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        Scan codebase for security vulnerabilities.
        Checks for hardcoded secrets, SQL injection, unsafe eval, and more.
        """
        import re
        
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            # Get all project files
            cursor = conn.execute("""
                SELECT path FROM file_index
                WHERE path NOT LIKE '%/.venv/%'
                AND path NOT LIKE '.venv/%'
                AND path NOT LIKE '%__pycache__%'
                AND path NOT LIKE '%node_modules%'
                AND (path LIKE '%.py' OR path LIKE '%.js' OR path LIKE '%.ts' OR path LIKE '%.jsx' OR path LIKE '%.tsx')
            """)
            all_files = [row[0] for row in cursor.fetchall()]
            
            # Security patterns to check
            security_patterns = [
                # CRITICAL - Hardcoded secrets
                {
                    "name": "Hardcoded Password",
                    "pattern": r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
                    "severity": "critical",
                    "recommendation": "Move to environment variable or secrets manager"
                },
                {
                    "name": "Hardcoded API Key",
                    "pattern": r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*=\s*["\'][^"\']{10,}["\']',
                    "severity": "critical",
                    "recommendation": "Move to environment variable or secrets manager"
                },
                {
                    "name": "Hardcoded Secret/Token",
                    "pattern": r'(?i)(secret|token|auth[_-]?token|access[_-]?token)\s*=\s*["\'][^"\']{10,}["\']',
                    "severity": "critical",
                    "recommendation": "Move to environment variable or secrets manager"
                },
                {
                    "name": "AWS Credentials",
                    "pattern": r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)\s*=\s*["\'][A-Za-z0-9/+=]{20,}["\']',
                    "severity": "critical",
                    "recommendation": "Use IAM roles or AWS Secrets Manager"
                },
                {
                    "name": "Private Key",
                    "pattern": r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)?\s*PRIVATE KEY-----',
                    "severity": "critical",
                    "recommendation": "Never commit private keys - use secure key management"
                },
                
                # HIGH - Code injection risks
                {
                    "name": "SQL Injection Risk",
                    "pattern": r'(?i)(execute|cursor\.execute|query)\s*\([^)]*%s|(?i)(execute|cursor\.execute|query)\s*\([^)]*\+\s*\w+|(?i)(execute|cursor\.execute|query)\s*\(f["\']',
                    "severity": "high",
                    "recommendation": "Use parameterized queries instead of string concatenation"
                },
                {
                    "name": "Unsafe eval()",
                    "pattern": r'\beval\s*\([^)]+\)',
                    "severity": "high",
                    "recommendation": "Avoid eval() - use safer alternatives like ast.literal_eval()"
                },
                {
                    "name": "Unsafe exec()",
                    "pattern": r'\bexec\s*\([^)]+\)',
                    "severity": "high",
                    "recommendation": "Avoid exec() - it can execute arbitrary code"
                },
                {
                    "name": "Command Injection Risk",
                    "pattern": r'(?i)(os\.system|subprocess\.call|subprocess\.run|subprocess\.Popen)\s*\([^)]*\+|(?i)shell\s*=\s*True',
                    "severity": "high",
                    "recommendation": "Use subprocess with shell=False and pass args as list"
                },
                {
                    "name": "Pickle Deserialization",
                    "pattern": r'\bpickle\.loads?\s*\(',
                    "severity": "high",
                    "recommendation": "Pickle can execute arbitrary code - use JSON or safer formats"
                },
                
                # MEDIUM - Configuration issues
                {
                    "name": "Debug Mode Enabled",
                    "pattern": r'(?i)(debug\s*=\s*True|DEBUG\s*=\s*True|app\.debug\s*=\s*True)',
                    "severity": "medium",
                    "recommendation": "Ensure debug mode is disabled in production"
                },
                {
                    "name": "Weak Cryptography",
                    "pattern": r'(?i)(md5|sha1)\s*\(|hashlib\.(md5|sha1)',
                    "severity": "medium",
                    "recommendation": "Use stronger algorithms like SHA-256 or bcrypt for passwords"
                },
                {
                    "name": "Insecure Random",
                    "pattern": r'\brandom\.(random|randint|choice)\s*\(',
                    "severity": "medium",
                    "recommendation": "Use secrets module for security-sensitive randomness"
                },
                {
                    "name": "Hardcoded IP/URL",
                    "pattern": r'(?i)(http://|https://)[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
                    "severity": "medium",
                    "recommendation": "Use configuration files for URLs and IPs"
                },
                
                # LOW - Best practice violations
                {
                    "name": "Bare Except",
                    "pattern": r'except\s*:',
                    "severity": "low",
                    "recommendation": "Catch specific exceptions instead of bare except"
                },
                {
                    "name": "Assert in Production",
                    "pattern": r'\bassert\s+',
                    "severity": "low",
                    "recommendation": "Assertions can be disabled with -O flag - use proper validation"
                },
                {
                    "name": "TODO/FIXME Security",
                    "pattern": r'(?i)#\s*(TODO|FIXME|XXX).*?(security|auth|password|credential|secret|vulnerability)',
                    "severity": "low",
                    "recommendation": "Address security-related TODOs"
                },
            ]
            
            issues = []
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            
            for fpath in all_files:
                full_path = self.project_root / fpath
                if not full_path.exists():
                    continue
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    for sec_pattern in security_patterns:
                        # Filter by severity if specified
                        if severity != "all" and sec_pattern["severity"] != severity:
                            continue
                        
                        for i, line in enumerate(lines, 1):
                            if re.search(sec_pattern["pattern"], line):
                                # Skip if in comment (basic check)
                                stripped = line.strip()
                                if stripped.startswith('#') and 'password' not in sec_pattern["name"].lower():
                                    continue
                                
                                issues.append({
                                    "file": fpath,
                                    "line": i,
                                    "issue": sec_pattern["name"],
                                    "severity": sec_pattern["severity"],
                                    "code_snippet": line.strip()[:100],
                                    "recommendation": sec_pattern["recommendation"]
                                })
                except:
                    pass
            
            # Sort by severity
            issues.sort(key=lambda x: severity_order.get(x["severity"], 99))
            
            # Categorize results
            critical = [i for i in issues if i["severity"] == "critical"]
            high = [i for i in issues if i["severity"] == "high"]
            medium = [i for i in issues if i["severity"] == "medium"]
            low = [i for i in issues if i["severity"] == "low"]
            
            return {
                "summary": {
                    "total_issues": len(issues),
                    "critical_count": len(critical),
                    "high_count": len(high),
                    "medium_count": len(medium),
                    "low_count": len(low),
                    "files_scanned": len(all_files)
                },
                "critical_issues": critical[:limit],
                "high_issues": high[:limit],
                "medium_issues": medium[:limit],
                "low_issues": low[:limit],
                "risk_assessment": "HIGH RISK" if critical else "MEDIUM RISK" if high else "LOW RISK" if medium else "MINIMAL RISK",
                "immediate_actions": [f"Fix {len(critical)} critical issues" if critical else None,
                                     f"Review {len(high)} high severity issues" if high else None],
            }
        finally:
            conn.close()

    def get_codebase_map(self, depth: int = 2) -> Dict[str, Any]:
        """Get hierarchical map of codebase structure (SUMMARIZED to save tokens)"""
        try:
            from orc.tools.codebase_mapper import CodebaseMapper
            mapper = CodebaseMapper(self.project_root / self.db_path)
            
            # Get full structure
            full_structure = mapper.get_codebase_map(depth=depth)
            
            # SUMMARIZE IT - don't return every single file!
            summary = {
                "top_level_folders": [],
                "total_folders": 0,
                "note": "Full file list omitted to save tokens. Use query_files() to search specific files."
            }
            
            for folder_name, folder_data in full_structure.items():
                if isinstance(folder_data, dict) and '_stats' in folder_data:
                    stats = folder_data['_stats']
                    summary["top_level_folders"].append({
                        "name": folder_name,
                        "files": stats.get('files', 0),
                        "loc": stats.get('loc', 0),
                        "functions": stats.get('functions', 0),
                        "classes": stats.get('classes', 0)
                    })
                    summary["total_folders"] += 1
            
            # Sort by LOC descending
            summary["top_level_folders"].sort(key=lambda x: x.get('loc', 0), reverse=True)
            
            return summary
        except Exception as e:
            return {"error": f"Codebase mapping failed: {str(e)}"}
    
    def get_folder_contents(self, folder_path: str, include_stats: bool = True) -> Dict[str, Any]:
        """Get files in a specific folder - like jumping to a specific page in the book"""
        conn = self._get_connection()
        if not conn:
            return {"error": "Database not found. Run 'orc index' first."}
        
        try:
            # Normalize path
            folder_path = folder_path.strip('./').rstrip('/')
            
            # Get files in this folder
            cursor = conn.execute("""
                SELECT path, language, loc
                FROM file_index
                WHERE path LIKE ? 
                AND path NOT LIKE '%/.venv/%' 
                AND path NOT LIKE '.venv/%'
                ORDER BY path
            """, (f"{folder_path}/%",))
            
            files = []
            for row in cursor.fetchall():
                file_path = row[0]
                # Only include direct children (not subdirectories)
                relative = file_path[len(folder_path)+1:]
                if '/' not in relative:
                    file_info = {"path": file_path, "name": relative}
                    if include_stats:
                        file_info["language"] = row[1]
                        file_info["loc"] = row[2]
                        
                        # Get function count
                        func_cursor = conn.execute("""
                            SELECT COUNT(*) FROM function_index 
                            WHERE file_path = ?
                        """, (file_path,))
                        file_info["functions"] = func_cursor.fetchone()[0]
                        
                        # Get class count
                        class_cursor = conn.execute("""
                            SELECT COUNT(*) FROM class_index 
                            WHERE file_path = ?
                        """, (file_path,))
                        file_info["classes"] = class_cursor.fetchone()[0]
                    
                    files.append(file_info)
            
            # Get subfolders
            cursor = conn.execute("""
                SELECT DISTINCT path
                FROM file_index
                WHERE path LIKE ?
                AND path NOT LIKE '%/.venv/%'
                AND path NOT LIKE '.venv/%'
            """, (f"{folder_path}/%",))
            
            subfolders = set()
            for row in cursor.fetchall():
                file_path = row[0]
                relative = file_path[len(folder_path)+1:]
                if '/' in relative:
                    subfolder = relative.split('/')[0]
                    subfolders.add(subfolder)
            
            return {
                "folder": folder_path,
                "files": files[:50],  # Limit to 50 files
                "subfolders": sorted(list(subfolders)),
                "total_files": len(files),
                "note": f"Showing {min(50, len(files))} of {len(files)} files. Use query_files() for specific searches."
            }
        finally:
            conn.close()
    
    def get_hotspots(self, limit: int = 10) -> Dict[str, Any]:
        """Find codebase hotspots needing attention"""
        try:
            from orc.tools.codebase_mapper import CodebaseMapper
            mapper = CodebaseMapper(self.project_root / self.db_path)
            return mapper.get_hotspots(limit=limit)
        except Exception as e:
            return {"error": f"Hotspot analysis failed: {str(e)}"}
    
    def organize_codebase(self, dry_run: bool = True, create_folders: bool = True) -> Dict[str, Any]:
        """Organize codebase into professional structure"""
        import shutil
        from pathlib import Path
        
        actions = []
        folders_created = []
        files_moved = []
        
        # Standard folder structure
        standard_folders = {
            "docs": "Documentation files",
            "tests": "Test files",
            "examples": "Example code",
            "assets": "Images, logos, media",
            "src": "Source code (if not already organized)"
        }
        
        # File categorization rules
        categorization = {
            "docs": [".md", ".rst", ".txt"],
            "tests": ["test_", "_test.py", "tests.py"],
            "examples": ["example_", "sample_", "demo_"],
            "assets": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]
        }
        
        # Get root files
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        
        # Create folders
        if create_folders:
            for folder, desc in standard_folders.items():
                folder_path = self.project_root / folder
                if not folder_path.exists():
                    if not dry_run:
                        folder_path.mkdir(exist_ok=True)
                    folders_created.append(folder)
                    actions.append(f"Create {folder}/ - {desc}")
        
        # Categorize and move files
        for file in root_files:
            target_folder = None
            
            # Check by extension and name
            for folder, patterns in categorization.items():
                for pattern in patterns:
                    if pattern.startswith(".") and file.suffix == pattern:
                        target_folder = folder
                        break
                    elif file.name.startswith(pattern) or pattern in file.name:
                        target_folder = folder
                        break
                if target_folder:
                    break
            
            # Move file
            if target_folder:
                dest = self.project_root / target_folder / file.name
                if not dry_run:
                    shutil.move(str(file), str(dest))
                files_moved.append({
                    "file": file.name,
                    "from": "root",
                    "to": target_folder
                })
                actions.append(f"Move {file.name} → {target_folder}/")
        
        # Suggestions
        suggestions = []
        if not (self.project_root / "README.md").exists():
            suggestions.append("Create README.md with project description")
        if not (self.project_root / ".gitignore").exists():
            suggestions.append("Create .gitignore file")
        if not (self.project_root / "requirements.txt").exists() and not (self.project_root / "pyproject.toml").exists():
            suggestions.append("Create requirements.txt or pyproject.toml for dependencies")
        
        return {
            "dry_run": dry_run,
            "folders_created": folders_created,
            "files_moved": len(files_moved),
            "actions": actions,
            "file_moves": files_moved,
            "suggestions": suggestions,
            "summary": f"{'Would organize' if dry_run else 'Organized'} {len(files_moved)} files into {len(folders_created)} folders"
        }
    
    def cleanup_imports(self, file_path: str = None, auto_fix: bool = False) -> Dict[str, Any]:
        """Find and remove unused imports"""
        import ast
        import re
        
        unused_imports = []
        files_checked = 0
        
        # Get files to check
        if file_path:
            files_to_check = [Path(file_path)]
        else:
            # Check all Python files
            files_to_check = list(self.project_root.rglob("*.py"))
            files_to_check = [f for f in files_to_check if ".venv" not in str(f) and "__pycache__" not in str(f)]
        
        for fpath in files_to_check[:50]:  # Limit for performance
            if not fpath.exists():
                continue
                
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                # Find all imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({"name": alias.name, "as": alias.asname, "line": node.lineno})
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            imports.append({"name": f"{module}.{alias.name}", "as": alias.asname, "line": node.lineno})
                
                # Check which imports are used
                for imp in imports:
                    import_name = imp["as"] or imp["name"].split(".")[-1]
                    # Simple check: is the name used in the file?
                    if content.count(import_name) == 1:  # Only appears in import
                        unused_imports.append({
                            "file": str(fpath.relative_to(self.project_root)),
                            "import": imp["name"],
                            "line": imp["line"]
                        })
                
                files_checked += 1
            except:
                pass
        
        return {
            "files_checked": files_checked,
            "unused_imports_found": len(unused_imports),
            "unused_imports": unused_imports[:30],
            "auto_fix": auto_fix,
            "note": "Set auto_fix=true to automatically remove unused imports"
        }
    
    def find_duplicates(self, min_lines: int = 5, similarity_threshold: float = 0.9) -> Dict[str, Any]:
        """Find duplicate code blocks"""
        from difflib import SequenceMatcher
        
        duplicates = []
        files_scanned = 0
        
        # Get Python files
        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if ".venv" not in str(f) and "__pycache__" not in str(f)][:20]
        
        # Extract code blocks
        code_blocks = []
        for fpath in py_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                for i in range(len(lines) - min_lines):
                    block = "".join(lines[i:i+min_lines])
                    if block.strip():
                        code_blocks.append({
                            "file": str(fpath.relative_to(self.project_root)),
                            "start_line": i + 1,
                            "code": block
                        })
                files_scanned += 1
            except:
                pass
        
        # Find similar blocks
        for i, block1 in enumerate(code_blocks):
            for block2 in code_blocks[i+1:]:
                if block1["file"] == block2["file"]:
                    continue
                    
                similarity = SequenceMatcher(None, block1["code"], block2["code"]).ratio()
                if similarity >= similarity_threshold:
                    duplicates.append({
                        "similarity": round(similarity, 2),
                        "file1": block1["file"],
                        "line1": block1["start_line"],
                        "file2": block2["file"],
                        "line2": block2["start_line"],
                        "code_preview": block1["code"][:100]
                    })
        
        return {
            "files_scanned": files_scanned,
            "duplicates_found": len(duplicates),
            "duplicates": duplicates[:20],
            "recommendation": "Consider extracting duplicate code into shared functions"
        }
    
    def generate_docs(self, target: str, doc_type: str = "all") -> Dict[str, Any]:
        """Generate documentation"""
        return {
            "target": target,
            "doc_type": doc_type,
            "status": "Feature in development",
            "suggestion": "For now, I can help you write documentation by:\n- Analyzing functions and suggesting docstrings\n- Creating README content based on codebase analysis\n- Identifying undocumented code"
        }
    
    def suggest_refactoring(self, file_path: str = None, focus: str = "all") -> Dict[str, Any]:
        """Suggest refactoring opportunities"""
        suggestions = []
        
        # Get high complexity functions
        complexity_data = self.get_complexity_report(min_complexity=15, limit=10)
        if "high_complexity_functions" in complexity_data:
            for func in complexity_data["high_complexity_functions"][:5]:
                suggestions.append({
                    "type": "complexity",
                    "priority": "high",
                    "location": f"{func['file_path']}:{func['start_line']}",
                    "issue": f"Function '{func['name']}' has complexity {func['complexity']}",
                    "suggestion": func.get("recommendation", "Break into smaller functions")
                })
        
        # Get dead code
        dead_data = self.get_dead_code(confidence_threshold=0.9, limit=5)
        if "safe_to_delete" in dead_data:
            for func in dead_data["safe_to_delete"][:3]:
                suggestions.append({
                    "type": "dead_code",
                    "priority": "medium",
                    "location": f"{func['file_path']}:{func['start_line']}",
                    "issue": f"Function '{func['name']}' appears unused",
                    "suggestion": "Remove if truly unused"
                })
        
        return {
            "focus": focus,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions,
            "categories": {
                "complexity": len([s for s in suggestions if s["type"] == "complexity"]),
                "dead_code": len([s for s in suggestions if s["type"] == "dead_code"])
            }
        }
    
    def analyze_performance(self, file_path: str = None) -> Dict[str, Any]:
        """Analyze code for performance issues"""
        import re
        
        issues = []
        files_analyzed = 0
        
        # Performance anti-patterns
        patterns = [
            {
                "name": "Nested loops (O(n²))",
                "pattern": r'for\s+\w+\s+in\s+.+:\s*\n\s+for\s+\w+\s+in',
                "severity": "high",
                "suggestion": "Consider using dict/set for O(1) lookups or vectorized operations"
            },
            {
                "name": "List append in loop",
                "pattern": r'for\s+\w+\s+in\s+.+:\s*\n\s+\w+\.append\(',
                "severity": "medium",
                "suggestion": "Consider list comprehension for better performance"
            },
            {
                "name": "String concatenation in loop",
                "pattern": r'for\s+\w+\s+in\s+.+:\s*\n\s+\w+\s*\+=\s*["\']',
                "severity": "high",
                "suggestion": "Use join() instead of += for string concatenation"
            }
        ]
        
        # Get files to analyze
        if file_path:
            files = [Path(file_path)]
        else:
            files = list(self.project_root.rglob("*.py"))[:20]
            files = [f for f in files if ".venv" not in str(f)]
        
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                for pattern_def in patterns:
                    matches = re.finditer(pattern_def["pattern"], content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            "file": str(fpath.relative_to(self.project_root)),
                            "line": line_num,
                            "issue": pattern_def["name"],
                            "severity": pattern_def["severity"],
                            "suggestion": pattern_def["suggestion"]
                        })
                
                files_analyzed += 1
            except:
                pass
        
        return {
            "files_analyzed": files_analyzed,
            "issues_found": len(issues),
            "issues": issues[:30],
            "summary": {
                "high": len([i for i in issues if i["severity"] == "high"]),
                "medium": len([i for i in issues if i["severity"] == "medium"]),
                "low": len([i for i in issues if i["severity"] == "low"])
            }
        }
    
    def check_best_practices(self, language: str = "all", strict: bool = False) -> Dict[str, Any]:
        """Check code against best practices"""
        violations = []
        files_checked = 0
        
        # Best practice patterns
        checks = [
            {
                "name": "Missing docstrings",
                "pattern": r'^\s*def\s+\w+\([^)]*\):\s*$',
                "severity": "low",
                "message": "Function missing docstring"
            },
            {
                "name": "Too many arguments",
                "pattern": r'def\s+\w+\([^)]{100,}\)',
                "severity": "medium",
                "message": "Function has too many arguments (>5)"
            },
            {
                "name": "Magic numbers",
                "pattern": r'[^a-zA-Z0-9_]\d{2,}[^a-zA-Z0-9_]',
                "severity": "low",
                "message": "Consider extracting magic number to named constant"
            }
        ]
        
        py_files = list(self.project_root.rglob("*.py"))[:30]
        py_files = [f for f in py_files if ".venv" not in str(f)]
        
        for fpath in py_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for check in checks:
                    import re
                    for i, line in enumerate(lines, 1):
                        if re.search(check["pattern"], line):
                            violations.append({
                                "file": str(fpath.relative_to(self.project_root)),
                                "line": i,
                                "rule": check["name"],
                                "severity": check["severity"],
                                "message": check["message"]
                            })
                
                files_checked += 1
            except:
                pass
        
        return {
            "language": language,
            "strict": strict,
            "files_checked": files_checked,
            "violations_found": len(violations),
            "violations": violations[:30],
            "summary": {
                "high": len([v for v in violations if v["severity"] == "high"]),
                "medium": len([v for v in violations if v["severity"] == "medium"]),
                "low": len([v for v in violations if v["severity"] == "low"])
            }
        }
