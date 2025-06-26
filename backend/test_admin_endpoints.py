#!/usr/bin/env python3
"""
Test script to verify admin endpoints are working
"""

import requests
import json

def test_admin_endpoints():
    """Test admin endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing admin endpoints...")
    
    # Test 1: Login as admin
    print("\n1. Testing admin login...")
    login_data = {
        "email": "admin@jyotiflow.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            print(f"Login success: {login_result.get('success')}")
            
            if login_result.get('success'):
                token = login_result.get('data', {}).get('token')
                print(f"Token received: {'Yes' if token else 'No'}")
                
                # Test 2: Admin stats endpoint
                print("\n2. Testing admin stats endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                stats_response = requests.get(f"{base_url}/api/admin/stats", headers=headers)
                print(f"Stats response status: {stats_response.status_code}")
                
                if stats_response.status_code == 200:
                    stats_result = stats_response.json()
                    print(f"Stats success: {stats_result.get('success')}")
                    if stats_result.get('success'):
                        print(f"Stats data: {json.dumps(stats_result.get('data', {}), indent=2)}")
                    else:
                        print(f"Stats error: {stats_result}")
                else:
                    print(f"Stats failed: {stats_response.text}")
                
                # Test 3: Admin monetization endpoint
                print("\n3. Testing admin monetization endpoint...")
                monetization_response = requests.get(f"{base_url}/api/admin/monetization", headers=headers)
                print(f"Monetization response status: {monetization_response.status_code}")
                
                if monetization_response.status_code == 200:
                    monetization_result = monetization_response.json()
                    print(f"Monetization success: {monetization_result.get('success')}")
                    if monetization_result.get('success'):
                        print(f"Monetization data keys: {list(monetization_result.get('data', {}).keys())}")
                    else:
                        print(f"Monetization error: {monetization_result}")
                else:
                    print(f"Monetization failed: {monetization_response.text}")
                
                # Test 4: Admin optimization endpoint
                print("\n4. Testing admin optimization endpoint...")
                optimization_response = requests.get(f"{base_url}/api/admin/optimization", headers=headers)
                print(f"Optimization response status: {optimization_response.status_code}")
                
                if optimization_response.status_code == 200:
                    optimization_result = optimization_response.json()
                    print(f"Optimization success: {optimization_result.get('success')}")
                    if optimization_result.get('success'):
                        print(f"Optimization data keys: {list(optimization_result.get('data', {}).keys())}")
                    else:
                        print(f"Optimization error: {optimization_result}")
                else:
                    print(f"Optimization failed: {optimization_response.text}")
                
            else:
                print(f"Login failed: {login_result}")
        else:
            print(f"Login request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    print("\n✅ Admin endpoint tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting admin endpoint tests...")
    test_admin_endpoints() 