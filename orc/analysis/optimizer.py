"""Optimization suggestion implementation.

Advanced optimization analyzer that provides specific code improvement
recommendations based on complexity analysis, pattern detection, and
best practices.
"""
from typing import Dict, Optional, List
import re


class OptimizationRule:
    """Represents an optimization rule with pattern and suggestion"""
    def __init__(self, name: str, pattern: str, suggestion: str,
                 current_complexity: str, suggested_complexity: str,
                 improvement_factor: float):
        self.name = name
        self.pattern = pattern
        self.suggestion = suggestion
        self.current_complexity = current_complexity
        self.suggested_complexity = suggested_complexity
        self.improvement_factor = improvement_factor


class Optimizer:
    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> List[OptimizationRule]:
        """Initialize optimization rules with common patterns"""
        return [
            OptimizationRule(
                name="Nested Loop to Hash Lookup",
                pattern=r"for\s+\w+\s+in\s+\w+:.*for\s+\w+\s+in\s+\w+:",
                suggestion="Consider using a hash table/dict for O(1) lookups instead of nested loops (O(n²) → O(n))",
                current_complexity="O(n²)",
                suggested_complexity="O(n)",
                improvement_factor=0.9
            ),
            OptimizationRule(
                name="List Comprehension",
                pattern=r"for\s+\w+\s+in\s+\w+:.*append",
                suggestion="Consider using list comprehension for better performance and readability",
                current_complexity="O(n)",
                suggested_complexity="O(n)",
                improvement_factor=0.1
            ),
            OptimizationRule(
                name="Redundant Function Call",
                pattern=r"\w+\(\w+\).*\w+\(\w+\)",  # Same function called multiple times
                suggestion="Cache the result of expensive function calls that are used multiple times",
                current_complexity="O(n)",
                suggested_complexity="O(n)",
                improvement_factor=0.2
            ),
            OptimizationRule(
                name="Inefficient Sorting",
                pattern=r"sorted\(.*\).*for",
                suggestion="Consider if the data structure can be maintained in sorted order to avoid repeated sorting",
                current_complexity="O(n log n)",
                suggested_complexity="O(log n)",
                improvement_factor=0.7
            ),
            OptimizationRule(
                name="String Concatenation in Loop",
                pattern=r"for.*:.*\+=\s*str",
                suggestion="Use ''.join() method for string concatenation in loops to avoid O(n²) complexity",
                current_complexity="O(n²)",
                suggested_complexity="O(n)",
                improvement_factor=0.8
            )
        ]

    def analyze_and_suggest(self, file: str, function: Optional[str] = None, code: Optional[str] = None) -> Dict:
        """Analyze code for optimization opportunities"""
        if code is None:
            # If no code is provided, return default response
            return {
                "current_complexity": "Unknown",
                "suggested_complexity": "Unknown",
                "suggestion": "No code provided for analysis",
                "optimized_code": None,
                "estimated_improvement": 0.0,
                "rules_matched": []
            }

        # Analyze the code against optimization rules
        matched_rules = self._find_matching_rules(code)

        if matched_rules:
            # Return the rule with highest improvement factor
            best_rule = max(matched_rules, key=lambda r: r.improvement_factor)

            return {
                "current_complexity": best_rule.current_complexity,
                "suggested_complexity": best_rule.suggested_complexity,
                "suggestion": best_rule.suggestion,
                "optimized_code": self._generate_optimized_code(code, best_rule),
                "estimated_improvement": best_rule.improvement_factor,
                "rules_matched": [rule.name for rule in matched_rules]
            }
        else:
            return {
                "current_complexity": "O(n) or better",
                "suggested_complexity": "O(n) or better",
                "suggestion": "Code appears well-optimized. Consider profiling for performance bottlenecks.",
                "optimized_code": None,
                "estimated_improvement": 0.05,
                "rules_matched": []
            }

    def _find_matching_rules(self, code: str) -> List[OptimizationRule]:
        """Find optimization rules that match the given code"""
        matched_rules = []

        for rule in self.rules:
            if re.search(rule.pattern, code, re.DOTALL | re.MULTILINE):
                matched_rules.append(rule)

        return matched_rules

    def _generate_optimized_code(self, original_code: str, rule: OptimizationRule) -> Optional[str]:
        """Generate optimized code example based on the rule"""
        # This is a simplified implementation - in a real system, this would
        # generate actual optimized code based on the specific rule
        optimization_examples = {
            "Nested Loop to Hash Lookup": self._optimize_nested_loops,
            "List Comprehension": self._optimize_list_comprehension,
            "String Concatenation in Loop": self._optimize_string_concatenation
        }

        if rule.name in optimization_examples:
            return optimization_examples[rule.name](original_code)

        return None

    def _optimize_nested_loops(self, code: str) -> str:
        """Generate example of converting nested loops to hash lookup"""
        example = """
# Before: O(n²) nested loops
for item in list1:
    for item2 in list2:
        if item == item2:
            print(item)

# After: O(n) with hash lookup
lookup = set(list2)
for item in list1:
    if item in lookup:
        print(item)
"""
        return example

    def _optimize_list_comprehension(self, code: str) -> str:
        """Generate example of converting loops to list comprehension"""
        example = """
# Before: Traditional loop with append
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# After: List comprehension
result = [transform(item) for item in items if condition(item)]
"""
        return example

    def _optimize_string_concatenation(self, code: str) -> str:
        """Generate example of optimizing string concatenation"""
        example = """
# Before: Inefficient string concatenation in loop
result = ""
for s in strings:
    result += s  # O(n²) complexity

# After: Efficient string joining
result = "".join(strings)  # O(n) complexity
"""
        return example

    def get_optimization_report(self, code: str) -> Dict:
        """Generate a comprehensive optimization report"""
        matched_rules = self._find_matching_rules(code)

        report = {
            "total_optimization_opportunities": len(matched_rules),
            "optimization_suggestions": [],
            "estimated_total_improvement": 0.0,
            "priority_suggestions": []
        }

        if matched_rules:
            # Calculate total potential improvement
            total_improvement = sum(rule.improvement_factor for rule in matched_rules)
            report["estimated_total_improvement"] = min(total_improvement, 1.0)  # Cap at 1.0

            # Add detailed suggestions
            for rule in matched_rules:
                report["optimization_suggestions"].append({
                    "rule_name": rule.name,
                    "suggestion": rule.suggestion,
                    "current_complexity": rule.current_complexity,
                    "suggested_complexity": rule.suggested_complexity,
                    "estimated_improvement": rule.improvement_factor
                })

            # Sort by improvement factor to show highest impact suggestions first
            report["priority_suggestions"] = sorted(
                report["optimization_suggestions"],
                key=lambda x: x["estimated_improvement"],
                reverse=True
            )

        return report