"""
🔵 FACEBOOK SERVICE - Real Facebook Graph API Integration
Complete Facebook posting service for social media automation
"""

import os
import logging
import asyncio
from typing import Dict, Optional, List
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FacebookService:
    """Facebook Graph API Service for automated posting"""
    
    def __init__(self):
        # Initialize without credentials - will load from database when needed
        self.base_url = "https://graph.facebook.com/v18.0"
        self._credentials_cache = None
        logger.info("🔵 Facebook service initialized - will load credentials from database")
    
    async def _get_credentials(self):
        """Get Facebook credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
        
        try:
            import db
            import json
            
            # Get database connection
            if not db.db_pool:
                logger.error("❌ Database pool not available")
                return None
            
            async with db.db_pool.acquire() as db_conn:
                # Get Facebook credentials from platform_settings
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = $1",
                    "facebook_credentials"
                )
                
                if row and row['value']:
                    try:
                        credentials = json.loads(row['value']) if isinstance(row['value'], str) else row['value']
                    except (json.JSONDecodeError, TypeError):
                        logger.error("❌ Invalid JSON format in Facebook credentials")
                        return None
                    
                    # Validate required fields
                    required_fields = ['app_id', 'app_secret', 'page_access_token']
                    missing_fields = [field for field in required_fields if not credentials.get(field)]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing Facebook credential fields: {', '.join(missing_fields)}")
                        return None
                    
                    # Cache credentials
                    self._credentials_cache = credentials
                    logger.info("✅ Facebook credentials loaded from database")
                    return credentials
                else:
                    logger.error("❌ Facebook credentials not found in database. Please configure them in the admin dashboard.")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to load Facebook credentials from database: {e}")
            return None
        
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to Facebook page"""
        # Get credentials from database
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Facebook credentials not configured in admin dashboard."
            }
        
        try:
            # Prepare the post message
            message = f"{content['title']}\n\n{content['description']}"
            
            # Add hashtags
            if content.get('hashtags'):
                hashtags = ' '.join(content['hashtags'])
                message = f"{message}\n\n{hashtags}"
            
            if media_url:
                # Post with media (photo/video)
                result = await self._post_with_media(message, media_url, credentials)
            else:
                # Text-only post
                result = await self._post_text_only(message, credentials)
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to Facebook: {result['post_id']}")
                return {
                    "success": True,
                    "post_id": result["post_id"],
                    "platform": "facebook",
                    "post_url": f"https://facebook.com/{result['post_id']}"
                }
            else:
                logger.error(f"❌ Facebook posting failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Facebook posting exception: {e}")
            return {
                "success": False,
                "error": f"Facebook posting failed: {str(e)}"
            }
    
    async def _post_text_only(self, message: str, credentials: Dict) -> Dict:
        """Post text-only content to Facebook"""
        url = f"{self.base_url}/{credentials['page_id']}/feed"
        
        data = {
            "message": message,
            "access_token": credentials['page_access_token']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "post_id": result.get("id")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Facebook API error: {response.status} - {error_text}"
                    }
    
    async def _post_with_media(self, message: str, media_url: str, credentials: Dict) -> Dict:
        """Post content with media (photo or video) to Facebook"""
        # First, determine if it's a photo or video based on URL
        is_video = any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm'])
        
        if is_video:
            return await self._post_video(message, media_url, credentials)
        else:
            return await self._post_photo(message, media_url, credentials)
    
    async def _post_photo(self, message: str, photo_url: str, credentials: Dict) -> Dict:
        """Post photo to Facebook"""
        url = f"{self.base_url}/{credentials['page_id']}/photos"
        
        data = {
            "url": photo_url,
            "caption": message,
            "access_token": credentials['page_access_token']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "post_id": result.get("id")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Facebook photo upload error: {response.status} - {error_text}"
                    }
    
    async def _post_video(self, message: str, video_url: str, credentials: Dict) -> Dict:
        """Post video to Facebook"""
        url = f"{self.base_url}/{credentials['page_id']}/videos"
        
        data = {
            "file_url": video_url,
            "description": message,
            "access_token": credentials['page_access_token']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "post_id": result.get("id")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Facebook video upload error: {response.status} - {error_text}"
                    }
    
    async def get_page_info(self) -> Dict:
        """Get Facebook page information"""
        credentials = await self._get_credentials()
        if not credentials:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        url = f"{self.base_url}/{credentials['page_id']}"
        params = {
            "fields": "id,name,username,followers_count,fan_count",
            "access_token": credentials['page_access_token']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "page_info": result
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to get page info: {response.status} - {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get page info: {str(e)}"
            }
    
    async def validate_credentials(self) -> Dict:
        """Validate Facebook API credentials"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Facebook credentials not configured in admin dashboard",
                "missing": ["app_id", "app_secret", "page_access_token", "page_id"]
            }
        
        # Test with a simple API call
        page_info = await self.get_page_info()
        if page_info.get("success"):
            return {
                "success": True,
                "message": "Facebook credentials are valid",
                "page_name": page_info["page_info"].get("name"),
                "page_id": page_info["page_info"].get("id")
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials or API error",
                "details": page_info.get("error")
            }

# Global instance
facebook_service = FacebookService()

# Export
__all__ = ["FacebookService", "facebook_service"]