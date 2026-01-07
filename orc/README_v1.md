# ORC (Optimization & Refactoring Catalyst) v1

ORC v1 is a codebase intelligence agent for Python projects that helps developers analyze, optimize, and understand their code. It features dead code detection, complexity analysis, dependency mapping, and natural language querying capabilities.

## Features

- **Dead Code Detection**: Identifies unused functions, classes, and files
- **Complexity Analysis**: Calculates algorithmic complexity and identifies performance hotspots
- **Dependency Analysis**: Maps relationships between modules and functions
- **Code Metrics**: Provides comprehensive project statistics
- **Pattern Detection**: Identifies code antipatterns and good practices
- **Optimization Suggestions**: Provides specific recommendations for code improvements
- **Natural Language Querying**: Query your codebase using plain English
- **Multi-language Support**: Primary focus on Python with support for JavaScript, TypeScript, and more

## Quick Start

### Installation

```bash
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```bash
# Initialize ORC in your project
orc init

# Index your codebase
orc index /path/to/your/project

# Analyze for issues
orc analyze

# Find dead code
orc dead

# Query using natural language
orc query "show circular dependencies"
orc query "find complex functions"
```

### Example Output

```
$ orc dead
Dead Code Findings:
[D-01] src/auth.py - unused_function
[D-02] src/utils.py - deprecated_helper

$ orc query "show complex functions"
High Complexity Functions
Function          File            Complexity    Lines
complex_algorithm src/algo.py     O(n²)         150
data_processor    src/process.py  O(n³)         200
```

## Architecture

ORC v1 follows a modular architecture:

- **Indexing**: Parses code using AST and builds structured representations
- **Storage**: Uses SQLite for efficient storage and retrieval
- **Analysis**: Performs dead code, complexity, dependency, and pattern analysis
- **Query Engine**: Processes natural language queries
- **CLI**: Command-line interface for human interaction
- **API**: REST API for AI tool integration

## Commands

### Core Commands
- `orc index <path>`: Index a codebase
- `orc analyze`: Run full analysis
- `orc dead`: Show dead code
- `orc query "<query>"`: Natural language query
- `orc serve`: Start web interface

### Management Commands
- `orc init`: Create configuration
- `orc config`: View/modify configuration
- `orc ignore <target>`: Ignore code permanently
- `orc explain <finding_id>`: Explain a finding
- `orc delete <finding_id>`: Delete dead code

## Configuration

ORC uses a `.orcrc` file for configuration:

```yaml
ignore:
  - 'tests/*'
  - 'venv/*'
  - 'node_modules/*'

dynamic_patterns:
  - 'eval'
  - 'getattr'
```

The `dynamic_patterns` key lists function or attribute names that the analysis treats as triggers for dynamic behavior detection — places where code is evaluated or attributes are accessed at runtime. Set `dynamic_patterns` to tune detection sensitivity and reduce false positives or false negatives. The example values `eval` and `getattr` are builtin functions that perform runtime evaluation and dynamic attribute access, respectively. You can add other builtins such as `exec`, specific third‑party API names used in your project, or (if supported) wildcards/regular expressions; remove or clear the `dynamic_patterns` key to disable dynamic-pattern detection.

## API

ORC provides a REST API for integration with AI tools. Below are the primary endpoints, their request/response schemas, examples, common errors, authentication requirements, and short usage snippets so reviewers can validate examples against the implementation.

### POST /api/context
- Purpose: Return a compressed context (string or base64) for AI queries for a given path or selection.
- Authentication: `Authorization: Bearer <token>` required. Rate limit: default 60 requests/min (adjustable in deployment).
- Request (JSON body):

```json
{
  "path": "string",            // required: project path or file path
  "max_tokens": 1000            // optional: max tokens or max length for returned context
}
```

- Response (200) schema:

```json
{
  "context": "string",        // compressed or plain context
  "length": 123                 // integer: length of returned context
}
```

- Example success payload:

```json
{
  "context": "<compressed-or-plain-text>",
  "length": 842
}
```

- Common errors:
  - `400 Bad Request` — missing or invalid `path` (e.g., `{ "error": "missing field 'path'" }`).
  - `401 Unauthorized` — missing/invalid token (e.g., `{ "error": "unauthorized" }`).
  - `429 Too Many Requests` — rate limit exceeded (e.g., `{ "error": "rate limit exceeded" }`).
  - `500 Internal Server Error` — server error (e.g., `{ "error": "internal error" }`).

- Usage snippets:

cURL:

```bash
curl -X POST https://your-orc-host/api/context \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"src/","max_tokens":800}'
```

Python (requests):

```python
import requests
resp = requests.post(
    'https://your-orc-host/api/context',
    headers={'Authorization': f'Bearer {TOKEN}'},
    json={'path':'src/','max_tokens':800}
)
print(resp.json())
```

### GET /api/deadcode
- Purpose: Return dead code findings for a project or path.
- Authentication: `Authorization: Bearer <token>` required. Rate limit: default 30 requests/min.
- Request: Query string parameters accepted:
  - `path` (string) — required: project or subpath to analyze (e.g., `?path=src/`).
  - `limit` (int) — optional: max findings to return.

- Response (200) schema:

```json
{
  "findings": [
    {
      "id": "D-01",
      "file": "src/utils.py",
      "symbol": "unused_function",
      "message": "unused function",
      "line": 42
    }
  ]
}
```

- Example success payload:

```json
{
  "findings": [
    {"id":"D-01","file":"src/auth.py","symbol":"old_helper","message":"unused function","line":10}
  ]
}
```

- Common errors:
  - `400 Bad Request` — missing `path` parameter (e.g., `{ "error": "missing 'path' query parameter" }`).
  - `401 Unauthorized` — invalid token.
  - `429 Too Many Requests` — rate limit exceeded.
  - `500 Internal Server Error` — server error.

- Usage snippets:

cURL:

```bash
curl -G "https://your-orc-host/api/deadcode" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "path=src/" --data-urlencode "limit=50"
```

Python (requests):

```python
import requests
resp = requests.get(
    'https://your-orc-host/api/deadcode',
    headers={'Authorization': f'Bearer {TOKEN}'},
    params={'path':'src/','limit':50}
)
print(resp.json())
```

### POST /api/query
- Purpose: Submit a natural-language query against the indexed codebase and return ranked answers or matches.
- Authentication: `Authorization: Bearer <token>` required. Rate limit: default 120 requests/min for interactive queries.
- Request (JSON body):

```json
{
  "query": "string",          // required: natural language query
  "top_k": 5                   // optional: number of top results to return
}
```

- Response (200) schema:

```json
{
  "results": [
    {
      "id": "R-1",
      "score": 0.93,
      "answer": "Matched function 'process_data' in src/process.py",
      "context": "..."
    }
  ]
}
```

- Example success payload:

```json
{
  "results": [
    {"id":"R-1","score":0.95,"answer":"Found complex function 'analyze' in src/analyzer.py","context":"def analyze(...):\n  ..."}
  ]
}
```

- Common errors:
  - `400 Bad Request` — missing `query` (e.g., `{ "error": "missing field 'query'" }`).
  - `401 Unauthorized` — invalid token.
  - `422 Unprocessable Entity` — query too long or invalid parameters.
  - `429 Too Many Requests` — rate limited.
  - `500 Internal Server Error`.

- Usage snippets:

cURL:

```bash
curl -X POST https://your-orc-host/api/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"find complex functions","top_k":3}'
```

Python (requests):

```python
import requests
resp = requests.post(
    'https://your-orc-host/api/query',
    headers={'Authorization': f'Bearer {TOKEN}'},
    json={'query':'find complex functions','top_k':3}
)
print(resp.json())
```

---

Notes:
- Each endpoint requires an `Authorization` header unless the server is explicitly configured to allow anonymous requests. Use short-lived tokens for interactive clients and long-lived service tokens for CI integrations.
- Rate limits mentioned are deployment defaults; consult your deployment config for exact values.
- Error bodies are JSON with an `error` field by default — implementers may add `code` or `details` fields for richer error handling.


## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
orc/
├── config/          # Configuration management
├── core/            # Indexing and analysis orchestration
├── parsers/         # Language-specific parsers
├── analysis/        # Analysis modules
├── storage/         # Database and caching
├── context/         # AI integration
├── optimization/    # Optimization engine
├── api/             # REST API
├── cli/             # Command-line interface
├── web/             # Web dashboard
├── tests/           # Test suite
└── docs/            # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue in the GitHub repository.