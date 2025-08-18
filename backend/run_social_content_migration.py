#!/usr/bin/env python3
"""
Run social_content table migration for RAG content storage
"""
import asyncio
import asyncpg
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Run the social_content migration"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Read migration file
        migration_file = "backend/migrations/025_add_social_content_columns.sql"
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Connect and run migration
        conn = await asyncpg.connect(database_url)
        try:
            await conn.execute(migration_sql)
            logger.info("✅ Social content migration completed successfully")
            return True
        finally:
            await conn.close()
            
    except FileNotFoundError:
        logger.error(f"Migration file not found: {migration_file}")
        return False
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    exit(0 if success else 1)
