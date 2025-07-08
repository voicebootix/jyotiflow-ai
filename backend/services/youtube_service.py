"""
🎥 YOUTUBE SERVICE - Real YouTube Data API v3 Integration
YouTube posting service for automated video uploads and management
"""

import logging
from typing import Dict, Optional
import aiohttp
import json
import base64

logger = logging.getLogger(__name__)

class YouTubeService:
    """YouTube Data API v3 Service for automated posting"""
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
        self._credentials_cache = None
        logger.info("🎥 YouTube service initialized - will load credentials from database")
    
    async def _get_credentials(self):
        """Get YouTube credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
        
        try:
            import db
            
            if not db.db_pool:
                logger.error("❌ Database pool not available")
                return None
            
            async with db.db_pool.acquire() as db_conn:
                # Get YouTube credentials from platform_settings
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = 'youtube_credentials'"
                )
                
                if row and row['value']:
                    credentials = row['value']
                    
                    # Validate required fields
                    required_fields = ['api_key', 'client_id', 'client_secret', 'access_token', 'refresh_token', 'channel_id']
                    missing_fields = [field for field in required_fields if not credentials.get(field)]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing YouTube credential fields: {', '.join(missing_fields)}")
                        return None
                    
                    # Cache credentials
                    self._credentials_cache = credentials
                    logger.info("✅ YouTube credentials loaded from database")
                    return credentials
                else:
                    logger.error("❌ YouTube credentials not found in database. Please configure them in the admin dashboard.")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to load YouTube credentials from database: {e}")
            return None
    
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to YouTube"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "YouTube credentials not configured in admin dashboard."
            }
        
        try:
            if media_url:
                # Upload video to YouTube
                result = await self._upload_video(content, media_url, credentials)
            else:
                # Create YouTube Community post (text-only)
                result = await self._create_community_post(content, credentials)
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to YouTube: {result['video_id']}")
                return {
                    "success": True,
                    "post_id": result["video_id"],
                    "platform": "youtube",
                    "post_url": f"https://youtube.com/watch?v={result['video_id']}"
                }
            else:
                logger.error(f"❌ YouTube posting failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ YouTube posting exception: {e}")
            return {
                "success": False,
                "error": f"YouTube posting failed: {str(e)}"
            }
    
    async def _upload_video(self, content: Dict, video_url: str, credentials: Dict) -> Dict:
        """Upload video to YouTube"""
        try:
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": content['title'][:100],  # YouTube title limit
                    "description": content['description'][:5000],  # YouTube description limit
                    "tags": content.get('hashtags', [])[:50],  # YouTube tags limit
                    "categoryId": "22",  # People & Blogs category
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public",  # Can be "private", "public", or "unlisted"
                    "embeddable": True,
                    "license": "youtube"
                }
            }
            
            # Upload video using resumable upload
            upload_result = await self._resumable_upload(video_metadata, video_url, credentials)
            return upload_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube video upload failed: {str(e)}"
            }
    
    async def _resumable_upload(self, metadata: Dict, video_url: str, credentials: Dict) -> Dict:
        """Perform resumable upload to YouTube"""
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json",
            "X-Upload-Content-Type": "video/*"
        }
        
        params = {
            "part": "snippet,status",
            "uploadType": "resumable"
        }
        
        # Step 1: Initiate resumable upload
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.upload_url,
                params=params,
                headers=headers,
                json=metadata
            ) as response:
                if response.status == 200:
                    upload_url = response.headers.get("Location")
                    if upload_url:
                        # Step 2: Upload video file
                        upload_result = await self._upload_video_file(upload_url, video_url, credentials)
                        return upload_result
                    else:
                        return {
                            "success": False,
                            "error": "Failed to get upload URL from YouTube"
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"YouTube upload initiation failed: {response.status} - {error_text}"
                    }
    
    async def _upload_video_file(self, upload_url: str, video_url: str, credentials: Dict) -> Dict:
        """Upload video file to YouTube"""
        try:
            # Download video from URL and upload to YouTube
            async with aiohttp.ClientSession() as session:
                # Download video
                async with session.get(video_url) as video_response:
                    if video_response.status == 200:
                        video_data = await video_response.read()
                        
                        # Upload to YouTube
                        headers = {
                            "Authorization": f"Bearer {credentials['access_token']}",
                            "Content-Type": "video/*"
                        }
                        
                        async with session.put(upload_url, headers=headers, data=video_data) as response:
                            if response.status == 200:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "video_id": result.get("id")
                                }
                            else:
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"YouTube video upload failed: {response.status} - {error_text}"
                                }
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to download video from URL: {video_response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Video file upload failed: {str(e)}"
            }
    
    async def _create_community_post(self, content: Dict, credentials: Dict) -> Dict:
        """Create YouTube Community post for text-only content"""
        # YouTube Community posts require special API access
        # For now, create a simple video with text overlay
        return {
            "success": False,
            "error": "YouTube Community posts require special API access. Use video content instead."
        }
    
    async def get_channel_info(self) -> Dict:
        """Get YouTube channel information"""
        credentials = await self._get_credentials()
        if not credentials:
            return {"success": False, "error": "YouTube credentials not configured"}
        
        url = f"{self.base_url}/channels"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": credentials['channel_id'],
            "key": credentials['api_key']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("items"):
                            return {
                                "success": True,
                                "channel_info": result["items"][0]
                            }
                        else:
                            return {
                                "success": False,
                                "error": "Channel not found"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to get channel info: {response.status} - {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get channel info: {str(e)}"
            }
    
    async def validate_credentials(self) -> Dict:
        """Validate YouTube API credentials"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "YouTube credentials not configured in admin dashboard",
                "missing": ["api_key", "client_id", "client_secret", "access_token", "refresh_token", "channel_id"]
            }
        
        # Test with channel info API call
        channel_info = await self.get_channel_info()
        if channel_info.get("success"):
            channel_data = channel_info["channel_info"]
            return {
                "success": True,
                "message": "YouTube credentials are valid",
                "channel_title": channel_data["snippet"].get("title"),
                "channel_id": channel_data.get("id"),
                "subscriber_count": channel_data["statistics"].get("subscriberCount")
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials or API error",
                "details": channel_info.get("error")
            }
    
    async def refresh_access_token(self) -> Dict:
        """Refresh YouTube access token using refresh token"""
        credentials = await self._get_credentials()
        if not credentials or not credentials.get('refresh_token'):
            return {"success": False, "error": "No refresh token available"}
        
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": credentials['client_id'],
            "client_secret": credentials['client_secret'],
            "refresh_token": credentials['refresh_token'],
            "grant_type": "refresh_token"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        new_access_token = result.get("access_token")
                        
                        if new_access_token:
                            # Update credentials in database
                            await self._update_access_token(new_access_token)
                            return {
                                "success": True,
                                "access_token": new_access_token
                            }
                    
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Token refresh failed: {response.status} - {error_text}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Token refresh failed: {str(e)}"
            }
    
    async def _update_access_token(self, new_token: str):
        """Update access token in database"""
        try:
            import db
            
            if db.db_pool and self._credentials_cache:
                self._credentials_cache['access_token'] = new_token
                
                async with db.db_pool.acquire() as db_conn:
                    await db_conn.execute(
                        "UPDATE platform_settings SET value = $1 WHERE key = 'youtube_credentials'",
                        json.dumps(self._credentials_cache)
                    )
                logger.info("✅ YouTube access token updated in database")
        except Exception as e:
            logger.error(f"❌ Failed to update access token: {e}")

# Global instance
youtube_service = YouTubeService()

# Export
__all__ = ["YouTubeService", "youtube_service"]