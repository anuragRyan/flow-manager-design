"""Sample task implementations for the Flow Manager.

This module contains example tasks that demonstrate how to implement
tasks for the flow execution engine. Each task is an async function
that receives a context dictionary and returns a result dictionary
with 'status', and optional 'data' or 'error' fields.
"""

import asyncio
import logging
import random
from typing import Dict, Any

from app.services.task_registry import register_task

logger = logging.getLogger(__name__)


@register_task("task1")
async def fetch_data_task(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Task 1: Fetching data...")
    
    # Simulate async I/O operation
    await asyncio.sleep(0.5)
    
    try:
        # Simulate data fetching
        # In production, this would be actual API calls or database queries
        fetched_data = {
            "records": [
                {"id": 1, "value": "data1"},
                {"id": 2, "value": "data2"},
                {"id": 3, "value": "data3"},
            ],
            "total_count": 3,
            "source": "external_api"
        }
        
        logger.info(f"Task 1: Successfully fetched {fetched_data['total_count']} records")
        
        return {
            "status": "success",
            "data": fetched_data
        }
        
    except Exception as e:
        logger.error(f"Task 1: Failed to fetch data: {e}")
        return {
            "status": "failure",
            "error": str(e)
        }


@register_task("task2")
async def process_data_task(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Task 2: Processing data...")
    
    await asyncio.sleep(0.3)
    
    try:
        task1_result = context.get("task1_result")
        
        if not task1_result:
            raise ValueError("No data from task1 found in context")
        
        records = task1_result.get("records", [])
        
        processed_records = []
        for record in records:
            processed_record = {
                "id": record["id"],
                "value": record["value"].upper(),
                "processed": True,
                "timestamp": "2025-10-28T10:00:00Z"
            }
            processed_records.append(processed_record)
        
        processed_data = {
            "processed_records": processed_records,
            "processed_count": len(processed_records),
            "processing_status": "completed"
        }
        
        logger.info(
            f"Task 2: Successfully processed {len(processed_records)} records"
        )
        
        return {
            "status": "success",
            "data": processed_data
        }
        
    except Exception as e:
        logger.error(f"Task 2: Failed to process data: {e}")
        return {
            "status": "failure",
            "error": str(e)
        }


@register_task("task3")
async def store_data_task(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Task 3: Storing data...")
    
    # Simulate async storage operation
    await asyncio.sleep(0.4)
    
    try:
        task2_result = context.get("task2_result")
        
        if not task2_result:
            raise ValueError("No data from task2 found in context")
        
        processed_records = task2_result.get("processed_records", [])
        
        storage_result = {
            "stored_count": len(processed_records),
            "storage_location": "database://main/processed_data",
            "storage_timestamp": "2025-10-28T10:00:00Z",
            "storage_status": "success"
        }
        
        logger.info(
            f"Task 3: Successfully stored {storage_result['stored_count']} records"
        )
        
        return {
            "status": "success",
            "data": storage_result
        }
        
    except Exception as e:
        logger.error(f"Task 3: Failed to store data: {e}")
        return {
            "status": "failure",
            "error": str(e)
        }


@register_task("validate_data")
async def validate_data_task(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Validating data...")
    
    await asyncio.sleep(0.2)
    
    is_valid = random.choice([True, True, True, False])
    
    if is_valid:
        return {
            "status": "success",
            "data": {"validation_status": "passed"}
        }
    else:
        return {
            "status": "failure",
            "error": "Data validation failed: Invalid data format"
        }


@register_task("send_notification")
async def send_notification_task(context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Sending notification...")
    
    await asyncio.sleep(0.1)
    
    return {
        "status": "success",
        "data": {
            "notification_sent": True,
            "recipients": ["admin@example.com"],
            "timestamp": "2025-10-28T10:00:00Z"
        }
    }
