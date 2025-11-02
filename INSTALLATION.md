# 🚀 Flow Manager - Installation & Testing Guide

## Prerequisites Check

Before you begin, ensure you have:
- ✅ Python 3.9 or higher installed
- ✅ pip (Python package manager)
- ✅ Terminal/Command line access

Verify Python installation:
```bash
python3 --version
# Should output: Python 3.9.x or higher
```

## Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd "/Users/aaryan/Desktop/Flow Manager"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv) prefix
```

**Note**: On Windows, use `venv\Scripts\activate` instead.

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- And other dependencies

### Step 4: Verify Installation

```bash
python verify.py
```

You should see all green checkmarks (✅) indicating successful installation.

### Step 5: Start the Server

```bash
uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Test the API

Open a **new terminal window** (keep the server running) and run:

```bash
# Activate virtual environment in new terminal
cd "/Users/aaryan/Desktop/Flow Manager"
source venv/bin/activate

# Run the test script
python test_flow.py
```

You should see output showing successful flow execution with all tasks completing.

## Quick Test Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000 in browser
- [ ] Can access http://localhost:8000/docs (Swagger UI)
- [ ] Health check returns {"status": "healthy"}
- [ ] Test script executes successfully
- [ ] All three tasks (task1, task2, task3) complete with success status

## Manual Testing via Browser

### 1. Open Interactive API Docs

Navigate to: http://localhost:8000/docs

### 2. Test Health Endpoint

- Click on `GET /health`
- Click "Try it out"
- Click "Execute"
- Should return `{"status": "healthy", ...}`

### 3. Execute Sample Flow

- Click on `POST /api/v1/flows/execute`
- Click "Try it out"
- Copy the contents of `flows/sample_flow.json` into the request body
- Click "Execute"
- Should return execution results with status "success"

## Testing with cURL

### Health Check
```bash
curl http://localhost:8000/health
```

### Execute Flow
```bash
curl -X POST "http://localhost:8000/api/v1/flows/execute" \
  -H "Content-Type: application/json" \
  -d @flows/sample_flow.json
```

### Get Execution State
```bash
# Replace {execution_id} with actual ID from previous response
curl "http://localhost:8000/api/v1/flows/executions/{execution_id}"
```

### List All Executions
```bash
curl "http://localhost:8000/api/v1/flows/executions"
```

## Testing with Python Script

Create a file `manual_test.py`:

```python
import requests
import json

# Test 1: Health check
print("Testing health check...")
response = requests.get("http://localhost:8000/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Execute flow
print("Executing sample flow...")
with open('flows/sample_flow.json', 'r') as f:
    flow_data = json.load(f)

response = requests.post(
    "http://localhost:8000/api/v1/flows/execute",
    json=flow_data
)
result = response.json()
print(f"Execution ID: {result['execution_id']}")
print(f"Status: {result['status']}")
print(f"Message: {result['message']}\n")

# Test 3: Get execution state
execution_id = result['execution_id']
print(f"Getting execution state for {execution_id}...")
response = requests.get(
    f"http://localhost:8000/api/v1/flows/executions/{execution_id}"
)
print(f"Found execution: {response.json()['flow_name']}\n")

print("✅ All tests passed!")
```

Run it:
```bash
python manual_test.py
```

## Expected Flow Execution Output

When you execute the sample flow, you should see:

```json
{
  "execution_id": "exec_xxxxx",
  "flow_id": "flow123",
  "status": "success",
  "message": "Flow 'Data processing flow' completed successfully. Executed 3 task(s).",
  "execution_state": {
    "task_results": [
      {
        "task_name": "task1",
        "status": "success",
        "data": {
          "records": [...],
          "total_count": 3
        }
      },
      {
        "task_name": "task2",
        "status": "success",
        "data": {
          "processed_records": [...],
          "processed_count": 3
        }
      },
      {
        "task_name": "task3",
        "status": "success",
        "data": {
          "stored_count": 3,
          "storage_location": "database://main/processed_data"
        }
      }
    ]
  }
}
```

## Docker Testing (Alternative)

If you prefer Docker:

```bash
# Build the image
docker build -t flow-manager .

# Run the container
docker run -p 8000:8000 flow-manager

# Or use Docker Compose
docker-compose up
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 is already in use"

**Solution**: Use a different port
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: "Permission denied" when running setup.sh

**Solution**: Make it executable
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: Server starts but can't execute flows

**Solution**: Check that tasks are registered
- Look for log message showing registered tasks
- Verify `app/tasks/sample_tasks.py` is being imported

### Issue: Virtual environment not activating

**Solution**: Make sure you're in the project directory
```bash
cd "/Users/aaryan/Desktop/Flow Manager"
source venv/bin/activate
```

## Verification Checklist

Before considering the installation complete, verify:

- ✅ All dependencies installed (`verify.py` passes)
- ✅ Server starts without errors
- ✅ Interactive docs accessible at /docs
- ✅ Sample flow executes successfully
- ✅ All three tasks complete with success status
- ✅ Execution state can be retrieved
- ✅ Health check responds

## Next Steps After Installation

1. ✅ Review the documentation:
   - `README.md` - Project overview
   - `DESIGN.md` - Architecture and design decisions
   - `API_DOCUMENTATION.md` - API reference
   - `PROJECT_SUMMARY.md` - Complete summary

2. ✅ Explore the interactive API docs:
   - http://localhost:8000/docs

3. ✅ Try creating custom flows:
   - Copy `flows/sample_flow.json`
   - Modify tasks and conditions
   - Execute your custom flow

4. ✅ Implement custom tasks:
   - Add new tasks in `app/tasks/sample_tasks.py`
   - Use the `@register_task` decorator
   - Test with custom flows

## Support

If you encounter any issues:

1. Check the server logs for error messages
2. Review the documentation files
3. Run `verify.py` to check module imports
4. Ensure virtual environment is activated
5. Verify all dependencies are installed

## Quick Command Reference

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify
python verify.py

# Run
uvicorn app.main:app --reload

# Test
python test_flow.py

# Docker
docker-compose up
```

Happy flow managing! 🎉
