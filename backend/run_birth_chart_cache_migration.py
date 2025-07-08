#!/usr/bin/env python3
"""
Birth Chart Caching Migration Script
Adds birth chart caching columns to the users table
"""

import os
import asyncio
import asyncpg
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Run the birth chart cache migration"""
    
    # Database connection - try SQLite first for local testing
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jyotiflow.db")
    
    try:
        logger.info("🚀 Starting birth chart cache migration...")
        
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if migration is needed
        logger.info("📊 Checking current schema...")
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('birth_chart_data', 'birth_chart_hash', 'birth_chart_cached_at', 'birth_chart_expires_at', 'has_free_birth_chart')
        """)
        
        existing_columns = [col['column_name'] for col in columns]
        logger.info(f"📋 Existing cache columns: {existing_columns}")
        
        # Add birth chart caching columns
        if 'birth_chart_data' not in existing_columns:
            logger.info("➕ Adding birth_chart_data column...")
            await conn.execute("ALTER TABLE users ADD COLUMN birth_chart_data JSONB")
        
        if 'birth_chart_hash' not in existing_columns:
            logger.info("➕ Adding birth_chart_hash column...")
            await conn.execute("ALTER TABLE users ADD COLUMN birth_chart_hash VARCHAR(64)")
        
        if 'birth_chart_cached_at' not in existing_columns:
            logger.info("➕ Adding birth_chart_cached_at column...")
            await conn.execute("ALTER TABLE users ADD COLUMN birth_chart_cached_at TIMESTAMP")
        
        if 'birth_chart_expires_at' not in existing_columns:
            logger.info("➕ Adding birth_chart_expires_at column...")
            await conn.execute("ALTER TABLE users ADD COLUMN birth_chart_expires_at TIMESTAMP")
        
        if 'has_free_birth_chart' not in existing_columns:
            logger.info("➕ Adding has_free_birth_chart column...")
            await conn.execute("ALTER TABLE users ADD COLUMN has_free_birth_chart BOOLEAN DEFAULT false")
        
        # Create indexes
        logger.info("🔍 Creating indexes...")
        
        # Check if indexes exist
        indexes = await conn.fetch("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'users' 
            AND indexname IN ('idx_users_birth_chart_hash', 'idx_users_birth_chart_expires')
        """)
        
        existing_indexes = [idx['indexname'] for idx in indexes]
        
        if 'idx_users_birth_chart_hash' not in existing_indexes:
            logger.info("🔍 Creating birth_chart_hash index...")
            await conn.execute("CREATE INDEX idx_users_birth_chart_hash ON users(birth_chart_hash)")
        
        if 'idx_users_birth_chart_expires' not in existing_indexes:
            logger.info("🔍 Creating birth_chart_expires_at index...")
            await conn.execute("CREATE INDEX idx_users_birth_chart_expires ON users(birth_chart_expires_at)")
        
        # Add column comments
        logger.info("📝 Adding column comments...")
        await conn.execute("""
            COMMENT ON COLUMN users.birth_chart_data IS 'Cached birth chart data from Prokerala API to avoid repeated API calls'
        """)
        await conn.execute("""
            COMMENT ON COLUMN users.birth_chart_hash IS 'SHA256 hash of birth details (date+time+location) for cache validation'
        """)
        await conn.execute("""
            COMMENT ON COLUMN users.birth_chart_cached_at IS 'When the birth chart data was cached'
        """)
        await conn.execute("""
            COMMENT ON COLUMN users.birth_chart_expires_at IS 'When the cached birth chart data expires (usually 1 year)'
        """)
        await conn.execute("""
            COMMENT ON COLUMN users.has_free_birth_chart IS 'Whether user has received their free birth chart on signup'
        """)
        
        # Verify migration
        logger.info("✅ Verifying migration...")
        final_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('birth_chart_data', 'birth_chart_hash', 'birth_chart_cached_at', 'birth_chart_expires_at', 'has_free_birth_chart')
            ORDER BY column_name
        """)
        
        logger.info("📋 Migration completed successfully!")
        logger.info("🔧 New columns added:")
        for col in final_columns:
            logger.info(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']}, default: {col['column_default']})")
        
        # Check indexes
        final_indexes = await conn.fetch("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'users' 
            AND indexname IN ('idx_users_birth_chart_hash', 'idx_users_birth_chart_expires')
        """)
        
        logger.info("🔍 Indexes created:")
        for idx in final_indexes:
            logger.info(f"   - {idx['indexname']}")
        
        # Test the cache service
        logger.info("🧪 Testing cache service...")
        from services.birth_chart_cache_service import BirthChartCacheService
        
        cache_service = BirthChartCacheService(DATABASE_URL)
        
        # Test hash generation
        test_birth_details = {
            'date': '1990-01-01',
            'time': '10:30',
            'location': 'Chennai, India',
            'timezone': 'Asia/Kolkata'
        }
        
        test_hash = cache_service.generate_birth_details_hash(test_birth_details)
        logger.info(f"✅ Hash generation test: {test_hash[:16]}...")
        
        # Test cache statistics
        stats = await cache_service.get_cache_statistics()
        logger.info(f"📊 Cache statistics: {stats}")
        
        await conn.close()
        
        logger.info("🎉 Birth chart caching migration completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   1. Restart your application server")
        logger.info("   2. Test the birth chart endpoints")
        logger.info("   3. Monitor cache hit rates")
        logger.info("   4. Set up cache cleanup scheduled tasks")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        exit(1)