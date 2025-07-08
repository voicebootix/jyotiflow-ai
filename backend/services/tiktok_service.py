"""
🎵 TIKTOK SERVICE - Real TikTok Business API Integration
TikTok posting service for automated video uploads and management
"""

import logging
import asyncio
from typing import Dict, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)

class TikTokService:
    """TikTok Business API Service for automated posting"""
    
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self._credentials_cache = None
        logger.info("🎵 TikTok service initialized - will load credentials from database")
    
    async def _get_credentials(self):
        """Get TikTok credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
        
        try:
            import db
            
            if not db.db_pool:
                logger.error("❌ Database pool not available")
                return None
            
            async with db.db_pool.acquire() as db_conn:
                # Get TikTok credentials from platform_settings
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = 'tiktok_credentials'"
                )
                
                if row and row['value']:
                    credentials = row['value']
                    
                    # Validate required fields
                    required_fields = ['client_key', 'client_secret', 'access_token', 'user_id']
                    missing_fields = [field for field in required_fields if not credentials.get(field)]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing TikTok credential fields: {', '.join(missing_fields)}")
                        return None
                    
                    # Cache credentials
                    self._credentials_cache = credentials
                    logger.info("✅ TikTok credentials loaded from database")
                    return credentials
                else:
                    logger.error("❌ TikTok credentials not found in database. Please configure them in the admin dashboard.")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to load TikTok credentials from database: {e}")
            return None
    
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to TikTok"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "TikTok credentials not configured in admin dashboard."
            }
        
        try:
            if media_url:
                # Upload video to TikTok
                result = await self._upload_video(content, media_url, credentials)
            else:
                # TikTok requires video content
                return {
                    "success": False,
                    "error": "TikTok requires video content. Text-only posts not supported."
                }
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to TikTok: {result['share_id']}")
                return {
                    "success": True,
                    "post_id": result["share_id"],
                    "platform": "tiktok",
                    "post_url": result.get("share_url", "")
                }
            else:
                logger.error(f"❌ TikTok posting failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ TikTok posting exception: {e}")
            return {
                "success": False,
                "error": f"TikTok posting failed: {str(e)}"
            }
    
    async def _upload_video(self, content: Dict, video_url: str, credentials: Dict) -> Dict:
        """Upload video to TikTok"""
        try:
            # Step 1: Initialize upload
            init_result = await self._initialize_upload(credentials)
            if not init_result.get("success"):
                return init_result
            
            upload_url = init_result["upload_url"]
            upload_id = init_result["upload_id"]
            
            # Step 2: Upload video file
            upload_result = await self._upload_video_file(upload_url, video_url)
            if not upload_result.get("success"):
                return upload_result
            
            # Step 3: Publish video
            publish_result = await self._publish_video(upload_id, content, credentials)
            return publish_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"TikTok video upload failed: {str(e)}"
            }
    
    async def _initialize_upload(self, credentials: Dict) -> Dict:
        """Initialize video upload to TikTok"""
        url = f"{self.base_url}/v2/post/publish/video/init/"
        
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "post_info": {
                "title": "",  # Will be set during publish
                "privacy_level": "SELF_ONLY",  # Can be "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": "",  # Will be set during upload
                "post_mode": "DIRECT_POST"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("data", {}).get("publish_id"):
                        return {
                            "success": True,
                            "upload_url": result["data"]["upload_url"],
                            "upload_id": result["data"]["publish_id"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"TikTok upload initialization failed: {result.get('message', 'Unknown error')}"
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"TikTok upload init failed: {response.status} - {error_text}"
                    }
    
    async def _upload_video_file(self, upload_url: str, video_url: str) -> Dict:
        """Upload video file to TikTok"""
        try:
            async with aiohttp.ClientSession() as session:
                # Download video from URL
                async with session.get(video_url) as video_response:
                    if video_response.status == 200:
                        video_data = await video_response.read()
                        
                        # Upload to TikTok
                        async with session.put(upload_url, data=video_data) as response:
                            if response.status == 200:
                                return {"success": True}
                            else:
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"TikTok video upload failed: {response.status} - {error_text}"
                                }
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to download video: {video_response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Video upload failed: {str(e)}"
            }
    
    async def _publish_video(self, upload_id: str, content: Dict, credentials: Dict) -> Dict:
        """Publish uploaded video to TikTok"""
        url = f"{self.base_url}/v2/post/publish/status/fetch/"
        
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "publish_id": upload_id
        }
        
        # Poll for upload completion and publish
        max_attempts = 24  # Increased from 10 to 24 (4 minutes total)
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        
        for attempt in range(max_attempts):
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for retry in range(3):  # Retry network failures
                    try:
                        async with session.post(url, headers=headers, json=data) as response:
                            if response.status == 200:
                                try:
                                    result = await response.json()
                                    status = result.get("data", {}).get("status")
                                    
                                    if status == "PROCESSING_UPLOAD":
                                        # Wait and retry - exponential backoff
                                        wait_time = min(10, 2 + (attempt * 0.5))  # 2s to 14s
                                        await asyncio.sleep(wait_time)
                                        break  # Break retry loop, continue outer loop
                                    elif status == "PUBLISH_COMPLETE":
                                        return {
                                            "success": True,
                                            "share_id": result["data"].get("share_id"),
                                            "share_url": result["data"].get("share_url")
                                        }
                                    elif status == "FAILED":
                                        return {
                                            "success": False,
                                            "error": f"TikTok publish failed: {result.get('data', {}).get('fail_reason', 'Unknown error')}"
                                        }
                                    else:
                                        return {
                                            "success": False,
                                            "error": f"TikTok publish failed with status: {status}"
                                        }
                                except (json.JSONDecodeError, KeyError):
                                    error_text = await response.text()
                                    return {
                                        "success": False,
                                        "error": f"TikTok API returned invalid JSON: {error_text}"
                                    }
                            elif response.status == 429:
                                if retry < 2:
                                    await asyncio.sleep(2 ** retry)
                                    continue
                                else:
                                    return {
                                        "success": False,
                                        "error": "TikTok API rate limit exceeded"
                                    }
                            else:
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"TikTok publish check failed: {response.status} - {error_text}"
                                }
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        if retry < 2:
                            await asyncio.sleep(2 ** retry)
                            continue
                        else:
                            return {
                                "success": False,
                                "error": f"TikTok publish check network error: {str(e)}"
                            }
                else:
                    # If we've exhausted all retries for this attempt, continue to next attempt
                    continue
        
        return {
            "success": False,
            "error": "TikTok publish timeout - video processing took too long (4+ minutes)"
        }
    
    async def get_user_info(self) -> Dict:
        """Get TikTok user information"""
        credentials = await self._get_credentials()
        if not credentials:
            return {"success": False, "error": "TikTok credentials not configured"}
        
        url = f"{self.base_url}/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("data"):
                            return {
                                "success": True,
                                "user_info": result["data"]
                            }
                        else:
                            return {
                                "success": False,
                                "error": "User info not found"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to get user info: {response.status} - {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get user info: {str(e)}"
            }
    
    async def validate_credentials(self) -> Dict:
        """Validate TikTok API credentials"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "TikTok credentials not configured in admin dashboard",
                "missing": ["client_key", "client_secret", "access_token", "user_id"]
            }
        
        # Test with user info API call
        user_info = await self.get_user_info()
        if user_info.get("success"):
            user_data = user_info["user_info"]
            return {
                "success": True,
                "message": "TikTok credentials are valid",
                "username": user_data.get("display_name"),
                "user_id": user_data.get("open_id"),
                "follower_count": user_data.get("follower_count")
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials or API error",
                "details": user_info.get("error")
            }

# Global instance
tiktok_service = TikTokService()

# Export
__all__ = ["TikTokService", "tiktok_service"]