#!/usr/bin/env python3
"""
Test API Endpoints for JyotiFlow
Tests the main API endpoints to ensure they work correctly
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "https://jyotiflow-ai.onrender.com"

async def test_endpoint(session, endpoint, method="GET", data=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            async with session.get(url) as response:
                status = response.status
                content = await response.text()
        elif method == "POST":
            async with session.post(url, json=data) as response:
                status = response.status
                content = await response.text()
        
        try:
            json_content = json.loads(content)
            return {
                "endpoint": endpoint,
                "status": status,
                "success": status < 400,
                "data": json_content
            }
        except json.JSONDecodeError:
            return {
                "endpoint": endpoint,
                "status": status,
                "success": status < 400,
                "data": content
            }
            
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": "ERROR",
            "success": False,
            "error": str(e)
        }

async def test_all_endpoints():
    """Test all main API endpoints"""
    print("🧪 Testing JyotiFlow API Endpoints")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test endpoints
        endpoints_to_test = [
            ("/health", "GET"),
            ("/api/services/types", "GET"),
            ("/api/services/credit-packages", "GET"),
            ("/api/services/stats", "GET"),
            ("/api/services/daily-free-credits", "GET"),
        ]
        
        results = []
        
        for endpoint, method in endpoints_to_test:
            print(f"Testing {method} {endpoint}...")
            result = await test_endpoint(session, endpoint, method)
            results.append(result)
            
            if result["success"]:
                print(f"✅ {endpoint} - Status: {result['status']}")
            else:
                print(f"❌ {endpoint} - Status: {result['status']}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        
        if successful == total:
            print("🎉 All endpoints are working correctly!")
        else:
            print("⚠️ Some endpoints have issues. Check the details above.")
        
        return results

async def main():
    """Main test function"""
    try:
        results = await test_all_endpoints()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Test results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 