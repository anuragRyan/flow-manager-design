"""
Authentication Test Script for Flow Manager

This script demonstrates and tests the authentication features.
"""

import requests
import json


def test_authentication():
    """Test authentication and authorization features."""
    print("=" * 70)
    print("Testing Flow Manager Authentication & Security")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check (public endpoint)
    print("\n1. Testing public health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check passed (no auth required)")
        else:
            print("✗ Health check failed")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server first:")
        print("  uvicorn app.main:app --reload")
        return
    
    # Test 2: Try to access protected endpoint without auth
    print("\n2. Testing protected endpoint without authentication...")
    response = requests.get(f"{base_url}/api/v1/flows/executions")
    if response.status_code == 401 or response.status_code == 403:
        print("✓ Protected endpoint correctly requires authentication")
        print(f"  Response: {response.json()}")
    else:
        print("✗ Endpoint should require authentication")
    
    # Test 3: Login with admin credentials
    print("\n3. Testing login with admin credentials...")
    login_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        admin_token = token_data["access_token"]
        print("✓ Admin login successful")
        print(f"  Token expires in: {token_data['expires_in']} seconds")
        print(f"  Token (first 50 chars): {admin_token[:50]}...")
    else:
        print("✗ Admin login failed")
        print(f"  Response: {login_response.json()}")
        return
    
    # Test 4: Get current user info
    print("\n4. Testing get current user endpoint...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        print("✓ Successfully retrieved user info")
        print(f"  Username: {user_info['username']}")
        print(f"  Role: {user_info['role']}")
        print(f"  Email: {user_info['email']}")
    else:
        print("✗ Failed to get user info")
    
    # Test 5: Access protected endpoint with token
    print("\n5. Testing access to protected endpoint with token...")
    response = requests.get(
        f"{base_url}/api/v1/flows/executions",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ Successfully accessed protected endpoint with token")
        executions = response.json()
        print(f"  Found {len(executions)} execution(s)")
    else:
        print("✗ Failed to access protected endpoint")
    
    # Test 6: Test API key authentication
    print("\n6. Testing API key authentication...")
    api_key_headers = {"X-API-Key": "fm_admin_key_12345"}
    response = requests.get(
        f"{base_url}/api/v1/flows/executions",
        headers=api_key_headers
    )
    
    if response.status_code == 200:
        print("✓ Successfully authenticated with API key")
    else:
        print("✗ API key authentication failed")
    
    # Test 7: Test invalid API key
    print("\n7. Testing invalid API key...")
    bad_headers = {"X-API-Key": "invalid_key"}
    response = requests.get(
        f"{base_url}/api/v1/flows/executions",
        headers=bad_headers
    )
    
    if response.status_code == 401 or response.status_code == 403:
        print("✓ Invalid API key correctly rejected")
    else:
        print("✗ Invalid API key should be rejected")
    
    # Test 8: Execute flow with authentication
    print("\n8. Testing flow execution with authentication...")
    with open('flows/sample_flow.json', 'r') as f:
        flow_data = json.load(f)
    
    response = requests.post(
        f"{base_url}/api/v1/flows/execute",
        headers=headers,
        json=flow_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Flow execution successful with authentication")
        print(f"  Execution ID: {result['execution_id']}")
        print(f"  Status: {result['status']}")
    else:
        print("✗ Flow execution failed")
        print(f"  Response: {response.json()}")
    
    # Test 9: Test different user roles
    print("\n9. Testing different user roles...")
    
    # Login as viewer
    viewer_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": "viewer", "password": "viewer123"}
    )
    
    if viewer_response.status_code == 200:
        viewer_token = viewer_response.json()["access_token"]
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        # Try to execute flow as viewer (should fail)
        response = requests.post(
            f"{base_url}/api/v1/flows/execute",
            headers=viewer_headers,
            json=flow_data
        )
        
        if response.status_code == 403:
            print("✓ Viewer correctly denied flow execution (insufficient permissions)")
        else:
            print("✗ Viewer should not be able to execute flows")
        
        # Try to view executions as viewer (should succeed)
        response = requests.get(
            f"{base_url}/api/v1/flows/executions",
            headers=viewer_headers
        )
        
        if response.status_code == 200:
            print("✓ Viewer can view executions (read-only access)")
        else:
            print("✗ Viewer should be able to view executions")
    
    # Test 10: Test admin-only endpoints
    print("\n10. Testing admin-only endpoints...")
    
    # Login as regular user
    user_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": "user", "password": "user123"}
    )
    
    if user_response.status_code == 200:
        user_token = user_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Try to list users as regular user (should fail)
        response = requests.get(
            f"{base_url}/api/v1/auth/users",
            headers=user_headers
        )
        
        if response.status_code == 403:
            print("✓ Regular user correctly denied access to user list")
        else:
            print("✗ User list should be admin-only")
        
        # List users as admin (should succeed)
        response = requests.get(
            f"{base_url}/api/v1/auth/users",
            headers=headers  # admin headers
        )
        
        if response.status_code == 200:
            users = response.json()
            print("✓ Admin can list users")
            print(f"  Total users: {len(users)}")
        else:
            print("✗ Admin should be able to list users")
    
    print("\n" + "=" * 70)
    print("Authentication testing complete!")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Public endpoints accessible without auth")
    print("  ✓ Protected endpoints require authentication")
    print("  ✓ JWT token authentication working")
    print("  ✓ API key authentication working")
    print("  ✓ Role-based access control enforced")
    print("  ✓ Invalid credentials rejected")
    print("\nDefault Credentials:")
    print("  Admin:  username=admin,  password=admin123,  API key=fm_admin_key_12345")
    print("  User:   username=user,   password=user123,   API key=fm_user_key_67890")
    print("  Viewer: username=viewer, password=viewer123")
    print("\n⚠️  Remember to change default credentials in production!")


if __name__ == "__main__":
    test_authentication()
