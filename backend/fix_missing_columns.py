#!/usr/bin/env python3
"""
🔧 Missing Columns Fix Script
Fix missing columns causing SQL errors in admin and service features.

This script addresses:
1. Missing 'credits_required' column in service_types table
2. Missing 'dt.user_id' column in donation_transactions table

Usage:
    python fix_missing_columns.py
"""

import asyncio
import asyncpg
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MissingColumnsFixup:
    """Handle missing columns fix for JyotiFlow database"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
        )
        
    async def run_migration(self):
        """Run the missing columns fix migration"""
        logger.info("🚀 Starting missing columns fix migration...")
        
        try:
            # Connect to database
            conn = await asyncpg.connect(self.database_url)
            logger.info("✅ Connected to database")
            
            # Read migration file
            migration_path = Path(__file__).parent / "migrations" / "fix_missing_columns.sql"
            
            if not migration_path.exists():
                logger.error(f"❌ Migration file not found: {migration_path}")
                return False
                
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
                
            logger.info("📋 Executing migration...")
            
            # Execute migration
            await conn.execute(migration_sql)
            
            logger.info("✅ Migration completed successfully!")
            
            # Verify the fixes
            await self._verify_fixes(conn)
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _verify_fixes(self, conn):
        """Verify that the fixes have been applied correctly"""
        logger.info("🔍 Verifying fixes...")
        
        try:
            # Check service_types table and credits_required column
            service_types_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'service_types'
                )
            """)
            
            if service_types_exists:
                logger.info("✅ service_types table exists")
                
                credits_required_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'service_types' AND column_name = 'credits_required'
                    )
                """)
                
                if credits_required_exists:
                    logger.info("✅ credits_required column exists in service_types")
                    
                    # Test the query that was failing
                    try:
                        test_services = await conn.fetch("""
                            SELECT 
                                id, name, 
                                COALESCE(credits_required, base_credits, 1) as credits_required,
                                COALESCE(price_usd, 0.0) as price_usd
                            FROM service_types 
                            WHERE COALESCE(enabled, true) = TRUE 
                            ORDER BY COALESCE(credits_required, base_credits, 1) ASC
                            LIMIT 5
                        """)
                        
                        logger.info(f"✅ Service types query test passed! Found {len(test_services)} services")
                        for service in test_services:
                            logger.info(f"  - {service['name']}: {service['credits_required']} credits")
                            
                    except Exception as e:
                        logger.error(f"❌ Service types query still failing: {e}")
                        
                else:
                    logger.error("❌ credits_required column missing from service_types")
            else:
                logger.error("❌ service_types table does not exist")
            
            # Check donation_transactions table and user_id column
            donation_transactions_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'donation_transactions'
                )
            """)
            
            if donation_transactions_exists:
                logger.info("✅ donation_transactions table exists")
                
                user_id_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'donation_transactions' AND column_name = 'user_id'
                    )
                """)
                
                if user_id_exists:
                    logger.info("✅ user_id column exists in donation_transactions")
                    
                    # Test the query that was failing
                    try:
                        test_donors = await conn.fetch("""
                            SELECT 
                                u.email,
                                u.first_name,
                                u.last_name,
                                COALESCE(SUM(dt.amount_usd), 0) as total_donated,
                                COUNT(dt.id) as donation_count
                            FROM users u
                            LEFT JOIN donation_transactions dt ON u.id = dt.user_id 
                                AND dt.status = 'completed'
                                AND dt.created_at >= date_trunc('month', CURRENT_DATE)
                            GROUP BY u.id, u.email, u.first_name, u.last_name
                            HAVING COALESCE(SUM(dt.amount_usd), 0) > 0
                            ORDER BY total_donated DESC
                            LIMIT 5
                        """)
                        
                        logger.info(f"✅ Monthly top donors query test passed! Found {len(test_donors)} donors")
                        for donor in test_donors:
                            logger.info(f"  - {donor['email']}: ${donor['total_donated']}")
                            
                    except Exception as e:
                        logger.error(f"❌ Monthly top donors query still failing: {e}")
                        
                else:
                    logger.error("❌ user_id column missing from donation_transactions")
            else:
                logger.error("❌ donation_transactions table does not exist")
            
            # Check donations table
            donations_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'donations'
                )
            """)
            
            if donations_exists:
                logger.info("✅ donations table exists")
                
                # Check if it has records
                donation_count = await conn.fetchval("SELECT COUNT(*) FROM donations")
                logger.info(f"📊 Found {donation_count} donation options")
                
            else:
                logger.error("❌ donations table does not exist")
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
    
    async def check_current_state(self):
        """Check the current state of the database without making changes"""
        logger.info("🔍 Checking current database state...")
        
        try:
            conn = await asyncpg.connect(self.database_url)
            logger.info("✅ Connected to database")
            
            # List all tables
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            logger.info(f"📋 Found {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table['table_name']}")
            
            # Check service_types columns
            if any(table['table_name'] == 'service_types' for table in tables):
                logger.info("\n🔍 service_types table columns:")
                columns = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'service_types' 
                    ORDER BY ordinal_position
                """)
                
                for col in columns:
                    logger.info(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check donation_transactions columns
            if any(table['table_name'] == 'donation_transactions' for table in tables):
                logger.info("\n🔍 donation_transactions table columns:")
                columns = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'donation_transactions' 
                    ORDER BY ordinal_position
                """)
                
                for col in columns:
                    logger.info(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return False

async def main():
    """Main function"""
    fixer = MissingColumnsFixup()
    
    # Check if user wants to inspect current state first
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        await fixer.check_current_state()
        return
    
    # Run the migration
    success = await fixer.run_migration()
    
    if success:
        logger.info("\n✅ SUCCESS: Missing columns fix migration completed!")
        logger.info("\n🎯 NEXT STEPS:")
        logger.info("1. Test the /api/services/types endpoint")
        logger.info("2. Test the /api/donations/top-donors/monthly endpoint")
        logger.info("3. Check admin dashboard service management")
        logger.info("4. Verify credit system functionality")
    else:
        logger.error("\n❌ FAILURE: Migration failed!")
        logger.error("Please check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())