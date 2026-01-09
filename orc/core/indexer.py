"""
ORC Core: Python Code Indexer using AST, plus a multi-language indexer
for the v2 "context compression" pipeline.
"""
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from parsers import (
        PythonParser as V2PythonParser,
        JavaScriptParser,
        TypeScriptParser,
        ReactParser,
        HTMLCSSParser,
        DjangoParser,
        FastAPIParser,
        TailwindParser,
        SCSSParser,
        SASSParser,
        LESSParser,
        MarkdownParser,
        JSONParser,
        YAMLParser,
    )
except ImportError:
    from orc.parsers import (
        PythonParser as V2PythonParser,
        JavaScriptParser,
        TypeScriptParser,
        ReactParser,
        HTMLCSSParser,
        DjangoParser,
        FastAPIParser,
        TailwindParser,
        SCSSParser,
        SASSParser,
        LESSParser,
        MarkdownParser,
        JSONParser,
        YAMLParser,
    )
from orc.storage.cache import Cache


@dataclass
class FunctionInfo:
    """Information about a function (v1 AST index).

    This structure is used by the original Python-only indexing pipeline
    and the analysis modules in ``orc_package.analysis``.
    """

    name: str                    # Function name
    file_path: str              # File containing function
    line_start: int             # Starting line number
    line_end: int               # Ending line number
    complexity: int             # Cyclomatic complexity
    calls: List[str]            # Functions this calls
    called_by: Set[str]         # Functions that call this
    parameters: List[str]       # Parameter names
    is_exported: bool           # Is it exported?
    is_used: bool               # Is it used anywhere?
    docstring: Optional[str]    # Docstring content


@dataclass
class ModuleInfo:
    """Information about a module/file (v1 AST index)."""

    path: str                           # File path
    lines: int                          # Total lines
    imports: List[str]                  # Imported modules
    exports: List[str]                  # Exported symbols
    functions: Dict[str, FunctionInfo]  # Functions in module
    classes: List[str]                  # Class names
    last_modified: float                # Timestamp
    hash: str                           # Content hash


class PythonIndexer:
    """Index Python files using AST (v1 pipeline).

    This remains the primary indexer used by the legacy CLI commands and
    tests under ``orc/tests/test_indexer.py``.
    """

    def __init__(self, config: 'ORCConfig'):
        self.config = config
        self.modules: Dict[str, ModuleInfo] = {}
        # Cache is shared across runs to avoid re-parsing unchanged files.
        # It is safe to construct here because it only touches the
        # filesystem under ``config.cache_path``.
        self._cache = Cache(config.cache_path)

    def index_file(self, file_path: Path) -> Optional[ModuleInfo]:
        """Parse and index a single Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            module = ModuleInfo(
                path=str(file_path),
                lines=len(content.splitlines()),
                imports=[],
                exports=[],
                functions={},
                classes=[],
                last_modified=file_path.stat().st_mtime,
                hash=hashlib.md5(content.encode()).hexdigest(),
            )

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    module.imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module.imports.append(node.module)

            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function(node, str(file_path))
                    module.functions[func_info.name] = func_info
                    # Mark as exported if not private
                    if not node.name.startswith('_'):
                        module.exports.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_function(node, str(file_path))
                    module.functions[func_info.name] = func_info
                    if not node.name.startswith('_'):
                        module.exports.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    module.classes.append(node.name)
                    if not node.name.startswith('_'):
                        module.exports.append(node.name)

            return module

        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
            return None

    def _extract_function(self, node: ast.AST, file_path: str) -> FunctionInfo:
        """Extract function information from AST node."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = self._calculate_complexity(node)
            calls = self._extract_calls(node)

            return FunctionInfo(
                name=node.name,
                file_path=file_path,
                line_start=node.lineno,
                line_end=getattr(node, 'end_lineno', node.lineno),
                complexity=complexity,
                calls=calls,
                called_by=set(),
                parameters=[arg.arg for arg in node.args.args],
                is_exported=not node.name.startswith('_'),
                is_used=False,
                docstring=ast.get_docstring(node),
            )
        raise ValueError(f"Node is not a function: {type(node)}")

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Assert, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):  # and/or
                complexity += len(child.values) - 1

        return complexity

    def _extract_calls(self, node: ast.AST) -> List[str]:
        """Extract function calls within a function."""
        calls: List[str] = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)

        return calls

    def index_directory(self, root_path: Path) -> Dict[str, ModuleInfo]:
        """Index all Python files in a directory.

        Respects both the global ``ORCConfig.ignore_patterns`` and any
        project-local patterns defined in ``.orcignore`` at the root.

        This implementation now uses a disk-backed cache to avoid
        re-parsing unchanged files and a small thread pool to parallelise
        AST parsing for cache misses.
        """
        root = Path(root_path)

        # Start with global ignore patterns from config, then extend with
        # any project-specific rules from .orcignore.
        ignore_patterns: List[str] = list(getattr(self.config, 'ignore_patterns', []) or [])
        ignore_patterns.extend(self._read_orcignore(root))

        # First discover candidate Python files.
        candidates: List[Path] = []
        for file_path in root.rglob('*.py'):
            # Skip ignored patterns
            if any(file_path.match(pattern) for pattern in ignore_patterns):
                continue

            # Check file size
            try:
                if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                    continue
            except OSError:
                # If the file disappears between discovery and stat, just
                # skip it gracefully.
                continue

            candidates.append(file_path)

        modules: Dict[str, ModuleInfo] = {}
        to_index: List[Path] = []

        # Phase 1: serve everything we can from cache in the main thread so
        # we do not contend on the cache index file across threads.
        for file_path in candidates:
            cache_key = f"python_index::{file_path}"
            cached = self._cache.get(cache_key)
            if cached is not None:
                modules[str(file_path)] = cached
            else:
                to_index.append(file_path)

        # Phase 2: parallel AST parsing for cache misses.
        if to_index:
            max_workers = max(1, getattr(self.config, 'parallel_workers', 4))

            def _worker(path: Path) -> Optional[ModuleInfo]:
                return self.index_file(path)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_path = {executor.submit(_worker, p): p for p in to_index}
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        module = future.result()
                    except Exception:
                        # Indexing errors are already logged in index_file;
                        # just skip this path.
                        continue

                    if module is not None:
                        modules[str(path)] = module
                        cache_key = f"python_index::{path}"
                        # Cache writes are serialized in the main thread.
                        self._cache.set(cache_key, module, ttl=24 * 3600, source_path=str(path))

        self.modules = modules
        return self.modules

    def _read_orcignore(self, root_path: Path) -> List[str]:
        """Read .orcignore file from ``root_path`` and return glob patterns.

        If the file does not exist, a sensible default one is created so
        that virtual environments and other noise are excluded by default.
        """
        orcignore_path = root_path / '.orcignore'
        ignore_patterns: List[str] = []

        if not orcignore_path.exists():
            # Create a default .orcignore on first run for a project.
            default_lines = [
                "# ORC ignore file - created automatically on first run",
                "# You can edit this to customise what ORC indexes.",
                "",
                ".venv/",
                "venv/",
                "node_modules/",
                "__pycache__/",
                ".git/",
                "dist/",
                "build/",
                ".pytest_cache/",
                ".orc/",
            ]
            try:
                with orcignore_path.open('w', encoding='utf-8') as f:
                    f.write("\n".join(default_lines) + "\n")
            except Exception:
                # Failure to create .orcignore is non-fatal; just continue
                # without project-specific patterns.
                return ignore_patterns

        # At this point the file exists (either pre-existing or created
        # above). Parse it into glob-style patterns usable with Path.match.
        try:
            with orcignore_path.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Treat trailing '/' as a directory pattern
                    if line.endswith('/'):
                        # Match this directory name anywhere in the tree
                        name = line.rstrip('/').lstrip('./')
                        pattern = f"**/{name}/**"
                    else:
                        # Generic glob applied anywhere in the path
                        pattern = f"**/{line}"
                    ignore_patterns.append(pattern)
        except Exception:
            # If something goes wrong reading/parsing, just fall back to
            # the global config-only ignore list.
            return []

        return ignore_patterns


class MultiLanguageIndexer:
    """Index multiple languages using the :mod:`orc.parsers` package.

    This produces the lightweight ``index`` dictionary that the v2
    components (``ContextBuilder``, ``ComplexityAnalyzer``) expect, with
    keys: ``files``, ``functions``, ``classes``, ``imports``,
    ``exports``.
    """

    def __init__(self, config: 'ORCConfig'):
        self.config = config
        self.parsers = {
            '.py': V2PythonParser(),
            '.js': JavaScriptParser(),
            '.ts': TypeScriptParser(),
            '.jsx': ReactParser(),
            '.tsx': ReactParser(),
            '.html': HTMLCSSParser(),
            '.htm': HTMLCSSParser(),
            '.css': HTMLCSSParser(),
            '.json': JSONParser(),
            '.md': MarkdownParser(),
            '.markdown': MarkdownParser(),
            '.yml': YAMLParser(),
            '.yaml': YAMLParser(),
            '.scss': SCSSParser(),
            '.sass': SASSParser(),
            '.less': LESSParser(),
        }
        # Shared cache for all parsed files across languages.
        self._cache = Cache(config.cache_path)

    def index_codebase(self, root_path: Path) -> Dict:
        """Index the entire codebase rooted at ``root_path``.

        Returns a single dictionary aggregating all parser outputs.

        Uses a cache + thread pool so unchanged files are skipped and new
        files are parsed in parallel.
        """
        root = Path(root_path)
        index: Dict[str, Dict] = {
            'files': {},
            'functions': {},
            'classes': {},
            'imports': {},
            'exports': {},
        }

        candidates = list(self._discover_files(root))
        to_index: List[Path] = []

        # Phase 1: read from cache on the main thread.
        for file_path in candidates:
            cache_key = f"ml_index::{file_path}"
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._merge_into_index(index, cached)
            else:
                to_index.append(file_path)

        # Phase 2: parallel parse for cache misses.
        if to_index:
            max_workers = max(1, getattr(self.config, 'parallel_workers', 4))

            def _worker(path: Path) -> Optional[Dict]:
                ext = path.suffix.lower()
                parser = self.parsers.get(ext)
                if not parser:
                    return None
                try:
                    return parser.parse_file(path)
                except Exception as e:  # pragma: no cover - defensive
                    print(f"Error parsing {path}: {e}")
                    return None

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_path = {executor.submit(_worker, p): p for p in to_index}
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                    except Exception:
                        continue

                    if result is not None:
                        self._merge_into_index(index, result)
                        cache_key = f"ml_index::{path}"
                        self._cache.set(cache_key, result, ttl=24 * 3600, source_path=str(path))

        return index

    # ------------------------------------------------------------------

    def _discover_files(self, root: Path) -> List[Path]:
        """Discover candidate source files for all known extensions."""
        # Read .orcignore patterns
        ignore_patterns = list(getattr(self.config, 'ignore_patterns', []) or [])
        ignore_patterns.extend(self._read_orcignore(root))
        
        files: List[Path] = []
        exts = set(self.parsers.keys())
        for ext in exts:
            for file in root.rglob(f'*{ext}'):
                if not self._should_ignore(file, ignore_patterns):
                    # Respect max file size similar to PythonIndexer
                    try:
                        if file.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                            continue
                    except OSError:
                        continue
                    files.append(file)
        return files

    def _should_ignore(self, path: Path, patterns: List[str]) -> bool:
        return any(path.match(pattern) for pattern in patterns)
    
    def _read_orcignore(self, root_path: Path) -> List[str]:
        """Read .orcignore file from root_path and return glob patterns.
        
        Uses the same logic as PythonIndexer for consistency.
        """
        orcignore_path = root_path / '.orcignore'
        ignore_patterns: List[str] = []

        if not orcignore_path.exists():
            return ignore_patterns

        try:
            with orcignore_path.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Treat trailing '/' as a directory pattern
                    if line.endswith('/'):
                        # Match this directory name anywhere in the tree
                        name = line.rstrip('/').lstrip('./')
                        pattern = f"**/{name}/**"
                    else:
                        # Generic glob applied anywhere in the path
                        pattern = f"**/{line}"
                    ignore_patterns.append(pattern)
        except Exception:
            return []

        return ignore_patterns

    def _merge_into_index(self, index: Dict[str, Dict], result: Dict) -> None:
        """Merge a single parser result into the global index."""
        # Files
        for file_id, meta in (result.get('files') or {}).items():
            index['files'][file_id] = meta

        # Functions
        for func_id, meta in (result.get('functions') or {}).items():
            index['functions'][func_id] = meta

        # Classes
        for cls_id, meta in (result.get('classes') or {}).items():
            index['classes'][cls_id] = meta

        # Imports - aggregate counts where possible
        for mod, meta in (result.get('imports') or {}).items():
            existing = index['imports'].get(mod)
            if existing is None:
                index['imports'][mod] = meta
            else:
                if isinstance(meta, dict) and 'count' in meta:
                    existing['count'] = existing.get('count', 0) + meta.get('count', 0)

        # Exports - last write wins (typically harmless)
        for sym, meta in (result.get('exports') or {}).items():
            index['exports'][sym] = meta
