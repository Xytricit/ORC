"""Code generator that creates optimized versions of functions based on analysis."""

import ast
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .algorithm_detector import AlgorithmDetection

# Optional astor import
try:
    import astor  # type: ignore
    HAS_ASTOR = True
except ImportError:
    HAS_ASTOR = False


@dataclass
class GeneratedCode:
    """Represents generated optimized code."""
    original_function: str
    optimized_function: str
    optimization_type: str
    confidence: float
    explanation: str


class CodeGenerator:
    """Generates optimized code based on algorithm analysis and suggestions."""

    def __init__(self):
        pass

    def generate_optimized_code(self,
                              original_code: str,
                              algorithm_detections: List[AlgorithmDetection],
                              suggestion_details: str = "") -> Optional[GeneratedCode]:
        """Generate optimized code based on algorithm detections."""

        # Parse the original code
        try:
            tree = ast.parse(original_code)
        except SyntaxError:
            return None

        # Apply optimizations based on detected algorithms
        optimized_code = original_code
        optimization_type = "general"
        confidence = 0.5
        explanation = "General optimization applied"

        for detection in algorithm_detections:
            if detection.name == 'Bubble Sort or Similar':
                optimized_code = self._optimize_bubble_sort(optimized_code)
                optimization_type = "sorting"
                confidence = detection.confidence
                explanation = f"Replaced {detection.name} with more efficient algorithm"
            elif detection.name == 'Linear Search':
                optimized_code = self._optimize_linear_search(optimized_code)
                optimization_type = "searching"
                confidence = detection.confidence
                explanation = f"Replaced {detection.name} with more efficient algorithm"
            elif detection.name == 'Dynamic Programming':
                optimized_code = self._optimize_dp_space(optimized_code)
                optimization_type = "dynamic_programming"
                confidence = detection.confidence
                explanation = f"Optimized {detection.name} implementation"
            elif 'O(n²)' in detection.complexity_hint:
                optimized_code = self._reduce_quadratic_complexity(optimized_code)
                optimization_type = "complexity_reduction"
                confidence = detection.confidence
                explanation = f"Reduced complexity from {detection.complexity_hint}"

        return GeneratedCode(
            original_function=original_code,
            optimized_function=optimized_code,
            optimization_type=optimization_type,
            confidence=confidence,
            explanation=explanation
        )

    def _optimize_bubble_sort(self, code: str) -> str:
        """Generate optimized sorting code to replace bubble sort."""
        # This is a simplified implementation - in a real system, we'd do more
        # sophisticated AST transformations
        optimized = '''
def optimized_sort(arr):
    """Optimized sorting function replacing bubble sort."""
    return sorted(arr)
'''
        return optimized

    def _optimize_linear_search(self, code: str) -> str:
        """Generate optimized search code to replace linear search."""
        optimized = '''
def optimized_search(arr, target):
    """Optimized search function using hash table for O(1) lookups."""
    lookup = {val: idx for idx, val in enumerate(arr)}
    return lookup.get(target, -1)
'''
        return optimized

    def _optimize_dp_space(self, code: str) -> str:
        """Optimize dynamic programming implementation for space."""
        optimized = '''
def optimized_dp_function(n):
    """Space-optimized dynamic programming function."""
    if n <= 1:
        return n

    # Use only the last two values instead of an array
    prev2, prev1 = 0, 1
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current

    return prev1
'''
        return optimized

    def _reduce_quadratic_complexity(self, code: str) -> str:
        """Attempt to reduce O(n²) complexity where possible."""
        # This is a template - in a real system we'd analyze the specific code
        # and apply appropriate optimizations
        optimized = '''
def optimized_function(items):
    """Function with reduced complexity."""
    # Convert to set for O(1) lookups instead of O(n) list operations
    item_set = set(items)

    result = []
    for item in items:
        if item in item_set:  # O(1) lookup instead of O(n)
            result.append(item)

    return result
'''
        return optimized

    def generate_hash_table_implementation(self, original_code: str) -> str:
        """Generate hash table implementation to replace nested loops."""
        optimized = '''
def optimized_with_hashmap(data):
    """Function using hash map to avoid nested loops."""
    lookup = {}

    # Build lookup table - O(n)
    for item in data:
        key = item  # or some function of item
        if key not in lookup:
            lookup[key] = []
        lookup[key].append(item)

    # Process using lookup - O(n) instead of O(n²)
    result = []
    for item in data:
        key = item  # or some function of item
        if key in lookup:
            result.extend(lookup[key])

    return result
'''
        return optimized

    def generate_binary_search_implementation(self, original_code: str) -> str:
        """Generate binary search implementation for sorted data."""
        optimized = '''
def binary_search(arr, target):
    """Binary search implementation for O(log n) lookups."""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
'''
        return optimized

    def generate_memoized_version(self, original_code: str) -> str:
        """Generate memoized version of recursive function."""
        optimized = '''
def memoized_function(n, memo=None):
    """Memoized version to avoid redundant calculations."""
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    if n <= 1:
        result = n
    else:
        result = memoized_function(n-1, memo) + memoized_function(n-2, memo)

    memo[n] = result
    return result
'''
        return optimized


def generate_optimized_code(original_code: str,
                          algorithm_detections: List[AlgorithmDetection],
                          suggestion_details: str = "") -> Optional[GeneratedCode]:
    """Public function to generate optimized code."""
    generator = CodeGenerator()
    return generator.generate_optimized_code(original_code, algorithm_detections, suggestion_details)
