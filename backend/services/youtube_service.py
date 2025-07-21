"""
🎥 YOUTUBE SERVICE - Real API Validation
Validates YouTube API credentials by making actual API calls
"""

import aiohttp
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class YouTubeService:
    """Real YouTube API validation service"""
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self._credentials_cache = None
    
    async def validate_credentials(self, api_key: str, channel_input: str) -> Dict:
        """
        Validate YouTube credentials by making real API calls
        Supports Channel ID, Channel URL, or Channel Handle (core.md & refresh.md compliant)
        Returns: {"success": bool, "message": str, "error": str}
        """
        try:
            # Test 1: Validate API key by calling channels endpoint
            channel_test = await self._test_api_key(api_key)
            if not channel_test["success"]:
                return channel_test
            
            # Test 2: Convert input to Channel ID and validate
            channel_conversion = await self._convert_to_channel_id(api_key, channel_input)
            if not channel_conversion["success"]:
                return channel_conversion
            
            actual_channel_id = channel_conversion["channel_id"]
            
            # Test 3: Validate the converted channel ID
            channel_validation = await self._validate_channel_id(api_key, actual_channel_id)
            if not channel_validation["success"]:
                return channel_validation
            
            # All tests passed
            return {
                "success": True,
                "message": f"YouTube credentials validated successfully. Channel: {channel_validation.get('channel_info', {}).get('title', 'Unknown')}",
                "channel_info": channel_validation.get("channel_info", {}),
                "original_input": channel_input,
                "resolved_channel_id": actual_channel_id
            }
            
        except Exception as e:
            logger.error(f"YouTube validation error: {e}")
            return {
                "success": False,
                "error": f"YouTube validation failed: {str(e)}"
            }
    
    async def _test_api_key(self, api_key: str) -> Dict:
        """Test if API key is valid by calling YouTube API (API key only - no OAuth required)"""
        try:
            # Use search endpoint instead of mine=true (which requires OAuth 2.0)
            url = f"{self.base_url}/search"
            params = {
                "part": "snippet",
                "q": "youtube api test",
                "type": "video",
                "maxResults": 1,
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
                        # Additional validation: check if we got valid search results
                        data = await response.json()
                        if "items" in data:
                            return {
                                "success": True,
                                "message": "YouTube API key is valid and working"
                            }
                        else:
                            return {
                                "success": False,
                                "error": "YouTube API key valid but returned unexpected data format"
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
    
    async def _convert_to_channel_id(self, api_key: str, channel_input: str) -> Dict:
        """
        Convert various YouTube channel input formats to Channel ID
        Supports: Channel ID, Channel URL, Channel Handle (core.md & refresh.md compliant)
        """
        try:
            # Clean up input
            channel_input = channel_input.strip()
            
            # Case 1: Already a Channel ID (starts with UC and 24 chars total - YouTube standard format)
            # Example: UCxxxxxxxxxxxxxxxxxxx (UC + 22 base64-like characters)
            if channel_input.startswith('UC') and len(channel_input) == 24:
                return {
                    "success": True,
                    "channel_id": channel_input,
                    "input_type": "channel_id"
                }
            
            # Case 2: Channel Handle (@username format)
            if channel_input.startswith('@'):
                handle = channel_input[1:]  # Remove @ prefix
                return await self._resolve_handle_to_channel_id(api_key, handle)
            
            # Case 3: Channel URL (various formats)
            if 'youtube.com' in channel_input:
                return await self._resolve_url_to_channel_id(api_key, channel_input)
            
            # Case 4: Plain username (try as handle)
            if not channel_input.startswith('UC') and len(channel_input) > 0:
                return await self._resolve_handle_to_channel_id(api_key, channel_input)
            
            # Case 5: Invalid format
            return {
                "success": False,
                "error": "Invalid channel format. Please provide: Channel ID (UC...), Channel URL (youtube.com/...), or Handle (@username)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Channel input conversion failed: {str(e)}"
            }
    
    async def _resolve_handle_to_channel_id(self, api_key: str, handle: str) -> Dict:
        """
        Resolve YouTube handle/username to Channel ID using search API
        (YouTube API v3 doesn't have direct handle→ID endpoint)
        Fixed: Enhanced debugging and fallback strategies
        """
        try:
            # Log the handle being resolved for debugging
            logger.info(f"🔍 Resolving YouTube handle: @{handle}")
            
            # Try multiple search strategies in sequence
            search_strategies = [
                f"@{handle}",           # Original with @
                handle,                 # Without @ prefix
                handle.replace("-", " ") if "-" in handle else None,  # Spaces instead of dashes
                handle.replace("-", "").replace("_", "") if "-" in handle or "_" in handle else None  # Remove separators
            ]
            
            for i, search_query in enumerate(search_strategies):
                if search_query is None:
                    continue
                    
                logger.info(f"🔍 Search strategy {i+1}: '{search_query}'")
                result = await self._search_channels_by_query(api_key, search_query, handle, i)
                if result["success"]:
                    logger.info(f"✅ Found channel with strategy {i+1}: {result.get('resolved_title')}")
                    return result
                else:
                    logger.warning(f"❌ Strategy {i+1} failed: {result.get('error')}")
            
            # Enhanced error message with debugging info
            return {
                "success": False,
                "error": f"No channel found for handle '@{handle}'. Please check the handle or use Channel ID instead.",
                "debug_info": {
                    "strategies_tried": [s for s in search_strategies if s is not None],
                    "suggestions": [
                        "Verify your YouTube API key is active in Google Cloud Console",
                        "Check that YouTube Data API v3 is enabled", 
                        "Ensure your channel is public and not suspended",
                        "Try using your channel URL instead of Channel ID",
                        "Make sure your API key has the correct restrictions"
                    ],
                    "help_links": [
                        {"text": "YouTube Data API Setup", "url": "https://developers.google.com/youtube/v3/getting-started"},
                        {"text": "Find Your Channel ID", "url": "https://support.google.com/youtube/answer/3250431"}
                    ]
                }
            }
                        
        except Exception as e:
            logger.error(f"❌ YouTube handle resolution failed: {e}")
            return {
                "success": False,
                "error": f"Handle resolution failed: {str(e)}"
            }
    
    async def _search_channels_by_query(self, api_key: str, search_query: str, original_handle: str, strategy_index: int) -> Dict:
        """
        Search for channels using a specific query
        Fixed: Uses separate session for each call to prevent resource conflicts
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                "part": "snippet",
                "q": search_query,
                "type": "channel",
                "maxResults": 5,
                "key": api_key
            }
            
            # Use separate session for each search to prevent resource conflicts
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"Search failed: HTTP {response.status}"
                        }
                        
                        data = await response.json()
                        items = data.get("items", [])
                        
                    if not items:
                        return {"success": False, "error": "No channels found"}
                    
                    # Look for best match using generic matching logic
                    best_match = self._find_best_channel_match(items, original_handle)
                    if best_match:
                        strategy_names = ["handle", "handle_fallback", "handle_space_fallback"]
                                return {
                                    "success": True,
                            "channel_id": best_match["channelId"],
                            "input_type": strategy_names[strategy_index] if strategy_index < len(strategy_names) else "handle_generic",
                            "resolved_title": best_match["title"],
                            "note": f"Found using search query: '{search_query}'"
                        }
                    
                    # If no specific match, return first result as approximate
                            first_item = items[0]["snippet"]
                            return {
                                "success": True,
                                "channel_id": first_item["channelId"],
                        "input_type": f"handle_approximate_{strategy_index}",
                                "resolved_title": first_item["title"],
                        "note": f"Approximate match using search query: '{search_query}'"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Search query failed: {str(e)}"
            }
    
    def _find_best_channel_match(self, items: list, original_handle: str) -> Dict:
        """
        Find the best matching channel from search results
        Fixed: Removed hardcoded matching, now uses generic similarity logic
        """
        handle_lower = original_handle.lower()
        
        for item in items:
            snippet = item.get("snippet", {})
            title = snippet.get("title", "").lower()
            custom_url = snippet.get("customUrl", "").lower()
            
            # Generic matching logic (not hardcoded to specific names)
            if (handle_lower in custom_url or 
                handle_lower in title or
                self._calculate_similarity(handle_lower, title) > 0.6):
                return snippet
        
        return None
    
    def _calculate_similarity(self, handle: str, title: str) -> float:
        """
        Calculate similarity between handle and channel title
        Simple word-based similarity for better matching
        """
        handle_words = set(handle.replace("-", " ").replace("_", " ").split())
        title_words = set(title.replace("-", " ").replace("_", " ").split())
        
        if not handle_words or not title_words:
            return 0.0
        
        common_words = handle_words.intersection(title_words)
        return len(common_words) / len(handle_words.union(title_words))
    
    async def _resolve_url_to_channel_id(self, api_key: str, url: str) -> Dict:
        """
        Extract Channel ID from various YouTube URL formats
        """
        try:
            import re
            
            # Pattern 1: Channel ID in URL (e.g., youtube.com/channel/UCxxxxx)
            channel_id_pattern = r'youtube\.com/channel/([A-Za-z0-9_-]{24})'
            match = re.search(channel_id_pattern, url)
            if match:
                return {
                    "success": True,
                    "channel_id": match.group(1),
                    "input_type": "channel_url"
                }
            
            # Pattern 2: User URL (e.g., youtube.com/user/username)
            user_pattern = r'youtube\.com/user/([A-Za-z0-9_-]+)'
            match = re.search(user_pattern, url)
            if match:
                username = match.group(1)
                return await self._resolve_handle_to_channel_id(api_key, username)
            
            # Pattern 3: Custom URL (e.g., youtube.com/c/customname)
            custom_pattern = r'youtube\.com/c/([A-Za-z0-9_-]+)'
            match = re.search(custom_pattern, url)
            if match:
                custom_name = match.group(1)
                return await self._resolve_handle_to_channel_id(api_key, custom_name)
            
            # Pattern 4: Handle URL (e.g., youtube.com/@handle)
            handle_pattern = r'youtube\.com/@([A-Za-z0-9_-]+)'
            match = re.search(handle_pattern, url)
            if match:
                handle = match.group(1)
                return await self._resolve_handle_to_channel_id(api_key, handle)
            
            # Pattern 5: Short URL (e.g., youtu.be/...)
            if 'youtu.be' in url:
                return {
                    "success": False,
                    "error": "Video URLs (youtu.be) not supported. Please provide channel URL or Channel ID."
                }
            
            return {
                "success": False,
                "error": f"Unsupported YouTube URL format: {url}. Please use channel URL, handle, or Channel ID."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"URL resolution failed: {str(e)}"
            }

# Global instance for consistent import pattern (refresh.md: consistent architecture)
youtube_service = YouTubeService()

# Export
__all__ = ["YouTubeService", "youtube_service"]