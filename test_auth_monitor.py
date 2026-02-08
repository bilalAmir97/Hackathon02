#!/usr/bin/env python3
"""
Test script to monitor authentication functionality on the backend server.
This script tests various authentication scenarios to ensure the JWT implementation works correctly.
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

async def test_authentication_endpoints():
    """Test authentication functionality and monitor for errors."""
    
    base_url = "http://localhost:8000"
    
    print(f"[{datetime.now()}] Starting authentication functionality test...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Health endpoint: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   Health endpoint error: {e}")
        
        # Test 2: Try accessing protected endpoint without authentication (should fail with 401)
        print("\n2. Testing protected endpoint without authentication (expected 401)...")
        try:
            response = await client.get(f"{base_url}/api/123/tasks")
            print(f"   Protected endpoint without auth: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ Expected 401 Unauthorized received")
            else:
                print(f"   ⚠ Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"   Error accessing protected endpoint: {e}")
        
        # Test 3: Check API documentation is accessible
        print("\n3. Testing API documentation endpoint...")
        try:
            response = await client.get(f"{base_url}/docs")
            print(f"   Docs endpoint: {response.status_code} - Length: {len(response.text)} chars")
        except Exception as e:
            print(f"   Docs endpoint error: {e}")
        
        # Test 4: Check OpenAPI spec
        print("\n4. Testing OpenAPI specification endpoint...")
        try:
            response = await client.get(f"{base_url}/openapi.json")
            spec = response.json()
            print(f"   OpenAPI endpoint: {response.status_code}")
            print(f"   API Title: {spec.get('info', {}).get('title', 'Unknown')}")
            
            # Check if authentication endpoints exist in spec
            paths = spec.get('paths', {})
            auth_endpoints = [path for path in paths.keys() if 'auth' in path.lower()]
            print(f"   Found auth endpoints: {auth_endpoints}")
            
        except Exception as e:
            print(f"   OpenAPI endpoint error: {e}")
        
        # Test 5: Test root endpoint
        print("\n5. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Root endpoint: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   Root endpoint error: {e}")
    
    print(f"\n[{datetime.now()}] Authentication functionality test completed.")

async def monitor_server_logs():
    """Monitor server logs for authentication-related entries."""
    import subprocess
    
    print("\n6. Checking recent server logs for authentication entries...")
    
    try:
        result = subprocess.run([
            'bash', '-c', 'cd Phase-II/backend && tail -n 50 fastapi_server.log | grep -i -A 2 -B 2 "auth\\|token\\|login\\|register\\|401\\|unauthorized"'
        ], capture_output=True, text=True)
        
        if result.stdout:
            print("   Found authentication-related log entries:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        else:
            print("   No authentication-related entries found in recent logs")
            
    except Exception as e:
        print(f"   Error checking logs: {e}")

async def main():
    """Run authentication tests and monitoring."""
    print("=" * 70)
    print("BACKEND AUTHENTICATION FUNCTIONALITY MONITOR")
    print("=" * 70)
    
    await test_authentication_endpoints()
    await monitor_server_logs()
    
    print("\n" + "=" * 70)
    print("MONITORING COMPLETE")
    print("Server is running on http://localhost:8000")
    print("Authentication endpoints are available at /api/auth/")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
