import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test imports
try:
    from orc_package.config.settings import ORCConfig
    print("ORCConfig import: SUCCESS")
except Exception as e:
    print(f"ORCConfig import: FAILED - {e}")

try:
    from core.indexer import PythonIndexer
    print("PythonIndexer import: SUCCESS")
except Exception as e:
    print(f"PythonIndexer import: FAILED - {e}")

try:
    from analysis.complexity import ComplexityAnalyzer
    print("ComplexityAnalyzer import: SUCCESS")
except Exception as e:
    print(f"ComplexityAnalyzer import: FAILED - {e}")

try:
    from analysis.optimizer import Optimizer
    print("Optimizer import: SUCCESS")
except Exception as e:
    print(f"Optimizer import: FAILED - {e}")

# Test basic functionality of complexity analyzer
try:
    mock_index = {
        "functions": {
            "test.py::simple_func": {
                "complexity": 2,
                "code": "def simple(): pass"
            }
        }
    }
    analyzer = ComplexityAnalyzer(mock_index, None)
    reports = analyzer.analyze_all()
    print(f"ComplexityAnalyzer functionality: SUCCESS - {len(reports)} reports generated")
except Exception as e:
    print(f"ComplexityAnalyzer functionality: FAILED - {e}")

# Test basic functionality of optimizer
try:
    optimizer = Optimizer()
    result = optimizer.analyze_and_suggest(
        file="test.py",
        function="test_func", 
        code="for i in range(10):\n    for j in range(10):\n        print(i, j)"
    )
    print(f"Optimizer functionality: SUCCESS - {result.get('suggestion', 'No suggestion')}")
except Exception as e:
    print(f"Optimizer functionality: FAILED - {e}")

print("All tests completed.")