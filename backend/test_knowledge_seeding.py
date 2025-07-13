#!/usr/bin/env python3
"""
Test script for knowledge seeding functionality
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_knowledge_seeding():
    """Test the knowledge seeding functionality"""
    try:
        logger.info("🧪 Testing Knowledge Seeding Functionality")
        
        # Test 1: Import the seeder
        logger.info("📦 Testing imports...")
        try:
            from knowledge_seeding_system import KnowledgeSeeder
            logger.info("✅ KnowledgeSeeder imported successfully")
        except Exception as e:
            logger.error(f"❌ Failed to import KnowledgeSeeder: {e}")
            return False
        
        # Test 2: Check dependencies
        logger.info("🔍 Checking dependencies...")
        try:
            import asyncpg  # type: ignore
            logger.info("✅ asyncpg available")
        except ImportError:
            logger.error("❌ asyncpg not available")
            return False
            
        try:
            from openai import AsyncOpenAI  # type: ignore
            logger.info("✅ OpenAI client available")
        except ImportError:
            logger.error("❌ OpenAI client not available")
        
        # Test 3: Check environment variables
        logger.info("🔑 Checking environment variables...")
        database_url = os.getenv("DATABASE_URL")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if database_url:
            logger.info("✅ DATABASE_URL is set")
        else:
            logger.error("❌ DATABASE_URL not set")
            return False
            
        if openai_key and openai_key != "fallback_key":
            logger.info("✅ OPENAI_API_KEY is set")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not set or using fallback")
        
        # Test 4: Test database connection
        logger.info("🗄️ Testing database connection...")
        try:
            db_pool = await asyncpg.create_pool(database_url)
            async with db_pool.acquire() as conn:
                # Check if table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'rag_knowledge_base'
                    )
                """)
                if table_exists:
                    logger.info("✅ rag_knowledge_base table exists")
                else:
                    logger.error("❌ rag_knowledge_base table does not exist")
                    return False
                    
                # Check current knowledge count
                count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
                logger.info(f"📊 Current knowledge base count: {count}")
                
            await db_pool.close()
            logger.info("✅ Database connection test successful")
            
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
        
        # Test 5: Test seeder initialization
        logger.info("🚀 Testing seeder initialization...")
        try:
            seeder = KnowledgeSeeder(None, openai_key or "fallback_key")
            logger.info("✅ Seeder initialized successfully")
        except Exception as e:
            logger.error(f"❌ Seeder initialization failed: {e}")
            return False
        
        # Test 6: Test OpenAI API if available
        if openai_key and openai_key != "fallback_key":
            logger.info("🤖 Testing OpenAI API...")
            try:
                from openai import AsyncOpenAI  # type: ignore
                client = AsyncOpenAI(api_key=openai_key)
                response = await client.embeddings.create(
                    model="text-embedding-ada-002",
                    input="test"
                )
                logger.info("✅ OpenAI API test successful")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI API test failed: {e}")
        
        logger.info("✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_knowledge_seeding())
    sys.exit(0 if success else 1)