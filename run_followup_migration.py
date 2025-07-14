#!/usr/bin/env python3
"""
Migration script to add follow-up tracking columns to sessions table
Run this script to apply the follow-up system database changes
"""

import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    """Run the follow-up tracking columns migration"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is required but not set")
        print("Please set the DATABASE_URL environment variable with your database connection string")
        sys.exit(1)
    
    try:
        # Connect to database
        print("🔄 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Read and execute migration
        print("📝 Running follow-up tracking columns migration...")
        
        migration_sql = """
        -- Add specific follow-up tracking columns to sessions table
        -- Migration: Add follow-up channel tracking columns

        -- Add follow-up email tracking
        ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_email_sent BOOLEAN DEFAULT FALSE;

        -- Add follow-up SMS tracking  
        ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_sms_sent BOOLEAN DEFAULT FALSE;

        -- Add follow-up WhatsApp tracking
        ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_whatsapp_sent BOOLEAN DEFAULT FALSE;

        -- Create indexes for better performance on follow-up queries
        CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_email_sent ON sessions(follow_up_email_sent);
        CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_sms_sent ON sessions(follow_up_sms_sent);
        CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_whatsapp_sent ON sessions(follow_up_whatsapp_sent);

        -- Update existing sessions to have default values
        UPDATE sessions SET 
            follow_up_email_sent = COALESCE(follow_up_email_sent, FALSE),
            follow_up_sms_sent = COALESCE(follow_up_sms_sent, FALSE),
            follow_up_whatsapp_sent = COALESCE(follow_up_whatsapp_sent, FALSE)
        WHERE follow_up_email_sent IS NULL 
           OR follow_up_sms_sent IS NULL 
           OR follow_up_whatsapp_sent IS NULL;
        """
        
        await conn.execute(migration_sql)
        
        print("✅ Migration completed successfully!")
        print("📊 Added columns:")
        print("   - follow_up_email_sent (BOOLEAN)")
        print("   - follow_up_sms_sent (BOOLEAN)")
        print("   - follow_up_whatsapp_sent (BOOLEAN)")
        print("   - Performance indexes created")
        
        # Verify the columns were added
        print("\n🔍 Verifying migration...")
        columns = await conn.fetch("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'sessions' 
            AND column_name IN ('follow_up_email_sent', 'follow_up_sms_sent', 'follow_up_whatsapp_sent')
            ORDER BY column_name
        """)
        
        if columns:
            print("✅ Columns verified:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        else:
            print("⚠️  Warning: Could not verify columns were added")
        
        await conn.close()
        print("\n🎉 Migration script completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🕉️ JyotiFlow.ai Follow-up System Migration")
    print("=" * 50)
    
    success = asyncio.run(run_migration())
    
    if success:
        print("\n✅ Migration successful! The follow-up system is ready to use.")
        print("📝 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Access admin dashboard → Follow-ups tab")
        print("   3. The system will automatically track follow-ups by channel")
    else:
        print("\n❌ Migration failed. Please check the error and try again.")
        exit(1) 