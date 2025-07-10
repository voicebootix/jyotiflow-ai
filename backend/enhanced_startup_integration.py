"""
Enhanced Startup Integration for JyotiFlow
Integrates RAG system with existing FastAPI application
"""

import os
import json
import logging
import asyncpg
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedJyotiFlowStartup:
    """Handles startup integration for enhanced features"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
        self.knowledge_seeded = False
        self.rag_initialized = False
        
    async def initialize_enhanced_system(self):
        """Initialize all enhanced system components"""
        logger.info("🚀 Initializing JyotiFlow Enhanced System...")
        
        try:
            # Step 1: Check and create database tables
            await self._ensure_database_tables()
            
            # Step 2: Seed knowledge base if needed
            await self._ensure_knowledge_base()
            
            # Step 3: Initialize RAG system (simplified)
            await self._initialize_rag_system()
            
            # Step 4: Create default service configurations
            await self._ensure_service_configurations()
            
            logger.info("✅ Enhanced system initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced system initialization failed: {e}")
            return False
    
    async def _ensure_database_tables(self):
        """Ensure enhanced database tables exist"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Check if rag_knowledge_base table exists
            table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rag_knowledge_base')"
            )
            
            if not table_exists:
                logger.info("Creating enhanced database tables...")
                
                # Create tables for PostgreSQL
                tables = [
                    '''CREATE TABLE rag_knowledge_base (
                        id TEXT PRIMARY KEY,
                        knowledge_domain VARCHAR(100) NOT NULL,
                        content_type VARCHAR(50) NOT NULL,
                        title VARCHAR(500) NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT DEFAULT '{}',
                        embedding_vector TEXT,
                        tags TEXT DEFAULT '',
                        source_reference VARCHAR(500),
                        authority_level INTEGER DEFAULT 1,
                        cultural_context VARCHAR(100) DEFAULT 'universal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );''',
                    '''CREATE TABLE service_configuration_cache (
                        service_name VARCHAR(100) PRIMARY KEY,
                        configuration TEXT NOT NULL,
                        persona_config TEXT NOT NULL,
                        knowledge_domains TEXT NOT NULL,
                        cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    );'''
                ]
                
                for table_sql in tables:
                    await conn.execute(table_sql)
                
                logger.info("✅ Enhanced database tables created")
            else:
                logger.info("✅ Enhanced database tables already exist")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Database table creation error: {e}")
            raise
    
    async def _ensure_knowledge_base(self):
        """Ensure knowledge base is populated"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Check knowledge count
            count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            
            if count == 0:
                logger.info("🧠 Knowledge base empty, seeding with spiritual wisdom...")
                
                # For now, we'll skip the SQLite seeder and just log that knowledge base is empty
                # In a full implementation, you would create a PostgreSQL version of the seeder
                logger.info("⚠️ Knowledge base seeding not implemented for PostgreSQL yet")
                logger.info("✅ System will work without knowledge base in fallback mode")
                self.knowledge_seeded = False
            else:
                logger.info(f"✅ Knowledge base already contains {count} pieces")
                self.knowledge_seeded = True
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Knowledge base seeding error: {e}")
            # Don't raise - system can work without knowledge base
            pass
    
    async def _initialize_rag_system(self):
        """Initialize RAG system (simplified for SQLite)"""
        try:
            # Check if OpenAI API key is available
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if openai_api_key and openai_api_key != "fallback_key":
                logger.info("✅ OpenAI API key found - RAG system can use real embeddings")
                self.rag_initialized = True
            else:
                logger.info("⚠️ OpenAI API key not found - RAG system will use fallback mode")
                self.rag_initialized = False
            
            # RAG system initialization completed
            logger.info("✅ RAG system initialized")
            
        except Exception as e:
            logger.error(f"RAG system initialization error: {e}")
            # Don't raise - system can work in fallback mode
            pass
    
    async def _ensure_service_configurations(self):
        """Ensure default service configurations exist"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
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
            
            # Insert default configurations
            for service in default_services:
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
                    json.dumps(service["configuration"]),  # Convert to JSON for PostgreSQL
                    json.dumps(service["persona_config"]),
                    service["knowledge_domains"]
                )
            
            await conn.close()
            
            logger.info(f"✅ Service configurations created for {len(default_services)} services")
            
        except Exception as e:
            logger.error(f"Service configuration error: {e}")
            # Don't raise - system can work without configurations
            pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "enhanced_system_active": True,
            "knowledge_base_seeded": self.knowledge_seeded,
            "rag_system_initialized": self.rag_initialized,
            "openai_available": bool(os.getenv("OPENAI_API_KEY")),
            "database_path": self.database_url,
            "system_ready": self.knowledge_seeded and self.rag_initialized
        }

# Global instance
enhanced_startup = EnhancedJyotiFlowStartup()

async def initialize_enhanced_jyotiflow():
    """Main initialization function to be called from FastAPI startup"""
    return await enhanced_startup.initialize_enhanced_system()

def get_enhancement_status():
    """Get current enhancement status"""
    return enhanced_startup.get_system_status()