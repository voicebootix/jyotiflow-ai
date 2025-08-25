"""
Global Knowledge Collector for JyotiFlow RAG System
Collects real-time knowledge from free sources across all domains
"""

import asyncio
import aiohttp
import feedparser
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class GlobalKnowledgeCollector:
    """
    Comprehensive global knowledge collection system
    Collects from multiple free sources with equal priority
    """
    
    def __init__(self):
        self.sources = {
            # --- Existing Categories ---
            "world_news": {
                "feeds": [
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.bbci.co.uk/news/world/rss.xml", 
                    "https://www.reuters.com/tools/rss",
                    "https://www.aljazeera.com/xml/rss/all.xml"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            },
            "indian_news": {
                "feeds": [
                    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
                    "https://www.thehindu.com/news/feeder/default.rss",
                    "https://indianexpress.com/feed/"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            },
            
            # --- NEW Categories ---
            "astrology": {
                "feeds": [
                    "https://www.drikpanchang.com/rss/drikpanchang-rss.xml",
                    "https://www.indastro.com/feeds/posts/default",
                    "https://www.speakingtree.in/blogs/astrology/feed"
                ],
                "priority": 2, # Higher priority
                "articles_per_source": 5
            },
            "tamil_knowledge": {
                "feeds": [
                    "https://keetru.com/feed",
                    "https://www.vikatan.com/rss/art-and-culture"
                ],
                "priority": 2, # Higher priority
                "articles_per_source": 4
            },
            "world_religions": {
                "feeds": [
                    "https://www.speakingtree.in/blogs/feed",
                    "https://www.learnreligions.com/feed",
                    "https://www.buddhanet.net/pali_promo.xml"
                ],
                "priority": 1,
                "articles_per_source": 4
            },

            # --- Existing Categories (Retained) ---
            "science_technology": {
                "feeds": [
                    "https://www.sciencedaily.com/rss/all.xml",
                    "https://www.space.com/feeds/all",
                    "https://rss.cnn.com/rss/edition_technology.rss",
                    "https://feeds.feedburner.com/oreilly/radar"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            },
            "health_medicine": {
                "feeds": [
                    "https://www.who.int/rss-feeds/news-english.xml",
                    "https://www.medicalnewstoday.com/rss",
                    "https://www.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            },
            "finance_economics": {
                "feeds": [
                    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
                    "https://www.moneycontrol.com/rss/latestnews.xml",
                    "https://feeds.reuters.com/reuters/businessNews"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            },
            "environment_climate": {
                "feeds": [
                    "https://www.un.org/sustainabledevelopment/feed/",
                    "https://www.nationalgeographic.com/environment/rss/"
                ],
                "priority": 1,
                "articles_per_source": 3 # Reduced for balance
            }
        }
        
        # Session for HTTP requests
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'JyotiFlow-Knowledge-Collector/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def clean_content(self, text: str) -> str:
        """Clean and normalize content text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common RSS artifacts
        text = re.sub(r'\[CDATA\[|\]\]', '', text)
        
        return text[:2000]  # Limit content length
    
    def extract_tags_from_content(self, title: str, content: str, category: str) -> List[str]:
        """Extract relevant tags from content"""
        base_tags = [category, "current_events", "global_knowledge"]
        
        # Add category-specific tags
        if "news" in category:
            base_tags.extend(["breaking_news", "world_events"])
        elif "science" in category:
            base_tags.extend(["research", "innovation", "discovery"])
        elif "health" in category:
            base_tags.extend(["wellness", "medical", "health_news"])
        elif "finance" in category:
            base_tags.extend(["economy", "market", "business"])
        elif "environment" in category:
            base_tags.extend(["climate", "sustainability", "ecology"])
        
        return base_tags
    
    async def collect_rss_feed(self, rss_url: str, category: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """Collect articles from a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"📡 Collecting from {urlparse(rss_url).netloc}...")
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                logger.warning(f"⚠️ No entries found in {rss_url}")
                return articles
            
            # Process entries
            for entry in feed.entries[:max_articles]:
                try:
                    # Clean and prepare content - using getattr for safety
                    title = getattr(entry, "title", "")
                    link = getattr(entry, "link", None) or rss_url  # fallback to feed URL
                    
                    title_cleaned = self.clean_content(title)
                    content = self.clean_content(
                        getattr(entry, 'summary', '') or 
                        getattr(entry, 'description', '') or 
                        title_cleaned
                    )
                    
                    if not title_cleaned or len(content) < 50:
                        continue
                    
                    # Create consistent link_var for both source_reference and metadata.source_url
                    link_var = link or rss_url
                    
                    # Create knowledge entry
                    article = {
                        "title": title_cleaned,
                        "content": content,
                        "knowledge_domain": f"global_{category}",
                        "content_type": "news_article",
                        "source_reference": link_var[:255],  # Safely truncate to 255 chars
                        "authority_level": 3,
                        "cultural_context": "global",
                        "tags": self.extract_tags_from_content(title_cleaned, content, category),
                        "metadata": {
                            "published_date": getattr(entry, 'published', str(datetime.now(timezone.utc))),
                            "source_url": link_var[:255],  # Consistent truncation
                            "category": category,
                            "collected_at": datetime.now(timezone.utc).isoformat(),
                            "rss_feed": rss_url
                        }
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing entry from {rss_url}: {e}")
                    continue
            
            logger.info(f"✅ Collected {len(articles)} articles from {urlparse(rss_url).netloc}")
            
        except Exception as e:
            logger.error(f"❌ Error collecting from {rss_url}: {e}")
        
        return articles
    
    async def collect_category(self, category: str, category_config: Dict) -> List[Dict[str, Any]]:
        """Collect all articles from a category with equal priority"""
        category_articles = []
        feeds = category_config["feeds"]
        articles_per_source = category_config["articles_per_source"]
        
        logger.info(f"🔄 Collecting {category} ({len(feeds)} sources)...")
        
        # Collect from all feeds in parallel
        tasks = []
        for feed_url in feeds:
            task = self.collect_rss_feed(feed_url, category, articles_per_source)
            tasks.append(task)
        
        # Wait for all feeds to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                category_articles.extend(result)
            else:
                logger.error(f"❌ Category collection error: {result}")
        
        logger.info(f"✅ {category}: {len(category_articles)} total articles")
        return category_articles
    
    async def collect_all_categories(self) -> List[Dict[str, Any]]:
        """
        Collect from ALL categories with EQUAL priority
        This is the main method for comprehensive knowledge collection
        """
        all_articles = []
        
        logger.info("🌍 Starting global knowledge collection from ALL categories...")
        logger.info(f"📊 Categories: {list(self.sources.keys())}")
        
        # Collect from all categories in parallel
        category_tasks = []
        for category, config in self.sources.items():
            task = self.collect_category(category, config)
            category_tasks.append(task)
        
        # Wait for all categories to complete
        category_results = await asyncio.gather(*category_tasks, return_exceptions=True)
        
        # Combine all results
        for result in category_results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                logger.error(f"❌ Error in category collection: {result}")
        
        # Log summary
        logger.info("📊 Collection Summary:")
        for category in self.sources.keys():
            category_count = len([a for a in all_articles if category in a["knowledge_domain"]])
            logger.info(f"  {category}: {category_count} articles")
        
        logger.info(f"🎉 Total collected: {len(all_articles)} articles from all categories")
        
        return all_articles

    async def fetch_and_parse_feed(self, url: str, max_articles: int) -> List[Dict[str, Any]]:
        """
        Fetches and parses a single RSS feed asynchronously.
        Made public to allow for testing.
        FIX: Runs synchronous feedparser.parse in a separate thread to avoid blocking asyncio event loop.
             Safely truncates source_reference to 255 chars.
        """
        articles = []
        try:
            logger.info(f"📡 Collecting from {urlparse(url).netloc}...")
            
            # Run the synchronous feedparser.parse in a separate thread
            feed = await asyncio.to_thread(feedparser.parse, url)
            
            if not feed.entries:
                logger.warning(f"⚠️ No entries found in {url}")
                return articles
            
            # Process entries
            for entry in feed.entries[:max_articles]:
                try:
                    # Clean and prepare content
                    title = self.clean_content(entry.title)
                    content = self.clean_content(
                        getattr(entry, 'summary', '') or 
                        getattr(entry, 'description', '') or 
                        title
                    )
                    
                    if not title or len(content) < 50:
                        continue
                    
                    # Create knowledge entry
                    article = {
                        "title": title,
                        "content": content,
                        "knowledge_domain": "global_test", # Placeholder for category
                        "content_type": "news_article",
                        "source_reference": (getattr(entry, "link", "") or "")[:255], # Safely truncate to 255 chars
                        "authority_level": 3,
                        "cultural_context": "global",
                        "tags": self.extract_tags_from_content(title, content, "test"), # Placeholder for category
                        "metadata": {
                            "published_date": getattr(entry, 'published', str(datetime.now(timezone.utc))),
                            "source_url": (getattr(entry, "link", "") or url)[:255],  # Consistent truncation
                            "category": "test", # Placeholder for category
                            "collected_at": datetime.now(timezone.utc).isoformat(),
                            "rss_feed": url
                        }
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing entry from {url}: {e}")
                    continue
            
            logger.info(f"✅ Collected {len(articles)} articles from {urlparse(url).netloc}")
            
        except Exception as e:
            logger.error(f"❌ Error collecting from {url}: {e}")
        
        return articles

# Convenience function for easy usage
async def collect_global_knowledge() -> List[Dict[str, Any]]:
    """
    Convenience function to collect global knowledge
    Usage: articles = await collect_global_knowledge()
    """
    async with GlobalKnowledgeCollector() as collector:
        return await collector.collect_all_categories()

# Test function
async def test_collector():
    """Test the collector with a small sample"""
    async with GlobalKnowledgeCollector() as collector:
        # Test just one category first
        test_articles = await collector.collect_category("world_news", collector.sources["world_news"])
        print(f"Test collected {len(test_articles)} articles")
        
        if test_articles:
            print("Sample article:")
            print(f"Title: {test_articles[0]['title']}")
            print(f"Content: {test_articles[0]['content'][:200]}...")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_collector())

