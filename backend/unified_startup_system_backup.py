"""
Unified JyotiFlow.ai Startup System
Consolidates main app pool, enhanced features initialization, and database fixes
"""

import os
import json
import asyncio
import asyncpg
import logging
import traceback
import time
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedJyotiFlowStartup:
    """Unified startup system handling all database and initialization tasks"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
        self.db_pool = None
        
        # System state tracking
        self.main_pool_ready = False
        self.schema_fixed = False
        self.knowledge_seeded = False
        self.rag_initialized = False
        self.service_configs_ready = False
        
        # Optimized connection settings for production - Compatible with Supabase
        self.pool_config = {
            'min_size': 2,  # Start with minimal connections
            'max_size': 12, # Scale up to reasonable limit
            'command_timeout': 60,
            'connect_timeout': 15,  # Prevent hanging on individual connections
            'server_settings': {
                'application_name': 'jyotiflow_unified_system'
                # Removed TCP keepalive settings - these cause hangs with Supabase connection pooler
            }
        }
    
    async def initialize_complete_system(self):
        """Main entry point - initialize everything in proper sequence"""
        init_start = time.time()
        logger.info("🚀 Starting Unified JyotiFlow.ai Initialization...")
        
        try:
            # Step 1: Validate environment
            logger.info("📋 Step 1/5: Validating environment configuration...")
            step_start = time.time()
            await self._validate_environment()
            logger.info(f"✅ Environment validation completed in {time.time() - step_start:.2f}s")
            
            # Step 2: Create main database pool (with retries) - CRITICAL STEP
            logger.info("🗄️ Step 2/5: Creating main database connection pool...")
            step_start = time.time()
            await self._create_main_pool()
            logger.info(f"✅ Database pool creation completed in {time.time() - step_start:.2f}s")
            
            # Step 3: Fix database schema issues
            logger.info("🔧 Step 3/5: Fixing database schema issues...")
            step_start = time.time()
            await self._fix_database_schema()
            logger.info(f"✅ Database schema fixes completed in {time.time() - step_start:.2f}s")
            
            # Step 4: Initialize enhanced features
            logger.info("⚡ Step 4/5: Initializing enhanced features...")
            step_start = time.time()
            await self._initialize_enhanced_features()
            logger.info(f"✅ Enhanced features initialization completed in {time.time() - step_start:.2f}s")
            
            # Step 5: Final system validation
            logger.info("🔍 Step 5/5: Performing final system validation...")
            step_start = time.time()
            await self._validate_system_health()
            logger.info(f"✅ System validation completed in {time.time() - step_start:.2f}s")
            
            total_time = time.time() - init_start
            logger.info(f"🎉 Unified JyotiFlow.ai system initialized successfully in {total_time:.2f} seconds!")
            logger.info("🎯 All systems operational - ready for production traffic")
            return self.db_pool
            
        except Exception as e:
            logger.error(f"❌ Unified system initialization failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Cleanup on failure
            if self.db_pool:
                try:
                    await self.db_pool.close()
                    self.db_pool = None
                except Exception:
                    pass
            raise
    
    async def _validate_environment(self):
        """Validate all required environment variables and settings"""
        logger.info("🔍 Validating environment configuration...")
        
        # Check DATABASE_URL
        if not self.database_url or self.database_url == "postgresql://user:password@localhost:5432/yourdb":
            raise ValueError("DATABASE_URL environment variable must be properly configured")
        
        # Extract and display database info
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            host_info = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
            logger.info(f"📍 Database target: {host_info}")
        except Exception:
            logger.info("📍 Database target: could not parse URL")
        
        # Check optional configurations
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "fallback_key":
            logger.info("✅ OpenAI API key configured - AI features available")
        else:
            logger.info("⚠️ OpenAI API key not configured - using fallback mode")
        
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            logger.info("✅ Sentry DSN configured - error monitoring enabled")
        else:
            logger.info("⚠️ Sentry DSN not configured - no error monitoring")
        
        logger.info("✅ Environment validation completed")
    
    async def _create_main_pool(self):
        """Create the main database connection pool with robust retry logic and comprehensive logging"""
        logger.info("🔗 Creating main database connection pool...")
        logger.info(f"📍 Database target: {self.database_url.split('@')[1].split('/')[0] if '@' in self.database_url else 'hidden'}")
        
        max_retries = 5
        base_delay = 3  # Start with shorter delays
        max_delay = 30  # Reasonable maximum delay
        
        for attempt in range(max_retries):
            current_pool = None
            try:
                # Calculate exponential backoff delay
                if attempt > 0:
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.info(f"⏸️ Waiting {delay} seconds before retry (backoff strategy)...")
                    await asyncio.sleep(delay)
                
                logger.info(f"🔄 Database connection attempt {attempt + 1}/{max_retries}")
                
                # Reasonable timeout: fast failure instead of hanging
                timeout = 30 if attempt == 0 else 45  # Much more reasonable timeouts
                logger.info(f"⏱️ Using {timeout}s outer timeout with {self.pool_config['connect_timeout']}s connection timeout")
                
                # Log connection attempt details
                logger.info(f"🔧 Pool config - min: {self.pool_config['min_size']}, max: {self.pool_config['max_size']}")
                logger.info("📡 Attempting database connection...")
                
                connection_start = time.time()
                current_pool = await asyncio.wait_for(
                    asyncpg.create_pool(
                        self.database_url,
                        min_size=self.pool_config['min_size'],
                        max_size=self.pool_config['max_size'],
                        command_timeout=self.pool_config['command_timeout'],
                        connect_timeout=self.pool_config['connect_timeout'],
                        server_settings=self.pool_config['server_settings']
                    ),
                    timeout=timeout
                )
                
                connection_time = time.time() - connection_start
                logger.info(f"✅ Database pool created successfully in {connection_time:.2f} seconds")
                
                # Test the connection with comprehensive validation
                logger.info("🧪 Testing database connection and health...")
                test_start = time.time()
                
                async with current_pool.acquire() as conn:
                    # Basic connectivity test
                    result = await conn.fetchval("SELECT 1 as test")
                    if result != 1:
                        raise Exception("Database test query returned unexpected result")
                    logger.info("✅ Basic connectivity test passed")
                    
                    # Database version and info
                    try:
                        version = await conn.fetchval("SELECT version()")
                        logger.info(f"🗄️ Connected to: {version.split(',')[0] if version else 'PostgreSQL'}")
                    except Exception as e:
                        logger.warning(f"⚠️ Database version check failed: {e}")
                    
                    # Check if we have basic tables (validates schema exists)
                    try:
                        table_count = await conn.fetchval("""
                            SELECT COUNT(*) FROM information_schema.tables 
                            WHERE table_schema = 'public'
                        """)
                        logger.info(f"📊 Database schema contains {table_count} tables")
                        if table_count < 3:
                            logger.warning("⚠️ Low table count - database schema may be incomplete")
                    except Exception as e:
                        logger.warning(f"⚠️ Schema validation failed: {e}")
                
                test_time = time.time() - test_start
                logger.info(f"✅ Database health check completed in {test_time:.2f} seconds")
                
                # Success! Assign the working pool
                self.db_pool = current_pool
                self.main_pool_ready = True
                current_pool = None  # Prevent cleanup
                logger.info("🎯 Main database pool ready for production use")
                return
                
            except asyncio.TimeoutError:
                elapsed_total = sum(min(base_delay * (2 ** i), max_delay) for i in range(attempt)) + timeout
                logger.warning(f"⏱️ Connection timeout on attempt {attempt + 1}/{max_retries} ({timeout}s)")
                logger.warning(f"⏰ Total elapsed time: {elapsed_total:.1f} seconds")
                
                if attempt < max_retries - 1:
                    next_timeout = 45  # Next attempt timeout
                    logger.info(f"🔄 Will retry with {next_timeout}s timeout (database may be cold starting)")
                else:
                    logger.error("❌ All connection attempts exhausted - deployment will fail")
                    logger.error("🚨 Database is not responding within reasonable timeframes")
                    self._log_troubleshooting_info()
                    raise
                    
            except asyncpg.InvalidAuthorizationSpecificationError as e:
                logger.error(f"🔐 Authentication failed on attempt {attempt + 1}/{max_retries}")
                logger.error(f"🔍 Auth error: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("🔄 Retrying authentication (may be temporary Supabase issue)...")
                else:
                    logger.error("❌ Database authentication permanently failed")
                    logger.error("💡 Verify DATABASE_URL credentials in Render environment variables")
                    logger.error("🔍 Check if Supabase project is active and not paused")
                    raise
                    
            except (asyncpg.InvalidCatalogNameError, asyncpg.CannotConnectNowError) as e:
                logger.error(f"🗄️ Database availability issue on attempt {attempt + 1}/{max_retries}")
                logger.error(f"🔍 Database error: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("🔄 Database may be starting up - retrying...")
                else:
                    logger.error("❌ Database is not available after all attempts")
                    self._log_troubleshooting_info()
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Unexpected connection error on attempt {attempt + 1}/{max_retries}")
                logger.error(f"🔍 Error type: {type(e).__name__}")
                logger.error(f"🔍 Error details: {str(e)}")
                if "SSL" in str(e).upper():
                    logger.error("🔐 SSL connection issue detected")
                if "timeout" in str(e).lower():
                    logger.error("⏱️ Connection timeout at network level")
                    
                if attempt < max_retries - 1:
                    logger.info("🔄 Retrying with exponential backoff...")
                else:
                    logger.error("❌ All connection attempts failed due to errors")
                    self._log_troubleshooting_info()
                    raise
            finally:
                # Clean up failed pool on errors
                if current_pool is not None:
                    try:
                        await current_pool.close()
                        logger.debug("🧹 Cleaned up failed connection pool")
                    except Exception as cleanup_error:
                        logger.debug(f"⚠️ Pool cleanup error (non-critical): {cleanup_error}")
                        pass
        
        # If we reach here, all attempts failed
        logger.error("🚨 DATABASE CONNECTION FAILED - DEPLOYMENT WILL FAIL")
        logger.error("💀 Unable to establish database connection after all retry attempts")
        raise Exception("Database connection failed after all retry attempts")
    
    def _log_troubleshooting_info(self):
        """Log comprehensive troubleshooting information"""
        # Detect deployment environment for targeted advice
        is_render = os.getenv("RENDER") == "true" or "render.com" in os.getenv("RENDER_EXTERNAL_URL", "")
        is_supabase = "supabase.com" in self.database_url
        
        logger.error("💡 Troubleshooting steps:")
        
        if is_render and is_supabase:
            logger.error("   🔍 RENDER + SUPABASE DEPLOYMENT DETECTED")
            logger.error("   1. Check Supabase dashboard - database should show 'Active' status")
            logger.error("   2. Verify DATABASE_URL in Render environment variables")
            logger.error("   3. Try manual redeploy - Supabase may need time to wake up")
            logger.error("   4. Check Render logs for network connectivity issues")
            logger.error("   5. Verify Supabase billing - paused databases can't connect")
            logger.error("   6. Check Supabase status page: https://status.supabase.com/")
        elif is_supabase:
            logger.error("   🔍 SUPABASE DATABASE DETECTED")
            logger.error("   1. Check Supabase dashboard shows database is active")
            logger.error("   2. Verify DATABASE_URL is correct in environment variables")
            logger.error("   3. Check Supabase billing status - paused projects can't connect")
            logger.error("   4. Try manual database restart in Supabase dashboard")
            logger.error("   5. Check Supabase status page for outages")
        else:
            logger.error("   1. Check your database service is running")
            logger.error("   2. Verify DATABASE_URL is correct in environment variables")
            logger.error("   3. Test database connectivity from deployment environment")
            logger.error("   4. Check firewall and network settings")
            logger.error("   5. Verify database server logs for errors")
    
    async def _fix_database_schema(self):
        """Fix all database schema issues in sequence"""
        logger.info("🔧 Fixing database schema and data issues...")
        
        try:
            # Ensure required extensions
            await self._ensure_postgresql_extensions()
            
            # Fix service configuration cache
            await self._fix_service_configuration_cache()
            
            # Ensure enhanced tables exist
            await self._ensure_enhanced_tables()
            
            # Clean up malformed data
            await self._cleanup_malformed_data()
            
            # Add performance indexes
            await self._ensure_performance_indexes()
            
            self.schema_fixed = True
            logger.info("✅ Database schema fixes completed")
            
        except Exception as e:
            logger.error(f"❌ Schema fix error: {e}")
            # Don't raise - system can work with basic schema
            self.schema_fixed = False
    
    async def _ensure_postgresql_extensions(self):
        """Ensure required PostgreSQL extensions are enabled"""
        logger.info("🔧 Ensuring required PostgreSQL extensions...")
        
        async with self.db_pool.acquire() as conn:
            # Enable pgcrypto for UUID generation
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
                logger.info("✅ pgcrypto extension enabled")
            except Exception as e:
                logger.warning(f"⚠️ Could not enable pgcrypto extension: {e}")
            
            # Enable pgvector if available (for AI embeddings)
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("✅ pgvector extension enabled")
                return True
            except Exception as e:
                logger.warning(f"⚠️ pgvector extension not available: {e}")
                return False
    
    async def _fix_service_configuration_cache(self):
        """Fix service_configuration_cache table schema"""
        logger.info("🔧 Fixing service_configuration_cache table...")
        
        async with self.db_pool.acquire() as conn:
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
                # Ensure all required columns exist
                await self._ensure_cache_table_columns(conn)
    
    async def _ensure_cache_table_columns(self, conn):
        """Ensure all required columns exist in cache table"""
        required_columns = {
            'cached_at': 'TIMESTAMP DEFAULT NOW()',
            'expires_at': 'TIMESTAMP DEFAULT (NOW() + INTERVAL \'1 hour\')'
        }
        
        for column_name, column_def in required_columns.items():
            column_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'service_configuration_cache' 
                    AND column_name = $1
                )
            """, column_name)
            
            if not column_exists:
                logger.info(f"➕ Adding {column_name} column...")
                await conn.execute(f"""
                    ALTER TABLE service_configuration_cache 
                    ADD COLUMN {column_name} {column_def}
                """)
                logger.info(f"✅ {column_name} column added")
    
    async def _ensure_enhanced_tables(self):
        """Ensure enhanced feature tables exist"""
        logger.info("📊 Ensuring enhanced feature tables...")
        
        vector_available = await self._check_vector_support()
        
        async with self.db_pool.acquire() as conn:
            # Create rag_knowledge_base table
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'rag_knowledge_base'
                )
            """)
            
            if not table_exists:
                logger.info("📦 Creating rag_knowledge_base table...")
                
                if vector_available:
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
                    logger.info("✅ rag_knowledge_base table created with vector support")
                else:
                    await conn.execute("""
                        CREATE TABLE rag_knowledge_base (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            knowledge_domain VARCHAR(100) NOT NULL,
                            content_type VARCHAR(50) NOT NULL,
                            title VARCHAR(500) NOT NULL,
                            content TEXT NOT NULL,
                            metadata JSONB DEFAULT '{}',
                            embedding_vector TEXT, -- Fallback: store as JSON string
                            tags TEXT[] DEFAULT '{}',
                            source_reference VARCHAR(500),
                            authority_level INTEGER DEFAULT 1,
                            cultural_context VARCHAR(100) DEFAULT 'universal',
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
                    logger.info("✅ rag_knowledge_base table created with fallback support")
    
    async def _check_vector_support(self):
        """Check if pgvector extension is available"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1::vector")
                return True
        except Exception:
            return False
    
    async def _cleanup_malformed_data(self):
        """Clean up any malformed JSON data"""
        logger.info("🧹 Cleaning up malformed data...")
        
        async with self.db_pool.acquire() as conn:
            try:
                # Find malformed JSON entries in service cache
                malformed_entries = await conn.fetch("""
                    SELECT service_name, configuration, persona_config 
                    FROM service_configuration_cache
                    WHERE NOT (configuration::TEXT ~ '^[[:space:]]*[{[]')
                       OR NOT (persona_config::TEXT ~ '^[[:space:]]*[{[]')
                """)
                
                for entry in malformed_entries:
                    logger.warning(f"Found malformed JSON in service: {entry['service_name']}")
                    
                    # Try to fix or remove the entry
                    config_fixed = self._fix_json_string(entry['configuration'])
                    persona_fixed = self._fix_json_string(entry['persona_config'])
                    
                    if config_fixed and persona_fixed:
                        await conn.execute("""
                            UPDATE service_configuration_cache 
                            SET configuration = $1, persona_config = $2
                            WHERE service_name = $3
                        """, config_fixed, persona_fixed, entry['service_name'])
                        logger.info(f"✅ Fixed malformed JSON for: {entry['service_name']}")
                    else:
                        await conn.execute("""
                            DELETE FROM service_configuration_cache 
                            WHERE service_name = $1
                        """, entry['service_name'])
                        logger.info(f"🗑️ Removed unfixable entry: {entry['service_name']}")
                
                # Clean up expired cache entries
                result = await conn.execute("""
                    DELETE FROM service_configuration_cache 
                    WHERE expires_at < NOW()
                """)
                
                # Safely parse DELETE result with defensive handling
                deleted_count = 0
                try:
                    if result and isinstance(result, str) and result.startswith("DELETE"):
                        parts = result.split()
                        if len(parts) >= 2 and parts[-1].isdigit():
                            deleted_count = int(parts[-1])
                except (ValueError, AttributeError, IndexError) as e:
                    logger.debug(f"Could not parse DELETE result '{result}': {e}")
                    deleted_count = 0
                
                if deleted_count > 0:
                    logger.info(f"🧹 Cleaned up {deleted_count} expired cache entries")
                
            except Exception as e:
                logger.warning(f"⚠️ Data cleanup warning: {e}")
                # Don't raise - cleanup failure shouldn't break system
    
    def _fix_json_string(self, json_str: str) -> Optional[str]:
        """Attempt to fix malformed JSON strings"""
        if not json_str:
            return None
        
        try:
            # Try parsing as-is first
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # Try common fixes
        fixes = [
            lambda s: s.replace("'", '"'),  # Single quotes to double quotes
            lambda s: '"' + s + '"' if not s.startswith('"') else s,  # Add quotes
            lambda s: '{"value": "' + s + '"}' if not s.startswith('{') else s  # Wrap in object
        ]
        
        for fix in fixes:
            try:
                fixed = fix(json_str)
                json.loads(fixed)  # Validate
                return fixed
            except (json.JSONDecodeError, Exception):
                continue
        
        return None
    
    async def _ensure_performance_indexes(self):
        """Add performance indexes for frequently queried columns"""
        logger.info("🚀 Adding performance indexes...")
        
        indexes = [
            ("idx_service_config_cached_at", "service_configuration_cache", "cached_at"),
            ("idx_service_config_expires_at", "service_configuration_cache", "expires_at"),
            ("idx_rag_knowledge_domain", "rag_knowledge_base", "knowledge_domain"),
            ("idx_rag_content_type", "rag_knowledge_base", "content_type"),
            ("idx_rag_created_at", "rag_knowledge_base", "created_at")
        ]
        
        async with self.db_pool.acquire() as conn:
            for index_name, table_name, column_name in indexes:
                try:
                    # Check if table exists first
                    table_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = $1
                        )
                    """, table_name)
                    
                    if not table_exists:
                        continue
                    
                    # Check if index exists
                    index_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes 
                            WHERE tablename = $1 AND indexname = $2
                        )
                    """, table_name, index_name)
                    
                    if not index_exists:
                        await conn.execute(f"""
                            CREATE INDEX {index_name} ON {table_name}({column_name})
                        """)
                        logger.info(f"✅ Added index: {index_name}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not create index {index_name}: {e}")
    
    async def _initialize_enhanced_features(self):
        """Initialize enhanced features in sequence"""
        logger.info("🌟 Initializing enhanced features...")
        
        try:
            # Initialize service configurations
            await self._initialize_service_configurations()
            
            # Seed knowledge base if needed
            await self._initialize_knowledge_base()
            
            # Initialize RAG system
            await self._initialize_rag_system()
            
            logger.info("✅ Enhanced features initialization completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Enhanced features initialization failed: {e}")
            logger.info("✅ System will continue in basic mode")
    
    async def _initialize_service_configurations(self):
        """Initialize default service configurations"""
        logger.info("⚙️ Initializing service configurations...")
        
        async with self.db_pool.acquire() as conn:
            # Check if configurations exist
            count = await conn.fetchval("SELECT COUNT(*) FROM service_configuration_cache")
            
            if count == 0:
                logger.info("📋 Creating default service configurations...")
                
                default_services = [
                    {
                        "service_name": "relationship_astrology_reading",
                        "configuration": {
                            "knowledge_domains": ["relationship_astrology", "compatibility_analysis", "vedic_matching"],
                            "analysis_depth": "comprehensive",
                            "persona_mode": "relationship_counselor"
                        },
                        "persona_config": {
                            "expertise_level": "relationship_master",
                            "speaking_style": "compassionate_guidance_with_astrological_insights",
                            "cultural_focus": "vedic_relationship_wisdom"
                        },
                        "knowledge_domains": "relationship_astrology,compatibility_analysis,vedic_matching"
                    },
                    {
                        "service_name": "career_success_consultation",
                        "configuration": {
                            "knowledge_domains": ["career_astrology", "world_knowledge", "psychological_integration"],
                            "analysis_depth": "comprehensive",
                            "persona_mode": "business_mentor_authority"
                        },
                        "persona_config": {
                            "expertise_level": "career_success_master",
                            "speaking_style": "confident_business_guidance_with_spiritual_wisdom",
                            "cultural_focus": "career_professional_dharma"
                        },
                        "knowledge_domains": "career_astrology,world_knowledge,psychological_integration"
                    }
                ]
                
                for service in default_services:
                    try:
                        await conn.execute("""
                            INSERT INTO service_configuration_cache (
                                service_name, configuration, persona_config, knowledge_domains, cached_at
                            ) VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                            ON CONFLICT (service_name) DO UPDATE SET
                                configuration = EXCLUDED.configuration,
                                persona_config = EXCLUDED.persona_config,
                                knowledge_domains = EXCLUDED.knowledge_domains,
                                cached_at = CURRENT_TIMESTAMP
                        """, 
                            service["service_name"],
                            json.dumps(service["configuration"]),
                            json.dumps(service["persona_config"]),
                            service["knowledge_domains"]
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Could not create service config {service['service_name']}: {e}")
                
                logger.info("✅ Service configurations initialized")
                self.service_configs_ready = True
            else:
                logger.info(f"✅ Service configurations already exist ({count} entries)")
                self.service_configs_ready = True
    
    async def _initialize_knowledge_base(self):
        """Initialize knowledge base with spiritual/astrological content"""
        logger.info("🧠 Initializing knowledge base...")
        
        async with self.db_pool.acquire() as conn:
            # Check if knowledge base has content
            count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            
            if count == 0:
                logger.info("🌱 Knowledge base empty, seeding with spiritual wisdom...")
                
                try:
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    
                    if openai_api_key and openai_api_key != "fallback_key":
                        # Use full knowledge seeding with embeddings
                        await self._seed_knowledge_with_embeddings(conn, openai_api_key)
                    else:
                        # Use basic seeding without embeddings
                        await self._seed_basic_knowledge(conn)
                    
                    self.knowledge_seeded = True
                    logger.info("✅ Knowledge base seeded successfully")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Knowledge seeding failed: {e}")
                    self.knowledge_seeded = False
            else:
                logger.info(f"✅ Knowledge base already contains {count} entries")
                self.knowledge_seeded = True
    
    async def _seed_basic_knowledge(self, conn):
        """Seed basic knowledge without embeddings"""
        basic_knowledge = [
            {
                "domain": "classical_astrology",
                "title": "Houses in Vedic Astrology",
                "content": "The 12 houses in Vedic astrology represent different life areas: 1st house (self), 2nd house (wealth), 3rd house (communication), 4th house (home), 5th house (creativity), 6th house (health), 7th house (partnerships), 8th house (transformation), 9th house (spirituality), 10th house (career), 11th house (gains), 12th house (liberation).",
                "tags": ["houses", "vedic", "basics"]
            },
            {
                "domain": "relationship_astrology", 
                "title": "Compatibility Analysis",
                "content": "In Vedic astrology, compatibility is analyzed through multiple factors: Guna Milan (36 points), Mangal Dosha, Nadi Dosha, and planetary positions. A score above 18 points is considered good for marriage compatibility.",
                "tags": ["compatibility", "marriage", "guna milan"]
            },
            {
                "domain": "remedial_measures",
                "title": "Planetary Remedies",
                "content": "Common remedies include wearing gemstones, chanting mantras, performing specific pujas, charity (daan), fasting on specific days, and visiting temples. Each planet has specific remedies for strengthening or pacifying its effects.",
                "tags": ["remedies", "gemstones", "mantras"]
            }
        ]
        
        for knowledge in basic_knowledge:
            await conn.execute("""
                INSERT INTO rag_knowledge_base (
                    knowledge_domain, content_type, title, content, tags, authority_level
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                knowledge["domain"], "foundational_knowledge", 
                knowledge["title"], knowledge["content"], 
                knowledge["tags"], 1
            )
    
    async def _seed_knowledge_with_embeddings(self, conn, openai_api_key):
        """Seed knowledge base with AI embeddings"""
        try:
            # Import the knowledge seeder
            from knowledge_seeding_system import KnowledgeSeeder
            
            # Create seeder instance using our existing pool
            seeder = KnowledgeSeeder(self.db_pool, openai_api_key)
            
            # Run seeding with timeout
            await asyncio.wait_for(
                seeder.seed_complete_knowledge_base(),
                timeout=180.0  # 3 minute timeout
            )
            
        except asyncio.TimeoutError:
            logger.warning("⚠️ Knowledge seeding timed out, using basic fallback")
            await self._seed_basic_knowledge(conn)
        except ImportError:
            logger.warning("⚠️ Knowledge seeding system not available, using basic fallback")
            await self._seed_basic_knowledge(conn)
        except Exception as e:
            logger.warning(f"⚠️ Advanced knowledge seeding failed: {e}, using basic fallback")
            await self._seed_basic_knowledge(conn)
    
    async def _initialize_rag_system(self):
        """Initialize RAG (Retrieval Augmented Generation) system"""
        logger.info("🤖 Initializing RAG system...")
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if openai_api_key and openai_api_key != "fallback_key":
            logger.info("✅ OpenAI API key found - RAG system ready for embeddings")
            self.rag_initialized = True
        else:
            logger.info("⚠️ OpenAI API key not found - RAG system in fallback mode")
            self.rag_initialized = False
    
    async def _validate_system_health(self):
        """Final validation of system health"""
        logger.info("🏥 Validating system health...")
        
        try:
            # Test database pool
            async with self.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            # Check table accessibility
            async with self.db_pool.acquire() as conn:
                tables = await conn.fetch("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('service_configuration_cache', 'rag_knowledge_base')
                """)
                table_names = [row['table_name'] for row in tables]
            
            logger.info("✅ System health check passed")
            logger.info(f"📊 Available tables: {', '.join(table_names)}")
            logger.info(f"🔧 Schema fixed: {self.schema_fixed}")
            logger.info(f"🧠 Knowledge seeded: {self.knowledge_seeded}")
            logger.info(f"🤖 RAG initialized: {self.rag_initialized}")
            logger.info(f"⚙️ Service configs ready: {self.service_configs_ready}")
            
        except Exception as e:
            logger.warning(f"⚠️ System health check warning: {e}")
            # Don't raise - system can still function
    
    async def cleanup(self):
        """Clean up resources"""
        if self.db_pool:
            logger.info("🔄 Gracefully closing database connection pool...")
            try:
                await self.db_pool.close()
                logger.info("✅ Database connection pool closed cleanly")
            except Exception as e:
                logger.warning(f"⚠️ Error during pool cleanup: {e}")
            finally:
                self.db_pool = None
    
    def get_system_status(self):
        """Get comprehensive system status"""
        return {
            "main_pool_ready": self.main_pool_ready,
            "schema_fixed": self.schema_fixed,
            "knowledge_seeded": self.knowledge_seeded,
            "rag_initialized": self.rag_initialized,
            "service_configs_ready": self.service_configs_ready,
            "database_configured": bool(self.database_url),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "system_ready": self.main_pool_ready and self.schema_fixed,
            "version": "3.0.0-unified"
        }

# Global instance for system state
_unified_startup_instance = None

async def initialize_unified_jyotiflow():
    """Main entry point for unified system initialization"""
    logger.info("🚀 Starting Unified JyotiFlow.ai Initialization...")
    start_time = time.time()
    
    global _unified_startup_instance
    _unified_startup_instance = UnifiedJyotiFlowStartup()
    logger.info("✅ Unified startup system instance created")
    
    try:
        logger.info("🔄 Beginning complete system initialization...")
        db_pool = await _unified_startup_instance.initialize_complete_system()
        
        elapsed_time = time.time() - start_time
        logger.info(f"🎉 Unified JyotiFlow.ai system fully initialized in {elapsed_time:.2f} seconds")
        logger.info("🎯 System ready to handle API requests")
        return db_pool
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ Unified system initialization failed after {elapsed_time:.2f} seconds")
        logger.error(f"🔍 Failure reason: {str(e)}")
        logger.error(f"🔍 Failure type: {type(e).__name__}")
        
        if _unified_startup_instance:
            logger.info("🧹 Cleaning up failed initialization...")
            await _unified_startup_instance.cleanup()
        raise

async def cleanup_unified_system():
    """Cleanup unified system resources"""
    global _unified_startup_instance
    if _unified_startup_instance:
        await _unified_startup_instance.cleanup()
        _unified_startup_instance = None

def get_unified_system_status():
    """Get current unified system status"""
    global _unified_startup_instance
    
    if _unified_startup_instance is None:
        return {
            "system_available": False,
            "main_pool_ready": False,
            "enhanced_features_ready": False,
            "system_ready": False,
            "version": "3.0.0-unified"
        }
    
    status = _unified_startup_instance.get_system_status()
    return {
        "system_available": True,
        "main_pool_ready": status["main_pool_ready"],
        "enhanced_features_ready": (status["knowledge_seeded"] and status["service_configs_ready"]),
        "database_configured": status["database_configured"],
        "openai_configured": status["openai_configured"],
        "system_ready": status["system_ready"],
        "version": status["version"],
        "details": status
    }