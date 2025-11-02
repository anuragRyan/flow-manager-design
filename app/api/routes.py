"""API routes for Flow Manager.

This module defines all REST API endpoints for the Flow Manager microservice.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.flow import Flow
from app.models.execution import ExecutionResult, FlowExecutionState
from app.models.auth import User, UserRole
from app.services.flow_manager import FlowManager
from app.api.dependencies import RoleChecker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["flows"])
flow_manager = FlowManager()
require_user = RoleChecker(UserRole.USER)
require_viewer = RoleChecker(UserRole.VIEWER)


@router.post("/flows/execute", response_model=ExecutionResult, status_code=status.HTTP_200_OK)
async def execute_flow(
    flow_request: dict,
    current_user: User = Depends(require_user)
):
    try:
        flow_data = flow_request.get("flow")
        if not flow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request must contain a 'flow' object"
            )
        
        flow = Flow(**flow_data)
        
        logger.info(
            f"User '{current_user.username}' executing flow: {flow.id}"
        )
        
        result = await flow_manager.execute_flow(flow)
        
        return result
        
    except ValueError as e:
        logger.error(f"Flow validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid flow definition: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Flow execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Flow execution failed: {str(e)}"
        )


@router.get("/flows/executions/{execution_id}", response_model=FlowExecutionState)
async def get_execution_state(
    execution_id: str,
    current_user: User = Depends(require_viewer)
):
    execution_state = flow_manager.get_execution_state(execution_id)
    
    if not execution_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution '{execution_id}' not found"
        )
    
    return execution_state


@router.get("/flows/executions", response_model=List[FlowExecutionState])
async def list_executions(current_user: User = Depends(require_viewer)):
    return flow_manager.list_executions()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Flow Manager",
        "version": "1.0.0"
    }
