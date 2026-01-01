# API Reference

Complete documentation of all API endpoints.

## Base URL

Development: `http://localhost:5000/api`
Production: `https://your-domain.com/api`

## Authentication

Currently, no authentication is required. For production deployments, add authentication headers.

## Endpoints

### Health Check

Check API status.

**Request:**
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Validate YAML

Validate GitLab CI YAML syntax.

**Request:**
```
POST /validate
Content-Type: application/json

{
  "yaml_content": "stages:\n  - build\n..."
}
```

**Response (Valid):**
```json
{
  "success": true,
  "valid": true,
  "message": "YAML is valid"
}
```

**Response (Invalid):**
```json
{
  "success": true,
  "valid": false,
  "error": "mapping values are not allowed here..."
}
```

---

### Analyze Pipeline

Analyze GitLab CI and generate dependency graph.

**Request:**
```
POST /analyze
Content-Type: application/json

{
  "yaml_content": "..."
}
```

**Response:**
```json
{
  "success": true,
  "graph": {
    "nodes": [
      {
        "id": "build",
        "label": "build",
        "stage": "build",
        "type": "regular",
        "allowFailure": false
      }
    ],
    "edges": [
      {
        "source": "build",
        "target": "test",
        "type": "needs"
      }
    ],
    "variables": {
      "VAR_NAME": "value"
    },
    "secrets": ["SECRET_KEY"],
    "stages": ["build", "test"]
  },
  "metrics": {
    "total_nodes": 2,
    "total_edges": 1,
    "total_stages": 2,
    "total_variables": 1,
    "total_secrets": 1,
    "cycles": 0,
    "critical_path_length": 2,
    "avg_job_dependencies": 0.5
  },
  "cycles": [],
  "critical_path": ["build", "test"],
  "job_references": {
    "build": [],
    "test": ["build"]
  },
  "variables": {
    "VAR_NAME": {
      "value": "value",
      "protected": false,
      "masked": false,
      "scope": "global"
    }
  },
  "secrets": [
    {
      "name": "SECRET_KEY",
      "type": "env",
      "description": "Protected variable"
    }
  ]
}
```

---

### Convert to GitHub Actions

Convert GitLab CI to GitHub Actions workflow.

**Request:**
```
POST /convert
Content-Type: application/json

{
  "yaml_content": "..."
}
```

**Response:**
```json
{
  "success": true,
  "github_workflow": "name: CI/CD Pipeline\non:\n  push:\n    branches: [main]\njobs:\n...",
  "gitlab_config": {
    "stages": ["build", "test"],
    "jobs": [
      {
        "name": "build",
        "stage": "build",
        "image": "python:3.11",
        "allow_failure": false,
        "when": "on_success",
        "dependencies": [],
        "needs": []
      }
    ],
    "variables": [
      {
        "name": "VAR_NAME",
        "value": "value",
        "protected": false,
        "masked": false
      }
    ],
    "secrets": [
      {
        "name": "SECRET",
        "type": "env",
        "description": "Secret variable"
      }
    ]
  }
}
```

---

### Upload File

Upload and process GitLab CI YAML file.

**Request:**
```
POST /upload
Content-Type: multipart/form-data

file: <.yaml or .yml file>
```

**Response:**
```json
{
  "success": true,
  "filename": "gitlab-ci.yaml",
  "gitlab_config": {
    "stages": ["build", "test"],
    "jobs_count": 2,
    "variables_count": 1,
    "secrets_count": 1
  },
  "graph": {
    "nodes": [...],
    "edges": [...],
    "variables": {...},
    "secrets": [...],
    "stages": [...]
  },
  "github_workflow": "...",
  "metrics": {...}
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Description of what went wrong"
}
```

### Common Status Codes

- `200` OK - Request successful
- `400` Bad Request - Missing or invalid parameters
- `404` Not Found - Endpoint doesn't exist
- `500` Internal Server Error - Server error

---

## Request/Response Sizes

- Maximum request size: **16 MB**
- Maximum YAML file size: **16 MB**
- Typical response time: **100-500ms**

---

## Rate Limiting

Currently no rate limiting. For production, consider implementing:

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/convert', methods=['POST'])
@limiter.limit("100 per hour")
def convert(): ...
```

---

## CORS Headers

All endpoints support CORS. In production, configure:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## Examples

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:5000/api/convert', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    yaml_content: '...'
  })
});

const result = await response.json();
```

### Python/Requests

```python
import requests

response = requests.post(
    'http://localhost:5000/api/convert',
    json={'yaml_content': '...'}
)

result = response.json()
```

### cURL

```bash
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"yaml_content":"..."}'
```

---

## Version History

### v1.0.0
- Initial release
- All endpoints functional
- Full GitLab to GitHub conversion
- Dependency graph generation
