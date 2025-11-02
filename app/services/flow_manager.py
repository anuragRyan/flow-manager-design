"""Flow Manager - Core flow execution engine.

This module implements the main flow execution logic, handling sequential
task execution and conditional branching based on task outcomes.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.models.flow import Flow
from app.models.execution import (
    FlowExecutionState,
    ExecutionStatus,
    ExecutionResult,
)
from app.services.task_registry import TaskRegistry

logger = logging.getLogger(__name__)


class FlowManager:
    def __init__(self):
        self.execution_states: Dict[str, FlowExecutionState] = {}
    
    async def execute_flow(
        self,
        flow: Flow,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        execution_state = FlowExecutionState(
            execution_id=execution_id,
            flow_id=flow.id,
            flow_name=flow.name,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )
        
        self.execution_states[execution_id] = execution_state
        
        logger.info(
            f"Starting flow execution: {execution_id} "
            f"for flow '{flow.name}' (ID: {flow.id})"
        )
        
        try:
            await self._run_flow(flow, execution_state, context or {})
            
            if execution_state.status == ExecutionStatus.RUNNING:
                execution_state.status = ExecutionStatus.SUCCESS
            
            execution_state.completed_at = datetime.now(timezone.utc)
            
            logger.info(
                f"Flow execution {execution_id} completed "
                f"with status: {execution_state.status}"
            )
            
            return ExecutionResult(
                execution_id=execution_id,
                flow_id=flow.id,
                status=execution_state.status,
                message=self._generate_result_message(execution_state),
                execution_state=execution_state
            )
            
        except Exception as e:
            execution_state.status = ExecutionStatus.FAILURE
            execution_state.error = str(e)
            execution_state.completed_at = datetime.now(timezone.utc)
            
            logger.error(
                f"Flow execution {execution_id} failed: {e}",
                exc_info=True
            )
            
            return ExecutionResult(
                execution_id=execution_id,
                flow_id=flow.id,
                status=ExecutionStatus.FAILURE,
                message=f"Flow execution failed: {str(e)}",
                execution_state=execution_state
            )
    
    async def _run_flow(
        self,
        flow: Flow,
        execution_state: FlowExecutionState,
        context: Dict[str, Any]
    ):
        current_task_name = flow.start_task
        max_iterations = 100
        iteration_count = 0
        
        while current_task_name != "end" and iteration_count < max_iterations:
            iteration_count += 1
            
            task = flow.get_task(current_task_name)
            if not task:
                raise ValueError(f"Task '{current_task_name}' not found in flow")
            
            execution_state.current_task = current_task_name
            
            logger.info(f"Executing task: {current_task_name}")
            
            task_result = await TaskRegistry.execute_task(
                current_task_name,
                context
            )
            
            execution_state.add_task_result(task_result)
            
            if task_result.data:
                context[f"{current_task_name}_result"] = task_result.data
            
            condition = flow.get_condition_for_task(current_task_name)
            
            if not condition:
                logger.info(
                    f"No condition found for task '{current_task_name}'. "
                    "Ending flow."
                )
                break
            
            next_task = self._evaluate_condition(condition, task_result)
            
            logger.info(
                f"Condition '{condition.name}' evaluated. "
                f"Next task: {next_task}"
            )
            
            current_task_name = next_task
        
        execution_state.current_task = None
        
        if iteration_count >= max_iterations:
            raise RuntimeError(
                "Flow execution exceeded maximum iterations. "
                "Possible infinite loop detected."
            )
    
    def _evaluate_condition(
        self,
        condition,
        task_result
    ) -> str:
        task_status = task_result.status.value
        expected_outcome = condition.outcome
        
        if task_status == expected_outcome:
            next_task = condition.target_task_success
            logger.debug(
                f"Task '{task_result.task_name}' status '{task_status}' "
                f"matches expected outcome '{expected_outcome}'. "
                f"Proceeding to '{next_task}'"
            )
        else:
            next_task = condition.target_task_failure
            logger.debug(
                f"Task '{task_result.task_name}' status '{task_status}' "
                f"does not match expected outcome '{expected_outcome}'. "
                f"Proceeding to '{next_task}'"
            )
        
        return next_task
    
    def _generate_result_message(self, execution_state: FlowExecutionState) -> str:
        if execution_state.status == ExecutionStatus.SUCCESS:
            return (
                f"Flow '{execution_state.flow_name}' completed successfully. "
                f"Executed {len(execution_state.task_results)} task(s)."
            )
        elif execution_state.status == ExecutionStatus.FAILURE:
            failed_task = None
            for result in execution_state.task_results:
                if result.status == ExecutionStatus.FAILURE:
                    failed_task = result.task_name
                    break
            
            if failed_task:
                return (
                    f"Flow '{execution_state.flow_name}' failed at "
                    f"task '{failed_task}'."
                )
            else:
                return f"Flow '{execution_state.flow_name}' failed."
        else:
            return f"Flow '{execution_state.flow_name}' status: {execution_state.status}"
    
    def get_execution_state(self, execution_id: str) -> Optional[FlowExecutionState]:
        return self.execution_states.get(execution_id)
    
    def list_executions(self) -> list[FlowExecutionState]:
        return list(self.execution_states.values())
