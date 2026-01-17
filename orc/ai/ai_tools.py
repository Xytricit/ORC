"""
ORC AI Tools

Tool definitions for AI function calling.
Allows AI to query the codebase database.

Author: ORC Team
Date: 2026-01-14
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ORCTools:
    """
    Tools for AI to query and analyze codebase.
    """
    
    def __init__(self, db):
        """
        Initialize tools with database connection.
        
        Args:
            db: GraphDB instance
        """
        self.db = db
    
    # Tool 1: Query Functions
    def query_functions(self, pattern: str = '%', limit: int = 50) -> List[Dict]:
        """
        Search for functions by name pattern.
        
        Args:
            pattern: SQL LIKE pattern (use % as wildcard)
            limit: Maximum results
        
        Returns:
            list: Function records
        """
        try:
            return self.db.query_functions(pattern=pattern, limit=limit)
        except Exception as e:
            logger.error(f"query_functions failed: {e}")
            return []
    
    # Tool 2: Get Complex Functions
    def get_complex_functions(self, min_complexity: int = 10, limit: int = 20) -> List[Dict]:
        """
        Find functions with high cyclomatic complexity.
        
        Args:
            min_complexity: Minimum complexity threshold
            limit: Maximum results
        
        Returns:
            list: Complex function records
        """
        try:
            return self.db.get_complex_functions(threshold=min_complexity, limit=limit)
        except Exception as e:
            logger.error(f"get_complex_functions failed: {e}")
            return []
    
    # Tool 3: Get Large Functions
    def get_large_functions(self, min_lines: int = 200, limit: int = 20) -> List[Dict]:
        """
        Find functions with many lines of code.
        
        Args:
            min_lines: Minimum line count
            limit: Maximum results
        
        Returns:
            list: Large function records
        """
        try:
            return self.db.get_large_functions(threshold=min_lines, limit=limit)
        except Exception as e:
            logger.error(f"get_large_functions failed: {e}")
            return []
    
    # Tool 4: Get File Dependencies
    def get_file_dependencies(self, file_path: str) -> Dict:
        """
        Get dependencies for a specific file.
        
        Args:
            file_path: Path to file
        
        Returns:
            dict: Dependencies (imports, exports, depends_on, depended_by)
        """
        try:
            return self.db.get_file_dependencies(file_path)
        except Exception as e:
            logger.error(f"get_file_dependencies failed: {e}")
            return {}
    
    # Tool 5: Find Circular Dependencies
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependency cycles.
        
        Returns:
            list: List of cycles (each cycle is a list of file paths)
        """
        try:
            return self.db.find_circular_dependencies()
        except Exception as e:
            logger.error(f"find_circular_dependencies failed: {e}")
            return []
    
    # Tool 6: Get Function Calls
    def get_function_calls(self, function_name: str) -> Dict:
        """
        Get what functions this function calls and what calls it.
        
        Args:
            function_name: Name of function
        
        Returns:
            dict: Call graph (calls, called_by)
        """
        try:
            return self.db.get_function_call_graph(function_name)
        except Exception as e:
            logger.error(f"get_function_calls failed: {e}")
            return {}
    
    # Tool 7: Get All Files
    def get_all_files(self, language: Optional[str] = None) -> List[Dict]:
        """
        Get all indexed files.
        
        Args:
            language: Filter by language (None = all)
        
        Returns:
            list: File records
        """
        try:
            return self.db.get_all_files(language=language)
        except Exception as e:
            logger.error(f"get_all_files failed: {e}")
            return []
    
    # Tool 8: Get Classes
    def get_classes(self, pattern: str = '%') -> List[Dict]:
        """
        Search for classes by name pattern.
        
        Args:
            pattern: SQL LIKE pattern
        
        Returns:
            list: Class records
        """
        try:
            return self.db.get_all_classes(name_pattern=pattern)
        except Exception as e:
            logger.error(f"get_classes failed: {e}")
            return []
    
    # Tool 9: Get Entry Points
    def get_entry_points(self) -> List[Dict]:
        """
        Get application entry points.
        
        Returns:
            list: Entry point records
        """
        try:
            return self.db.get_entry_points()
        except Exception as e:
            logger.error(f"get_entry_points failed: {e}")
            return []
    
    # Tool 10: Get Function by Name
    def get_function_by_name(self, name: str, file_path: Optional[str] = None) -> Optional[Dict]:
        """
        Get specific function details.
        
        Args:
            name: Function name
            file_path: Optional file path filter
        
        Returns:
            dict: Function record or None
        """
        try:
            funcs = self.query_functions(pattern=name, limit=1)
            if funcs:
                return funcs[0]
            return None
        except Exception as e:
            logger.error(f"get_function_by_name failed: {e}")
            return None
    
    # Tool 11: Get Statistics
    def get_statistics(self) -> Dict:
        """
        Get codebase statistics.
        
        Returns:
            dict: Stats (file_count, function_count, class_count, etc.)
        """
        try:
            files = self.get_all_files()
            functions = self.query_functions()
            classes = self.get_classes()
            
            return {
                'total_files': len(files),
                'total_functions': len(functions),
                'total_classes': len(classes),
                'languages': list(set(f.get('language', '') for f in files)),
                'avg_complexity': sum(f.get('complexity', 0) for f in functions) / len(functions) if functions else 0,
            }
        except Exception as e:
            logger.error(f"get_statistics failed: {e}")
            return {}


# Tool definitions for AI (OpenAI function calling format)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_functions",
            "description": "Search for functions by name pattern. Use % as wildcard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "SQL LIKE pattern (e.g., 'calculate%' or '%handler%')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_complex_functions",
            "description": "Find functions with high cyclomatic complexity (code that's hard to understand).",
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
                        "description": "Maximum results",
                        "default": 20
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_large_functions",
            "description": "Find functions with many lines of code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_lines": {
                        "type": "integer",
                        "description": "Minimum line count",
                        "default": 200
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 20
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_dependencies",
            "description": "Get import/export dependencies for a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_circular_dependencies",
            "description": "Find circular dependency cycles in the codebase.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_function_calls",
            "description": "Get call graph for a function (what it calls and what calls it).",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of function"
                    }
                },
                "required": ["function_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_files",
            "description": "Get list of all indexed files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Filter by language (e.g., 'python', 'javascript')",
                        "enum": ["python", "javascript", "typescript"]
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_classes",
            "description": "Search for classes by name pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "SQL LIKE pattern",
                        "default": "%"
                    }
                },
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_entry_points",
            "description": "Get application entry points (main functions, if __name__ == '__main__', etc.).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistics",
            "description": "Get overall codebase statistics (file count, function count, average complexity, etc.).",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]


def get_tools_for_ai() -> List[Dict]:
    """
    Get tool definitions for AI function calling.
    
    Returns:
        list: Tool definitions in OpenAI format
    """
    return TOOL_DEFINITIONS


def execute_tool(tool_name: str, arguments: Dict, tools_instance: ORCTools) -> Any:
    """
    Execute a tool by name.
    
    Args:
        tool_name: Name of tool to execute
        arguments: Tool arguments
        tools_instance: ORCTools instance
    
    Returns:
        Tool execution result
    """
    if not hasattr(tools_instance, tool_name):
        return f"Error: Tool '{tool_name}' not found"
    
    try:
        method = getattr(tools_instance, tool_name)
        result = method(**arguments)
        return result
    except Exception as e:
        logger.error(f"Tool execution failed: {tool_name}({arguments}) - {e}")
        return f"Error executing {tool_name}: {str(e)}"
