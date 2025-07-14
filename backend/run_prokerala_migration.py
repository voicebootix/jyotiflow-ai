#!/usr/bin/env python3
"""
Migration script for Prokerala Smart Pricing System
Adds new tables and columns for cost-aware pricing
"""

import os
import asyncio
import asyncpg
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_prokerala_migration():
    """Run the Prokerala smart pricing migration"""
    
    # Database connection - no hardcoded fallback
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("🚀 Starting Prokerala Smart Pricing Migration...")
        
        # Read migration file using absolute path
        script_dir = Path(__file__).parent
        migration_file = script_dir / "migrations" / "add_prokerala_smart_pricing.sql"
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Begin transaction for atomicity
        async with conn.transaction():
            # Use a more robust method to split SQL statements
            # This handles semicolons inside strings and comments better
            statements = []
            current_statement = ""
            in_string = False
            string_char = None
            
            for char in migration_sql:
                if char in ("'", '"') and not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and in_string:
                    in_string = False
                    string_char = None
                elif char == ';' and not in_string:
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                    current_statement = ""
                    continue
                
                current_statement += char
            
            # Add the last statement if it exists
            if current_statement.strip():
                statements.append(current_statement.strip())
            
            # Execute all statements within the transaction
            for i, statement in enumerate(statements):
                try:
                    await conn.execute(statement)
                    logger.info(f"✅ [{i+1}/{len(statements)}] Executed: {statement[:50]}...")
                except Exception as e:
                    logger.error(f"❌ [{i+1}/{len(statements)}] Error: {str(e)[:100]}")
                    # Critical error - let transaction rollback
                    raise
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(run_prokerala_migration())