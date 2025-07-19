"""
📘 FACEBOOK SERVICE - Real API Validation
Validates Facebook API credentials by making actual Graph API calls
"""

import aiohttp
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class FacebookService:
    """Real Facebook Graph API validation service"""
    
    def __init__(self):
        self.graph_url = "https://graph.facebook.com/v18.0"
        self._credentials_cache = None
    
    async def validate_credentials(self, app_id: str, app_secret: str, access_token: str) -> Dict:
        """
        Validate Facebook credentials by making real Graph API calls
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate access token
            token_test = await self._validate_access_token(access_token)
            if not token_test["success"]:
                return token_test
            
            # Test 2: Validate app credentials
            app_test = await self._validate_app_credentials(app_id, app_secret)
            if not app_test["success"]:
                return app_test
            
            # Test 3: Check permissions
            permissions_test = await self._check_permissions(access_token)
            if not permissions_test["success"]:
                return permissions_test
            
            return {
                "success": True,
                "message": "Facebook credentials validated successfully. Ready for posting!",
                "permissions": permissions_test.get("permissions", [])
            }
            
        except Exception as e:
            logger.error(f"Facebook credential validation error: {e}")
            return {
                "success": False,
                "error": f"Facebook API validation failed: {str(e)}"
            }
    
    async def _validate_access_token(self, access_token: str) -> Dict:
        """Validate access token by calling /me endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "id,name"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": f"Access token valid for user: {data.get('name', 'Unknown')}",
                            "user_id": data["id"]
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Invalid access token")
                        return {
                            "success": False,
                            "error": f"Access token validation failed: {error_msg}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Access token test failed: {str(e)}"
            }
    
    async def _validate_app_credentials(self, app_id: str, app_secret: str) -> Dict:
        """Validate app credentials by getting app access token"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/oauth/access_token"
                params = {
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "grant_type": "client_credentials"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "access_token" in data:
                        return {
                            "success": True,
                            "message": "App credentials validated successfully",
                            "app_token": data["access_token"]
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Invalid app credentials")
                        return {
                            "success": False,
                            "error": f"App credentials validation failed: {error_msg}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"App credentials test failed: {str(e)}"
            }
    
    async def _check_permissions(self, access_token: str) -> Dict:
        """Check what permissions the access token has"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me/permissions"
                params = {"access_token": access_token}
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "data" in data:
                        granted_permissions = [
                            perm["permission"] for perm in data["data"] 
                            if perm["status"] == "granted"
                        ]
                        
                        required_permissions = ["pages_manage_posts", "pages_read_engagement"]
                        missing_permissions = [p for p in required_permissions if p not in granted_permissions]
                        
                        if missing_permissions:
                            return {
                                "success": False,
                                "error": f"Missing required permissions: {', '.join(missing_permissions)}",
                                "permissions": granted_permissions
                            }
                        else:
                            return {
                                "success": True,
                                "message": "All required permissions granted",
                                "permissions": granted_permissions
                            }
                    else:
                        return {
                            "success": False,
                            "error": "Could not retrieve permissions"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Permissions check failed: {str(e)}"
            }
    
    async def get_pages(self, access_token: str) -> Dict:
        """Get user's Facebook pages"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me/accounts"
                params = {
                    "access_token": access_token,
                    "fields": "id,name,access_token"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "data" in data:
                        return {
                            "success": True,
                            "pages": data["data"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Could not retrieve pages"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Pages retrieval failed: {str(e)}"
            }