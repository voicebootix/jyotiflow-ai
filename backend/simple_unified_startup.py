"""
Simple Unified JyotiFlow.ai Startup System
Clean, minimal database initialization with shared pool architecture
Now includes proper migration support following .cursor rules
"""

import os
import asyncpg
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_jyotiflow_simple():
    """Simple, reliable database initialization with shared pool and migrations"""
    logger.info("🚀 Starting JyotiFlow.ai with clean architecture...")
    start_time = time.time()
    
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
    
    try:
        # Step 1: Apply database migrations first (critical for test functionality)
        logger.info("🔄 Applying database migrations...")
        try:
            from run_migrations import MigrationRunner
            migration_runner = MigrationRunner(database_url)
            migration_success = await migration_runner.run_migrations()
            if migration_success:
                logger.info("✅ Database migrations applied successfully")
            else:
                logger.warning("⚠️ Some migrations failed but continuing startup")
        except Exception as e:
            logger.error(f"❌ Migration system failed: {e}")
            logger.warning("⚠️ Continuing without migrations - some features may not work")
        
        # Step 2: Create single shared database pool
        logger.info("🗄️ Creating shared database pool...")
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            timeout=15,  # Connection timeout in seconds
            command_timeout=60,
            server_settings={
                'application_name': 'jyotiflow_clean_system'
            }
        )
        
        # Step 3: Test connection
        logger.info("🧪 Testing database connection...")
        async with db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1 as test")
            if result != 1:
                raise Exception("Database test query failed")
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ JyotiFlow.ai initialized successfully in {elapsed_time:.2f} seconds")
        logger.info("🎯 Clean shared pool architecture ready")
        
        return db_pool
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ System initialization failed after {elapsed_time:.2f} seconds: {e}")
        raise

async def cleanup_jyotiflow_simple(db_pool=None):
    """Simple cleanup function with proper pool closure"""
    logger.info("🔄 Shutting down JyotiFlow.ai...")
    
    if db_pool:
        try:
            await db_pool.close()
            logger.info("🗄️ Database pool closed successfully")
        except Exception as e:
            logger.error(f"⚠️ Error closing database pool: {e}")
    else:
        logger.warning("⚠️ No database pool provided for cleanup")
    
    logger.info("✅ Cleanup completed")

# Global instance tracking (minimal)
_startup_instance = None

async def initialize_unified_jyotiflow():
    """Main entry point for compatibility with existing main.py"""
    global _startup_instance
    return await initialize_jyotiflow_simple()

async def cleanup_unified_system(db_pool=None):
    """Cleanup entry point for compatibility with existing main.py"""  
    await cleanup_jyotiflow_simple(db_pool)

def get_unified_system_status():
    """Get simple system status for health checks"""
    return {
        "system_available": True,
        "architecture": "clean_shared_pool",
        "startup_type": "simplified"
    }