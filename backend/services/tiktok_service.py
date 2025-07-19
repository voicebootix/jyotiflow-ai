"""
🎵 TIKTOK SERVICE - Real API Validation  
Validates TikTok API credentials by making actual API calls
"""

import aiohttp
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TikTokService:
    """Real TikTok API validation service"""
    
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, client_key: str, client_secret: str) -> Dict:
        """
        Validate TikTok credentials by making real API calls
        Fixed: Proper API scope handling (core.md & refresh.md compliant)
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Get app access token using client credentials
            token_test = await self._test_client_credentials(client_key, client_secret)
            if not token_test["success"]:
                return token_test
            
            # Test 2: Validate the app access token with app-specific endpoints
            access_token = token_test.get("access_token")
            
            # Fix: Ensure access token exists before proceeding (no false positives)
            if not access_token:
                return {
                    "success": False,
                    "error": "No access token received from TikTok API"
                }
            
            # Fix: Use app-specific endpoint instead of user endpoint
            app_validation = await self._validate_app_access_token(access_token)
            if not app_validation["success"]:
                return app_validation
            
            # Both tests passed with proper API scope
            return {
                "success": True,
                "message": "TikTok app credentials validated successfully",
                "access_token": access_token,
                "token_type": "app_access_token"
            }
            
        except Exception as e:
            logger.error(f"TikTok validation error: {e}")
            return {
                "success": False,
                "error": f"TikTok validation failed: {str(e)}"
            }
    
    async def _test_client_credentials(self, client_key: str, client_secret: str) -> Dict:
        """Test client credentials by getting access token"""
        try:
            url = f"{self.base_url}/v2/oauth/token/"
            
            data = {
                "client_key": client_key,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("error"):
                            error_code = result["error"].get("code")
                            error_message = result["error"].get("message", "Unknown error")
                            
                            if error_code == "invalid_client":
                                return {
                                    "success": False,
                                    "error": "Invalid TikTok client key or client secret"
                                }
                            elif error_code == "access_denied":
                                return {
                                    "success": False,
                                    "error": "TikTok API access denied. Check app permissions."
                                }
                            else:
                                return {
                                    "success": False,
                                    "error": f"TikTok API error: {error_message}"
                                }
                        
                        access_token = result.get("access_token")
                        if access_token:
                            return {
                                "success": True,
                                "message": "Client credentials are valid",
                                "access_token": access_token
                            }
                        else:
                            return {
                                "success": False,
                                "error": "No access token received from TikTok"
                            }
                    
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid TikTok client credentials"
                        }
                    elif response.status == 403:
                        return {
                            "success": False,
                            "error": "TikTok API access forbidden. Check app status."
                        }
                    elif response.status == 429:
                        return {
                            "success": False,
                            "error": "TikTok API rate limit exceeded. Try again later."
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"TikTok API returned status {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to test TikTok client credentials: {str(e)}"
            }
    
    async def _validate_app_access_token(self, access_token: str) -> Dict:
        """
        Validate app access token using app-specific endpoints
        Fixed: Uses proper API scope for app tokens (core.md & refresh.md compliant)
        """
        try:
            # Use app-specific endpoint that works with app access tokens
            # /v2/app/info/ is an app-level endpoint (not user-specific)
            url = f"{self.base_url}/v2/app/info/"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("error"):
                            error_message = result["error"].get("message", "App token validation failed")
                            return {
                                "success": False,
                                "error": f"TikTok app token validation failed: {error_message}"
                            }
                        
                        # App token is valid
                        return {
                            "success": True,
                            "message": "App access token is valid",
                            "app_info": result.get("data", {})
                        }
                    
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid or expired TikTok app access token"
                        }
                    elif response.status == 403:
                        return {
                            "success": False,
                            "error": "TikTok API access forbidden for this app token"
                        }
                    elif response.status == 400:
                        return {
                            "success": False,
                            "error": "Bad request - invalid app token format"
                        }
                    elif response.status == 404:
                        return {
                            "success": False,
                            "error": "TikTok app API endpoint not found - check API version"
                        }
                    elif response.status == 429:
                        return {
                            "success": False,
                            "error": "Rate limit exceeded - too many API requests"
                        }
                    elif response.status >= 500:
                        return {
                            "success": False,
                            "error": f"TikTok API server error (status: {response.status})"
                        }
                    else:
                        # All non-200 status codes should be treated as failures
                        # Only 200 indicates successful app token validation
                        return {
                            "success": False,
                            "error": f"App token validation failed with status {response.status}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"App token validation failed: {str(e)}"
            }

# Global instance for consistent import pattern (refresh.md: consistent architecture)
tiktok_service = TikTokService()

# Export
__all__ = ["TikTokService", "tiktok_service"]