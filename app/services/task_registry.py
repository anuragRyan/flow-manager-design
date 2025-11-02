"""Task registry for managing and executing tasks.

This module provides a registry pattern for task management, allowing
dynamic task registration and execution.
"""

from typing import Callable, Dict, Any
from functools import wraps
import logging

from app.models.execution import TaskResult, ExecutionStatus

logger = logging.getLogger(__name__)

_TASK_REGISTRY: Dict[str, Callable] = {}


def register_task(task_name: str):
    def decorator(func: Callable):
        if task_name in _TASK_REGISTRY:
            logger.warning(f"Task '{task_name}' already registered. Overwriting.")
        _TASK_REGISTRY[task_name] = func
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class TaskRegistry:
    @staticmethod
    def register(task_name: str, task_func: Callable):
        _TASK_REGISTRY[task_name] = task_func
        logger.info(f"Registered task: {task_name}")
    
    @staticmethod
    def get_task(task_name: str) -> Callable:
        if task_name not in _TASK_REGISTRY:
            raise KeyError(f"Task '{task_name}' not found in registry")
        return _TASK_REGISTRY[task_name]
    
    @staticmethod
    def is_registered(task_name: str) -> bool:
        return task_name in _TASK_REGISTRY
    
    @staticmethod
    async def execute_task(
        task_name: str,
        context: Dict[str, Any] = None
    ) -> TaskResult:
        from datetime import datetime
        
        if context is None:
            context = {}
        
        result = TaskResult(
            task_name=task_name,
            status=ExecutionStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        try:
            task_func = TaskRegistry.get_task(task_name)
            logger.info(f"Executing task: {task_name}")
            
            task_output = await task_func(context=context)
            
            if isinstance(task_output, dict):
                status = task_output.get('status', 'failure')
                data = task_output.get('data')
                error = task_output.get('error')
                
                result.status = (
                    ExecutionStatus.SUCCESS if status == 'success'
                    else ExecutionStatus.FAILURE
                )
                result.data = data
                result.error = error
            else:
                result.status = ExecutionStatus.FAILURE
                result.error = f"Invalid task output format: {type(task_output)}"
            
            result.completed_at = datetime.utcnow()
            logger.info(
                f"Task '{task_name}' completed with status: {result.status}"
            )
            
        except KeyError as e:
            result.status = ExecutionStatus.FAILURE
            result.error = f"Task not found: {str(e)}"
            result.completed_at = datetime.utcnow()
            logger.error(f"Task '{task_name}' not found: {e}")
            
        except Exception as e:
            result.status = ExecutionStatus.FAILURE
            result.error = f"Task execution failed: {str(e)}"
            result.completed_at = datetime.utcnow()
            logger.error(f"Task '{task_name}' failed: {e}", exc_info=True)
        
        return result
    
    @staticmethod
    def list_tasks() -> list:
        return list(_TASK_REGISTRY.keys())
    
    @staticmethod
    def clear():
        _TASK_REGISTRY.clear()
        logger.info("Task registry cleared")
