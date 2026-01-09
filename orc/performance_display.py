def format_performance_bottleneck(file, line, issue, scale, frequency, runtime, optimization):
    return f"""
{file} line {line}
Algorithm: {issue['algorithm']}
Context: {issue['context']}
Scale: {scale}
Frequency: {frequency} calls per day
Current runtime: {runtime} average
Optimization potential: {optimization}% reduction
"""

def format_bottleneck_summary(count, total_improvement, effort):
    return f"""
Total estimated performance gain: {total_improvement}x faster
Estimated implementation effort: {effort} hours

Which bottleneck would you like details on?
"""

# Example usage
if __name__ == "__main__":
    issue = {
        'algorithm': 'O(n²) bubble sort',
        'context': 'Data processing in user dashboard'
    }
    print(format_performance_bottleneck(
        "user_dashboard.py", 142, issue, "Large", 1500, "2.3s", 78
    ))
    print(format_bottleneck_summary(3, 4.2, 8))