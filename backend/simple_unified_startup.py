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
        # Step 1: Create single shared database pool first
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
        
        # Step 2: Ensure base tables exist first (required for migrations)
        logger.info("🗄️ Ensuring base monitoring tables exist...")
        try:
            async with db_pool.acquire() as conn:
                # Create monitoring tables if they don't exist
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS business_logic_issues (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255),
                        issue_type VARCHAR(100) NOT NULL,
                        description TEXT,
                        severity VARCHAR(20) DEFAULT 'medium',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS integration_validations (
                        id SERIAL PRIMARY KEY,
                        integration_point VARCHAR(100) NOT NULL,
                        validation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) NOT NULL,
                        response_data JSONB,
                        performance_ms INTEGER
                    )
                """)
                logger.info("✅ Base monitoring tables ensured")
        except Exception as table_error:
            logger.error(f"❌ Failed to create base monitoring tables: {table_error}")
            raise Exception(f"Base table creation failed: {table_error}") from table_error
        
        # Step 3: Apply database migrations (critical for test functionality)
        logger.info("🔄 Applying database migrations...")
        try:
            from run_migrations import MigrationRunner
            migration_runner = MigrationRunner(database_url)
            logger.info("🔄 Running migration system...")
            migration_success = await migration_runner.run_migrations()
            if migration_success:
                logger.info("✅ Database migrations applied successfully")
            else:
                logger.error("❌ Database migrations returned False")
                raise Exception("Migration failure: Test Results Dashboard requires successful migrations for auto_fixable and error_message columns")
        except ImportError as import_error:
            logger.error(f"❌ Migration system not available: {import_error}")
            raise Exception("Migration system required: Cannot start without migration support for database-driven features") from import_error
        except Exception as e:
            # Don't re-wrap our own migration failure exceptions
            if "Migration failure: Test Results Dashboard" in str(e):
                raise  # Re-raise the original exception without wrapping
            else:
                logger.error(f"❌ Migration system failed: {e}")
                logger.error("🚫 Halting startup: Test monitor functionality requires successful migrations")
                raise Exception(f"Critical migration failure: {e}. Test Results Dashboard cannot function without proper database schema.") from e
        
        # Step 4: Test connection
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