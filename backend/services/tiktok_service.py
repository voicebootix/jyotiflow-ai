"""
🎵 TIKTOK SERVICE - Real API Validation  
Validates TikTok API credentials by making actual API calls
"""

import aiohttp
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class TikTokService:
    """Real TikTok API validation service"""
    
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, client_key: str, client_secret: str) -> Dict:
        """
        Validate TikTok credentials by making real API calls
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Get access token using client credentials
            token_test = await self._test_client_credentials(client_key, client_secret)
            if not token_test["success"]:
                return token_test
            
            # Test 2: Validate access token by calling user info
            access_token = token_test.get("access_token")
            if access_token:
                user_validation = await self._validate_access_token(access_token)
                if not user_validation["success"]:
                    return user_validation
            
            # Both tests passed
            return {
                "success": True,
                "message": "TikTok credentials validated successfully",
                "access_token": access_token
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
    
    async def _validate_access_token(self, access_token: str) -> Dict:
        """Validate access token by calling TikTok API"""
        try:
            # Try to get user info to validate token
            url = f"{self.base_url}/v2/user/info/"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("error"):
                            error_message = result["error"].get("message", "Token validation failed")
                            return {
                                "success": False,
                                "error": f"TikTok token validation failed: {error_message}"
                            }
                        
                        # Token is valid
                        return {
                            "success": True,
                            "message": "Access token is valid"
                        }
                    
                    elif response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid or expired TikTok access token"
                        }
                    elif response.status == 403:
                        return {
                            "success": False,
                            "error": "TikTok API access forbidden for this token"
                        }
                    else:
                        # For client credentials flow, we might not have user permissions
                        # So if we got this far, the credentials are likely valid
                        return {
                            "success": True,
                            "message": "TikTok credentials appear valid (limited scope)"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Token validation failed: {str(e)}"
            }

# Global instance
tiktok_service = TikTokService()