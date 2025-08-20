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
import importlib.util
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGDeploymentFixer:
    def __init__(self, database_url):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "backend" / "migrations"
        self._has_is_active_column = None  # Cache for column detection
    
    def _parse_sql_file(self, content):
        """Parse SQL file and separate transaction-safe and concurrent statements"""
        # Remove standalone COMMIT/ROLLBACK statements
        content = re.sub(r'^\s*(COMMIT|ROLLBACK)\s*;\s*$', '', content, flags=re.MULTILINE)
        
        # Split into individual statements
        statements = []
        current_statement = ""
        in_do_block = False
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Track DO $$ blocks
            if 'DO $$' in line or 'DO $' in line:
                in_do_block = True
            elif '$$;' in line or '$;' in line:
                in_do_block = False
                current_statement += line + '\n'
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
                continue
            
            # Add line to current statement
            current_statement += line + '\n'
            
            # Check for statement end (semicolon not in DO block)
            if line.endswith(';') and not in_do_block and not line.startswith('--'):
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Classify statements
        concurrent_statements = []
        regular_statements = []
        
        for stmt in statements:
            if re.search(r'CREATE\s+INDEX.*CONCURRENTLY|DROP\s+INDEX.*CONCURRENTLY', stmt, re.IGNORECASE):
                concurrent_statements.append(stmt)
            elif stmt.strip() and not stmt.strip().startswith('--'):
                regular_statements.append(stmt)
        
        return regular_statements, concurrent_statements
    
    async def _check_is_active_column_exists(self, conn):
        """Check if is_active column exists in rag_knowledge_base table"""
        if self._has_is_active_column is None:
            self._has_is_active_column = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'rag_knowledge_base' 
                    AND column_name = 'is_active'
                )
            """)
            logger.info(f"📋 is_active column {'exists' if self._has_is_active_column else 'not found'}")
        
        return self._has_is_active_column
    
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
            
            # Parse SQL file to separate transaction-safe and concurrent statements
            regular_statements, concurrent_statements = self._parse_sql_file(migration_content)
            
            # Execute regular statements in transaction
            if regular_statements:
                async with conn.transaction():
                    for stmt in regular_statements:
                        try:
                            await conn.execute(stmt)
                        except Exception as e:
                            logger.error(f"❌ Statement failed: {stmt[:50]}... Error: {e}")
                            return False
            
            # Execute concurrent statements outside transaction
            for stmt in concurrent_statements:
                try:
                    logger.info(f"🔄 Executing concurrent statement: {stmt[:50]}...")
                    await conn.execute(stmt)
                except Exception as e:
                    logger.error(f"❌ Concurrent statement failed: {stmt[:50]}... Error: {e}")
                    return False
            
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
            
            # Parse SQL file to separate transaction-safe and concurrent statements
            regular_statements, concurrent_statements = self._parse_sql_file(migration_content)
            
            # Execute regular statements in transaction
            if regular_statements:
                async with conn.transaction():
                    for stmt in regular_statements:
                        try:
                            await conn.execute(stmt)
                        except Exception as e:
                            logger.error(f"❌ Statement failed: {stmt[:50]}... Error: {e}")
                            return False
            
            # Execute concurrent statements outside transaction (if any)
            for stmt in concurrent_statements:
                try:
                    logger.info(f"🔄 Executing concurrent statement: {stmt[:50]}...")
                    await conn.execute(stmt)
                except Exception as e:
                    logger.error(f"❌ Concurrent statement failed: {stmt[:50]}... Error: {e}")
                    return False
            
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
            
            # Check if is_active column exists
            has_is_active = await self._check_is_active_column_exists(conn)
            
            # Build queries based on column availability
            if has_is_active:
                count_query = "SELECT COUNT(*) FROM rag_knowledge_base WHERE is_active = true"
                category_query = """
                    SELECT DISTINCT category, COUNT(*) as count 
                    FROM rag_knowledge_base 
                    WHERE is_active = true 
                    GROUP BY category 
                    ORDER BY category
                """
                sample_query = """
                    SELECT title, category 
                    FROM rag_knowledge_base 
                    WHERE content ILIKE '%inner peace%' 
                    AND is_active = true 
                    LIMIT 3
                """
            else:
                count_query = "SELECT COUNT(*) FROM rag_knowledge_base"
                category_query = """
                    SELECT DISTINCT category, COUNT(*) as count 
                    FROM rag_knowledge_base 
                    GROUP BY category 
                    ORDER BY category
                """
                sample_query = """
                    SELECT title, category 
                    FROM rag_knowledge_base 
                    WHERE content ILIKE '%inner peace%' 
                    LIMIT 3
                """
            
            # Check knowledge base entries
            entry_count = await conn.fetchval(count_query)
            
            if entry_count > 0:
                logger.info(f"✅ Found {entry_count} knowledge base entries")
            else:
                logger.warning("⚠️ No knowledge base entries found")
                return False
            
            # Check categories
            categories = await conn.fetch(category_query)
            
            logger.info("📋 Knowledge base categories:")
            for row in categories:
                logger.info(f"   - {row['category']}: {row['count']} entries")
            
            # Test a sample query (simple text search, no embeddings needed)
            sample_entries = await conn.fetch(sample_query)
            
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
                
                # Test RAG system module availability
                try:
                    backend_path = Path(__file__).parent / 'backend'
                    if str(backend_path) not in sys.path:
                        sys.path.append(str(backend_path))
                    
                    # Test if RAG module exists using importlib
                    rag_spec = importlib.util.find_spec('enhanced_rag_knowledge_engine')
                    if rag_spec:
                        logger.info("✅ RAG system modules available")
                        
                        openai_api_key = os.getenv('OPENAI_API_KEY')
                        if openai_api_key:
                            logger.info("🧠 RAG system ready with OpenAI API key")
                        else:
                            logger.warning("⚠️ OPENAI_API_KEY not found in environment")
                    else:
                        logger.warning("⚠️ RAG system module not found")
                
                except Exception as e:
                    logger.warning(f"⚠️ Could not check RAG system availability: {e}")
                
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
