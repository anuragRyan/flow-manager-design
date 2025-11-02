"""
Test script for Flow Manager

This script demonstrates how to test the Flow Manager API.
Run this after starting the server.
"""

import requests
import json
import time


def test_flow_execution():
    """Test the flow execution endpoint."""
    print("=" * 60)
    print("Testing Flow Manager API")
    print("=" * 60)
    
    # Base URL
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check passed:", response.json())
        else:
            print("✗ Health check failed:", response.status_code)
            return
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server first:")
        print("  uvicorn app.main:app --reload")
        return
    
    # Test 2: Execute sample flow
    print("\n2. Testing flow execution...")
    
    # Load sample flow
    with open('flows/sample_flow.json', 'r') as f:
        flow_data = json.load(f)
    
    # Execute flow
    response = requests.post(
        f"{base_url}/api/v1/flows/execute",
        json=flow_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Flow execution successful!")
        print(f"  Execution ID: {result['execution_id']}")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        
        # Display task results
        print("\n  Task Results:")
        for task_result in result['execution_state']['task_results']:
            status_symbol = "✓" if task_result['status'] == 'success' else "✗"
            print(f"    {status_symbol} {task_result['task_name']}: {task_result['status']}")
            if task_result.get('data'):
                print(f"      Data: {json.dumps(task_result['data'], indent=6)}")
        
        execution_id = result['execution_id']
        
        # Test 3: Get execution state
        print("\n3. Testing get execution state...")
        response = requests.get(
            f"{base_url}/api/v1/flows/executions/{execution_id}"
        )
        
        if response.status_code == 200:
            print("✓ Successfully retrieved execution state")
        else:
            print("✗ Failed to retrieve execution state")
        
        # Test 4: List all executions
        print("\n4. Testing list executions...")
        response = requests.get(f"{base_url}/api/v1/flows/executions")
        
        if response.status_code == 200:
            executions = response.json()
            print(f"✓ Found {len(executions)} execution(s)")
        else:
            print("✗ Failed to list executions")
        
    else:
        print("✗ Flow execution failed:", response.status_code)
        print("  Error:", response.json())
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    print("\nTo view interactive API docs, visit:")
    print("  http://localhost:8000/docs")


if __name__ == "__main__":
    test_flow_execution()
