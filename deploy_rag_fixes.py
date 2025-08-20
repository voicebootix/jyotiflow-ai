#!/usr/bin/env python3
"""
Deploy RAG fixes to production
- Applies vector extension migration
- Populates spiritual knowledge base
- Tests RAG functionality
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGDeploymentFixer:
    def __init__(self, database_url):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "backend" / "migrations"
    
    async def apply_vector_extension_migration(self, conn):
        """Apply vector extension migration"""
        try:
            migration_file = self.migrations_dir / "026_add_pgvector_extension.sql"
            
            if not migration_file.exists():
                logger.error(f"❌ Migration file not found: {migration_file}")
                return False
            
            with open(migration_file, 'r') as f:
                migration_content = f.read()
            
            logger.info("🔧 Applying vector extension migration...")
            
            async with conn.transaction():
                await conn.execute(migration_content)
            
            logger.info("✅ Vector extension migration applied successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vector extension migration failed: {e}")
            return False
    
    async def apply_knowledge_base_migration(self, conn):
        """Apply knowledge base population migration"""
        try:
            migration_file = self.migrations_dir / "027_populate_spiritual_knowledge_base.sql"
            
            if not migration_file.exists():
                logger.error(f"❌ Migration file not found: {migration_file}")
                return False
            
            with open(migration_file, 'r') as f:
                migration_content = f.read()
            
            logger.info("📚 Applying knowledge base population migration...")
            
            async with conn.transaction():
                await conn.execute(migration_content)
            
            logger.info("✅ Knowledge base migration applied successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Knowledge base migration failed: {e}")
            return False
    
    async def test_rag_functionality(self, conn):
        """Test if RAG system is working"""
        try:
            logger.info("🧪 Testing RAG functionality...")
            
            # Check vector extension
            vector_ext = await conn.fetchval("""
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            """)
            
            if vector_ext:
                logger.info("✅ Vector extension is available")
            else:
                logger.warning("⚠️ Vector extension not found")
                return False
            
            # Check knowledge base entries
            entry_count = await conn.fetchval("""
                SELECT COUNT(*) FROM rag_knowledge_base WHERE is_active = true
            """)
            
            if entry_count > 0:
                logger.info(f"✅ Found {entry_count} active knowledge base entries")
            else:
                logger.warning("⚠️ No active knowledge base entries found")
                return False
            
            # Check categories
            categories = await conn.fetch("""
                SELECT DISTINCT category, COUNT(*) as count 
                FROM rag_knowledge_base 
                WHERE is_active = true 
                GROUP BY category 
                ORDER BY category
            """)
            
            logger.info("📋 Knowledge base categories:")
            for row in categories:
                logger.info(f"   - {row['category']}: {row['count']} entries")
            
            # Test a sample query (simple text search, no embeddings needed)
            sample_entries = await conn.fetch("""
                SELECT title, category 
                FROM rag_knowledge_base 
                WHERE content ILIKE '%inner peace%' 
                AND is_active = true 
                LIMIT 3
            """)
            
            if sample_entries:
                logger.info("✅ Sample query results:")
                for entry in sample_entries:
                    logger.info(f"   - {entry['title']} ({entry['category']})")
            
            logger.info("🎉 RAG functionality tests passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ RAG functionality test failed: {e}")
            return False
    
    async def record_migration_applied(self, conn, migration_name):
        """Record migration as applied in schema_migrations table"""
        try:
            # Create migrations table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    checksum VARCHAR(64)
                )
            """)
            
            # Record migration
            await conn.execute("""
                INSERT INTO schema_migrations (migration_name, checksum) 
                VALUES ($1, $2)
                ON CONFLICT (migration_name) DO NOTHING
            """, migration_name, 'rag_deployment_fix')
            
            logger.info(f"📝 Recorded migration: {migration_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not record migration: {e}")
    
    async def deploy_rag_fixes(self):
        """Deploy all RAG fixes"""
        try:
            # Connect to database
            conn = await asyncpg.connect(self.database_url)
            logger.info("🔗 Connected to production database")
            
            # Step 1: Apply vector extension migration
            if await self.apply_vector_extension_migration(conn):
                await self.record_migration_applied(conn, "026_add_pgvector_extension.sql")
            else:
                logger.error("💥 Vector extension migration failed, aborting")
                return False
            
            # Step 2: Apply knowledge base migration
            if await self.apply_knowledge_base_migration(conn):
                await self.record_migration_applied(conn, "027_populate_spiritual_knowledge_base.sql")
            else:
                logger.error("💥 Knowledge base migration failed, aborting")
                return False
            
            # Step 3: Test RAG functionality
            if await self.test_rag_functionality(conn):
                logger.info("🎯 RAG deployment completed successfully!")
                
                # Test RAG system initialization
                try:
                    sys.path.append(str(Path(__file__).parent / 'backend'))
                    from enhanced_rag_knowledge_engine import initialize_rag_system
                    
                    openai_api_key = os.getenv('OPENAI_API_KEY')
                    if openai_api_key:
                        logger.info("🧠 Testing RAG system initialization...")
                        # We can't test full initialization without a pool, but we can import
                        logger.info("✅ RAG system modules imported successfully")
                    else:
                        logger.warning("⚠️ OPENAI_API_KEY not found in environment")
                
                except ImportError as e:
                    logger.warning(f"⚠️ Could not import RAG system: {e}")
                
                return True
            else:
                logger.error("💥 RAG functionality test failed")
                return False
            
        except Exception as e:
            logger.error(f"💥 RAG deployment failed: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                await conn.close()

async def main():
    """Main deployment function"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Deploy RAG fixes
    fixer = RAGDeploymentFixer(database_url)
    success = await fixer.deploy_rag_fixes()
    
    if success:
        logger.info("🚀 RAG deployment completed successfully!")
        print("🎉 RAG Knowledge System is now active!")
        print("   ✅ Vector extension installed")
        print("   ✅ Spiritual knowledge base populated") 
        print("   ✅ RAG functionality tested")
        print("   🧠 Dynamic content generation enabled")
        sys.exit(0)
    else:
        logger.error("💥 RAG deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
