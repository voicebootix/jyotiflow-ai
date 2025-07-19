"""
🎥 YOUTUBE SERVICE - Real API Validation
Validates YouTube API credentials by making actual API calls
"""

import aiohttp
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class YouTubeService:
    """Real YouTube API validation service"""
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self._credentials_cache = None
    
    async def validate_credentials(self, api_key: str, channel_id: str) -> Dict:
        """
        Validate YouTube credentials by making real API calls
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate API key by calling channels endpoint
            channel_test = await self._test_api_key(api_key)
            if not channel_test["success"]:
                return channel_test
            
            # Test 2: Validate specific channel ID
            channel_validation = await self._validate_channel_id(api_key, channel_id)
            if not channel_validation["success"]:
                return channel_validation
            
            # Both tests passed
            return {
                "success": True,
                "message": "YouTube credentials validated successfully",
                "channel_info": channel_validation.get("channel_info", {})
            }
            
        except Exception as e:
            logger.error(f"YouTube validation error: {e}")
            return {
                "success": False,
                "error": f"YouTube validation failed: {str(e)}"
            }
    
    async def _test_api_key(self, api_key: str) -> Dict:
        """Test if API key is valid by calling YouTube API"""
        try:
            url = f"{self.base_url}/channels"
            params = {
                "part": "snippet",
                "mine": "true",
                "key": api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 401:
                        return {
                            "success": False,
                            "error": "Invalid YouTube API key"
                        }
                    elif response.status == 403:
                        data = await response.json()
                        error_reason = data.get("error", {}).get("errors", [{}])[0].get("reason", "forbidden")
                        if error_reason == "quotaExceeded":
                            return {
                                "success": False,
                                "error": "YouTube API quota exceeded. Try again later."
                            }
                        else:
                            return {
                                "success": False,
                                "error": "YouTube API access forbidden. Check API key permissions."
                            }
                    elif response.status == 400:
                        return {
                            "success": False,
                            "error": "Invalid YouTube API request format"
                        }
                    elif response.status == 200:
                        return {
                            "success": True,
                            "message": "API key is valid"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"YouTube API returned status {response.status}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to test YouTube API key: {str(e)}"
            }
    
    async def _validate_channel_id(self, api_key: str, channel_id: str) -> Dict:
        """Validate specific channel ID exists and is accessible"""
        try:
            url = f"{self.base_url}/channels"
            params = {
                "part": "snippet,statistics",
                "id": channel_id,
                "key": api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        if not items:
                            return {
                                "success": False,
                                "error": f"Channel ID '{channel_id}' not found"
                            }
                        
                        channel_info = items[0]
                        return {
                            "success": True,
                            "message": f"Channel validated: {channel_info['snippet']['title']}",
                            "channel_info": {
                                "title": channel_info["snippet"]["title"],
                                "subscriber_count": channel_info.get("statistics", {}).get("subscriberCount", "Hidden"),
                                "video_count": channel_info.get("statistics", {}).get("videoCount", "0")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to validate channel ID: HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Channel ID validation failed: {str(e)}"
            }

# Global instance
youtube_service = YouTubeService()