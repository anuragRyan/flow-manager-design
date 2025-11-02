# Flow Manager Design Explanation

## Overview

The Flow Manager is a microservice designed to execute tasks sequentially with conditional branching logic. It provides a flexible, generic framework for defining and executing complex workflows.

## Architecture Components

### 1. Data Models (`app/models/`)

#### Flow Definition
- **Task**: Represents a single unit of work with a name and description
- **Condition**: Defines branching logic based on task outcomes
- **Flow**: Complete workflow definition containing tasks and conditions

#### Execution Tracking
- **TaskResult**: Captures the outcome of a single task execution
- **FlowExecutionState**: Tracks the overall flow execution state
- **ExecutionResult**: Final result returned to API clients

### 2. Task Registry (`app/services/task_registry.py`)

The task registry implements a **Registry Pattern** for task management:

- **Dynamic Registration**: Tasks can be registered using the `@register_task` decorator
- **Decoupled Execution**: Task implementations are separated from flow logic
- **Extensibility**: New tasks can be added without modifying core code

#### Task Contract
Each task must:
- Be an async function
- Accept a `context` dictionary parameter
- Return a dictionary with:
  - `status`: "success" or "failure"
  - `data`: Optional output data
  - `error`: Optional error message

### 3. Flow Manager (`app/services/flow_manager.py`)

The Flow Manager is the core execution engine that orchestrates task execution.

#### Execution Algorithm

```
1. Initialize execution state
2. Set current_task = flow.start_task
3. While current_task != "end":
   a. Execute current_task
   b. Store task result
   c. Find condition for current_task
   d. Evaluate condition based on task result
   e. Determine next_task from condition
   f. Set current_task = next_task
4. Mark flow as complete
5. Return execution result
```

#### Key Design Decisions

**Sequential Execution**: Tasks run one at a time, ensuring predictable order and enabling each task to depend on previous results.

**Context Passing**: A shared context dictionary allows tasks to communicate data. Each task's results are automatically added to the context.

**Condition Evaluation**: After each task, conditions determine the next step:
- If task status matches condition's expected outcome → proceed to `target_task_success`
- If task status doesn't match → proceed to `target_task_failure`

**Termination**: Flow ends when:
- Next task is "end"
- An unhandled error occurs
- Maximum iterations reached (prevents infinite loops)

### 4. API Layer (`app/api/routes.py`)

RESTful API endpoints:

- `POST /api/v1/flows/execute`: Execute a flow from JSON definition
- `GET /api/v1/flows/executions/{id}`: Retrieve execution state
- `GET /api/v1/flows/executions`: List all executions
- `GET /health`: Health check

### 5. Task Implementations (`app/tasks/sample_tasks.py`)

Sample tasks demonstrate the pattern:

- **task1 (Fetch)**: Simulates data retrieval from external source
- **task2 (Process)**: Transforms data from previous task
- **task3 (Store)**: Persists processed data

## How Tasks Depend on Each Other

### Dependency Chain

```
task1 → condition_task1_result → task2 → condition_task2_result → task3 → end
   ↓                               ↓
  end                             end
```

1. **Data Dependencies**: Tasks access previous task results via the context:
   ```python
   task1_result = context.get("task1_result")
   ```

2. **Execution Dependencies**: Conditions control the flow:
   - task2 only executes if task1 succeeds
   - task3 only executes if task2 succeeds

3. **Context Accumulation**: The context grows as tasks execute:
   ```python
   context = {
       "task1_result": {...},
       "task2_result": {...},
       # Available to task3
   }
   ```

## Success/Failure Evaluation

### Task Level

Each task returns a status:
```python
{
    "status": "success",  # or "failure"
    "data": {...},
    "error": None
}
```

### Condition Evaluation

Conditions specify an expected outcome:
```json
{
    "source_task": "task1",
    "outcome": "success",
    "target_task_success": "task2",
    "target_task_failure": "end"
}
```

**Evaluation Logic**:
- Compare task result status with condition's expected outcome
- If they match → condition is satisfied → proceed to success target
- If they don't match → condition fails → proceed to failure target

### Example Scenarios

#### Scenario 1: All Tasks Succeed
```
task1 [success] → task2 [success] → task3 [success] → end
Result: Flow completes successfully
```

#### Scenario 2: task1 Fails
```
task1 [failure] → condition evaluates → end
Result: Flow terminates early
task2 and task3 never execute
```

#### Scenario 3: task2 Fails
```
task1 [success] → task2 [failure] → condition evaluates → end
Result: Flow terminates after task2
task3 never executes
```

## What Happens on Success/Failure?

### On Task Success

1. Task result is captured with status "success"
2. Task data is added to context
3. Condition is evaluated
4. If condition expects "success":
   - Flow proceeds to next task
5. If condition expects "failure":
   - Flow goes to failure path (usually "end")

### On Task Failure

1. Task result is captured with status "failure"
2. Error message is recorded
3. Condition is evaluated
4. If condition expects "failure":
   - Flow proceeds to designated path
5. If condition expects "success":
   - Flow goes to failure path (usually "end")

### Final Flow Status

The flow's final status is determined by:
- **SUCCESS**: All executed tasks completed successfully
- **FAILURE**: At least one task failed, or an error occurred
- Task results are preserved for audit and debugging

## Benefits of This Design

1. **Flexibility**: Generic framework works with any tasks and conditions
2. **Maintainability**: Clear separation of concerns
3. **Extensibility**: Easy to add new tasks and flows
4. **Observability**: Complete execution history and state tracking
5. **Reliability**: Error handling and validation at every level
6. **Testability**: Each component can be tested independently

## Example Flow Execution

Given the sample flow:

```json
{
  "flow": {
    "id": "flow123",
    "name": "Data processing flow",
    "start_task": "task1",
    "tasks": [...],
    "conditions": [...]
  }
}
```

**Execution Trace**:
1. Start: task1 (Fetch data)
2. Execute task1 → Success (fetched 3 records)
3. Evaluate condition_task1_result
   - task1 status: "success"
   - Expected outcome: "success"
   - Match! → Proceed to task2
4. Execute task2 (Process data) → Success (processed 3 records)
5. Evaluate condition_task2_result
   - task2 status: "success"
   - Expected outcome: "success"
   - Match! → Proceed to task3
6. Execute task3 (Store data) → Success (stored 3 records)
7. No more conditions → End
8. Final Status: SUCCESS

**Result**:
```json
{
  "execution_id": "exec_abc123",
  "status": "success",
  "task_results": [
    {"task_name": "task1", "status": "success", ...},
    {"task_name": "task2", "status": "success", ...},
    {"task_name": "task3", "status": "success", ...}
  ]
}
```
