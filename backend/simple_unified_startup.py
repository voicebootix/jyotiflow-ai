"""
Simple Unified JyotiFlow.ai Startup System
Clean, minimal database initialization with shared pool architecture
Now includes proper migration support following .cursor rules
"""

import os
try:
    import psycopg
    from psycopg import AsyncConnection
    from psycopg.rows import dict_row
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False
    
# Import our compatibility adapter
from knowledge_seeding_system import AsyncPGCompatPool
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_dashboard_migration_directly(db_pool):
    """Apply the critical dashboard migration directly for Test Results Dashboard functionality"""
    logger.info("🔄 Applying dashboard migration directly (007_fix_missing_monitoring_columns)")
    try:
        async with db_pool.acquire() as conn:
            # First check if tables exist, if not, skip migration gracefully
            tables_exist = await conn.fetchrow("""
                SELECT 
                    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'business_logic_issues') as bli_exists,
                    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'integration_validations') as iv_exists
            """)
            
            if not tables_exist['bli_exists']:
                logger.warning("⚠️ business_logic_issues table doesn't exist - skipping auto_fixable column migration")
            else:
                # Apply the auto_fixable column to business_logic_issues
                await conn.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'business_logic_issues' 
                            AND column_name = 'auto_fixable'
                            AND table_schema = 'public'
                        ) THEN
                            ALTER TABLE business_logic_issues 
                            ADD COLUMN auto_fixable BOOLEAN DEFAULT FALSE;
                            RAISE NOTICE 'Added auto_fixable column to business_logic_issues table';
                        ELSE
                            RAISE NOTICE 'auto_fixable column already exists in business_logic_issues table';
                        END IF;
                    END $$;
                """)
                
                # Add comment for documentation (only if table exists)
                try:
                    await conn.execute("""
                        COMMENT ON COLUMN business_logic_issues.auto_fixable IS 'Indicates if the issue can be automatically fixed by the system';
                    """)
                except Exception:
                    logger.warning("⚠️ Could not add comment to business_logic_issues.auto_fixable column")
            
            if not tables_exist['iv_exists']:
                logger.warning("⚠️ integration_validations table doesn't exist - skipping error_message column migration")
            else:
                # Apply the error_message column to integration_validations
                await conn.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'integration_validations' 
                            AND column_name = 'error_message'
                            AND table_schema = 'public'
                        ) THEN
                            ALTER TABLE integration_validations 
                            ADD COLUMN error_message TEXT;
                            RAISE NOTICE 'Added error_message column to integration_validations table';
                        ELSE
                            RAISE NOTICE 'error_message column already exists in integration_validations table';
                        END IF;
                    END $$;
                """)
                
                # Add comment for documentation (only if table exists)
                try:
                    await conn.execute("""
                        COMMENT ON COLUMN integration_validations.error_message IS 'Detailed error message when validation fails';
                    """)
                except Exception:
                    logger.warning("⚠️ Could not add comment to integration_validations.error_message column")
            
            logger.info("✅ Dashboard migration applied directly - Test Results Dashboard ready")
    except Exception as e:
        logger.warning(f"⚠️ Dashboard migration failed but continuing startup: {e}")
        logger.info("   → Test Results Dashboard may have limited functionality")
        # Don't raise the exception - allow startup to continue

async def initialize_jyotiflow_simple():
    """Simple, reliable database initialization with shared pool and migrations"""
    logger.info("🚀 Starting JyotiFlow.ai with clean architecture...")
    start_time = time.time()
    
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
    
    try:
        # Step 1: Create single shared database pool first
        logger.info("🗄️ Creating shared database pool...")
        if PSYCOPG_AVAILABLE:
            db_pool = AsyncPGCompatPool(database_url)
            logger.info("✅ Using psycopg v3 with asyncpg compatibility adapter")
        else:
            raise ImportError("psycopg not available - please install psycopg[binary]")
        
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
                logger.warning("⚠️ Some migrations failed - applying critical dashboard migration directly")
                # Apply our specific dashboard migration directly since it's critical
                await apply_dashboard_migration_directly(db_pool)
        except ImportError as import_error:
            logger.error(f"❌ Migration system not available: {import_error}")
            logger.info("🔄 Applying critical dashboard migration directly as fallback")
            await apply_dashboard_migration_directly(db_pool)
        except Exception as e:
            # Don't re-wrap our own migration failure exceptions
            if "Migration failure: Test Results Dashboard" in str(e):
                raise  # Re-raise the original exception without wrapping
            else:
                logger.warning(f"⚠️ Migration system failed: {e}")
                logger.info("🔄 Applying critical dashboard migration directly as fallback")
                await apply_dashboard_migration_directly(db_pool)
        
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