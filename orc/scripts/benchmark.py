"""
ORC Scripts: Performance Benchmarking
"""
import time
import cProfile
import pstats
from pathlib import Path
from typing import Dict, Any
import tempfile
import os

from orc.core.indexer import PythonIndexer
from orc.config.settings import ORCConfig
from orc.core.analyzer import Analyzer

def run_benchmark():
    """Run performance benchmarks for ORC components"""
    print("Starting ORC Performance Benchmarking...")
    
    # Create a temporary codebase for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create some test files
        create_test_codebase(temp_path)
        
        # Benchmark indexing
        indexing_time = benchmark_indexing(temp_path)
        print(f"Indexing time: {indexing_time:.4f} seconds")
        
        # Benchmark analysis
        analysis_time = benchmark_analysis(temp_path)
        print(f"Analysis time: {analysis_time:.4f} seconds")
        
        # Run profiling
        profile_results = run_profiling(temp_path)
        print("Profiling completed")
        
        return {
            'indexing_time': indexing_time,
            'analysis_time': analysis_time,
            'profile_results': profile_results
        }

def create_test_codebase(base_path: Path):
    """Create a test codebase with multiple files"""
    # Create several Python files with different complexities
    for i in range(10):  # Create 10 files
        file_path = base_path / f"module_{i}.py"
        with open(file_path, 'w') as f:
            f.write(f"""
# Test module {i}

def simple_function_{i}():
    return {i}

def complex_function_{i}():
    result = 0
    for j in range(100):
        if j % 2 == 0:
            if j % 3 == 0:
                result += j
            else:
                result -= j
        else:
            result *= 2
    return result

class TestClass_{i}:
    def method_{i}(self):
        if True:
            for k in range(10):
                while k > 0:
                    k -= 1
        return "done"

def function_with_calls_{i}():
    simple_function_{i}()
    complex_function_{i}()
    obj = TestClass_{i}()
    return obj.method_{i}()
""")

def benchmark_indexing(path: Path) -> float:
    """Benchmark the indexing process"""
    config = ORCConfig(project_root=path)
    indexer = PythonIndexer(config)
    
    start_time = time.time()
    modules = indexer.index_directory(path)
    end_time = time.time()
    
    print(f"Indexed {len(modules)} modules")
    return end_time - start_time

def benchmark_analysis(path: Path) -> float:
    """Benchmark the analysis process"""
    config = ORCConfig(project_root=path)
    indexer = PythonIndexer(config)
    modules = indexer.index_directory(path)
    
    analyzer = Analyzer(config)
    
    start_time = time.time()
    report = analyzer.run_all(modules)
    end_time = time.time()
    
    print(f"Analyzed modules with {len(report)} report sections")
    return end_time - start_time

def run_profiling(path: Path) -> Dict[str, Any]:
    """Run profiling on the indexing and analysis process"""
    config = ORCConfig(project_root=path)
    
    def profile_target():
        indexer = PythonIndexer(config)
        modules = indexer.index_directory(path)
        
        analyzer = Analyzer(config)
        report = analyzer.run_all(modules)
        return report
    
    profiler = cProfile.Profile()
    profiler.enable()
    profile_target()
    profiler.disable()
    
    # Create stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    # Print top 10 functions by cumulative time
    print("\nTop 10 functions by cumulative time:")
    stats.print_stats(10)
    
    return stats

if __name__ == "__main__":
    run_benchmark()