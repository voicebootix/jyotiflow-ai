"""
Fix Service Configuration Cache Schema Issues
Ensures the service_configuration_cache table has the correct schema
"""

import os
import asyncio
import asyncpg
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_service_configuration_cache():
    """Fix service_configuration_cache table schema issues"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
        conn = await asyncpg.connect(DATABASE_URL)
        
        logger.info("🔧 Checking service_configuration_cache table schema...")
        
        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'service_configuration_cache'
            )
        """)
        
        if not table_exists:
            logger.info("📦 Creating service_configuration_cache table...")
            await conn.execute("""
                CREATE TABLE service_configuration_cache (
                    service_name VARCHAR(100) PRIMARY KEY,
                    configuration JSONB NOT NULL,
                    persona_config JSONB NOT NULL,
                    knowledge_domains TEXT[] NOT NULL,
                    cached_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
                )
            """)
            logger.info("✅ service_configuration_cache table created")
        else:
            logger.info("✅ service_configuration_cache table exists")
            
            # Check if cached_at column exists
            cached_at_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'service_configuration_cache' 
                    AND column_name = 'cached_at'
                )
            """)
            
            if not cached_at_exists:
                logger.info("➕ Adding cached_at column to service_configuration_cache...")
                await conn.execute("""
                    ALTER TABLE service_configuration_cache 
                    ADD COLUMN cached_at TIMESTAMP DEFAULT NOW()
                """)
                logger.info("✅ cached_at column added")
            else:
                logger.info("✅ cached_at column already exists")
            
            # Check if expires_at column exists
            expires_at_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'service_configuration_cache' 
                    AND column_name = 'expires_at'
                )
            """)
            
            if not expires_at_exists:
                logger.info("➕ Adding expires_at column to service_configuration_cache...")
                await conn.execute("""
                    ALTER TABLE service_configuration_cache 
                    ADD COLUMN expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
                """)
                logger.info("✅ expires_at column added")
            else:
                logger.info("✅ expires_at column already exists")
        
        # Ensure proper indexes exist
        logger.info("🔍 Checking indexes...")
        
        # Check for primary key (should exist)
        pk_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'service_configuration_cache' 
                AND indexname LIKE '%_pkey'
            )
        """)
        
        if not pk_exists:
            logger.info("➕ Adding primary key to service_configuration_cache...")
            await conn.execute("""
                ALTER TABLE service_configuration_cache 
                ADD PRIMARY KEY (service_name)
            """)
            logger.info("✅ Primary key added")
        
        # Add index on cached_at for performance
        cached_at_index_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'service_configuration_cache' 
                AND indexname = 'idx_service_config_cached_at'
            )
        """)
        
        if not cached_at_index_exists:
            logger.info("➕ Adding index on cached_at...")
            await conn.execute("""
                CREATE INDEX idx_service_config_cached_at 
                ON service_configuration_cache(cached_at)
            """)
            logger.info("✅ cached_at index added")
        
        # Add index on expires_at for cleanup queries
        expires_at_index_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'service_configuration_cache' 
                AND indexname = 'idx_service_config_expires_at'
            )
        """)
        
        if not expires_at_index_exists:
            logger.info("➕ Adding index on expires_at...")
            await conn.execute("""
                CREATE INDEX idx_service_config_expires_at 
                ON service_configuration_cache(expires_at)
            """)
            logger.info("✅ expires_at index added")
        
        await conn.close()
        logger.info("✅ Service configuration cache schema fixed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error fixing service configuration cache: {e}")
        raise

async def cleanup_expired_cache():
    """Clean up expired cache entries"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Delete expired entries and count them
        result = await conn.execute("""
            DELETE FROM service_configuration_cache 
            WHERE expires_at < NOW()
        """)
        # Result format is "DELETE n" where n is the number of deleted rows
        deleted_count = int(result.split()[-1]) if result and result.startswith("DELETE") else 0
        
        if deleted_count:
            logger.info(f"🧹 Cleaned up {deleted_count} expired cache entries")
        else:
            logger.info("✅ No expired cache entries to clean up")
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up cache: {e}")
        # Don't raise - cleanup failure shouldn't break the system

if __name__ == "__main__":
    asyncio.run(fix_service_configuration_cache())
    asyncio.run(cleanup_expired_cache())