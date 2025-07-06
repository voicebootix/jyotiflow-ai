#!/usr/bin/env python3
"""
AI Recommendations Migration Script
தமிழ் - AI பரிந்துரைகள் மைக்கிரேஷன் ஸ்கிரிப்ட்
"""

import asyncio
import asyncpg
import os
from pathlib import Path

async def run_ai_migration():
    """Run AI recommendations table migration"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/jyotiflow')
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("🔄 Connected to database")
        
        # Read migration SQL
        migration_file = Path(__file__).parent / "migrations" / "ai_recommendations_table.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("🔄 Running AI recommendations migration...")
        await conn.execute(migration_sql)
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('ai_recommendations', 'monetization_experiments', 'ai_insights_cache')
        """)
        
        created_tables = [row['table_name'] for row in tables]
        print(f"✅ Created tables: {created_tables}")
        
        # Check sample data
        recommendations_count = await conn.fetchval("SELECT COUNT(*) FROM ai_recommendations")
        experiments_count = await conn.fetchval("SELECT COUNT(*) FROM monetization_experiments")
        
        print(f"📊 Sample data inserted:")
        print(f"   • {recommendations_count} AI recommendations")
        print(f"   • {experiments_count} monetization experiments")
        
        await conn.close()
        print("✅ AI migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_ai_migration()) 