#!/usr/bin/env python3
"""
Test script for Global Knowledge Collection System
Run this to test the new global knowledge collection features
"""

import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from global_knowledge_collector import GlobalKnowledgeCollector, collect_global_knowledge

async def test_single_category():
    """Test collecting from a single category"""
    logger.info("🧪 Testing single category collection...")
    
    async with GlobalKnowledgeCollector() as collector:
        # Test world news category
        articles = await collector.collect_category("world_news", collector.sources["world_news"])
        
        logger.info(f"✅ Collected {len(articles)} world news articles")
        
        if articles:
            sample = articles[0]
            logger.info("📰 Sample article:")
            logger.info(f"  Title: {sample['title']}")
            logger.info(f"  Content: {sample['content'][:200]}...")
            logger.info(f"  Tags: {sample['tags']}")
            logger.info(f"  Domain: {sample['knowledge_domain']}")

async def test_all_categories():
    """Test collecting from all categories"""
    logger.info("🧪 Testing ALL categories collection...")
    
    articles = await collect_global_knowledge()
    
    logger.info(f"✅ Total articles collected: {len(articles)}")
    
    # Show breakdown by category
    categories = {}
    for article in articles:
        domain = article['knowledge_domain']
        categories[domain] = categories.get(domain, 0) + 1
    
    logger.info("📊 Articles by category:")
    for category, count in categories.items():
        logger.info(f"  {category}: {count} articles")

async def test_content_quality():
    """Test the quality of collected content"""
    logger.info("🧪 Testing content quality...")
    
    articles = await collect_global_knowledge()
    
    if not articles:
        logger.error("❌ No articles collected!")
        return
    
    # Quality checks
    quality_stats = {
        'total': len(articles),
        'with_content': 0,
        'min_content_length': float('inf'),
        'max_content_length': 0,
        'avg_content_length': 0,
        'categories': set(),
        'unique_titles': set()
    }
    
    total_content_length = 0
    
    for article in articles:
        title = article['title']
        content = article['content']
        
        if content and len(content) > 50:
            quality_stats['with_content'] += 1
            
        content_len = len(content)
        quality_stats['min_content_length'] = min(quality_stats['min_content_length'], content_len)
        quality_stats['max_content_length'] = max(quality_stats['max_content_length'], content_len)
        total_content_length += content_len
        
        quality_stats['categories'].add(article['knowledge_domain'])
        quality_stats['unique_titles'].add(title)
    
    quality_stats['avg_content_length'] = total_content_length / len(articles) if articles else 0
    
    logger.info("📊 Content Quality Report:")
    logger.info(f"  Total articles: {quality_stats['total']}")
    logger.info(f"  Articles with good content: {quality_stats['with_content']}")
    logger.info(f"  Unique titles: {len(quality_stats['unique_titles'])}")
    logger.info(f"  Categories covered: {len(quality_stats['categories'])}")
    logger.info(f"  Avg content length: {quality_stats['avg_content_length']:.0f} chars")
    logger.info(f"  Content length range: {quality_stats['min_content_length']} - {quality_stats['max_content_length']}")

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Global Knowledge Collection Tests...")
    
    try:
        # Test 1: Single category
        await test_single_category()
        await asyncio.sleep(2)
        
        # Test 2: All categories
        await test_all_categories()
        await asyncio.sleep(2)
        
        # Test 3: Content quality
        await test_content_quality()
        
        logger.info("🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Install required packages reminder
    logger.info("📦 Required packages: aiohttp, feedparser")
    logger.info("   Install with: pip install aiohttp feedparser")
    
    # Run tests
    asyncio.run(main())
