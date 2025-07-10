#!/usr/bin/env python3
"""
Database Migration Runner for JyotiFlow Platform
Safely applies database migrations without disrupting existing functionality
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationRunner:
    def __init__(self, database_url):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "migrations"
        
    async def create_migrations_table(self, conn):
        """Create migrations tracking table if it doesn't exist"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                checksum VARCHAR(64)
            )
        """)
        logger.info("✅ Migrations tracking table ready")
    
    async def get_applied_migrations(self, conn):
        """Get list of already applied migrations"""
        rows = await conn.fetch("SELECT migration_name FROM schema_migrations ORDER BY applied_at")
        return {row['migration_name'] for row in rows}
    
    async def calculate_checksum(self, migration_content):
        """Calculate checksum for migration content"""
        import hashlib
        return hashlib.sha256(migration_content.encode()).hexdigest()
    
    async def apply_migration(self, conn, migration_file):
        """Apply a single migration file"""
        migration_name = migration_file.name
        
        try:
            # Read migration content
            with open(migration_file, 'r') as f:
                migration_content = f.read()
            
            # Calculate checksum
            checksum = await self.calculate_checksum(migration_content)
            
            logger.info(f"🔄 Applying migration: {migration_name}")
            
            # Start transaction
            async with conn.transaction():
                # Execute migration
                await conn.execute(migration_content)
                
                # Record migration as applied
                await conn.execute("""
                    INSERT INTO schema_migrations (migration_name, checksum) 
                    VALUES ($1, $2)
                    ON CONFLICT (migration_name) DO NOTHING
                """, migration_name, checksum)
            
            logger.info(f"✅ Migration applied successfully: {migration_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {migration_name} - {str(e)}")
            return False
    
    async def run_migrations(self):
        """Run all pending migrations"""
        try:
            # Connect to database
            conn = await asyncpg.connect(self.database_url)
            logger.info("🔗 Connected to database")
            
            # Create migrations table
            await self.create_migrations_table(conn)
            
            # Get applied migrations
            applied_migrations = await self.get_applied_migrations(conn)
            logger.info(f"📋 Found {len(applied_migrations)} previously applied migrations")
            
            # Get all migration files
            migration_files = sorted([
                f for f in self.migrations_dir.glob("*.sql")
                if f.is_file()
            ])
            
            if not migration_files:
                logger.info("📂 No migration files found")
                return True
            
            # Apply pending migrations
            pending_migrations = [
                f for f in migration_files 
                if f.name not in applied_migrations
            ]
            
            if not pending_migrations:
                logger.info("✅ All migrations are up to date")
                return True
            
            logger.info(f"🚀 Applying {len(pending_migrations)} pending migrations")
            
            success_count = 0
            for migration_file in pending_migrations:
                if await self.apply_migration(conn, migration_file):
                    success_count += 1
                else:
                    logger.error(f"💥 Migration failed, stopping at: {migration_file.name}")
                    break
            
            await conn.close()
            
            if success_count == len(pending_migrations):
                logger.info(f"🎉 All {success_count} migrations applied successfully!")
                return True
            else:
                logger.error(f"⚠️ Only {success_count}/{len(pending_migrations)} migrations applied")
                return False
                
        except Exception as e:
            logger.error(f"💥 Migration runner failed: {str(e)}")
            return False

async def main():
    """Main migration runner"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Run migrations
    runner = MigrationRunner(database_url)
    success = await runner.run_migrations()
    
    if success:
        logger.info("🎯 Migration process completed successfully")
        sys.exit(0)
    else:
        logger.error("💥 Migration process failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

