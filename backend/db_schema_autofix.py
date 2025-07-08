import os
import asyncpg
import asyncio

DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/jyotiflow')

async def ensure_base_credits_column():
    conn = await asyncpg.connect(DB_URL)
    try:
        # Check if base_credits column exists
        col_exists = await conn.fetchval("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='service_types' AND column_name='base_credits'
        """)
        if not col_exists:
            print("[AUTO-FIX] Adding missing column: base_credits to service_types...")
            await conn.execute("ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 1;")
            print("[AUTO-FIX] base_credits column added!")
        else:
            print("[AUTO-FIX] base_credits column already exists.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(ensure_base_credits_column()) 