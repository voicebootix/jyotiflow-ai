"""
🐦 TWITTER SERVICE - Real Twitter API v2 Integration
Twitter posting service for automated tweets and management
"""

import logging
import asyncio
from typing import Dict, Optional
import aiohttp
import json
import base64

logger = logging.getLogger(__name__)

class TwitterService:
    """Twitter API v2 Service for automated posting"""
    
    def __init__(self):
        self.base_url = "https://api.twitter.com/2"
        self.upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        self._credentials_cache = None
        logger.info("🐦 Twitter service initialized - will load credentials from database")
    
    async def _get_credentials(self):
        """Get Twitter credentials from database (platform_settings table)"""
        if self._credentials_cache:
            return self._credentials_cache
        
        try:
            import db
            
            if not db.db_pool:
                logger.error("❌ Database pool not available")
                return None
            
            async with db.db_pool.acquire() as db_conn:
                # Get Twitter credentials from platform_settings
                row = await db_conn.fetchrow(
                    "SELECT value FROM platform_settings WHERE key = 'twitter_credentials'"
                )
                
                if row and row['value']:
                    credentials = row['value']
                    
                    # Validate required fields
                    required_fields = ['api_key', 'api_secret', 'access_token', 'access_token_secret', 'bearer_token']
                    missing_fields = [field for field in required_fields if not credentials.get(field)]
                    
                    if missing_fields:
                        logger.error(f"❌ Missing Twitter credential fields: {', '.join(missing_fields)}")
                        return None
                    
                    # Cache credentials
                    self._credentials_cache = credentials
                    logger.info("✅ Twitter credentials loaded from database")
                    return credentials
                else:
                    logger.error("❌ Twitter credentials not found in database. Please configure them in the admin dashboard.")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to load Twitter credentials from database: {e}")
            return None
    
    async def post_content(self, content: Dict, media_url: Optional[str] = None) -> Dict:
        """Post content to Twitter"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Twitter credentials not configured in admin dashboard."
            }
        
        try:
            if media_url:
                # Upload media and post tweet with media
                result = await self._post_with_media(content, media_url, credentials)
            else:
                # Post text-only tweet
                result = await self._post_text_tweet(content, credentials)
            
            if result.get("success"):
                logger.info(f"✅ Successfully posted to Twitter: {result['tweet_id']}")
                return {
                    "success": True,
                    "post_id": result["tweet_id"],
                    "platform": "twitter",
                    "post_url": f"https://twitter.com/user/status/{result['tweet_id']}"
                }
            else:
                logger.error(f"❌ Twitter posting failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Twitter posting exception: {e}")
            return {
                "success": False,
                "error": f"Twitter posting failed: {str(e)}"
            }
    
    async def _post_text_tweet(self, content: Dict, credentials: Dict) -> Dict:
        """Post text-only tweet"""
        url = f"{self.base_url}/tweets"
        
        # Prepare tweet text (280 character limit)
        tweet_text = f"{content['title']}\n\n{content['description']}"
        if content.get('hashtags'):
            hashtags = ' '.join(content['hashtags'][:5])  # Limit hashtags
            tweet_text = f"{tweet_text}\n\n{hashtags}"
        
        # Truncate if too long
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
        
        headers = {
            "Authorization": f"Bearer {credentials['bearer_token']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "text": tweet_text
        }
        
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(3):
                try:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 201:
                            try:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "tweet_id": result["data"]["id"]
                                }
                            except (json.JSONDecodeError, KeyError):
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Twitter API returned invalid JSON: {error_text}"
                                }
                        elif response.status == 429:
                            if attempt < 2:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            else:
                                return {
                                    "success": False,
                                    "error": "Twitter API rate limit exceeded"
                                }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Twitter posting failed: {response.status} - {error_text}"
                            }
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Twitter posting network error: {str(e)}"
                        }
            
            return {
                "success": False,
                "error": "Twitter posting failed after 3 attempts"
            }
    
    async def _post_with_media(self, content: Dict, media_url: str, credentials: Dict) -> Dict:
        """Post tweet with media"""
        try:
            # Step 1: Upload media
            media_result = await self._upload_media(media_url, credentials)
            if not media_result.get("success"):
                return media_result
            
            media_id = media_result["media_id"]
            
            # Step 2: Post tweet with media
            result = await self._post_tweet_with_media_id(content, media_id, credentials)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Twitter media posting failed: {str(e)}"
            }
    
    async def _upload_media(self, media_url: str, credentials: Dict) -> Dict:
        """Upload media to Twitter"""
        try:
            # Download media first
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as media_response:
                    if media_response.status == 200:
                        media_data = await media_response.read()
                        
                        # Determine media type
                        content_type = media_response.headers.get('content-type', '')
                        if 'video' in content_type:
                            media_category = "tweet_video"
                        elif 'image' in content_type:
                            media_category = "tweet_image"
                        else:
                            media_category = "tweet_image"  # Default
                        
                        # Upload to Twitter
                        auth_header = self._get_oauth_header(credentials, "POST", self.upload_url, {'media_category': media_category})
                        
                        # Create multipart form data
                        form_data = aiohttp.FormData()
                        form_data.add_field('media', media_data, filename='media', content_type=content_type)
                        form_data.add_field('media_category', media_category)
                        
                        headers = {
                            "Authorization": auth_header
                        }
                        
                        async with session.post(self.upload_url, headers=headers, data=form_data) as response:
                            if response.status == 200:
                                result = await response.json()
                                return {
                                    "success": True,
                                    "media_id": result.get("media_id_string")
                                }
                            else:
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Twitter media upload failed: {response.status} - {error_text}"
                                }
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to download media: {media_response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Media upload failed: {str(e)}"
            }
    
    async def _post_tweet_with_media_id(self, content: Dict, media_id: str, credentials: Dict) -> Dict:
        """Post tweet with uploaded media ID"""
        url = f"{self.base_url}/tweets"
        
        # Prepare tweet text
        tweet_text = f"{content['title']}\n\n{content['description']}"
        if content.get('hashtags'):
            hashtags = ' '.join(content['hashtags'][:5])
            tweet_text = f"{tweet_text}\n\n{hashtags}"
        
        # Truncate if too long
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
        
        headers = {
            "Authorization": f"Bearer {credentials['bearer_token']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "text": tweet_text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    return {
                        "success": True,
                        "tweet_id": result["data"]["id"]
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Twitter posting with media failed: {response.status} - {error_text}"
                    }
    
    def _get_oauth_header(self, credentials: Dict, method: str, url: str, params: Optional[Dict] = None) -> str:
        """Generate OAuth 1.0a header for Twitter API v1.1 endpoints"""
        import time
        import secrets
        import urllib.parse
        import hmac
        import hashlib
        
        oauth_params = {
            'oauth_consumer_key': credentials['api_key'],
            'oauth_token': credentials['access_token'],
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': secrets.token_hex(16),
            'oauth_version': '1.0'
        }
        
        # Combine OAuth params with request params for signature
        all_params = oauth_params.copy()
        if params:
            all_params.update(params)
        
        # Create signature base string
        sorted_params = sorted(all_params.items())
        param_string = '&'.join([f"{urllib.parse.quote(str(k), safe='')}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(credentials['api_secret'], safe='')}&{urllib.parse.quote(credentials['access_token_secret'], safe='')}"
        
        # Generate signature
        signature = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        oauth_params['oauth_signature'] = base64.b64encode(signature).decode()
        
        # Create authorization header
        auth_header = 'OAuth ' + ', '.join([f'{urllib.parse.quote(str(k), safe="")}="{urllib.parse.quote(str(v), safe="")}"' for k, v in oauth_params.items()])
        return auth_header
    
    async def get_user_info(self) -> Dict:
        """Get Twitter user information"""
        credentials = await self._get_credentials()
        if not credentials:
            return {"success": False, "error": "Twitter credentials not configured"}
        
        url = f"{self.base_url}/users/me"
        params = {
            "user.fields": "public_metrics,verified,description"
        }
        
        headers = {
            "Authorization": f"Bearer {credentials['bearer_token']}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
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
        """Validate Twitter API credentials"""
        credentials = await self._get_credentials()
        if not credentials:
            return {
                "success": False,
                "error": "Twitter credentials not configured in admin dashboard",
                "missing": ["api_key", "api_secret", "access_token", "access_token_secret", "bearer_token"]
            }
        
        # Test with user info API call
        user_info = await self.get_user_info()
        if user_info.get("success"):
            user_data = user_info["user_info"]
            return {
                "success": True,
                "message": "Twitter credentials are valid",
                "username": user_data.get("username"),
                "user_id": user_data.get("id"),
                "follower_count": user_data.get("public_metrics", {}).get("followers_count")
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials or API error",
                "details": user_info.get("error")
            }

# Global instance
twitter_service = TwitterService()

# Export
__all__ = ["TwitterService", "twitter_service"]