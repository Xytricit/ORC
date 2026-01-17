"""
ORC Parsers Module

Language parsers for Python, JavaScript, TypeScript, and more.
"""

from orc.parsers.all_parsers import BaseParser, PythonParser, JavaScriptParser, TypeScriptParser

# Parser registry
PARSERS = {
    '.py': PythonParser,
    '.js': JavaScriptParser,
    '.jsx': JavaScriptParser,
    '.ts': TypeScriptParser,
    '.tsx': TypeScriptParser,
    '.mjs': JavaScriptParser,
}


def get_parser(file_path):
    """
    Get appropriate parser for file.
    
    Args:
        file_path: Path object or string
    
    Returns:
        Parser instance or None
    """
    from pathlib import Path
    
    path = Path(file_path)
    ext = path.suffix
    
    parser_class = PARSERS.get(ext)
    if parser_class:
        return parser_class()
    return None


def register_parser(extension, parser_class):
    """
    Register custom parser for file extension.
    
    Args:
        extension: File extension (e.g., '.py')
        parser_class: Parser class (subclass of BaseParser)
    """
    PARSERS[extension] = parser_class


__all__ = [
    'BaseParser',
    'PythonParser',
    'JavaScriptParser',
    'TypeScriptParser',
    'PARSERS',
    'get_parser',
    'register_parser',
]
