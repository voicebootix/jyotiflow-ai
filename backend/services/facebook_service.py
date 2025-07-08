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
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        # Validate required credentials
        missing_creds = []
        if not self.app_id:
            missing_creds.append("FACEBOOK_APP_ID")
        if not self.app_secret:
            missing_creds.append("FACEBOOK_APP_SECRET")
        if not self.page_access_token:
            missing_creds.append("FACEBOOK_PAGE_ACCESS_TOKEN")
        if not self.page_id:
            missing_creds.append("FACEBOOK_PAGE_ID")
        
        if missing_creds:
            logger.error(f"❌ Missing Facebook credentials: {', '.join(missing_creds)}")
            self.is_configured = False
        else:
            self.is_configured = True
            logger.info("✅ Facebook service initialized successfully")
        
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to Facebook page"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "Facebook service not properly configured. Check environment variables."
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
                result = await self._post_with_media(message, media_url)
            else:
                # Text-only post
                result = await self._post_text_only(message)
            
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
    
    async def _post_text_only(self, message: str) -> Dict:
        """Post text-only content to Facebook"""
        url = f"{self.base_url}/{self.page_id}/feed"
        
        data = {
            "message": message,
            "access_token": self.page_access_token
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
    
    async def _post_with_media(self, message: str, media_url: str) -> Dict:
        """Post content with media (photo or video) to Facebook"""
        # First, determine if it's a photo or video based on URL
        is_video = any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi', '.webm'])
        
        if is_video:
            return await self._post_video(message, media_url)
        else:
            return await self._post_photo(message, media_url)
    
    async def _post_photo(self, message: str, photo_url: str) -> Dict:
        """Post photo to Facebook"""
        url = f"{self.base_url}/{self.page_id}/photos"
        
        data = {
            "url": photo_url,
            "caption": message,
            "access_token": self.page_access_token
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
    
    async def _post_video(self, message: str, video_url: str) -> Dict:
        """Post video to Facebook"""
        url = f"{self.base_url}/{self.page_id}/videos"
        
        data = {
            "file_url": video_url,
            "description": message,
            "access_token": self.page_access_token
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
        if not self.is_configured:
            return {"success": False, "error": "Facebook service not configured"}
        
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "id,name,username,followers_count,fan_count",
            "access_token": self.page_access_token
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
        if not self.is_configured:
            return {
                "success": False,
                "error": "Missing required credentials",
                "missing": [cred for cred in ["FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET", "FACEBOOK_PAGE_ACCESS_TOKEN", "FACEBOOK_PAGE_ID"] 
                           if not os.getenv(cred)]
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