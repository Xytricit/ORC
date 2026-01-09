"""
Tests for complexity analysis and optimization modules
"""
import pytest
from orc.analysis.complexity import ComplexityAnalyzer, ComplexityReport
from orc.analysis.optimizer import Optimizer


def test_complexity_analyzer_basic():
    """Test basic functionality of complexity analyzer"""
    # Create a mock index with function data
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
    
    # Mock graph (None for this test)
    graph = None
    
    # Create analyzer
    analyzer = ComplexityAnalyzer(mock_index, graph)
    
    # Test analysis of all functions
    reports = analyzer.analyze_all()
    
    # Should have 2 reports
    assert len(reports) == 2
    
    # Check that reports are sorted by complexity (highest first)
    assert reports[0].complexity_score >= reports[1].complexity_score
    
    # Test getting complex functions
    complex_reports = analyzer.get_complex_functions(threshold=10)
    assert len(complex_reports) == 1
    assert complex_reports[0].function == "complex_func"


def test_complexity_report_structure():
    """Test the structure of complexity reports"""
    report = ComplexityReport(
        function="test_func",
        file="test.py",
        time_complexity="O(n)",
        space_complexity="O(1)",
        hotspot=False,
        suggestion="Optimize this",
        estimated_improvement=0.5,
        complexity_score=10
    )
    
    assert report.function == "test_func"
    assert report.file == "test.py"
    assert report.time_complexity == "O(n)"
    assert report.space_complexity == "O(1)"
    assert report.hotspot == False
    assert report.suggestion == "Optimize this"
    assert report.estimated_improvement == 0.5
    assert report.complexity_score == 10


def test_optimizer_basic():
    """Test basic functionality of optimizer"""
    optimizer = Optimizer()
    
    # Test with nested loops (should match the first rule)
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
    
    assert result["current_complexity"] == "O(n²)"
    assert result["suggested_complexity"] == "O(n)"
    assert "hash table" in result["suggestion"]
    assert result["estimated_improvement"] == 0.9
    assert "Nested Loop to Hash Lookup" in result["rules_matched"]


def test_optimizer_list_comprehension():
    """Test optimizer with list comprehension pattern"""
    optimizer = Optimizer()
    
    # Test with loop and append (should match list comprehension rule)
    code_with_append = """
result = []
for item in items:
    if condition(item):
        result.append(item)
"""
    
    result = optimizer.analyze_and_suggest(
        file="test.py",
        function="test_func",
        code=code_with_append
    )
    
    # Should match the list comprehension rule
    matched_rules = result["rules_matched"]
    assert any("List Comprehension" in rule for rule in matched_rules)


def test_optimizer_string_concatenation():
    """Test optimizer with string concatenation in loop"""
    optimizer = Optimizer()
    
    # Test with string concatenation in loop
    code_with_concat = """
result = ""
for s in strings:
    result += s
"""
    
    result = optimizer.analyze_and_suggest(
        file="test.py",
        function="test_func",
        code=code_with_concat
    )
    
    # Should match the string concatenation rule
    matched_rules = result["rules_matched"]
    assert any("String Concatenation" in rule for rule in matched_rules)


def test_optimizer_no_matches():
    """Test optimizer with code that doesn't match any rules"""
    optimizer = Optimizer()
    
    # Test with simple code that doesn't match any patterns
    simple_code = """
def simple_function():
    return 42
"""
    
    result = optimizer.analyze_and_suggest(
        file="test.py",
        function="test_func",
        code=simple_code
    )
    
    # Should return default response for well-optimized code
    assert result["suggestion"] == "Code appears well-optimized. Consider profiling for performance bottlenecks."
    assert result["estimated_improvement"] == 0.05
    assert len(result["rules_matched"]) == 0


def test_optimizer_report_generation():
    """Test optimization report generation"""
    optimizer = Optimizer()
    
    # Test with nested loops
    code_with_nested_loops = """
for item in list1:
    for item2 in list2:
        if item == item2:
            print(item)
    """
    
    report = optimizer.get_optimization_report(code_with_nested_loops)
    
    # Should have found optimization opportunities
    assert report["total_optimization_opportunities"] > 0
    assert len(report["optimization_suggestions"]) > 0
    assert len(report["priority_suggestions"]) > 0
    assert report["estimated_total_improvement"] > 0
    
    # Check that the highest priority suggestion is for nested loops
    highest_priority = report["priority_suggestions"][0]
    assert "nested loops" in highest_priority["suggestion"].lower()


def test_complexity_hotspot_detection():
    """Test hotspot detection in complexity analyzer"""
    # Create a mock index
    mock_index = {
        "functions": {
            "test.py::hotspot_func": {
                "complexity": 15,
                "code": "def hotspot(): pass"
            }
        }
    }
    
    # Create a mock graph that returns multiple callers
    class MockGraph:
        def get_function_callers(self, func_id):
            if "hotspot_func" in func_id:
                return ["caller1", "caller2", "caller3", "caller4", "caller5", "caller6"]  # 6 callers
            return []
    
    mock_graph = MockGraph()
    analyzer = ComplexityAnalyzer(mock_index, mock_graph)
    
    # Analyze the function
    report = analyzer.analyze_function("test.py::hotspot_func", mock_index["functions"]["test.py::hotspot_func"])
    
    # Should be detected as a hotspot (called by more than 5 functions)
    assert report.hotspot == True


def test_complexity_suggestions():
    """Test complexity-based suggestions"""
    mock_index = {
        "functions": {
            "test.py::bad_func": {
                "complexity": 100,  # Very high complexity
                "code": "def bad(): pass"
            }
        }
    }
    
    analyzer = ComplexityAnalyzer(mock_index, None)
    report = analyzer.analyze_function("test.py::bad_func", mock_index["functions"]["test.py::bad_func"])
    
    # Should have a high complexity score
    assert report.complexity_score == 100
    # Should have a high estimated improvement
    assert report.estimated_improvement > 0.7
    # Should have a suggestion for the complexity type
    assert "exponential" in report.suggestion.lower() or "dynamic programming" in report.suggestion


if __name__ == "__main__":
    pytest.main([__file__])