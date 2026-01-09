"""Advanced algorithm detector that identifies common algorithmic patterns in code."""

import ast
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AlgorithmDetection:
    """Represents an algorithm detection result."""
    algorithm_type: str
    name: str
    confidence: float
    description: str
    line_numbers: Tuple[int, int]
    complexity_hint: str


class AlgorithmDetector:
    """Detects algorithmic patterns in code using AST analysis."""

    def __init__(self):
        self.patterns = self._define_patterns()

    def _define_patterns(self) -> Dict[str, Dict]:
        """Define known algorithm patterns to detect."""
        return {
            # Sorting algorithms
            'bubble_sort': {
                'name': 'Bubble Sort',
                'description': 'Simple comparison-based sorting algorithm',
                'complexity': 'O(n²)',
                'confidence': 0.9,
                'structure': {
                    'nested_loops': True,
                    'comparison_op': ['Lt', 'Gt', 'LtE', 'GtE'],
                    'swap_operation': True
                }
            },
            'quick_sort': {
                'name': 'Quick Sort',
                'description': 'Divide-and-conquer sorting algorithm',
                'complexity': 'O(n log n) average, O(n²) worst',
                'confidence': 0.85,
                'structure': {
                    'recursive_call': True,
                    'partition_logic': True,
                    'pivot_selection': True
                }
            },
            'merge_sort': {
                'name': 'Merge Sort',
                'description': 'Divide-and-conquer sorting algorithm',
                'complexity': 'O(n log n)',
                'confidence': 0.85,
                'structure': {
                    'recursive_call': True,
                    'divide_conquer': True,
                    'merge_operation': True
                }
            },

            # Search algorithms
            'binary_search': {
                'name': 'Binary Search',
                'description': 'Search algorithm for sorted arrays',
                'complexity': 'O(log n)',
                'confidence': 0.9,
                'structure': {
                    'loop_or_recursive': True,
                    'mid_calculation': True,
                    'comparison_with_mid': True
                }
            },
            'linear_search': {
                'name': 'Linear Search',
                'description': 'Sequential search algorithm',
                'complexity': 'O(n)',
                'confidence': 0.8,
                'structure': {
                    'single_loop': True,
                    'element_comparison': True
                }
            },

            # Dynamic Programming
            'fibonacci_dp': {
                'name': 'Fibonacci (Dynamic Programming)',
                'description': 'Fibonacci sequence calculation with memoization',
                'complexity': 'O(n)',
                'confidence': 0.85,
                'structure': {
                    'memoization': True,
                    'iterative_calculation': True
                }
            },
            'knapsack_dp': {
                'name': 'Knapsack Problem (Dynamic Programming)',
                'description': 'Classic DP optimization problem',
                'complexity': 'O(nW)',
                'confidence': 0.8,
                'structure': {
                    '2d_array_use': True,
                    'optimal_substructure': True
                }
            },

            # Graph algorithms
            'dfs': {
                'name': 'Depth-First Search',
                'description': 'Graph traversal algorithm',
                'complexity': 'O(V + E)',
                'confidence': 0.85,
                'structure': {
                    'recursive_call': True,
                    'visited_tracking': True,
                    'adjacency_list_use': True
                }
            },
            'bfs': {
                'name': 'Breadth-First Search',
                'description': 'Graph traversal algorithm',
                'complexity': 'O(V + E)',
                'confidence': 0.85,
                'structure': {
                    'queue_use': True,
                    'level_by_level_processing': True,
                    'visited_tracking': True
                }
            },

            # Tree algorithms
            'tree_traversal': {
                'name': 'Tree Traversal',
                'description': 'Various tree traversal methods (inorder, preorder, postorder)',
                'complexity': 'O(n)',
                'confidence': 0.8,
                'structure': {
                    'recursive_tree_walk': True,
                    'node_processing': True
                }
            },

            # Mathematical algorithms
            'gcd_euclidean': {
                'name': 'Euclidean Algorithm (GCD)',
                'description': 'Efficient algorithm for computing greatest common divisor',
                'complexity': 'O(log min(a,b))',
                'confidence': 0.9,
                'structure': {
                    'modulo_operation': True,
                    'recursive_or_iterative': True
                }
            }
        }

    def detect_algorithms_in_function(self, code: str, func_name: str = "unknown") -> List[AlgorithmDetection]:
        """Detect algorithms in a function's code."""
        try:
            tree = ast.parse(code)
            detections = []

            # Analyze the AST for algorithmic patterns
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_detections = self._analyze_function(node, code)
                    detections.extend(func_detections)

            # If no function definitions found, analyze the whole code
            if not detections:
                detections = self._analyze_code_structure(ast.parse(code), code, func_name)

            return detections

        except SyntaxError:
            # If parsing fails, return empty list
            return []

    def _analyze_function(self, func_node: ast.FunctionDef, full_code: str) -> List[AlgorithmDetection]:
        """Analyze a specific function for algorithmic patterns."""
        detections = []

        # Get the source code for this function
        try:
            import astor  # type: ignore
            func_code = astor.to_source(func_node)
        except (ImportError, Exception):
            # If astor is not available, extract manually
            lines = full_code.split('\n')
            start_line = func_node.lineno - 1
            end_line = getattr(func_node, 'end_lineno', start_line + 10)  # Fallback if end_lineno not available
            func_code = '\n'.join(lines[start_line:end_line])

        # Analyze the function structure
        detections.extend(self._analyze_code_structure(func_node, func_code, func_node.name))

        return detections

    def _analyze_code_structure(self, node: ast.AST, code: str, func_name: str = "unknown") -> List[AlgorithmDetection]:
        """Analyze code structure for algorithmic patterns."""
        detections = []

        # Check for various algorithmic patterns
        if self._has_nested_loops(node):
            if self._has_swap_operation(node):
                detections.append(AlgorithmDetection(
                    algorithm_type='sorting',
                    name='Bubble Sort or Similar',
                    confidence=0.7,
                    description='Nested loops with swap operations suggest sorting algorithm',
                    line_numbers=(1, 10),  # Placeholder
                    complexity_hint='O(n²)'
                ))

        if self._has_binary_search_pattern(node):
            detections.append(AlgorithmDetection(
                algorithm_type='search',
                name='Binary Search',
                confidence=0.85,
                description='Binary search pattern detected',
                line_numbers=(1, 10),  # Placeholder
                complexity_hint='O(log n)'
            ))

        if self._has_recursive_pattern(node) and self._has_divide_logic(node):
            detections.append(AlgorithmDetection(
                algorithm_type='divide_conquer',
                name='Divide and Conquer',
                confidence=0.8,
                description='Recursive divide-and-conquer pattern detected',
                line_numbers=(1, 10),  # Placeholder
                complexity_hint='O(n log n) or O(n²)'
            ))

        if self._has_dynamic_programming_indicators(node):
            detections.append(AlgorithmDetection(
                algorithm_type='dynamic_programming',
                name='Dynamic Programming',
                confidence=0.75,
                description='Dynamic programming pattern detected',
                line_numbers=(1, 10),  # Placeholder
                complexity_hint='O(n) to O(n²) depending on implementation'
            ))

        if self._has_graph_traversal_indicators(node):
            if self._uses_recursion_for_traversal(node):
                algo_name = 'DFS'
                complexity = 'O(V + E)'
            else:
                algo_name = 'BFS'
                complexity = 'O(V + E)'

            detections.append(AlgorithmDetection(
                algorithm_type='graph_traversal',
                name=f'Graph Traversal ({algo_name})',
                confidence=0.8,
                description=f'Graph traversal algorithm ({algo_name}) detected',
                line_numbers=(1, 10),  # Placeholder
                complexity_hint=complexity
            ))

        return detections

    def _has_nested_loops(self, node: ast.AST) -> bool:
        """Check if the code has nested loops."""
        loop_count = 0

        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loop_count += 1
                # Check if this loop contains another loop
                for inner_child in child.body:
                    if isinstance(inner_child, (ast.For, ast.While, ast.AsyncFor)):
                        return True

        return False

    def _has_swap_operation(self, node: ast.AST) -> bool:
        """Check if the code has swap operations."""
        for child in ast.walk(node):
            # Look for assignments that look like swaps
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Tuple) and len(target.elts) == 2:
                        # This might be a tuple assignment like a, b = b, a
                        return True
                    elif isinstance(child.value, ast.Tuple) and isinstance(target, ast.Name):
                        # Another form of swap
                        return True
        return False

    def _has_binary_search_pattern(self, node: ast.AST) -> bool:
        """Check for binary search pattern."""
        has_mid_calc = False
        has_comparison_with_mid = False

        for child in ast.walk(node):
            # Look for mid calculation (left + right) // 2
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.FloorDiv):
                if isinstance(child.left, ast.BinOp) and isinstance(child.left.op, ast.Add):
                    has_mid_calc = True

            # Look for comparisons involving mid-like variables
            if isinstance(child, ast.Compare):
                for comparator in child.comparators:
                    if isinstance(comparator, ast.Name) and 'mid' in comparator.id.lower():
                        has_comparison_with_mid = True
                    elif isinstance(comparator, ast.Subscript) and isinstance(comparator.value, ast.Name):
                        if 'arr' in comparator.value.id.lower() or 'list' in comparator.value.id.lower():
                            has_comparison_with_mid = True

        return has_mid_calc and has_comparison_with_mid

    def _has_recursive_pattern(self, node: ast.AST) -> bool:
        """Check if the code has recursive calls."""
        # This is a simplified check - in practice, we'd need to track function names
        # and see if the function calls itself
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    # In a real implementation, we'd need to track the current function name
                    # and see if it's calling itself
                    pass
                elif isinstance(child.func, ast.Attribute):
                    # Method calls
                    pass
        # For now, return a basic check
        return len([n for n in ast.walk(node) if isinstance(n, ast.Call)]) > 5  # Heuristic

    def _has_divide_logic(self, node: ast.AST) -> bool:
        """Check for divide logic typical in divide-and-conquer."""
        # Look for operations that split data
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp):
                if isinstance(child.op, (ast.FloorDiv, ast.Mod)):
                    return True
                elif isinstance(child.op, ast.Add):
                    # Check if adding indices or positions
                    pass
        return False

    def _has_dynamic_programming_indicators(self, node: ast.AST) -> bool:
        """Check for DP indicators like memoization or tabulation."""
        has_array_access = False
        has_assignment_to_index = False

        for child in ast.walk(node):
            if isinstance(child, ast.Subscript):
                has_array_access = True
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Subscript):
                        has_assignment_to_index = True

        return has_array_access and has_assignment_to_index

    def _has_graph_traversal_indicators(self, node: ast.AST) -> bool:
        """Check for graph traversal indicators."""
        has_adjacency_list = False
        has_queue_stack = False
        has_visited_set = False

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                name_lower = child.id.lower()
                if any(adj_word in name_lower for adj_word in ['adj', 'graph', 'edge', 'neighbor']):
                    has_adjacency_list = True
                elif any(queue_word in name_lower for queue_word in ['queue', 'stack', 'deque']):
                    has_queue_stack = True
                elif any(visit_word in name_lower for visit_word in ['visited', 'seen', 'discovered']):
                    has_visited_set = True

        return has_adjacency_list or has_queue_stack or has_visited_set

    def _uses_recursion_for_traversal(self, node: ast.AST) -> bool:
        """Check if traversal is done recursively (DFS) vs iteratively (BFS)."""
        # Simplified check - in reality, we'd need more sophisticated analysis
        recursive_calls = [n for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        return len(recursive_calls) > 3  # Heuristic


def detect_algorithm(code: str) -> List[AlgorithmDetection]:
    """Public function to detect algorithms in code."""
    detector = AlgorithmDetector()
    return detector.detect_algorithms_in_function(code)
