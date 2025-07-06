import asyncpg
from fastapi import Depends
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

# Global database pool (will be set by main.py)
db_pool = None

def set_db_pool(pool):
    """Set the database pool from main.py"""
    global db_pool
    db_pool = pool

async def get_db():
    """Get database connection from pool"""
    if db_pool is None:
        # Fallback to direct connection if pool not available
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            yield conn
        finally:
            await conn.close()
    else:
        # Use connection pool
        async with db_pool.acquire() as conn:
            yield conn 