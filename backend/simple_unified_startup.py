"""
Simple Unified JyotiFlow.ai Startup System
Clean, minimal database initialization with shared pool architecture
"""

import os
import asyncpg
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_jyotiflow_simple():
    """Simple, reliable database initialization with shared pool"""
    logger.info("🚀 Starting JyotiFlow.ai with clean architecture...")
    start_time = time.time()
    
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
    
    try:
        # Create single shared database pool
        logger.info("🗄️ Creating shared database pool...")
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
            server_settings={
                'application_name': 'jyotiflow_clean_system'
            }
        )
        
        # Test connection
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