#!/usr/bin/env python3
"""
Birth Chart Fix Test Script
===========================

This script tests the authentication fixes for the birth chart system.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"  # Change to your backend URL
TEST_BIRTH_DETAILS = {
    "date": "1983-09-07",
    "time": "10:10",
    "location": "Jaffna, Sri Lanka",
    "timezone": "Asia/Colombo"
}

async def test_birth_chart_endpoint():
    """Test birth chart endpoint without authentication"""
    print("🧪 Testing Birth Chart Endpoint")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test without authentication (should work now)
            response = await client.post(
                f"{BASE_URL}/api/spiritual/birth-chart",
                json={"birth_details": TEST_BIRTH_DETAILS},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Birth chart endpoint working without authentication!")
                print(f"Success: {data.get('success', False)}")
                print(f"Data Source: {data.get('birth_chart', {}).get('metadata', {}).get('data_source', 'Unknown')}")
                print(f"Cache Hit: {data.get('birth_chart', {}).get('metadata', {}).get('cache_hit', False)}")
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print()

async def test_user_profile_endpoint():
    """Test user profile endpoint without authentication"""
    print("🧪 Testing User Profile Endpoint")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test without authentication (should return guest user)
            response = await client.get(
                f"{BASE_URL}/api/user/profile",
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: User profile endpoint working without authentication!")
                print(f"User ID: {data.get('id', 'Unknown')}")
                print(f"Name: {data.get('name', 'Unknown')}")
                print(f"Email: {data.get('email', 'Unknown')}")
                print(f"Credits: {data.get('credits', 0)}")
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print()

async def test_with_invalid_token():
    """Test endpoints with invalid authentication token"""
    print("🧪 Testing With Invalid Token")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test with invalid token (should still work, fallback to guest)
            response = await client.post(
                f"{BASE_URL}/api/spiritual/birth-chart",
                json={"birth_details": TEST_BIRTH_DETAILS},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer invalid_token_12345"
                }
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Invalid token handled gracefully!")
                data = response.json()
                print(f"Success: {data.get('success', False)}")
            else:
                print(f"❌ ERROR: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
    
    print()

async def main():
    """Run all tests"""
    print("🕉️  JyotiFlow Birth Chart Fix Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    await test_user_profile_endpoint()
    await test_birth_chart_endpoint()
    await test_with_invalid_token()
    
    print("🎯 Test Results Summary:")
    print("- All endpoints should return 200 status code")
    print("- Birth chart should work without authentication")
    print("- User profile should return guest user info")
    print("- Invalid tokens should be handled gracefully")
    print()
    print("If all tests pass, the authentication fix is working correctly! ✅")

if __name__ == "__main__":
    asyncio.run(main())