# Flow Manager API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, implement JWT or API key authentication.

## Endpoints

### 1. Execute Flow

Execute a flow definition and get the execution result.

**Endpoint**: `POST /api/v1/flows/execute`

**Request Body**:
```json
{
  "flow": {
    "id": "string",
    "name": "string",
    "start_task": "string",
    "tasks": [
      {
        "name": "string",
        "description": "string"
      }
    ],
    "conditions": [
      {
        "name": "string",
        "description": "string",
        "source_task": "string",
        "outcome": "success|failure",
        "target_task_success": "string",
        "target_task_failure": "string"
      }
    ]
  }
}
```

**Success Response** (200 OK):
```json
{
  "execution_id": "exec_abc123",
  "flow_id": "flow123",
  "status": "success",
  "message": "Flow completed successfully. Executed 3 task(s).",
  "execution_state": {
    "execution_id": "exec_abc123",
    "flow_id": "flow123",
    "flow_name": "Data processing flow",
    "status": "success",
    "current_task": null,
    "task_results": [
      {
        "task_name": "task1",
        "status": "success",
        "data": {
          "records": [...],
          "total_count": 3
        },
        "error": null,
        "started_at": "2025-10-28T10:00:00Z",
        "completed_at": "2025-10-28T10:00:01Z"
      }
    ],
    "started_at": "2025-10-28T10:00:00Z",
    "completed_at": "2025-10-28T10:00:05Z",
    "error": null
  }
}
```

**Error Responses**:

- `400 Bad Request`: Invalid flow definition
```json
{
  "detail": "Invalid flow definition: start_task 'invalid' not found in tasks list"
}
```

- `500 Internal Server Error`: Execution failure
```json
{
  "detail": "Flow execution failed: ..."
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/flows/execute" \
  -H "Content-Type: application/json" \
  -d @flows/sample_flow.json
```

**Python Example**:
```python
import requests

with open('flows/sample_flow.json') as f:
    flow_data = json.load(f)

response = requests.post(
    'http://localhost:8000/api/v1/flows/execute',
    json=flow_data
)

result = response.json()
print(f"Execution ID: {result['execution_id']}")
print(f"Status: {result['status']}")
```

---

### 2. Get Execution State

Retrieve the execution state for a specific execution.

**Endpoint**: `GET /api/v1/flows/executions/{execution_id}`

**Path Parameters**:
- `execution_id` (string, required): Unique execution identifier

**Success Response** (200 OK):
```json
{
  "execution_id": "exec_abc123",
  "flow_id": "flow123",
  "flow_name": "Data processing flow",
  "status": "success",
  "current_task": null,
  "task_results": [...],
  "started_at": "2025-10-28T10:00:00Z",
  "completed_at": "2025-10-28T10:00:05Z",
  "error": null
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Execution 'exec_invalid' not found"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/flows/executions/exec_abc123"
```

---

### 3. List All Executions

Retrieve all flow execution states.

**Endpoint**: `GET /api/v1/flows/executions`

**Success Response** (200 OK):
```json
[
  {
    "execution_id": "exec_abc123",
    "flow_id": "flow123",
    "flow_name": "Data processing flow",
    "status": "success",
    "current_task": null,
    "task_results": [...],
    "started_at": "2025-10-28T10:00:00Z",
    "completed_at": "2025-10-28T10:00:05Z",
    "error": null
  },
  {
    "execution_id": "exec_def456",
    "flow_id": "flow456",
    "flow_name": "Another flow",
    "status": "failure",
    "current_task": null,
    "task_results": [...],
    "started_at": "2025-10-28T10:05:00Z",
    "completed_at": "2025-10-28T10:05:02Z",
    "error": "Task execution failed"
  }
]
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/flows/executions"
```

---

### 4. Health Check

Check if the service is running.

**Endpoint**: `GET /health`

**Success Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Flow Manager",
  "version": "1.0.0"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/health"
```

---

### 5. Root Endpoint

Get API information.

**Endpoint**: `GET /`

**Success Response** (200 OK):
```json
{
  "service": "Flow Manager",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "api_prefix": "/api/v1"
}
```

---

## Interactive API Documentation

### Swagger UI
Access interactive API documentation at:
```
http://localhost:8000/docs
```

### ReDoc
Alternative API documentation at:
```
http://localhost:8000/redoc
```

---

## Flow Definition Schema

### Task Object
```json
{
  "name": "string (required, unique)",
  "description": "string (required)"
}
```

### Condition Object
```json
{
  "name": "string (required, unique)",
  "description": "string (required)",
  "source_task": "string (required, must reference existing task)",
  "outcome": "success|failure (required)",
  "target_task_success": "string (required, task name or 'end')",
  "target_task_failure": "string (required, task name or 'end')"
}
```

### Flow Object
```json
{
  "id": "string (required, unique)",
  "name": "string (required)",
  "start_task": "string (required, must reference existing task)",
  "tasks": "array of Task objects (required, min 1)",
  "conditions": "array of Condition objects (required)"
}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Examples

### Example 1: Simple Linear Flow

```json
{
  "flow": {
    "id": "simple_flow",
    "name": "Simple linear flow",
    "start_task": "task1",
    "tasks": [
      {"name": "task1", "description": "First task"},
      {"name": "task2", "description": "Second task"}
    ],
    "conditions": [
      {
        "name": "cond1",
        "description": "Check task1",
        "source_task": "task1",
        "outcome": "success",
        "target_task_success": "task2",
        "target_task_failure": "end"
      }
    ]
  }
}
```

### Example 2: Flow with Error Handling

```json
{
  "flow": {
    "id": "error_handling_flow",
    "name": "Flow with error handling",
    "start_task": "validate_data",
    "tasks": [
      {"name": "validate_data", "description": "Validate input"},
      {"name": "process_data", "description": "Process valid data"},
      {"name": "send_notification", "description": "Notify on failure"}
    ],
    "conditions": [
      {
        "name": "validate_check",
        "description": "Check validation",
        "source_task": "validate_data",
        "outcome": "success",
        "target_task_success": "process_data",
        "target_task_failure": "send_notification"
      },
      {
        "name": "process_check",
        "description": "Check processing",
        "source_task": "process_data",
        "outcome": "success",
        "target_task_success": "end",
        "target_task_failure": "send_notification"
      }
    ]
  }
}
```

---

## Rate Limiting

Currently not implemented. Consider adding rate limiting for production use.

## Versioning

API version is included in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.
