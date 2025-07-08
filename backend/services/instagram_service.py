"""
📸 INSTAGRAM SERVICE - Real Instagram Graph API Integration
Instagram posting service using Facebook Graph API (Instagram uses Facebook's API)
"""

import logging
import asyncio
from typing import Dict, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)

class InstagramService:
    """Instagram Graph API Service for automated posting"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self._credentials_cache = None
        logger.info("📸 Instagram service initialized - will load credentials from database")
    
    async def _get_credentials(self):
        """Get Instagram credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
        
        try:
            import db
            
            if not db.db_pool:
                logger.error("❌ Database pool not available")
                return None
            
            async with db.db_pool.acquire() as db_conn:
                # Get Instagram credentials from platform_settings
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = 'instagram_credentials'"
                )
                
                if row and row['value']:
                    credentials = row['value']
                    
                    # Validate required fields
                    required_fields = ['app_id', 'app_secret', 'access_token', 'user_id']
                    missing_fields = [field for field in required_fields if not credentials.get(field)]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing Instagram credential fields: {', '.join(missing_fields)}")
                        return None
                    
                    # Validate account type (must be Business or Creator)
                    account_type = credentials.get('account_type')
                    if account_type not in ['BUSINESS', 'CREATOR']:
                        logger.error(f"❌ Instagram account type must be BUSINESS or CREATOR, got: {account_type}")
                        return None
                    
                    # Cache credentials
                    self._credentials_cache = credentials
                    logger.info("✅ Instagram credentials loaded from database")
                    return credentials
                else:
                    logger.error("❌ Instagram credentials not found in database. Please configure them in the admin dashboard.")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to load Instagram credentials from database: {e}")
            return None
    
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to Instagram"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Instagram credentials not configured in admin dashboard."
            }
        
        try:
            if media_url:
                # Instagram requires media for posts
                result = await self._post_with_media(content, media_url, credentials)
            else:
                # Instagram Stories for text-only content
                result = await self._post_story(content, credentials)
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to Instagram: {result['post_id']}")
                return {
                    "success": True,
                    "post_id": result["post_id"],
                    "platform": "instagram",
                    "post_url": f"https://instagram.com/p/{result['post_id']}"
                }
            else:
                logger.error(f"❌ Instagram posting failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Instagram posting exception: {e}")
            return {
                "success": False,
                "error": f"Instagram posting failed: {str(e)}"
            }
    
    async def _post_with_media(self, content: Dict, media_url: str, credentials: Dict) -> Dict:
        """Post media content to Instagram"""
        try:
            # Step 1: Create media container
            container_result = await self._create_media_container(content, media_url, credentials)
            if not container_result.get("success"):
                return container_result
            
            # Step 2: Publish the media
            publish_result = await self._publish_media(container_result["container_id"], credentials)
            return publish_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Instagram media posting failed: {str(e)}"
            }
    
    async def _create_media_container(self, content: Dict, media_url: str, credentials: Dict) -> Dict:
        """Create Instagram media container"""
        url = f"{self.base_url}/{credentials['user_id']}/media"
        
        # Prepare caption
        caption = f"{content['title']}\n\n{content['description']}"
        if content.get('hashtags'):
            hashtags = ' '.join(content['hashtags'])
            caption = f"{caption}\n\n{hashtags}"
        
        # Determine media type
        is_video = any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi'])
        
        data = {
            "image_url" if not is_video else "video_url": media_url,
            "caption": caption,
            "access_token": credentials['access_token']
        }
        
        timeout = aiohttp.ClientTimeout(total=120, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(3):
                try:
                    async with session.post(url, data=data) as response:
                        if response.status == 200:
                            try:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "container_id": result.get("id")
                                }
                            except (json.JSONDecodeError, KeyError):
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Instagram API returned invalid JSON: {error_text}"
                                }
                        elif response.status == 429:
                            if attempt < 2:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                return {
                                    "success": False,
                                    "error": "Instagram API rate limit exceeded"
                                }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Instagram container creation error: {response.status} - {error_text}"
                            }
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Instagram container creation network error: {str(e)}"
                        }
            
            return {
                "success": False,
                "error": "Instagram container creation failed after 3 attempts"
            }
    
    async def _publish_media(self, container_id: str, credentials: Dict) -> Dict:
        """Publish Instagram media container"""
        url = f"{self.base_url}/{credentials['user_id']}/media_publish"
        
        data = {
            "creation_id": container_id,
            "access_token": credentials['access_token']
        }
        
        timeout = aiohttp.ClientTimeout(total=120, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(3):
                try:
                    async with session.post(url, data=data) as response:
                        if response.status == 200:
                            try:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "post_id": result.get("id")
                                }
                            except (json.JSONDecodeError, KeyError):
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Instagram API returned invalid JSON: {error_text}"
                                }
                        elif response.status == 429:
                            if attempt < 2:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                return {
                                    "success": False,
                                    "error": "Instagram API rate limit exceeded"
                                }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Instagram publish error: {response.status} - {error_text}"
                            }
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Instagram publish network error: {str(e)}"
                        }
            
            return {
                "success": False,
                "error": "Instagram publish failed after 3 attempts"
            }
    
    async def _post_story(self, content: Dict, credentials: Dict) -> Dict:
        """Post Instagram Story for text-only content"""
        # Instagram Stories implementation would go here
        # For now, return not implemented
        return {
            "success": False,
            "error": "Instagram Stories posting not yet implemented"
        }
    
    async def get_account_info(self) -> Dict:
        """Get Instagram account information"""
        credentials = await self._get_credentials()
        if not credentials:
            return {"success": False, "error": "Instagram credentials not configured"}
        
        url = f"{self.base_url}/{credentials['user_id']}"
        params = {
            "fields": "id,username,account_type,media_count,followers_count",
            "access_token": credentials['access_token']
        }
        
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(3):
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            try:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "account_info": result
                                }
                            except (json.JSONDecodeError, KeyError):
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Instagram API returned invalid JSON: {error_text}"
                                }
                        elif response.status == 429:
                            if attempt < 2:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                return {
                                    "success": False,
                                    "error": "Instagram API rate limit exceeded"
                                }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Failed to get account info: {response.status} - {error_text}"
                            }
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to get account info: {str(e)}"
                        }
            
            return {
                "success": False,
                "error": "Instagram account info request failed after 3 attempts"
            }
    
    async def validate_credentials(self) -> Dict:
        """Validate Instagram API credentials"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Instagram credentials not configured in admin dashboard",
                "missing": ["app_id", "app_secret", "access_token", "user_id", "account_type"]
            }
        
        # Test with account info API call
        account_info = await self.get_account_info()
        if account_info.get("success"):
            return {
                "success": True,
                "message": "Instagram credentials are valid",
                "username": account_info["account_info"].get("username"),
                "user_id": account_info["account_info"].get("id")
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials or API error",
                "details": account_info.get("error")
            }

# Global instance
instagram_service = InstagramService()

# Export
__all__ = ["InstagramService", "instagram_service"]