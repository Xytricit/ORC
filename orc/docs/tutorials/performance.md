# Performance Optimization with ORC

Learn how to identify and fix performance issues in your code.

## Overview

ORC can help you find:
- Algorithmic inefficiencies (O(n²) → O(n))
- Memory leaks
- Unnecessary computations
- Slow database queries
- Large functions
- Inefficient loops

## Quick Start

```bash
# Run performance analysis
orc analyze --performance
```

## Common Performance Issues

### 1. Nested Loops (O(n²))

**Problem:**
```python
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
```

**ORC Output:**
```
⚠️  Nested loops detected
📁 File: src/utils.py:45
⏱️  Complexity: O(n²)
💡 Suggestion: Use set for O(n) solution
```

**Fixed:**
```python
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

### 2. Inefficient String Concatenation

**Problem:**
```python
def build_report(data):
    report = ""
    for item in data:
        report += f"{item['name']}: {item['value']}\n"
    return report
```

**ORC Output:**
```
⚠️  String concatenation in loop
📁 File: src/reports.py:23
⏱️  Each iteration creates new string object
💡 Suggestion: Use list + join()
```

**Fixed:**
```python
def build_report(data):
    lines = [f"{item['name']}: {item['value']}" for item in data]
    return "\n".join(lines)
```

### 3. Unnecessary List Copying

**Problem:**
```python
def process_large_list(items):
    # Creates full copy of list
    sorted_items = sorted(items)
    filtered = [x for x in sorted_items if x > 10]
    return filtered
```

**ORC Output:**
```
⚠️  Large list copied unnecessarily
📁 File: src/processors.py:67
💾 Memory: Doubles memory usage
💡 Suggestion: Use generator or in-place operations
```

**Fixed:**
```python
def process_large_list(items):
    # Sort in place if items can be modified
    items.sort()
    # Or use generator
    return [x for x in items if x > 10]
```

### 4. Repeated Computations

**Problem:**
```python
def calculate_total(items):
    total = 0
    for item in items:
        # Calls expensive function repeatedly
        if is_valid(item):
            total += item.price * get_tax_rate()
    return total
```

**ORC Output:**
```
⚠️  Function called repeatedly in loop
📁 File: src/billing.py:89
🔄 Called get_tax_rate() 1000+ times
💡 Suggestion: Cache result outside loop
```

**Fixed:**
```python
def calculate_total(items):
    total = 0
    tax_rate = get_tax_rate()  # Call once
    for item in items:
        if is_valid(item):
            total += item.price * tax_rate
    return total
```

### 5. N+1 Query Problem

**Problem:**
```python
def get_users_with_posts():
    users = User.query.all()
    result = []
    for user in users:
        # Separate query for each user!
        posts = Post.query.filter_by(user_id=user.id).all()
        result.append({
            'user': user,
            'posts': posts
        })
    return result
```

**ORC Output:**
```
⚠️  N+1 query detected
📁 File: src/api/users.py:45
🐌 Makes 1 + N database queries
💡 Suggestion: Use JOIN or eager loading
```

**Fixed:**
```python
def get_users_with_posts():
    # SQLAlchemy
    users = User.query.options(
        joinedload(User.posts)
    ).all()
    
    # Or raw SQL with JOIN
    query = """
        SELECT u.*, p.*
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
    """
    return execute_query(query)
```

## Using AI for Optimization

### Ask for Specific Help

```bash
orc chat
```

```
You: How can I optimize this function?
[paste code]

🤖: I see several optimization opportunities:

1. Line 5: Nested loop creates O(n²) complexity
   Replace with hash table for O(n) solution
   
2. Line 12: String concatenation in loop
   Use list and join() instead
   
3. Line 18: Repeated calculation
   Cache the result before the loop

Here's the optimized version:
[optimized code]

Performance improvement: ~10x faster for n=1000
```

### Get Algorithm Suggestions

```
You: What's a better algorithm for finding duplicates?

🤖: For finding duplicates, here are the options:

1. Set-based (O(n)) - Best for most cases:
   [code example]
   
2. Counter (O(n)) - If you need counts:
   [code example]
   
3. Sorted + compare (O(n log n)) - Memory efficient:
   [code example]

I recommend option 1 for your use case.
```

## Profiling Integration

### Python: cProfile

```python
# profile_code.py
import cProfile
import pstats

def main():
    # Your code here
    pass

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    
    main()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### JavaScript: Performance API

```javascript
// Measure function performance
const start = performance.now();
myFunction();
const end = performance.now();
console.log(`Execution time: ${end - start}ms`);
```

### Combine with ORC

```bash
# 1. Run ORC analysis
orc analyze --performance --output issues.json

# 2. Profile identified functions
python profile_code.py

# 3. Compare results
orc chat "Compare profiling results with your analysis"
```

## Performance Testing

### Before & After

```python
import time

def benchmark(func, *args, runs=100):
    times = []
    for _ in range(runs):
        start = time.time()
        func(*args)
        end = time.time()
        times.append(end - start)
    
    avg = sum(times) / len(times)
    print(f"Average: {avg*1000:.2f}ms")
    return avg

# Test old implementation
old_time = benchmark(old_function, test_data)

# Test new implementation
new_time = benchmark(new_function, test_data)

# Calculate improvement
improvement = ((old_time - new_time) / old_time) * 100
print(f"Improvement: {improvement:.1f}%")
```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << EOF
from locust import HttpUser, task

class MyUser(HttpUser):
    @task
    def test_endpoint(self):
        self.client.get("/api/users")
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:5000
```

## Optimization Checklist

### Algorithms
- [ ] Replace O(n²) with O(n) or O(n log n)
- [ ] Use appropriate data structures (dict/set vs list)
- [ ] Avoid unnecessary sorting
- [ ] Cache computed results

### Memory
- [ ] Use generators for large datasets
- [ ] Avoid unnecessary copies
- [ ] Clear large objects when done
- [ ] Use memory-efficient data types

### Database
- [ ] Fix N+1 queries
- [ ] Add indexes to frequently queried columns
- [ ] Use connection pooling
- [ ] Batch operations when possible
- [ ] Use SELECT only needed columns

### I/O
- [ ] Read files in chunks, not all at once
- [ ] Use async I/O for concurrent operations
- [ ] Cache frequently accessed data
- [ ] Compress large responses

### Code Structure
- [ ] Break large functions into smaller ones
- [ ] Remove redundant calculations
- [ ] Use built-in functions (they're optimized)
- [ ] Avoid premature optimization

## Framework-Specific Tips

### Django

```python
# Bad: N+1 queries
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # Separate query!

# Good: Use select_related
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # No extra query

# Bad: Load everything
all_users = User.objects.all()

# Good: Paginate or filter
users = User.objects.all()[:100]
```

### Flask

```python
# Use caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/expensive')
@cache.cached(timeout=300)  # Cache for 5 minutes
def expensive_operation():
    # Expensive computation
    return result

# Use blueprints for organization
from flask import Blueprint

api = Blueprint('api', __name__)

@api.route('/users')
def users():
    return get_users()
```

### React

```javascript
// Use memo for expensive computations
const expensiveValue = useMemo(() => {
    return computeExpensiveValue(data);
}, [data]);

// Use callback to prevent re-renders
const handleClick = useCallback(() => {
    doSomething();
}, [dependency]);

// Lazy load components
const HeavyComponent = lazy(() => import('./HeavyComponent'));
```

## Monitoring & Metrics

### Application Performance Monitoring (APM)

```python
# Integrate with New Relic, DataDog, etc.
import newrelic.agent

@newrelic.agent.function_trace()
def my_function():
    # Your code
    pass
```

### Custom Metrics

```python
import time
from functools import wraps

def track_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        # Log to monitoring system
        log_metric(f"{func.__name__}.duration", duration)
        
        return result
    return wrapper

@track_performance
def important_function():
    # Your code
    pass
```

## CI/CD Integration

```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run ORC Performance Analysis
        run: |
          pip install orc-cli
          orc init
          orc index
          orc analyze --performance --output perf.json
      
      - name: Check for regressions
        run: |
          python scripts/check_performance.py perf.json
```

## Summary

Key takeaways:
- ✅ Use ORC to identify bottlenecks
- ✅ Fix algorithmic issues first (biggest impact)
- ✅ Profile before and after changes
- ✅ Test with realistic data sizes
- ✅ Monitor performance in production
- ✅ Automate performance checks in CI/CD

## Next Steps

- [Configuration](../configuration.md) - Configure performance thresholds
- [CLI Reference](../cli/README.md) - All analysis options
- [Using AI Chat](ai_chat.md) - Get optimization suggestions

Happy optimizing! ⚡
