#!/usr/bin/env python3
"""
Auto-Deployment Migration Script for JyotiFlow
Ensures all migrations run properly during deployment
Includes Prokerala Smart Pricing System setup
"""

import os
import sys
import asyncio
import asyncpg
import logging
from pathlib import Path

# Add backend directory to Python path for robust imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Try robust import for knowledge seeding
try:
    from knowledge_seeding_system import run_knowledge_seeding
except ImportError as e:
    logging.warning(f"⚠️ Could not import run_knowledge_seeding: {e}. Seeding will be skipped.")
    run_knowledge_seeding = None


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_sql_statements(migration_sql: str) -> list:
    """
    Parse SQL migration file into individual statements, handling:
    - String literals with escaped quotes
    - SQL comments (single-line -- and multi-line /* */)
    - Semicolons within strings and comments
    
    Args:
        migration_sql: Raw SQL content from migration file
        
    Returns:
        List of parsed SQL statements
    """
    statements = []
    current_statement = ""
    in_string = False
    string_char = None
    in_comment = False
    i = 0
    
    while i < len(migration_sql):
        char = migration_sql[i]
        
        # Handle single-line comments (-- comment)
        if not in_string and not in_comment and char == '-' and i + 1 < len(migration_sql) and migration_sql[i + 1] == '-':
            in_comment = True
            current_statement += char
            i += 1
            continue
        
        # Handle multi-line comments (/* comment */)
        if not in_string and not in_comment and char == '/' and i + 1 < len(migration_sql) and migration_sql[i + 1] == '*':
            in_comment = True
            current_statement += char
            i += 1
            continue
            
        # End of single-line comment
        if in_comment and char == '\n':
            in_comment = False
            current_statement += char
            i += 1
            continue
            
        # End of multi-line comment
        if in_comment and char == '*' and i + 1 < len(migration_sql) and migration_sql[i + 1] == '/':
            in_comment = False
            current_statement += char
            i += 1
            current_statement += migration_sql[i]
            i += 1
            continue
        
        # Skip processing if we're in a comment
        if in_comment:
            current_statement += char
            i += 1
            continue
        
        # Handle string literals
        if char in ("'", '"') and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            # Handle escaped quotes properly
            next_char = migration_sql[i + 1] if i + 1 < len(migration_sql) else None
            
            # SQL standard: doubled quotes ('') escape the quote
            if next_char == string_char:
                # Doubled quote - skip both characters and stay in string
                current_statement += char
                i += 1
                current_statement += migration_sql[i]
                i += 1
                continue
            
            # Backslash escapes: count consecutive backslashes
            backslash_count = 0
            check_pos = i - 1
            while check_pos >= 0 and migration_sql[check_pos] == '\\':
                backslash_count += 1
                check_pos -= 1
            
            # If odd number of backslashes, quote is escaped
            if backslash_count % 2 == 1:
                pass  # Escaped quote, stay in string
            else:
                # Not escaped, end of string
                in_string = False
                string_char = None
        elif char == ';' and not in_string:
            # End of statement
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
            i += 1
            continue
        
        current_statement += char
        i += 1
    
    # Add the last statement if it exists
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    return statements

async def run_auto_deployment_migrations():
    """Run all necessary migrations for deployment"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
    
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("📡 Database connection established")
        
        # Validate database connection and permissions
        try:
            # Test basic query execution
            result = await conn.fetchval("SELECT 1")
            if result != 1:
                raise RuntimeError("Database connection test failed")
            
            # Check if we can create tables (required for migrations)
            await conn.execute("SELECT current_user, session_user")
            
            # Test write permissions by attempting to create a temp table
            await conn.execute("""
                CREATE TEMP TABLE __migration_test__ (id INT);
                DROP TABLE __migration_test__;
            """)
            
            logger.info("✅ Database connection validated with required permissions")
            
        except Exception as e:
            logger.error(f"❌ Database validation failed: {e}")
            logger.error("💡 Please ensure the database user has CREATE, INSERT, UPDATE permissions")
            raise RuntimeError(f"Database validation failed: {e}") from e
        
        logger.info("🚀 Starting auto-deployment migrations...")
        
        # 1. Ensure migrations tracking table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                checksum VARCHAR(64)
            )
        """)
        logger.info("✅ Migrations tracking table ready")
        
        # 2. Get list of applied migrations
        applied_migrations = await conn.fetch("SELECT migration_name FROM schema_migrations")
        applied_set = {row['migration_name'] for row in applied_migrations}
        
        # 3. Critical migrations to ensure
        critical_migrations = [
            "025_create_rag_knowledge_base.sql", # <-- MUST RUN FIRST
            "add_prokerala_smart_pricing.sql",
            "enhance_service_types_rag.sql",
            "026_add_source_reference_column.sql",
            "026_add_pgvector_extension.sql",
            "027_populate_spiritual_knowledge_base.sql",
            "028_fix_sessions_table.sql"
        ]
        
        migrations_dir = Path(__file__).parent / "migrations"
        
        for migration_name in critical_migrations:
            if migration_name not in applied_set:
                migration_file = migrations_dir / migration_name
                
                if migration_file.exists():
                    logger.info(f"📦 Applying migration: {migration_name}")
                    
                    try:
                        with open(migration_file, 'r') as f:
                            migration_sql = f.read()
                        
                        # Parse SQL statements using extracted function
                        statements = parse_sql_statements(migration_sql)
                        
                        # Execute all statements within a transaction for atomicity
                        # This ensures either ALL statements succeed or ALL get rolled back
                        # preventing partial migration states that could corrupt the database
                        async with conn.transaction():
                            for i, statement in enumerate(statements):
                                try:
                                    await conn.execute(statement)
                                    logger.info(f"  ✅ Statement {i+1}/{len(statements)} executed")
                                except Exception as e:
                                    error_msg = str(e).lower()
                                    # Check if it's a critical error that should stop migration
                                    if any(critical in error_msg for critical in ['syntax error', 'permission denied', 'access denied', 'connection', 'authentication']):
                                        logger.error(f"  ❌ Critical error in statement {i+1}: {str(e)[:100]}")
                                        logger.error(f"  🔄 Rolling back migration {migration_name}")
                                        raise e
                                    else:
                                        # Non-critical errors (IF NOT EXISTS, etc.)
                                        logger.warning(f"  ⚠️ Statement {i+1} warning: {str(e)[:100]}")
                            
                            # Mark as applied within the same transaction
                            await conn.execute("""
                                INSERT INTO schema_migrations (migration_name) 
                                VALUES ($1) ON CONFLICT (migration_name) DO NOTHING
                            """, migration_name)
                            
                            logger.info(f"  💾 Transaction committed for {migration_name}")
                        
                        logger.info(f"✅ Migration {migration_name} completed")
                        
                    except Exception as e:
                        logger.error(f"❌ Migration {migration_name} failed: {e}")
                        
                        # For critical migrations, stop deployment immediately
                        if migration_name in critical_migrations:
                            logger.error(f"🛑 Critical migration {migration_name} failed - stopping deployment")
                            logger.error(f"💡 Please fix the migration error before retrying deployment")
                            raise RuntimeError(f"Critical migration failed: {migration_name} - {e}") from e
                        else:
                            # For non-critical migrations, log warning and continue
                            logger.warning(f"⚠️ Non-critical migration {migration_name} failed - continuing deployment")
                            continue
                else:
                    logger.warning(f"⚠️ Migration file not found: {migration_name}")
            else:
                logger.info(f"⏭️ Migration {migration_name} already applied")
        
        # 4. Ensure basic service types exist
        await ensure_basic_service_types(conn)
        
        # 5. Ensure Prokerala configuration exists
        await ensure_prokerala_config(conn)
        
        # 6. CRITICAL & IDEMPOTENT: Seed the knowledge base from Python script
        if run_knowledge_seeding:
            await run_idempotent_knowledge_seeding(conn)
        else:
            logger.error("❌ Cannot run knowledge seeding because the function was not imported.")

        logger.info("🎉 Auto-deployment migrations completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Auto-deployment migration failed: {e}")
        return False
    finally:
        # Seeding must run regardless of prior migration failures,
        # as the table might exist from a partial run.
        logger.info("Finalizing deployment: ensuring knowledge seeding is attempted.")
        if conn:
            try:
                # We check for the function's existence here, right before using it.
                if run_knowledge_seeding:
                    await run_idempotent_knowledge_seeding(conn)
                else:
                    logger.error("❌ Knowledge seeding function not available, cannot seed.")
            except Exception as seed_error:
                logger.error(f"❌ Knowledge seeding in finally block failed: {seed_error}")

        if conn:
            await conn.close()

async def run_idempotent_knowledge_seeding(conn):
    """
    Run knowledge seeding if it hasn't been done before.
    This is idempotent and uses its own robust database pool.
    """
    seeding_marker = "rag_knowledge_seeded_python_v2"
    
    already_seeded = await conn.fetchval("""
        SELECT EXISTS (
            SELECT 1 FROM schema_migrations WHERE migration_name = $1
        )
    """, seeding_marker)
    
    if already_seeded:
        logger.info(f"⏭️ RAG knowledge base seeding is already done (marker found: {seeding_marker}). Skipping.")
        return

    logger.info("🧠 Seeding RAG knowledge base from Python source...")
    pool = None
    try:
        # Create a dedicated pool for the seeder to ensure it has a connection
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            logger.error("❌ Cannot seed knowledge base: DATABASE_URL is not set.")
            return
        
        pool = await asyncpg.create_pool(DATABASE_URL)
        
        # Call the seeder with the dedicated pool (Dependency Injection)
        await run_knowledge_seeding(db_pool_override=pool)
        
        # Mark as completed in the migrations table
        await conn.execute("""
            INSERT INTO schema_migrations (migration_name) VALUES ($1)
            ON CONFLICT (migration_name) DO NOTHING
        """, seeding_marker)
        
        logger.info(f"✅ RAG knowledge base seeding completed. Marker '{seeding_marker}' set.")

    except Exception as e:
        logger.error(f"❌ RAG knowledge base seeding from Python script failed: {e}")
        raise RuntimeError(f"Failed to seed RAG knowledge base: {e}") from e
    finally:
        # Ensure the dedicated pool is closed
        if pool:
            await pool.close()
            logger.info("Dedicated seeding database pool closed.")

async def ensure_basic_service_types(conn):
    """Ensure basic service types exist"""
    try:
        # Check if service_types table has data
        count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
        
        if count == 0:
            logger.info("📋 Creating basic service types...")
            
            # Create basic service types
            basic_services = [
                {
                    'name': 'spiritual_guidance_session',
                    'display_name': 'Spiritual Guidance Session',
                    'description': 'Personal spiritual guidance with astrological insights',
                    'credits_required': 5,
                    'duration_minutes': 15
                },
                {
                    'name': 'birth_chart_analysis',
                    'display_name': 'Birth Chart Analysis',
                    'description': 'Comprehensive birth chart reading',
                    'credits_required': 8,
                    'duration_minutes': 20
                },
                {
                    'name': 'love_compatibility_reading',
                    'display_name': 'Love Compatibility Reading',
                    'description': 'Relationship compatibility analysis',
                    'credits_required': 6,
                    'duration_minutes': 18
                }
            ]
            
            for service in basic_services:
                try:
                    await conn.execute("""
                        INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, enabled)
                        VALUES ($1, $2, $3, $4, $5, true)
                        ON CONFLICT (name) DO NOTHING
                    """, 
                    service['name'], service['display_name'], service['description'],
                    service['credits_required'], service['duration_minutes'])
                    
                    logger.info(f"  ✅ Created service: {service['display_name']}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Service creation warning: {e}")
        else:
            logger.info(f"✅ Service types already exist ({count} services)")
            
    except Exception as e:
        logger.warning(f"⚠️ Service types check failed: {e}")

async def ensure_prokerala_config(conn):
    """Ensure Prokerala configuration exists"""
    try:
        # Check if prokerala_cost_config table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'prokerala_cost_config'
            )
        """)
        
        if not table_exists:
            logger.warning("⚠️ prokerala_cost_config table does not exist - skipping configuration check")
            return
        
        # Table exists, check if it has data
        count = await conn.fetchval("SELECT COUNT(*) FROM prokerala_cost_config")
        
        if count == 0:
            logger.info("⚙️ Creating default Prokerala configuration...")
            
            await conn.execute("""
                INSERT INTO prokerala_cost_config (max_cost_per_call, margin_percentage, cache_discount_enabled)
                VALUES (0.036, 500.00, TRUE)
            """)
            
            logger.info("✅ Default Prokerala configuration created")
        else:
            logger.info("✅ Prokerala configuration already exists")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during Prokerala config check: {e}")
        raise

if __name__ == "__main__":
    success = asyncio.run(run_auto_deployment_migrations())
    if success:
        logger.info("✅ Deployment migration successful!")
        sys.exit(0)
    else:
        logger.error("❌ Deployment migration failed!")
        sys.exit(1)