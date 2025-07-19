"""
📸 INSTAGRAM SERVICE - Real API Validation
Validates Instagram API credentials by making actual Instagram Basic Display API calls
"""

import aiohttp
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class InstagramService:
    """Real Instagram Basic Display API validation service"""
    
    def __init__(self):
        self.graph_url = "https://graph.instagram.com"
        self.basic_url = "https://api.instagram.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, client_id: str, client_secret: str, access_token: str) -> Dict:
        """
        Validate Instagram credentials by making real API calls
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate access token
            token_test = await self._validate_access_token(access_token)
            if not token_test["success"]:
                return token_test
            
            # Test 2: Get user profile info
            profile_test = await self._get_user_profile(access_token)
            if not profile_test["success"]:
                return profile_test
            
            # Test 3: Check if it's a business account (for posting)
            business_test = await self._check_business_account(access_token)
            
            return {
                "success": True,
                "message": "Instagram credentials validated successfully. Ready for API calls!",
                "user_info": profile_test.get("user_info", {}),
                "is_business": business_test.get("is_business", False)
            }
            
        except Exception as e:
            logger.error(f"Instagram credential validation error: {e}")
            return {
                "success": False,
                "error": f"Instagram API validation failed: {str(e)}"
            }
    
    async def _validate_access_token(self, access_token: str) -> Dict:
        """Validate access token by calling /me endpoint"""
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
                            "message": f"Access token valid for user: @{data.get('username', 'Unknown')}",
                            "user_id": data["id"],
                            "username": data.get("username")
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
        """Get user profile information"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "id,username,account_type,media_count"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": "User profile retrieved successfully",
                            "user_info": {
                                "id": data["id"],
                                "username": data.get("username"),
                                "account_type": data.get("account_type", "PERSONAL"),
                                "media_count": data.get("media_count", 0)
                            }
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Could not retrieve profile")
                        return {
                            "success": False,
                            "error": f"Profile retrieval failed: {error_msg}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Profile retrieval failed: {str(e)}"
            }
    
    async def _check_business_account(self, access_token: str) -> Dict:
        """Check if account is business account (required for posting via API)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "account_type"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        account_type = data.get("account_type", "PERSONAL")
                        is_business = account_type in ["BUSINESS", "CREATOR"]
                        
                        return {
                            "success": True,
                            "is_business": is_business,
                            "account_type": account_type,
                            "message": f"Account type: {account_type}" + 
                                     (" (Can post via API)" if is_business else " (Cannot post via API - need Business/Creator account)")
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Could not determine account type"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Business account check failed: {str(e)}"
            }
    
    async def get_user_media(self, access_token: str, limit: int = 10) -> Dict:
        """Get user's recent media"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me/media"
                params = {
                    "access_token": access_token,
                    "fields": "id,media_type,media_url,thumbnail_url,permalink,timestamp",
                    "limit": limit
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "data" in data:
                        return {
                            "success": True,
                            "media": data["data"],
                            "count": len(data["data"])
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Could not retrieve media"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Media retrieval failed: {str(e)}"
            }
    
    async def validate_webhook_signature(self, signature: str, payload: str, client_secret: str) -> bool:
        """Validate Instagram webhook signature"""
        import hmac
        import hashlib
        
        try:
            expected_signature = hmac.new(
                client_secret.encode(),
                payload.encode(),
                hashlib.sha1
            ).hexdigest()
            
            return signature == f"sha1={expected_signature}"
        except Exception as e:
            logger.error(f"Webhook signature validation failed: {e}")
            return False