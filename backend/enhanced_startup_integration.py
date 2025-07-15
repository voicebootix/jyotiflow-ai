"""
Enhanced JyotiFlow Startup Integration with Robust Database Connection Management
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
import traceback

# Enhanced imports for robust database handling
try:
    import asyncpg
    from asyncpg.pool import Pool
    ASYNCPG_AVAILABLE = True
except ImportError:
    asyncpg = None
    Pool = None
    ASYNCPG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedJyotiFlowStartup:
    """Handles startup integration for enhanced features with robust connection management"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            logger.error("❌ DATABASE_URL environment variable is required but not set")
            raise ValueError("DATABASE_URL environment variable must be provided")
        self.knowledge_seeded = False
        self.rag_initialized = False
        
        # Enhanced connection settings - optimized for Render environment
        self.connection_config = {
            'min_size': 2,
            'max_size': 10,
            'command_timeout': 60,
            'server_settings': {
                'application_name': 'jyotiflow_startup_integration',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '60',
                'tcp_keepalives_count': '5'
            }
        }
        
    async def _create_robust_connection(self, max_retries: int = 5):
        """Create a robust database connection with progressive backoff"""
        if not ASYNCPG_AVAILABLE or not asyncpg:
            raise Exception("asyncpg is not available")
            
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
        if not ASYNCPG_AVAILABLE or not asyncpg:
            raise Exception("asyncpg is not available")
            
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

    async def initialize_enhanced_system(self):
        """Initialize all enhanced system components with graceful fallback"""
        logger.info("🚀 Initializing JyotiFlow Enhanced System...")
        
        initialization_steps = [
            ("Database Tables", self._ensure_database_tables),
            ("Knowledge Base", self._ensure_knowledge_base),
            ("RAG System", self._initialize_rag_system),
            ("Service Configurations", self._ensure_service_configurations)
        ]
        
        successful_steps = 0
        total_steps = len(initialization_steps)
        
        for step_name, step_func in initialization_steps:
            try:
                logger.info(f"📋 Initializing {step_name}...")
                await step_func()
                successful_steps += 1
                logger.info(f"✅ {step_name} initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ {step_name} initialization failed: {e}")
                logger.debug(f"Full traceback for {step_name}: {traceback.format_exc()}")
                # Continue with next step - don't let one failure stop the entire process
                continue
        
        if successful_steps == total_steps:
            logger.info("✅ Enhanced system initialization completed successfully!")
        elif successful_steps > 0:
            logger.info(f"⚠️ Enhanced system partially initialized ({successful_steps}/{total_steps} steps successful)")
        else:
            logger.warning("❌ Enhanced system initialization failed - running in fallback mode")
        
        # Always return success - system can run in fallback mode
        return successful_steps > 0
    
    async def _ensure_database_tables(self):
        """Ensure all required database tables exist"""
        if not ASYNCPG_AVAILABLE or not asyncpg:
            logger.warning("⚠️ asyncpg not available, skipping database table creation")
            return
            
        conn = None
        try:
            conn = await self._create_robust_connection()
            
            # Check if enhanced tables exist
            enhanced_tables = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('rag_knowledge_base', 'service_configuration_cache')
            """)
            
            if enhanced_tables >= 2:
                logger.info("✅ Enhanced database tables already exist")
            else:
                logger.info("📊 Creating enhanced database tables...")
                
                # Create rag_knowledge_base table if it doesn't exist
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS rag_knowledge_base (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        knowledge_domain VARCHAR(100) NOT NULL,
                        content_type VARCHAR(50) NOT NULL DEFAULT 'knowledge',
                        title VARCHAR(500) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        embedding_vector TEXT,
                        tags TEXT[] DEFAULT '{}',
                        source_reference VARCHAR(500),
                        authority_level INTEGER DEFAULT 1,
                        cultural_context VARCHAR(100) DEFAULT 'universal',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                logger.info("✅ rag_knowledge_base table created")
                
                # Create service_configuration_cache table if it doesn't exist
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS service_configuration_cache (
                        service_name VARCHAR(100) PRIMARY KEY,
                        configuration JSONB NOT NULL,
                        persona_config JSONB NOT NULL,
                        knowledge_domains TEXT NOT NULL,
                        cached_at TIMESTAMP DEFAULT NOW(),
                        expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
                    )
                """)
                logger.info("✅ service_configuration_cache table created")
                
                logger.info("✅ Enhanced database tables created successfully")
                
        except Exception as e:
            logger.error(f"Database table creation error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Don't raise - system should try to continue
        finally:
            if conn:
                await conn.close()

    async def _ensure_knowledge_base(self):
        """Ensure knowledge base is populated with robust connection handling"""
        conn = None
        try:
            conn = await self._create_robust_connection()
            
            # Check knowledge count
            count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            
            if count == 0:
                logger.info("🧠 Knowledge base empty, seeding with spiritual wisdom...")
                
                # Import and run PostgreSQL knowledge seeding
                try:
                    from knowledge_seeding_system import KnowledgeSeeder
                    import os
                    
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    db_pool = None
                    
                    if not openai_api_key or openai_api_key == "fallback_key":
                        logger.info("⚠️ OpenAI API key not available - using basic seeding without embeddings")
                        # Create a basic seeder without OpenAI
                        seeder = KnowledgeSeeder(None, "fallback_key")
                    else:
                        # Create database pool for seeder with robust settings
                        db_pool = await self._create_robust_pool()
                        seeder = KnowledgeSeeder(db_pool, openai_api_key)
                    
                    try:
                        # Run the seeding process with timeout
                        await asyncio.wait_for(
                            seeder.seed_complete_knowledge_base(),
                            timeout=120.0  # 2 minute timeout for seeding
                        )
                        logger.info("✅ Knowledge base seeded successfully with spiritual wisdom")
                        self.knowledge_seeded = True
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Knowledge seeding timed out, system will run in fallback mode")
                        self.knowledge_seeded = False
                    finally:
                        # Always close the pool if it was created
                        if db_pool:
                            await db_pool.close()
                    
                except Exception as seeding_error:
                    logger.error(f"Knowledge seeding error: {seeding_error}")
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    logger.info("✅ System will work without knowledge base in fallback mode")
                    self.knowledge_seeded = False
            else:
                logger.info(f"✅ Knowledge base already contains {count} pieces")
                self.knowledge_seeded = True
            
        except Exception as e:
            logger.error(f"Knowledge base seeding error: {e}")
            # Don't raise - system can work without knowledge base
            self.knowledge_seeded = False
        finally:
            if conn:
                await conn.close()

    async def _initialize_rag_system(self):
        """Initialize RAG system with OpenAI if available"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if openai_api_key and openai_api_key != "fallback_key":
                logger.info("✅ OpenAI API key found - RAG system can use real embeddings")
                self.rag_initialized = True
            else:
                logger.info("⚠️ OpenAI API key not found - RAG system will use fallback mode")
                self.rag_initialized = False
                
            logger.info("✅ RAG system initialized")
            
        except Exception as e:
            logger.error(f"RAG initialization error: {e}")
            self.rag_initialized = False

    async def _ensure_service_configurations(self):
        """Ensure default service configurations exist with robust JSON handling"""
        conn = None
        try:
            conn = await self._create_robust_connection()
            
            # First, ensure the table schema is correct
            await self._fix_service_configuration_cache_schema(conn)
            
            # Clean up any malformed JSON data first
            await self._cleanup_malformed_json_data(conn)
            
            # Define default service configurations
            default_services = [
                {
                    "service_name": "love_relationship_mastery",
                    "configuration": {
                        "knowledge_domains": ["relationship_astrology", "remedial_measures", "tamil_spiritual_literature"],
                        "analysis_depth": "comprehensive",
                        "persona_mode": "relationship_counselor_authority"
                    },
                    "persona_config": {
                        "expertise_level": "master_relationship_guide",
                        "speaking_style": "warm_understanding_with_relationship_wisdom",
                        "cultural_focus": "love_marriage_family_dynamics"
                    },
                    "knowledge_domains": "relationship_astrology,remedial_measures,tamil_spiritual_literature"
                },
                {
                    "service_name": "business_success_mastery", 
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
                },
                {
                    "service_name": "comprehensive_life_reading_30min",
                    "configuration": {
                        "knowledge_domains": ["classical_astrology", "tamil_spiritual_literature", "health_astrology", "career_astrology", "relationship_astrology", "remedial_measures"],
                        "analysis_depth": "comprehensive_30_minute",
                        "persona_mode": "comprehensive_life_master"
                    },
                    "persona_config": {
                        "expertise_level": "complete_life_analysis_authority",
                        "speaking_style": "profound_wisdom_with_comprehensive_understanding",
                        "cultural_focus": "complete_life_transformation"
                    },
                    "knowledge_domains": "classical_astrology,tamil_spiritual_literature,health_astrology,career_astrology,relationship_astrology,remedial_measures"
                }
            ]
            
            # Insert default configurations with proper JSON serialization
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
                        json.dumps(service["configuration"]),  # Proper JSON serialization
                        json.dumps(service["persona_config"]),
                        service["knowledge_domains"]
                    )
                except Exception as service_error:
                    logger.error(f"Error inserting service {service['service_name']}: {service_error}")
                    continue
            
            logger.info(f"✅ Service configurations created for {len(default_services)} services")
            
        except Exception as e:
            logger.error(f"Service configuration error: {e}")
            # Don't raise - system can work without configurations
            pass
        finally:
            if conn:
                await conn.close()
    
    async def _cleanup_malformed_json_data(self, conn):
        """Clean up any malformed JSON data in service configurations"""
        try:
            # Find and fix any malformed JSON entries
            malformed_entries = await conn.fetch("""
                SELECT service_name, configuration, persona_config 
                FROM service_configuration_cache
                WHERE NOT (configuration::TEXT ~ '^[[:space:]]*[{[]')
                   OR NOT (persona_config::TEXT ~ '^[[:space:]]*[{[]')
            """)
            
            for entry in malformed_entries:
                logger.warning(f"Found malformed JSON in service: {entry['service_name']}")
                
                # Try to fix the configuration
                config_fixed = self._fix_json_string(entry['configuration'])
                persona_fixed = self._fix_json_string(entry['persona_config'])
                
                if config_fixed and persona_fixed:
                    await conn.execute("""
                        UPDATE service_configuration_cache 
                        SET configuration = $1, persona_config = $2
                        WHERE service_name = $3
                    """, config_fixed, persona_fixed, entry['service_name'])
                    logger.info(f"✅ Fixed malformed JSON for service: {entry['service_name']}")
                else:
                    # If we can't fix it, delete the entry
                    await conn.execute("""
                        DELETE FROM service_configuration_cache 
                        WHERE service_name = $1
                    """, entry['service_name'])
                    logger.info(f"🗑️ Removed unfixable malformed entry: {entry['service_name']}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up malformed JSON: {e}")
            # Don't raise - continue with normal operation
    
    def _fix_json_string(self, json_str: str) -> Optional[str]:
        """Attempt to fix malformed JSON strings"""
        if not json_str:
            return None
            
        try:
            # If it's already valid JSON, return it
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # Try to fix common JSON issues
        try:
            # If it's a plain string that should be an object
            if not json_str.strip().startswith(('{', '[')):
                return json.dumps({"value": json_str})
            
            # Try to fix unquoted keys
            import re
            fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
            json.loads(fixed)
            return fixed
            
        except (json.JSONDecodeError, Exception):
            pass
        
        return None

    async def _fix_service_configuration_cache_schema(self, conn):
        """Fix service_configuration_cache table schema issues"""
        try:
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
                
        except Exception as e:
            logger.error(f"Schema fix error: {e}")
            # Don't raise - continue with existing schema
            pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "knowledge_seeded": self.knowledge_seeded,
            "rag_initialized": self.rag_initialized,
            "database_configured": bool(self.database_url),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
        }

# Global instance for maintaining system state
_enhanced_startup_instance = None

async def initialize_enhanced_jyotiflow():
    """Initialize the enhanced JyotiFlow system"""
    global _enhanced_startup_instance
    _enhanced_startup_instance = EnhancedJyotiFlowStartup()
    success = await _enhanced_startup_instance.initialize_enhanced_system()
    return success

def get_enhancement_status():
    """Get current enhancement status with real-time system information"""
    global _enhanced_startup_instance
    
    if _enhanced_startup_instance is None:
        return {
            "enhanced_system_available": False,
            "knowledge_base_seeded": False,
            "rag_system_initialized": False,
            "database_configured": False,
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "system_ready": False,
            "version": "2.0.0-robust"
        }
    
    # Return dynamic system status matching the original API contract
    base_status = _enhanced_startup_instance.get_system_status()
    return {
        "enhanced_system_available": True,
        "knowledge_base_seeded": base_status.get("knowledge_seeded", False),
        "rag_system_initialized": base_status.get("rag_initialized", False),
        "database_configured": base_status.get("database_configured", False),
        "openai_configured": base_status.get("openai_configured", False),
        "system_ready": (base_status.get("knowledge_seeded", False) and base_status.get("rag_initialized", False)),
        "version": "2.0.0-robust"
    }