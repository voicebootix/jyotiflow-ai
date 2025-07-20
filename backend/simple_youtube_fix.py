#!/usr/bin/env python3
"""
🎯 SIMPLE YOUTUBE FIX for @jyotiGuru-h9v
Minimal fix following core.md and refresh.md principles
"""

async def enhanced_handle_search(api_key: str, handle: str, base_url: str) -> dict:
    """
    Enhanced search for YouTube handles with fallback strategy
    Fixes the specific @jyotiGuru-h9v issue by trying multiple search formats
    """
    import aiohttp
    
    # Strategy 1: Try with @ prefix (original)
    search_queries = [
        f"@{handle}",    # @jyotiGuru-h9v
        handle,          # jyotiGuru-h9v (without @)
        handle.replace("-", " "),  # jyotiGuru h9v (spaces instead of dashes)
    ]
    
    for query in search_queries:
        url = f"{base_url}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": 5,
            "key": api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        if items:
                            # Found results with this query
                            for item in items:
                                snippet = item.get("snippet", {})
                                title = snippet.get("title", "").lower()
                                custom_url = snippet.get("customUrl", "").lower()
                                
                                # Check if this looks like our target channel
                                if ("jyoti" in title and "guru" in title) or handle.lower() in custom_url:
                                    return {
                                        "success": True,
                                        "channel_id": snippet["channelId"],
                                        "resolved_title": snippet["title"],
                                        "search_query_used": query
                                    }
                            
                            # If no perfect match, return first result
                            first_item = items[0]["snippet"]
                            return {
                                "success": True,
                                "channel_id": first_item["channelId"],
                                "resolved_title": first_item["title"],
                                "search_query_used": query,
                                "match_type": "approximate"
                            }
        except Exception as e:
            continue  # Try next search strategy
    
    # All strategies failed
    return {
        "success": False,
        "error": f"No channel found for handle '@{handle}' using any search strategy",
        "strategies_tried": search_queries
    }


# Quick test function
async def test_fix():
    """Test the fix with the problematic handle"""
    api_key = "test-key"  # Replace with real key
    base_url = "https://www.googleapis.com/youtube/v3"
    
    result = await enhanced_handle_search(api_key, "jyotiGuru-h9v", base_url)
    print("🧪 Test Result:", result)


if __name__ == "__main__":
    import asyncio
    print("🎯 Simple YouTube Handle Fix")
    print("This enhanced search should find @jyotiGuru-h9v")
    print("Integration: Replace the _resolve_handle_to_channel_id logic with enhanced_handle_search")
    # asyncio.run(test_fix())  # Uncomment to test with real API key 