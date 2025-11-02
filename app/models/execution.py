"""Execution result models for tracking flow execution state."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    PENDING = "pending"


class TaskResult(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    status: ExecutionStatus = Field(..., description="Execution status")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Task output data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion timestamp")
    
    def is_successful(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS


class FlowExecutionState(BaseModel):
    execution_id: str = Field(..., description="Unique execution ID")
    flow_id: str = Field(..., description="Flow identifier")
    flow_name: str = Field(..., description="Flow name")
    status: ExecutionStatus = Field(..., description="Current status")
    current_task: Optional[str] = Field(default=None, description="Currently executing task")
    task_results: List[TaskResult] = Field(default_factory=list, description="Results of executed tasks")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Execution start time")
    completed_at: Optional[datetime] = Field(default=None, description="Execution completion time")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    def add_task_result(self, result: TaskResult):
        self.task_results.append(result)
    
    def get_last_task_result(self) -> Optional[TaskResult]:
        return self.task_results[-1] if self.task_results else None


class ExecutionResult(BaseModel):
    execution_id: str = Field(..., description="Execution ID")
    flow_id: str = Field(..., description="Flow ID")
    status: ExecutionStatus = Field(..., description="Final status")
    message: str = Field(..., description="Result message")
    execution_state: FlowExecutionState = Field(..., description="Detailed execution information")
