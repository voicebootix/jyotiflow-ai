"""
📘 FACEBOOK SERVICE - Real API Validation
Validates Facebook API credentials by making actual Graph API calls
"""

import aiohttp
import logging
import db
import json
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class FacebookService:
    """Real Facebook Graph API validation service"""
    
    def __init__(self):
        # Updated to Facebook Graph API v21.0 (latest as of October 2024)
        # Following core.md & refresh.md principles: stay current with API versions
        # Benefits: latest security patches, new features, improved stability
        self.graph_url = "https://graph.facebook.com/v21.0"
        self._credentials_cache = None
    
    async def validate_credentials(self, app_id: str, app_secret: str, access_token: str) -> Dict:
        """
        Validate Facebook credentials by making real Graph API calls
        Supports both user access tokens and page access tokens (core.md & refresh.md compliant)
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate app credentials first
            app_test = await self._validate_app_credentials(app_id, app_secret)
            if not app_test["success"]:
                return app_test
            
            # Test 2: Determine token type and validate accordingly
            token_info = await self._analyze_token_type(access_token)
            
            if token_info.get("is_page_token"):
                # Page access token validation (different endpoints)
                page_test = await self._validate_page_access_token(access_token)
                if not page_test["success"]:
                    return page_test
                
                return {
                    "success": True,
                    "message": "Facebook page credentials validated successfully. Ready for posting!",
                    "token_type": "page_access_token",
                    "page_id": page_test.get("page_id"),
                    "page_name": page_test.get("page_name")
                }
            else:
                # User access token validation (original flow)
                token_test = await self._validate_access_token(access_token)
                if not token_test["success"]:
                    return token_test
                
                # Test 3: Check permissions for user tokens
                permissions_test = await self._check_permissions(access_token)
                if not permissions_test["success"]:
                    return permissions_test
                
                return {
                    "success": True,
                    "message": "Facebook user credentials validated successfully. Ready for posting!",
                    "token_type": "user_access_token",
                    "user_id": token_test.get("user_id"),
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
                        
                        # Updated Facebook Graph API permissions for comprehensive social media management
                        # Following core.md principle: explicit, complete requirements
                        required_permissions = [
                            "pages_manage_posts",           # Create, edit, delete posts
                            "pages_read_engagement",        # Read likes, comments, shares metrics  
                            "pages_manage_engagement",      # Moderate comments, manage interactions
                            "pages_read_user_engagement",   # Read detailed user interaction data
                            "publish_video"                 # Publish video content (future-ready)
                        ]
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
    
    async def _analyze_token_type(self, access_token: str) -> Dict:
        """
        Analyze access token to determine if it's a user token or page token
        Uses /me endpoint with explicit field requests (core.md & refresh.md: reliable detection)
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.graph_url}/me"
                # Fix: Explicitly request page-specific fields for reliable detection
                params = {
                    "access_token": access_token,
                    "fields": "id,name,category,about,fan_count,email,first_name,last_name"
                }
        
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "id" in data:
                        # Check if this is a page by looking for explicitly requested page-specific fields
                        # Page tokens will have category, about, fan_count; User tokens will have email, first_name, last_name
                        page_indicators = ["category", "about", "fan_count"]
                        user_indicators = ["email", "first_name", "last_name"]
                        
                        has_page_fields = any(field in data for field in page_indicators)
                        has_user_fields = any(field in data for field in user_indicators)
                        
                        if has_page_fields and not has_user_fields:
                            return {
                                "is_page_token": True, 
                                "token_type": "page",
                                "detection_method": "explicit_page_fields",
                                "page_name": data.get("name")
                            }
                        elif has_user_fields and not has_page_fields:
                            return {
                                "is_page_token": False, 
                                "token_type": "user",
                                "detection_method": "explicit_user_fields",
                                "user_name": data.get("name")
                            }
                        else:
                            # Fallback: If unclear, default to user token for safety
                            logger.warning(f"Ambiguous token type detection. Page fields: {has_page_fields}, User fields: {has_user_fields}")
                            return {
                                "is_page_token": False, 
                                "token_type": "user",
                                "detection_method": "fallback_to_user"
                            }
                    else:
                        # If /me fails, default to user token validation
                        error_msg = data.get("error", {}).get("message", "Unknown error")
                        logger.warning(f"Token type analysis failed: {error_msg}")
                        return {
                            "is_page_token": False, 
                            "token_type": "user",
                            "detection_method": "api_error_fallback"
                        }
            
        except Exception as e:
            logger.error(f"Token type analysis error: {e}")
            # Default to user token validation if analysis fails
            return {
                "is_page_token": False, 
                "token_type": "user",
                "detection_method": "exception_fallback"
            }
    
    async def _validate_page_access_token(self, access_token: str) -> Dict:
        """
        Validate page access token using page-specific endpoints
        Different from user tokens - uses page info endpoint (refresh.md: proper scope)
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Use /me endpoint for page info (works for page tokens)
                url = f"{self.graph_url}/me"
                params = {
                    "access_token": access_token,
                    "fields": "id,name,category,about,fan_count"
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if response.status == 200 and "id" in data:
                        return {
                            "success": True,
                            "message": f"Page access token valid for: {data.get('name', 'Unknown')}",
                            "page_id": data["id"],
                            "page_name": data.get("name"),
                            "category": data.get("category"),
                            "fan_count": data.get("fan_count")
                        }
                    else:
                        error_msg = data.get("error", {}).get("message", "Invalid page access token")
                        return {
                            "success": False,
                            "error": f"Page access token validation failed: {error_msg}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Page access token test failed: {str(e)}"
            }

    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to Facebook page"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Facebook credentials not configured in admin dashboard."
            }
        
        try:
            # Prepare post content
            post_message = content.get('content_text', content.get('description', ''))
            post_title = content.get('title', '')
            
            # Combine title and message
            if post_title and post_message:
                full_message = f"{post_title}\n\n{post_message}"
            else:
                full_message = post_message or post_title
            
            # Add hashtags if provided (Facebook recommends max 10 hashtags for optimal reach)
            if content.get('hashtags'):
                hashtags = ' '.join(content['hashtags'][:10])  # Facebook hashtag limit: max 10 for optimal engagement
                full_message = f"{full_message}\n\n{hashtags}"
            
            # ✅ FIXED: Validate Facebook's 63,206 character limit
            if len(full_message) > 63206:
                return {
                    "success": False,
                    "error": f"Facebook post content exceeds 63,206 character limit. Current length: {len(full_message)} characters. Please shorten the content."
                }
            
            # Post to Facebook page
            if media_url:
                result = await self._post_with_media(credentials, full_message, media_url)
            else:
                result = await self._post_text_only(credentials, full_message)
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to Facebook: {result.get('post_id')}")
                return {
                    "success": True,
                    "post_id": result.get('post_id'),
                    "platform": "facebook",
                    "post_url": result.get('post_url', 'https://facebook.com'),
                    "content_length": len(full_message)
                }
            else:
                logger.error(f"❌ Facebook posting failed: {result.get('error')}")
                # ✅ FIXED: Return consistent error format instead of raw result
                return {
                    "success": False,
                    "error": result.get('error', 'Facebook posting failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Facebook posting exception: {e}")
            return {
                "success": False,
                "error": f"Facebook posting failed: {str(e)}"
            }
    
    def invalidate_credentials_cache(self):
        """Invalidate the credentials cache to force fresh fetch from database"""
        logger.info("🔄 Facebook credentials cache invalidated")
        self._credentials_cache = None
    
    async def _get_credentials(self):
        """Get Facebook credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
            
        try:
            if not db.db_pool:
                return None
                
            async with db.db_pool.acquire() as db_conn:
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = $1",
                    "facebook_credentials"
                )
                if row and row['value']:
                    try:
                        # ✅ FIXED: Added error handling for JSON parsing
                        if isinstance(row['value'], str):
                            credentials = json.loads(row['value'])
                        else:
                            credentials = row['value']
                        self._credentials_cache = credentials
                        return credentials
                    except json.JSONDecodeError as json_error:
                        logger.error(f"❌ Facebook credentials JSON decode error: {json_error}")
                        return None
                    except Exception as parse_error:
                        logger.error(f"❌ Facebook credentials parsing error: {parse_error}")
                        return None
        except Exception as e:
            logger.error(f"Failed to get Facebook credentials: {e}")
            
        return None

# Global instance for consistent import pattern (refresh.md: consistent architecture)
facebook_service = FacebookService()

# Export
__all__ = ["FacebookService", "facebook_service"]

# Note: Use FacebookService() to create new instances for better isolation
# No global instances - consistent pattern across all services