"""
📸 INSTAGRAM SERVICE - Real API Validation
Validates Instagram API credentials by making actual Instagram Basic Display API calls
"""

import aiohttp
import logging
from typing import Dict, Optional
import json
import hmac
import hashlib

logger = logging.getLogger(__name__)

class InstagramService:
    """Real Instagram Basic Display API validation service"""
    
    def __init__(self):
        self.graph_url = "https://graph.instagram.com"
        self.basic_url = "https://api.instagram.com"
        self._credentials_cache = None
    
    async def validate_credentials(self, app_id: str, app_secret: str, access_token: str) -> Dict:
        """
        Validate Instagram credentials by making real API calls
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate app credentials
            if app_id and app_secret:
                app_test = await self._validate_app_credentials(app_id, app_secret)
                if not app_test["success"]:
                    return app_test
            
            # Test 2: Validate access token
            token_test = await self._validate_access_token(access_token)
            if not token_test["success"]:
                return token_test
            
            # Test 3: Get user profile info
            profile_test = await self._get_user_profile(access_token)
            if not profile_test["success"]:
                return profile_test
            
            # Test 4: Check if it's a business account (for posting)
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
    
    async def _validate_app_credentials(self, app_id: str, app_secret: str) -> Dict:
        """Validate Instagram app credentials (Instagram uses Facebook Graph API)"""
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
    
    def validate_webhook_signature(self, signature: str, payload: str, app_secret: str) -> bool:
        """
        Validate Instagram webhook signature using Meta Graph API requirements
        
        Args:
            signature: The X-Hub-Signature-256 header value from Meta (e.g., "sha256=abc123...")
            payload: The raw webhook payload as string
            app_secret: Instagram app secret for HMAC validation
            
        Returns:
            bool: True if signature is valid, False otherwise
            
        Note: 
        - Synchronous method as HMAC operations don't require async
        - Updated for latest Meta Graph API which uses SHA256 instead of deprecated SHA1
        - Follows core.md principle of simplicity and reliability
        """
        try:
            # Remove 'sha256=' prefix if present (Meta format: 'sha256=<hex_digest>')
            if signature.startswith('sha256='):
                received_signature = signature[7:]  # Remove 'sha256=' prefix
            else:
                # Fallback: assume signature is the raw hex digest
                received_signature = signature
            
            # Calculate expected signature using SHA256 (Meta Graph API standard)
            expected_signature = hmac.new(
                app_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Secure comparison to prevent timing attacks
            is_valid = hmac.compare_digest(received_signature, expected_signature)
            
            if not is_valid:
                logger.warning(f"Instagram webhook signature validation failed")
                logger.debug(f"Expected: {expected_signature[:8]}..., Received: {received_signature[:8]}...")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Instagram webhook signature validation error: {e}")
            return False
    
    def verify_webhook_request(self, headers: Dict[str, str], payload: str, app_secret: str) -> Dict[str, bool]:
        """
        Comprehensive webhook request verification for Instagram
        
        Args:
            headers: HTTP headers from the webhook request
            payload: Raw webhook payload
            app_secret: Instagram app secret
            
        Returns:
            Dict with verification results and details
            
        Note: Follows Meta Graph API webhook security best practices
        """
        verification_result = {
            "signature_valid": False,
            "has_signature_header": False,
            "error": None
        }
        
        try:
            # Check for X-Hub-Signature-256 header (Meta standard)
            signature_header = headers.get('X-Hub-Signature-256') or headers.get('x-hub-signature-256')
            
            if not signature_header:
                # Fallback: check for deprecated SHA1 header
                legacy_header = headers.get('X-Hub-Signature') or headers.get('x-hub-signature')
                if legacy_header:
                    verification_result["error"] = "Using deprecated SHA1 signature. Please upgrade to SHA256."
                    logger.warning("Instagram webhook using deprecated SHA1 signature")
                else:
                    verification_result["error"] = "Missing X-Hub-Signature-256 header"
                return verification_result
            
            verification_result["has_signature_header"] = True
            
            # Validate signature using synchronous method (core.md simplicity)
            signature_valid = self.validate_webhook_signature(signature_header, payload, app_secret)
            verification_result["signature_valid"] = signature_valid
            
            if not signature_valid:
                verification_result["error"] = "Invalid webhook signature"
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            verification_result["error"] = f"Verification failed: {str(e)}"
            return verification_result
    
    async def validate_webhook_signature_async(self, signature: str, payload: str, app_secret: str) -> bool:
        """
        Async wrapper for validate_webhook_signature for backward compatibility
        
        Note: This is just a wrapper around the synchronous method.
        The core HMAC validation doesn't require async operations.
        Use the sync version (validate_webhook_signature) for better performance.
        
        Args:
            signature: The X-Hub-Signature-256 header value
            payload: The raw webhook payload as string  
            app_secret: Instagram app secret for HMAC validation
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return self.validate_webhook_signature(signature, payload, app_secret)

# Export - Following standardized new-instance pattern
__all__ = ["InstagramService"]

# Note: Use InstagramService() to create new instances for better isolation
# No global instances - consistent pattern across all services
# 
# Key Methods:
# - validate_credentials(): Real Instagram API validation  
# - validate_webhook_signature(): Modern SHA256 webhook verification (SYNC - core.md compliant)
# - validate_webhook_signature_async(): Async wrapper for backward compatibility
# - verify_webhook_request(): Comprehensive webhook validation (SYNC - reliable)
#
# Design Note: Webhook validation is synchronous as HMAC operations don't require async.
# This follows core.md principles of simplicity and avoids deprecated asyncio patterns.