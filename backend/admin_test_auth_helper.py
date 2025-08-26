#!/usr/bin/env python3
"""
Admin Test Authentication Helper
Provides authenticated HTTP requests for admin endpoint testing
"""

import httpx
import os
import time
from typing import Optional, Dict, Any, Tuple
import logging
import json

logger = logging.getLogger(__name__)

class AdminTestAuthHelper:
    """Helper class for authenticated admin endpoint testing"""
    
    def __init__(self, api_base_url: Optional[str] = None):
        self.api_base_url = api_base_url or os.getenv('API_BASE_URL', 'https://jyotiflow-ai.onrender.com')
        self.admin_token: Optional[str] = None
        
        admin_email = os.getenv('ADMIN_TEST_EMAIL')
        admin_password = os.getenv('ADMIN_TEST_PASSWORD')

        if not admin_email or not admin_password:
            raise ValueError("ADMIN_TEST_EMAIL and ADMIN_TEST_PASSWORD environment variables must be set for admin tests.")

        self.admin_credentials = {
            "email": admin_email, 
            "password": admin_password
        }
    
    async def get_admin_token(self) -> Tuple[bool, str, Optional[str]]:
        """
        Login and get admin authentication token
        
        Returns:
            Tuple of (success: bool, message: str, token: Optional[str])
        """
        if self.admin_token:
            return True, "Using cached token", self.admin_token
            
        login_url = self.api_base_url.rstrip('/') + '/api/auth/login'
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                login_response = await client.post(login_url, json=self.admin_credentials)
                
                if login_response.status_code != 200:
                    return False, f"Admin login failed: {login_response.status_code}", None
                
                login_data = login_response.json()
                admin_token = login_data.get("access_token")
                
                if not admin_token:
                    return False, "No access token in login response", None
                
                # Verify it's an admin token by checking user info
                user_info = login_data.get("user", {})
                user_role = user_info.get("role", "user")
                
                if user_role not in ["admin", "super_admin"]:
                    return False, f"User role '{user_role}' does not have admin access", None
                
                self.admin_token = admin_token
                logger.info(f"Successfully authenticated admin user: {user_info.get('email')}")
                return True, f"Admin authenticated successfully as {user_role}", admin_token
                
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            return False, f"Authentication error: {str(e)}", None
    
    async def make_authenticated_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to an admin endpoint
        
        Args:
            endpoint: API endpoint (e.g., '/api/admin/analytics/overview')
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body data for POST/PUT requests
            params: Query parameters for GET requests
            
        Returns:
            Dict with test results including status, response_time, etc.
        """
        # Get admin token first
        auth_success, auth_message, token = await self.get_admin_token()
        
        if not auth_success:
            return {
                "status": "failed",
                "error": f"Authentication failed: {auth_message}",
                "business_function": "Admin Authentication"
            }
        
        # Prepare request
        url = self.api_base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start_time = time.time()
                print(f"🌐 Making authenticated {method} request to: {url}")
                
                # Make request based on method
                if method.upper() == 'GET':
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == 'POST':
                    response = await client.post(url, json=data, headers=headers)
                elif method.upper() == 'PUT':
                    response = await client.put(url, json=data, headers=headers)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url, headers=headers)
                else:
                    response = await client.request(method, url, json=data, params=params, headers=headers)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                status_code = response.status_code
                
                # Admin endpoints should return 200 or business logic errors (422), not auth errors
                expected_codes = [200, 201, 204, 422]  # No 401/403/400 expected with proper auth
                
                test_status = 'passed'
                failure_reason = None

                if status_code in [401, 403]:
                    test_status = 'failed'
                    failure_reason = f"Authentication/Authorization Failure: Status Code {status_code}"
                elif status_code not in expected_codes:
                    test_status = 'failed'
                    failure_reason = f"Unexpected Status Code: {status_code}"

                print(f"📊 Response: {status_code} ({response_time_ms}ms)")
                
                # Try to get response content
                try:
                    response_content = response.json()
                except json.JSONDecodeError:
                    # Safely handle non-JSON responses or decoding errors
                    raw_content = response.text if response.text else ""
                    response_content = {"raw_content": raw_content[:200] + "..." if len(raw_content) > 200 else raw_content}
                
                return {
                    "status": test_status,
                    "execution_time_ms": response_time_ms,
                    "details": {
                        "status_code": status_code,
                        "response_time_ms": response_time_ms,
                        "url": url,
                        "method": method.upper(),
                        "endpoint": endpoint,
                        "authenticated": True,
                        "response_content": response_content,
                        "failure_reason": failure_reason # Add failure reason to details
                    }
                }
                
        except Exception as http_error:
            logger.error(f"HTTP request failed: {http_error}")
            return {
                "status": "failed", 
                "error": f"HTTP request failed: {str(http_error)}",
                "failure_reason": f"Exception during request: {str(http_error)}"
            }

# Convenience functions for common admin endpoints
async def test_admin_endpoint_with_auth(endpoint: str, method: str = "GET", test_data: Optional[Dict] = None, business_function: str = "Admin Endpoint"):
    """
    Test any admin endpoint with proper authentication
    
    Args:
        endpoint: The admin endpoint to test
        method: HTTP method to use
        test_data: Data to send (for POST/PUT) or params (for GET)
        business_function: Description of what this endpoint does
        
    Returns:
        Test result dictionary
    """
    helper = AdminTestAuthHelper()
    
    if method.upper() == "GET":
        result = await helper.make_authenticated_request(endpoint, method, params=test_data)
    else:
        result = await helper.make_authenticated_request(endpoint, method, data=test_data)
    
    result["business_function"] = business_function
    return result

# Example usage functions that can be copied into test cases:
async def test_admin_overview_endpoint_authenticated():
    """Test admin overview endpoint with proper authentication"""
    return await test_admin_endpoint_with_auth(
        endpoint="/api/admin/analytics/overview",
        method="GET",
        test_data={"timeframe": "7d", "metrics": ["users", "sessions", "revenue"]},
        business_function="Admin Dashboard Overview"
    )

async def test_admin_revenue_insights_authenticated():
    """Test admin revenue insights endpoint with proper authentication"""
    return await test_admin_endpoint_with_auth(
        endpoint="/api/admin/analytics/revenue-insights",
        method="GET", 
        test_data={"period": "30d", "breakdown": ["daily", "source"]},
        business_function="Admin Revenue Insights"
    )

async def test_admin_analytics_authenticated():
    """Test admin analytics endpoint with proper authentication"""
    return await test_admin_endpoint_with_auth(
        endpoint="/api/admin/analytics/analytics",
        method="GET",
        test_data={"view": "dashboard", "filters": ["active_users", "revenue"]},
        business_function="Admin Analytics"
    )

if __name__ == "__main__":
    import asyncio
    
    async def test_all_admin_endpoints():
        """Test all admin endpoints with authentication"""
        print("🚀 Testing admin endpoints with authentication...")
        
        endpoints_to_test = [
            ("/api/admin/analytics/overview", "GET", {"timeframe": "7d"}, "Admin Overview"),
            ("/api/admin/analytics/revenue-insights", "GET", {"period": "30d"}, "Revenue Insights"),
            ("/api/admin/analytics/analytics", "GET", {"view": "dashboard"}, "Admin Analytics"),
        ]
        
        for endpoint, method, test_data, description in endpoints_to_test:
            print(f"\n🔍 Testing: {description}")
            result = await test_admin_endpoint_with_auth(endpoint, method, test_data, description)
            
            if result["status"] == "passed":
                print(f"✅ {description}: PASSED ({result.get('execution_time_ms', 0)}ms)")
            else:
                print(f"❌ {description}: FAILED - {result.get('error', 'Unknown error')}")
                if 'details' in result:
                    print(f"   Status Code: {result['details'].get('status_code', 'N/A')}")
    
    # Run the tests
    asyncio.run(test_all_admin_endpoints())




