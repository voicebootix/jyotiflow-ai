"""
JyotiFlow.ai Database Pool Initialization
Provides shared database pool for the entire application
Follows single responsibility principle - ONLY creates and manages the database pool
"""

import os
import asyncpg
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database_pool():
    """Create and return a shared database connection pool"""
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
    
    logger.info("Creating shared database connection pool...")
    
    try:
        # Create pool with production-ready settings
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            connect_timeout=15,
            command_timeout=60,
            server_settings={
                'application_name': 'jyotiflow_main_app'
            }
        )
        
        # Test the pool
        async with db_pool.acquire() as test_conn:
            await test_conn.fetchval("SELECT 1")
        
        logger.info("Database pool created and tested successfully")
        return db_pool
        
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

async def initialize_jyotiflow_simple():
    """Initialize JyotiFlow with ONLY database pool creation - no migrations, no table creation"""
    logger.info("Initializing JyotiFlow database connection...")
    start_time = time.time()
    
    try:
        # ONLY create the database pool - nothing else
        db_pool = await create_database_pool()
        
        elapsed_time = time.time() - start_time
        logger.info(f"JyotiFlow database pool ready in {elapsed_time:.2f} seconds")
        
        return db_pool
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Database pool initialization failed after {elapsed_time:.2f} seconds: {e}")
        raise

async def cleanup_jyotiflow_simple(db_pool=None):
    """Simple cleanup function with proper pool closure"""
    logger.info("Shutting down JyotiFlow.ai...")
    
    if db_pool:
        try:
            await db_pool.close()
            logger.info("Database pool closed successfully")
        except Exception as e:
            logger.error(f"Error closing database pool: {e}")
    else:
        logger.warning("No database pool provided for cleanup")
    
    logger.info("Cleanup completed")

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