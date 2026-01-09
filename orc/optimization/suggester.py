"""Optimization suggester that provides specific recommendations based on algorithm analysis."""

from typing import Dict, List
from dataclasses import dataclass
from .algorithm_detector import AlgorithmDetector, AlgorithmDetection
from orc.analysis.complexity import ComplexityReport


@dataclass
class OptimizationSuggestion:
    """Represents an optimization suggestion."""
    function_name: str
    file_path: str
    current_algorithm: str
    suggested_algorithm: str
    estimated_performance_gain: float  # 0.0 to 1.0
    suggestion_details: str
    implementation_example: str
    complexity_reduction: str  # e.g., "O(n²) to O(n log n)"


class OptimizationSuggester:
    """Provides optimization suggestions based on algorithm analysis."""

    def __init__(self):
        self.algorithm_detector = AlgorithmDetector()

    def generate_suggestions(self,
                           function_code: str,
                           function_name: str,
                           file_path: str,
                           complexity_report: ComplexityReport = None) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for a function."""
        suggestions = []

        # Detect algorithms in the function
        algorithm_detections = self.algorithm_detector.detect_algorithms_in_function(
            function_code, function_name
        )

        for detection in algorithm_detections:
            suggestion = self._create_suggestion(
                detection, function_name, file_path, complexity_report
            )
            if suggestion:
                suggestions.append(suggestion)

        # Add general optimization suggestions based on complexity
        if complexity_report:
            general_suggestions = self._generate_general_suggestions(
                function_name, file_path, complexity_report
            )
            suggestions.extend(general_suggestions)

        return suggestions

    def _create_suggestion(self,
                          detection: AlgorithmDetection,
                          function_name: str,
                          file_path: str,
                          complexity_report: ComplexityReport) -> OptimizationSuggestion:
        """Create a specific optimization suggestion based on algorithm detection."""

        # Map detected algorithms to possible optimizations
        optimizations = {
            'Bubble Sort or Similar': {
                'suggested': 'Quick Sort or Merge Sort',
                'gain': 0.8,
                'details': 'Replace quadratic sorting algorithm with O(n log n) alternative',
                'example': self._get_sorting_example(),
                'complexity': 'O(n²) to O(n log n)'
            },
            'Binary Search': {
                'suggested': 'Binary Search (already optimal)',
                'gain': 0.0,
                'details': 'Binary search is already optimal for sorted arrays',
                'example': '',
                'complexity': 'O(log n) - already optimal'
            },
            'Linear Search': {
                'suggested': 'Binary Search or Hash Table Lookup',
                'gain': 0.6,
                'details': 'Consider using binary search (if sorted) or hash table for O(1) lookups',
                'example': self._get_search_optimization_example(),
                'complexity': 'O(n) to O(log n) or O(1)'
            },
            'Dynamic Programming': {
                'suggested': 'Optimized DP or Alternative Approach',
                'gain': 0.3,
                'details': 'Consider space-optimized DP or mathematical simplification',
                'example': self._get_dp_optimization_example(),
                'complexity': 'Reduced constant factors or space complexity'
            }
        }

        opt_info = optimizations.get(detection.name, None)
        if not opt_info:
            return None

        return OptimizationSuggestion(
            function_name=function_name,
            file_path=file_path,
            current_algorithm=detection.name,
            suggested_algorithm=opt_info['suggested'],
            estimated_performance_gain=opt_info['gain'],
            suggestion_details=opt_info['details'],
            implementation_example=opt_info['example'],
            complexity_reduction=opt_info['complexity']
        )

    def _generate_general_suggestions(self,
                                    function_name: str,
                                    file_path: str,
                                    complexity_report: ComplexityReport) -> List[OptimizationSuggestion]:
        """Generate general optimization suggestions based on complexity."""
        suggestions = []

        # High complexity functions
        if complexity_report.complexity_score > 20:
            if 'O(n²)' in complexity_report.time_complexity:
                suggestions.append(OptimizationSuggestion(
                    function_name=function_name,
                    file_path=file_path,
                    current_algorithm=f"High complexity function ({complexity_report.time_complexity})",
                    suggested_algorithm="Optimize with better algorithm",
                    estimated_performance_gain=0.7,
                    suggestion_details="This function has high time complexity. Consider using a more efficient algorithm or data structure.",
                    implementation_example=self._get_complexity_reduction_example(),
                    complexity_reduction=f"{complexity_report.time_complexity} to O(n log n) or better"
                ))
            elif 'O(2^n)' in complexity_report.time_complexity:
                suggestions.append(OptimizationSuggestion(
                    function_name=function_name,
                    file_path=file_path,
                    current_algorithm=f"Exponential complexity function ({complexity_report.time_complexity})",
                    suggested_algorithm="Dynamic Programming or Memoization",
                    estimated_performance_gain=0.9,
                    suggestion_details="This function has exponential time complexity. Consider using dynamic programming or memoization to eliminate redundant calculations.",
                    implementation_example=self._get_exponential_optimization_example(),
                    complexity_reduction=f"{complexity_report.time_complexity} to O(n) or O(n²)"
                ))

        return suggestions

    def _get_sorting_example(self) -> str:
        """Return an example of optimized sorting."""
        return """
# Instead of bubble sort O(n²):
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Use built-in sort O(n log n):
def optimized_sort(arr):
    return sorted(arr)

# Or implement merge sort:
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)
"""

    def _get_search_optimization_example(self) -> str:
        """Return an example of search optimization."""
        return """
# Instead of linear search O(n):
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1

# Use binary search O(log n) for sorted arrays:
def binary_search(arr, target):
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

# Or use hash table O(1) for frequent lookups:
class LookupTable:
    def __init__(self, items):
        self.lookup = {item: idx for idx, item in enumerate(items)}

    def find(self, item):
        return self.lookup.get(item, -1)
"""

    def _get_dp_optimization_example(self) -> str:
        """Return an example of DP optimization."""
        return """
# Instead of naive recursion O(2^n):
def fibonacci_naive(n):
    if n <= 1:
        return n
    return fibonacci_naive(n-1) + fibonacci_naive(n-2)

# Use memoization O(n):
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

# Or bottom-up DP O(n) time, O(1) space:
def fibonacci_optimized(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""

    def _get_complexity_reduction_example(self) -> str:
        """Return a general example of complexity reduction."""
        return """
# Look for nested loops that might be optimized:
# Instead of O(n²):
result = []
for i in range(len(list1)):
    for j in range(len(list2)):
        if list1[i] == list2[j]:
            result.append((i, j))

# Use set for O(n) lookup:
set2 = set(list2)
result = [(i, list2.index(list1[i])) for i in range(len(list1)) if list1[i] in set2]
"""

    def _get_exponential_optimization_example(self) -> str:
        """Return an example of exponential optimization."""
        return """
# Instead of trying all combinations O(2^n):
def subset_sum_exponential(arr, target):
    n = len(arr)
    for i in range(1 << n):  # 2^n possibilities
        current_sum = 0
        for j in range(n):
            if i & (1 << j):
                current_sum += arr[j]
        if current_sum == target:
            return True
    return False

# Use dynamic programming O(n * target):
def subset_sum_dp(arr, target):
    n = len(arr)
    dp = [[False for _ in range(target + 1)] for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = True

    for i in range(1, n + 1):
        for j in range(1, target + 1):
            if j < arr[i-1]:
                dp[i][j] = dp[i-1][j]
            else:
                dp[i][j] = dp[i-1][j] or dp[i-1][j-arr[i-1]]

    return dp[n][target]
"""


def suggest_optimizations(function_code: str,
                         function_name: str,
                         file_path: str,
                         complexity_report: ComplexityReport = None) -> List[OptimizationSuggestion]:
    """Public function to suggest optimizations for code."""
    suggester = OptimizationSuggester()
    return suggester.generate_suggestions(function_code, function_name, file_path, complexity_report)


class Suggester:
    """Legacy suggester class for backward compatibility."""

    def __init__(self):
        self.optimizer = OptimizationSuggester()

    def suggest(self, file: str, function: str = None, code: str = None) -> Dict:
        """Provide optimization suggestions."""
        if code:
            suggestions = self.optimizer.generate_suggestions(code, function or "unknown", file)
            if suggestions:
                best_suggestion = suggestions[0]  # Return the first/most relevant suggestion
                return {
                    "suggestion": best_suggestion.suggestion_details,
                    "estimated_improvement": best_suggestion.estimated_performance_gain,
                    "current_algorithm": best_suggestion.current_algorithm,
                    "suggested_algorithm": best_suggestion.suggested_algorithm,
                    "example": best_suggestion.implementation_example
                }

        return {"suggestion": "No specific optimization detected", "estimated_improvement": 0.0}
