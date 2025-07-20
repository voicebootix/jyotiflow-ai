"""
🎵 TIKTOK SERVICE - Clean Implementation (core.md & refresh.md compliant)  
Real TikTok API validation with proper error handling
Following the proven pattern from Facebook service
"""

import aiohttp
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TikTokService:
    """Clean TikTok API validation service"""
    
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, client_key: str, client_secret: str) -> Dict:
        """
        Validate TikTok credentials by making real API calls
        Following core.md & refresh.md: evidence-based validation
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Get app access token using client credentials
            token_test = await self._get_app_access_token(client_key, client_secret)
            if not token_test["success"]:
                return token_test
            
            # Test 2: Validate the app access token
            access_token = token_test.get("access_token")
            if not access_token:
                return {
                    "success": False,
                    "error": "No access token received from TikTok API"
                }
            
            # Test 3: Validate app access token with app info endpoint
            validation_test = await self._validate_app_access_token(access_token)
            if not validation_test["success"]:
                return validation_test
            
            # All tests passed
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
    
    async def _get_app_access_token(self, client_key: str, client_secret: str) -> Dict:
        """Get app access token using client credentials"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v2/oauth/token/"
                
                data = {
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials"
                }
                
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                async with session.post(url, data=data, headers=headers) as response:
                    result = await response.json()
                    
                    if response.status == 200:
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
                            "error": f"TikTok API error {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Client credentials test failed: {str(e)}"
            }
    
    async def _validate_app_access_token(self, access_token: str) -> Dict:
        """Validate app access token using app info endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use app info endpoint for validation
                url = f"{self.base_url}/v2/app/info/"
                params = {
                    "access_token": access_token
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        app_info = data.get("data", {})
                        if app_info:
                            return {
                                "success": True,
                                "message": "App access token is valid",
                                "app_info": app_info
                            }
                        else:
                            return {
                                "success": False,
                                "error": "App access token validation failed - no app info"
                            }
                    else:
                        error_msg = data.get("error", {}).get("message", "Token validation failed")
                        return {
                            "success": False,
                            "error": f"App token validation failed: {error_msg}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"App token validation failed: {str(e)}"
            }

# Global instance for consistent access pattern (following Facebook service)
tiktok_service = TikTokService() 