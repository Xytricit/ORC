#!/usr/bin/env python
"""
Simple test to verify ORC components work
"""

def test_basic_imports():
    """Test basic imports"""
    try:
        from orc_package.config.settings import ORCConfig
        print("✓ ORCConfig imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ORCConfig: {e}")
        return False

    try:
        from core.indexer import PythonIndexer
        print("✓ PythonIndexer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PythonIndexer: {e}")
        return False

    try:
        from analysis.complexity import ComplexityAnalyzer
        print("✓ ComplexityAnalyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ComplexityAnalyzer: {e}")
        return False

    try:
        from analysis.optimizer import Optimizer
        print("✓ Optimizer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Optimizer: {e}")
        return False

    return True

def test_complexity_analyzer():
    """Test complexity analyzer functionality"""
    try:
        from analysis.complexity import ComplexityAnalyzer
        
        # Create a mock index
        mock_index = {
            "functions": {
                "test.py::simple_func": {
                    "complexity": 2,
                    "code": "def simple(): pass"
                },
                "test.py::complex_func": {
                    "complexity": 25,
                    "code": "def complex(): pass"
                }
            }
        }
        
        analyzer = ComplexityAnalyzer(mock_index, None)
        reports = analyzer.analyze_all()
        
        if len(reports) == 2:
            print("✓ Complexity analyzer works correctly")
            return True
        else:
            print(f"✗ Complexity analyzer returned {len(reports)} reports instead of 2")
            return False
    except Exception as e:
        print(f"✗ Complexity analyzer test failed: {e}")
        return False

def test_optimizer():
    """Test optimizer functionality"""
    try:
        from analysis.optimizer import Optimizer
        
        optimizer = Optimizer()
        
        # Test with nested loops
        code_with_nested_loops = """
for item in list1:
    for item2 in list2:
        if item == item2:
            print(item)
        """
        
        result = optimizer.analyze_and_suggest(
            file="test.py",
            function="test_func",
            code=code_with_nested_loops
        )
        
        if "Nested Loop to Hash Lookup" in result.get("rules_matched", []):
            print("✓ Optimizer works correctly")
            return True
        else:
            print(f"✗ Optimizer didn't match expected rule. Result: {result}")
            return False
    except Exception as e:
        print(f"✗ Optimizer test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ORC v1 components...")
    print()
    
    success = True
    success &= test_basic_imports()
    print()
    success &= test_complexity_analyzer()
    print()
    success &= test_optimizer()
    print()
    
    if success:
        print("✓ All tests passed! ORC v1 is working correctly.")
    else:
        print("✗ Some tests failed.")