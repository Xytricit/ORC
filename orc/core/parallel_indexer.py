"""
Parallel file indexing for faster performance on large codebases.

Uses multiprocessing to parse multiple files simultaneously.
"""
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from functools import partial


def parse_file_worker(file_path: Path, parser_name: str) -> Dict:
    """Worker function for parallel parsing"""
    try:
        # Import inside worker to avoid pickling issues
        if parser_name == "python":
            from orc.parsers.python_parser import PythonParser
            parser = PythonParser()
        elif parser_name == "javascript":
            from orc.parsers.javascript_parser import JavaScriptParser
            parser = JavaScriptParser()
        elif parser_name == "typescript":
            from orc.parsers.typescript_parser import TypeScriptParser
            parser = TypeScriptParser()
        else:
            return {}
        
        result = parser.parse_file(file_path)
        return result
    except Exception as e:
        # Return error info for debugging
        return {
            "error": str(e),
            "file": str(file_path),
            "files": {str(file_path): {"language": "error", "loc": 0}},
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {}
        }


class ParallelIndexer:
    """Indexes files in parallel for better performance"""
    
    def __init__(self, max_workers: int = None):
        """
        Args:
            max_workers: Number of parallel workers (default: CPU count)
        """
        self.max_workers = max_workers or max(1, multiprocessing.cpu_count() - 1)
    
    def index_files(self, files: List[Path], parser_map: Dict[str, str]) -> Dict:
        """
        Index multiple files in parallel.
        
        Args:
            files: List of file paths to index
            parser_map: Dict mapping file extensions to parser names
                       e.g., {'.py': 'python', '.js': 'javascript'}
        
        Returns:
            Combined index dict with all parsed data
        """
        # Group files by parser type
        files_by_parser = {}
        for file_path in files:
            ext = file_path.suffix.lower()
            parser_name = parser_map.get(ext)
            if parser_name:
                files_by_parser.setdefault(parser_name, []).append(file_path)
        
        # Combined results (including new fields)
        combined = {
            "files": {},
            "functions": {},
            "classes": {},
            "imports": {},
            "exports": {},
            "imports_detailed": [],  # NEW
            "entry_points": []       # NEW
        }
        
        # Process files in parallel
        total_files = sum(len(f) for f in files_by_parser.values())
        processed = 0
        
        for parser_name, file_list in files_by_parser.items():
            # Use ProcessPoolExecutor for true parallelism
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(parse_file_worker, file_path, parser_name): file_path
                    for file_path in file_list
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    processed += 1
                    
                    try:
                        result = future.result()
                        
                        # Merge result into combined index
                        self._merge_index(combined, result)
                        
                        # Optional: print progress
                        if processed % 10 == 0:
                            print(f"Indexed {processed}/{total_files} files...")
                    
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        return combined
    
    def _merge_index(self, target: Dict, source: Dict):
        """Merge source index into target index"""
        # Merge dict-type data
        for key in ["files", "functions", "classes", "imports", "exports"]:
            if key in source:
                target[key].update(source[key])
        
        # Merge list-type data (NEW)
        for key in ["imports_detailed", "entry_points"]:
            if key in source:
                target[key].extend(source[key])


def index_directory_parallel(directory: Path, max_workers: int = None,
                            file_extensions: List[str] = None,
                            with_ai_summaries: bool = False) -> Dict:
    """
    Convenience function to index an entire directory in parallel.
    
    Args:
        directory: Root directory to index
        max_workers: Number of parallel workers
        file_extensions: List of extensions to index (default: common code files)
        with_ai_summaries: Generate AI summaries (default: False - only on demand)
    
    Returns:
        Combined index dictionary with optional AI summaries
    """
    if file_extensions is None:
        file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
    
    # Parser map
    parser_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
    }
    
    # Find all files
    files = []
    for ext in file_extensions:
        files.extend(directory.rglob(f"*{ext}"))
    
    # Filter out common directories to skip
    skip_dirs = {'node_modules', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build'}
    files = [
        f for f in files
        if not any(skip_dir in f.parts for skip_dir in skip_dirs)
    ]
    
    # Index in parallel
    indexer = ParallelIndexer(max_workers=max_workers)
    result = indexer.index_files(files, parser_map)
    
    # Resolve dependencies
    print("\nResolving dependencies...")
    from orc.core.dependency_resolver import DependencyResolver
    resolver = DependencyResolver()
    resolved = resolver.resolve(result)
    
    # Add resolved dependencies to result
    result['file_dependencies_resolved'] = resolved['file_dependencies']
    result['function_calls_resolved'] = resolved['function_calls_resolved']
    result['circular_dependencies'] = resolved['circular_dependencies']
    
    if resolved['circular_dependencies']:
        print(f"  Warning: Found {len(resolved['circular_dependencies'])} circular dependencies")
    
    # Generate AI summaries if requested
    if with_ai_summaries:
        try:
            print("\nGenerating AI summaries...")
            from orc.ai_summarizer import AICodeSummarizer
            
            summarizer = AICodeSummarizer()
            summaries = summarizer.generate_summaries(result)
            result['summaries'] = summaries
            
        except Exception as e:
            print(f"Warning: Failed to generate AI summaries: {e}")
            print("Continuing without summaries...")
            result['summaries'] = {}
    
    return result


# Example usage:
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path.cwd()
    
    print(f"Indexing {directory} in parallel...")
    result = index_directory_parallel(directory)
    
    print(f"\nResults:")
    print(f"  Files: {len(result['files'])}")
    print(f"  Functions: {len(result['functions'])}")
    print(f"  Classes: {len(result['classes'])}")
    print(f"  Imports: {len(result['imports'])}")
    print(f"  Exports: {len(result['exports'])}")
