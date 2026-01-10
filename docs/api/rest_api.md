# REST API Reference

The ORC REST API provides HTTP endpoints for remote analysis and integration.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Most endpoints require authentication. Generate an API token via the web dashboard.

```http
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

---

### Project Analysis

**POST** `/api/v1/analyze`

Analyze a project or specific files.

**Request Body:**
```json
{
  "path": "./src",
  "recursive": true,
  "include_patterns": ["*.py"],
  "exclude_patterns": ["*_test.py"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_files": 150,
    "total_lines": 15000,
    "complexity": {
      "average": 8.5,
      "max": 25,
      "hotspots": [...]
    },
    "dead_code": {
      "count": 12,
      "items": [...]
    }
  }
}
```

---

### Complexity Analysis

**GET** `/api/v1/complexity`

Get complexity analysis for the project.

**Query Parameters:**
- `threshold` (int): Minimum complexity to report (default: 10)
- `limit` (int): Maximum results to return (default: 50)

**Response:**
```json
{
  "functions": [
    {
      "name": "complex_function",
      "file": "module.py",
      "line": 42,
      "complexity": 15,
      "severity": "high"
    }
  ]
}
```

---

### Search Code

**GET** `/api/v1/search`

Search for code elements.

**Query Parameters:**
- `query` (string): Search pattern
- `type` (string): Element type (functions, classes, files)
- `limit` (int): Max results

**Response:**
```json
{
  "results": [
    {
      "name": "authenticate_user",
      "type": "function",
      "file": "auth.py",
      "line": 23
    }
  ]
}
```

---

### Project Statistics

**GET** `/api/v1/stats`

Get project statistics.

**Response:**
```json
{
  "files": 150,
  "lines": 15000,
  "functions": 500,
  "classes": 80,
  "languages": {
    "Python": 120,
    "JavaScript": 30
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Default: 100 requests per hour per token.

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Examples

### Python

```python
import requests

API_URL = "http://localhost:5000/api/v1"
TOKEN = "your-api-token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Analyze project
response = requests.post(
    f"{API_URL}/analyze",
    json={"path": "./src"},
    headers=headers
)

data = response.json()
print(f"Analyzed {data['data']['total_files']} files")
```

### cURL

```bash
# Get stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/v1/stats

# Analyze project
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": "./src"}' \
  http://localhost:5000/api/v1/analyze
```

### JavaScript

```javascript
const API_URL = 'http://localhost:5000/api/v1';
const TOKEN = 'your-api-token';

async function analyzeProject() {
  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ path: './src' })
  });
  
  const data = await response.json();
  console.log(data);
}
```
