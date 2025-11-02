"""Flow definition models using Pydantic for validation."""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Task(BaseModel):
    name: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")


class Condition(BaseModel):
    name: str = Field(..., description="Unique condition identifier")
    description: str = Field(..., description="Condition description")
    source_task: str = Field(..., description="Task to evaluate")
    outcome: str = Field(..., description="Expected outcome (success/failure)")
    target_task_success: str = Field(..., description="Next task if condition is met")
    target_task_failure: str = Field(..., description="Next task if condition fails")
    
    @validator('outcome')
    def validate_outcome(cls, v):
        if v not in ['success', 'failure']:
            raise ValueError("Outcome must be 'success' or 'failure'")
        return v


class Flow(BaseModel):
    id: str = Field(..., description="Unique flow identifier")
    name: str = Field(..., description="Flow name")
    start_task: str = Field(..., description="Initial task to execute")
    tasks: List[Task] = Field(..., description="List of tasks")
    conditions: List[Condition] = Field(..., description="List of conditions")
    
    @validator('tasks')
    def validate_tasks_not_empty(cls, v):
        if not v:
            raise ValueError("Flow must have at least one task")
        return v
    
    @validator('start_task')
    def validate_start_task_exists(cls, v, values):
        if 'tasks' in values:
            task_names = [task.name for task in values['tasks']]
            if v not in task_names:
                raise ValueError(f"start_task '{v}' not found in tasks list")
        return v
    
    def get_task(self, task_name: str) -> Optional[Task]:
        for task in self.tasks:
            if task.name == task_name:
                return task
        return None
    
    def get_condition_for_task(self, task_name: str) -> Optional[Condition]:
        for condition in self.conditions:
            if condition.source_task == task_name:
                return condition
        return None
