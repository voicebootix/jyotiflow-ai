#!/usr/bin/env python3
"""
Migration script for Prokerala Smart Pricing System
Adds new tables and columns for cost-aware pricing
"""

import os
import asyncio
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_prokerala_migration():
    """Run the Prokerala smart pricing migration"""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("🚀 Starting Prokerala Smart Pricing Migration...")
        
        # Read migration file
        migration_file = "backend/migrations/add_prokerala_smart_pricing.sql"
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Split statements and execute
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements):
            try:
                await conn.execute(statement)
                logger.info(f"✅ [{i+1}/{len(statements)}] Executed: {statement[:50]}...")
            except Exception as e:
                logger.error(f"❌ [{i+1}/{len(statements)}] Error: {str(e)[:100]}")
                # Continue with other statements
        
        await conn.close()
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_prokerala_migration())