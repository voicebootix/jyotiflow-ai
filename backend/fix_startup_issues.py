"""
Comprehensive Fix for JyotiFlow.ai Startup Issues
Addresses knowledge base seeding, service configuration cache, and Sentry configuration
"""

import os
import asyncio
import asyncpg
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JyotiFlowStartupFixer:
    """Comprehensive fixer for JyotiFlow.ai startup issues with robust connection management"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
        
        # Enhanced connection settings - optimized for Render environment
        self.connection_config = {
            'min_size': 2,
            'max_size': 10,
            'command_timeout': 60,
            'server_settings': {
                'application_name': 'jyotiflow_startup_fixer',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '60',
                'tcp_keepalives_count': '5'
            }
        }
        
    async def _create_robust_connection(self, max_retries: int = 5):
        """Create a robust database connection with progressive backoff"""
        for attempt in range(max_retries):
            conn = None
            try:
                # Progressive timeout: starts at 30s, increases by 10s each attempt
                timeout = 30.0 + (attempt * 10)
                conn = await asyncio.wait_for(
                    asyncpg.connect(
                        self.database_url,
                        command_timeout=self.connection_config['command_timeout'],
                        server_settings=self.connection_config['server_settings']
                    ),
                    timeout=timeout
                )
                
                # Verify connection health - separate try block to ensure cleanup
                try:
                    await conn.fetchval("SELECT 1")
                    return conn
                except Exception as health_error:
                    # Health check failed - close connection before re-raising
                    await conn.close()
                    conn = None  # Prevent double-close in outer handler
                    raise health_error
                    
            except (asyncio.TimeoutError, Exception) as e:
                # Ensure connection is closed if it was created but health check failed
                if conn is not None:
                    try:
                        await conn.close()
                    except Exception:
                        pass  # Ignore cleanup errors
                        
                if attempt == max_retries - 1:
                    raise
                delay = min(2 ** attempt, 10)  # Cap delay at 10 seconds
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}, retrying in {delay}s...")
                await asyncio.sleep(delay)
        
    async def _create_robust_pool(self, max_retries: int = 5):
        """Create a robust database pool with enhanced settings"""
        for attempt in range(max_retries):
            pool = None
            try:
                # Progressive timeout: starts at 40s, increases by 10s each attempt
                timeout = 40.0 + (attempt * 10)
                pool = await asyncio.wait_for(
                    asyncpg.create_pool(
                        self.database_url,
                        min_size=self.connection_config['min_size'],
                        max_size=self.connection_config['max_size'],
                        command_timeout=self.connection_config['command_timeout'],
                        server_settings=self.connection_config['server_settings']
                    ),
                    timeout=timeout
                )
                
                # Test pool health - separate try block to ensure cleanup
                try:
                    async with pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                    return pool
                except Exception as health_error:
                    # Health check failed - close pool before re-raising
                    await pool.close()
                    pool = None  # Prevent double-close in outer handler
                    raise health_error
                    
            except (asyncio.TimeoutError, Exception) as e:
                # Ensure pool is closed if it was created but health check failed
                if pool is not None:
                    try:
                        await pool.close()
                    except Exception:
                        pass  # Ignore cleanup errors
                        
                if attempt == max_retries - 1:
                    raise
                delay = min(2 ** attempt, 10)  # Cap delay at 10 seconds
                logger.warning(f"Pool creation attempt {attempt + 1} failed: {e}, retrying in {delay}s...")
                await asyncio.sleep(delay)
    
    async def fix_all_issues(self):
        """Fix all identified startup issues"""
        logger.info("🔧 Starting comprehensive JyotiFlow.ai startup fixes...")
        
        try:
            # Fix 1: Service Configuration Cache Schema
            await self.fix_service_configuration_cache()
            
            # Fix 2: Knowledge Base Seeding
            await self.fix_knowledge_base_seeding()
            
            # Fix 3: Sentry Configuration (informational)
            self.check_sentry_configuration()
            
            logger.info("✅ All startup issues addressed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error during startup fixes: {e}")
            raise
    
    async def fix_service_configuration_cache(self):
        """Fix service_configuration_cache table schema issues with robust connection handling"""
        conn = None
        try:
            conn = await self._create_robust_connection()
            
            logger.info("🔧 Fixing service_configuration_cache schema...")
            
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
                
                # Check and fix cached_at column
                cached_at_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'service_configuration_cache' 
                        AND column_name = 'cached_at'
                    )
                """)
                
                if not cached_at_exists:
                    logger.info("➕ Adding cached_at column...")
                    await conn.execute("""
                        ALTER TABLE service_configuration_cache 
                        ADD COLUMN cached_at TIMESTAMP DEFAULT NOW()
                    """)
                    logger.info("✅ cached_at column added")
                else:
                    logger.info("✅ cached_at column already exists")
                
                # Check and fix expires_at column
                expires_at_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'service_configuration_cache' 
                        AND column_name = 'expires_at'
                    )
                """)
                
                if not expires_at_exists:
                    logger.info("➕ Adding expires_at column...")
                    await conn.execute("""
                        ALTER TABLE service_configuration_cache 
                        ADD COLUMN expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
                    """)
                    logger.info("✅ expires_at column added")
                else:
                    logger.info("✅ expires_at column already exists")
            
            # Add performance indexes
            await self._ensure_service_cache_indexes(conn)
            
            await conn.close()
            logger.info("✅ Service configuration cache schema fixed!")
            
        except Exception as e:
            logger.error(f"❌ Error fixing service configuration cache: {e}")
            raise
    
    async def _ensure_service_cache_indexes(self, conn):
        """Ensure proper indexes exist for service_configuration_cache"""
        try:
            # Index on cached_at
            cached_at_index_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE tablename = 'service_configuration_cache' 
                    AND indexname = 'idx_service_config_cached_at'
                )
            """)
            
            if not cached_at_index_exists:
                logger.info("➕ Adding cached_at index...")
                await conn.execute("""
                    CREATE INDEX idx_service_config_cached_at 
                    ON service_configuration_cache(cached_at)
                """)
                logger.info("✅ cached_at index added")
            
            # Index on expires_at
            expires_at_index_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE tablename = 'service_configuration_cache' 
                    AND indexname = 'idx_service_config_expires_at'
                )
            """)
            
            if not expires_at_index_exists:
                logger.info("➕ Adding expires_at index...")
                await conn.execute("""
                    CREATE INDEX idx_service_config_expires_at 
                    ON service_configuration_cache(expires_at)
                """)
                logger.info("✅ expires_at index added")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring indexes: {e}")
            # Don't raise - indexes are optional for functionality
    
    async def fix_knowledge_base_seeding(self):
        """Fix knowledge base seeding for PostgreSQL with robust connection handling"""
        conn = None
        try:
            conn = await self._create_robust_connection()
            
            logger.info("🧠 Checking knowledge base seeding...")
            
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'rag_knowledge_base'
                )
            """)
            
            if not table_exists:
                logger.info("📦 Creating rag_knowledge_base table...")
                
                # Ensure required extensions are available
                logger.info("🔧 Ensuring required PostgreSQL extensions...")
                
                # Enable pgcrypto extension for gen_random_uuid()
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
                    logger.info("✅ pgcrypto extension enabled")
                except Exception as e:
                    logger.warning(f"⚠️ Could not enable pgcrypto extension: {e}")
                
                # Check if pgvector extension is available and try to enable it
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    vector_available = True
                    logger.info("✅ pgvector extension enabled")
                except Exception as e:
                    logger.warning(f"⚠️ Could not enable pgvector extension: {e}")
                    vector_available = False
                
                if vector_available:
                    logger.info("✅ Creating table with vector support")
                    await conn.execute("""
                        CREATE TABLE rag_knowledge_base (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            knowledge_domain VARCHAR(100) NOT NULL,
                            content_type VARCHAR(50) NOT NULL,
                            title VARCHAR(500) NOT NULL,
                            content TEXT NOT NULL,
                            metadata JSONB DEFAULT '{}',
                            embedding_vector VECTOR(1536),
                            tags TEXT[] DEFAULT '{}',
                            source_reference VARCHAR(500),
                            authority_level INTEGER DEFAULT 1,
                            cultural_context VARCHAR(100) DEFAULT 'universal',
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
                else:
                    logger.info("⚠️ Creating table without vector support (using fallback)")
                    await conn.execute("""
                        CREATE TABLE rag_knowledge_base (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            knowledge_domain VARCHAR(100) NOT NULL,
                            content_type VARCHAR(50) NOT NULL,
                            title VARCHAR(500) NOT NULL,
                            content TEXT NOT NULL,
                            metadata JSONB DEFAULT '{}',
                            embedding_vector TEXT, -- Store as JSON string instead of vector
                            tags TEXT[] DEFAULT '{}',
                            source_reference VARCHAR(500),
                            authority_level INTEGER DEFAULT 1,
                            cultural_context VARCHAR(100) DEFAULT 'universal',
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
                
                logger.info("✅ rag_knowledge_base table created")
            
            # Check knowledge count
            count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            
            if count == 0:
                logger.info("🌱 Knowledge base is empty, seeding with spiritual wisdom...")
                
                # Import and run the knowledge seeder
                try:
                    from knowledge_seeding_system import KnowledgeSeeder
                    
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    db_pool = None
                    
                    if not openai_api_key or openai_api_key == "fallback_key":
                        logger.info("⚠️ OpenAI API key not available - using basic seeding")
                        seeder = KnowledgeSeeder(None, "fallback_key")
                    else:
                        # Create database pool for seeder with robust settings
                        db_pool = await self._create_robust_pool()
                        seeder = KnowledgeSeeder(db_pool, openai_api_key)
                    
                    try:
                        # Run seeding with timeout
                        await asyncio.wait_for(
                            seeder.seed_complete_knowledge_base(),
                            timeout=120.0  # 2 minute timeout for seeding
                        )
                        logger.info("✅ Knowledge base seeded successfully!")
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Knowledge seeding timed out, system will run in fallback mode")
                    finally:
                        # Always close the pool if it was created
                        if db_pool:
                            await db_pool.close()
                            logger.info("✅ Database pool closed")
                    
                except Exception as seeding_error:
                    import traceback
                    logger.error(f"Knowledge seeding error: {seeding_error}")
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    logger.info("✅ System will work without knowledge base in fallback mode")
            else:
                logger.info(f"✅ Knowledge base already contains {count} pieces")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error fixing knowledge base seeding: {e}")
            # Don't raise - system can work without knowledge base
            pass
    
    def check_sentry_configuration(self):
        """Check and provide guidance on Sentry configuration"""
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if not sentry_dsn:
            logger.info("⚠️ Sentry DSN not configured")
            logger.info("📖 To enable Sentry monitoring:")
            logger.info("   1. Sign up at https://sentry.io")
            logger.info("   2. Create a project for JyotiFlow.ai")
            logger.info("   3. Set SENTRY_DSN environment variable")
            logger.info("   4. Optional: Set SENTRY_TRACES_SAMPLE_RATE=0.1")
            logger.info("✅ Application will run normally without Sentry")
        else:
            logger.info("✅ Sentry DSN configured - monitoring enabled")
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Delete expired entries and count them
            result = await conn.execute("""
                DELETE FROM service_configuration_cache 
                WHERE expires_at < NOW()
            """)
            
            # Extract the number of deleted rows from the result
            # Result format is "DELETE n" where n is the number of deleted rows
            deleted_count = int(result.split()[-1]) if result and result.startswith("DELETE") else 0
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} expired cache entries")
            else:
                logger.info("✅ No expired cache entries to clean up")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up cache: {e}")
            # Don't raise - cleanup failure shouldn't break the system

async def main():
    """Main function to run all fixes"""
    fixer = JyotiFlowStartupFixer()
    await fixer.fix_all_issues()
    await fixer.cleanup_expired_cache()

if __name__ == "__main__":
    asyncio.run(main())