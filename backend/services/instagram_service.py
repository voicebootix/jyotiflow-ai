"""
📸 INSTAGRAM SERVICE - Clean Implementation (core.md & refresh.md compliant)
Real Instagram Basic Display API validation with proper error handling
Following the proven pattern from Facebook service
"""

import aiohttp
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class InstagramService:
    """Clean Instagram Basic Display API validation service"""
    
    def __init__(self):
        self.graph_url = "https://graph.instagram.com"
        self.basic_url = "https://api.instagram.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, app_id: str, app_secret: str, access_token: str) -> Dict:
        """
        Validate Instagram credentials by making real API calls
        Following core.md & refresh.md: evidence-based validation
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate app credentials
            if app_id and app_secret:
                app_test = await self._validate_app_credentials(app_id, app_secret)
                if not app_test["success"]:
                    return app_test
            
            # Test 2: Validate access token
            if access_token:
                token_test = await self._validate_access_token(access_token)
                if not token_test["success"]:
                    return token_test
                
                # Test 3: Get user profile info
                profile_test = await self._get_user_profile(access_token)
                if not profile_test["success"]:
                    return profile_test
                
                return {
                    "success": True,
                    "message": "Instagram credentials validated successfully. Ready for API calls!",
                    "user_info": profile_test.get("user_info", {}),
                    "token_type": "access_token"
                }
            else:
                return {
                    "success": False,
                    "error": "Access token is required for Instagram API validation"
                }
                    
        except Exception as e:
            logger.error(f"Instagram credential validation error: {e}")
            return {
                "success": False,
                "error": f"Instagram API validation failed: {str(e)}"
            }
    
    async def _validate_app_credentials(self, app_id: str, app_secret: str) -> Dict:
        """Validate Instagram app credentials using Facebook Graph API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Instagram apps use Facebook Graph API for app token validation
                url = "https://graph.facebook.com/oauth/access_token"
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
                            "message": "Instagram app credentials validated successfully",
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
    
    async def _validate_access_token(self, access_token: str) -> Dict:
        """Validate Instagram access token"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "id,username"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": "Instagram access token is valid",
                            "user_id": data["id"],
                            "username": data.get("username", "Unknown")
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
    
    async def _get_user_profile(self, access_token: str) -> Dict:
        """Get Instagram user profile information"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "id,username,account_type,media_count"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        return {
                            "success": True,
                            "user_info": {
                                "id": data.get("id"),
                                "username": data.get("username"),
                                "account_type": data.get("account_type", "PERSONAL"),
                                "media_count": data.get("media_count", 0)
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to retrieve user profile"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Profile retrieval failed: {str(e)}"
            }

# Global instance for consistent access pattern (following Facebook service)
instagram_service = InstagramService() 