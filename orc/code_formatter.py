def format_optimization_example(current, optimized, explanation):
    return f"""
Current implementation at line {current['line']}:

{current['description']}

Execution pattern:
{current['pattern']}

Optimization strategy:

{explanation}

New complexity: {optimized['complexity']}
New operation count: {optimized['ops']}
Estimated new runtime: {optimized['runtime']}
Performance improvement: {optimized['improvement']}% reduction
"""

# Example usage
if __name__ == "__main__":
    current = {
        'line': 45,
        'description': 'Nested loops iterating over user data',
        'pattern': 'for user in users:\n    for item in items:\n        process(user, item)'
    }
    optimized = {
        'complexity': 'O(n log n)',
        'ops': '1,200 operations',
        'runtime': '0.3s',
        'improvement': 85
    }
    explanation = "Use a hash map to reduce nested iteration complexity"
    
    print(format_optimization_example(current, optimized, explanation))