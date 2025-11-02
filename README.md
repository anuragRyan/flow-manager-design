# Flow Manager Microservice

A sophisticated flow execution engine that manages sequential task execution with conditional branching. The system evaluates task results and dynamically determines the flow path based on success or failure conditions.

## Architecture Overview

### Flow Design

The Flow Manager implements a directed graph execution model where:

1. **Task Dependencies**: Tasks are executed sequentially based on the flow definition. Each task's execution depends on the successful completion of its predecessor (or the initial start task).

2. **Success/Failure Evaluation**: 
   - Each task returns a result with a `status` field (`success` or `failure`)
   - Conditions evaluate the task outcome and determine the next step
   - The flow manager checks conditions after each task execution

3. **Conditional Branching**:
   - **Success Path**: If a task succeeds, the flow proceeds to `target_task_success`
   - **Failure Path**: If a task fails, the flow proceeds to `target_task_failure` (often "end")
   - **Flow Termination**: When "end" is reached, the flow execution completes

### Project Structure

```
flow-manager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── flow.py            # Flow, Task, Condition models
│   │   └── execution.py       # Execution result models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── flow_manager.py    # Core flow execution engine
│   │   └── task_registry.py   # Task implementation registry
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── sample_tasks.py    # Sample task implementations
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # Configuration management
│   └── utils/
│       ├── __init__.py
│       └── logger.py          # Logging utilities
├── flows/
│   └── sample_flow.json       # Sample flow definition
├── requirements.txt
├── Dockerfile
└── README.md
```

## Features

- ✅ Generic flow execution engine supporting any number of tasks and conditions
- ✅ Dynamic task registration and execution
- ✅ Conditional branching based on task outcomes
- ✅ RESTful API for flow management
- ✅ Comprehensive logging and error handling
- ✅ Pydantic models for data validation
- ✅ Asynchronous task execution support
- ✅ Flow execution history and state tracking

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### 1. Execute Flow
```
POST /api/v1/flows/execute
Content-Type: application/json

Body: {flow definition JSON}
```

### 2. Get Flow Execution Status
```
GET /api/v1/flows/executions/{execution_id}
```

### 3. List All Executions
```
GET /api/v1/flows/executions
```

### 4. Health Check
```
GET /health
```

## Usage Example

```bash
curl -X POST "http://localhost:8000/api/v1/flows/execute" \
  -H "Content-Type: application/json" \
  -d @flows/sample_flow.json
```

## Flow Definition Schema

See `flows/sample_flow.json` for a complete example.

## Docker Support

Build and run with Docker:

```bash
docker build -t flow-manager .
docker run -p 8000:8000 flow-manager
```

## Development

- **Testing**: Run tests with `pytest`
- **Linting**: Use `pylint` or `flake8`
- **Formatting**: Use `black` for code formatting

## License

MIT
