#!/usr/bin/env python3
"""
Migration runner for welcome credits configuration
"""

import asyncio
import asyncpg
import os
from datetime import datetime

async def run_migration():
    """Run the welcome credits migration"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/jyotiflow")
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Add welcome credits configuration
        await conn.execute("""
            INSERT INTO pricing_config (key, value, description, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                description = EXCLUDED.description,
                updated_at = EXCLUDED.updated_at
        """, (
            'welcome_credits',
            '20',
            'Number of credits given to new users upon registration',
            True,
            datetime.now(),
            datetime.now()
        ))
        
        # Add configuration for different user tiers
        await conn.execute("""
            INSERT INTO pricing_config (key, value, description, is_active, created_at, updated_at)
            VALUES 
                ($1, $2, $3, $4, $5, $6),
                ($7, $8, $9, $10, $11, $12)
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                description = EXCLUDED.description,
                updated_at = EXCLUDED.updated_at
        """, (
            'premium_welcome_credits', '50', 'Welcome credits for premium users', True, datetime.now(), datetime.now(),
            'vip_welcome_credits', '100', 'Welcome credits for VIP users', True, datetime.now(), datetime.now()
        ))
        
        await conn.close()
        print("✅ Welcome credits migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())