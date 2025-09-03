from typing import Optional, Any

import os

try:
    import psycopg
    from psycopg import AsyncConnection
    import pgvector.psycopg # Needed for pgvector adapter registration
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False
    print("⚠️ psycopg not available - please install psycopg[binary]")

from .knowledge_seeding_system import AsyncPGCompatPool, AsyncPGCompatConnection

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

# Global database pool (will be set by main.py)
db_pool: Optional[AsyncPGCompatPool] = None

def set_db_pool(pool: AsyncPGCompatPool):
    """Set the database pool from main.py"""
    global db_pool
    db_pool = pool

def get_db_pool() -> Optional[AsyncPGCompatPool]:
    """Get the current database pool"""
    return db_pool

async def get_db():
    """Get database connection from pool"""
    if db_pool is None:
        # Fallback to direct connection if pool not available
        if PSYCOPG_AVAILABLE:
            conn = await AsyncConnection.connect(DATABASE_URL)
            try:
                # Register pgvector type adapters for direct connection
                await pgvector.psycopg.register_vector_async(conn)
                yield AsyncPGCompatConnection(conn)
            finally:
                await conn.close()
        else:
            raise ModuleNotFoundError("psycopg not available for direct connection fallback")
    else:
        # Use connection pool
        async with db_pool.acquire() as conn:
            yield conn

# Database manager for compatibility
class DatabaseManager:
    def __init__(self):
        self.database_url = DATABASE_URL
        self.is_sqlite = False  # We're using PostgreSQL
    
    async def get_connection(self) -> AsyncPGCompatConnection:
        """Get database connection"""
        if db_pool is None:
            # If no pool, create a direct connection
            if PSYCOPG_AVAILABLE:
                conn = await AsyncConnection.connect(self.database_url)
                # Register pgvector type adapters for direct connection
                await pgvector.psycopg.register_vector_async(conn)
                return AsyncPGCompatConnection(conn)
            else:
                raise ModuleNotFoundError("psycopg not available for direct connection fallback")
        else:
            return await db_pool.acquire().__aenter__() # Manually enter context for direct use
    
    async def release_connection(self, conn: AsyncPGCompatConnection):
        """Release database connection"""
        if db_pool is None:
            await conn._conn.close()
        else:
            await conn.__aexit__(None, None, None) # Manually exit context

# Create global instance
db_manager = DatabaseManager() 