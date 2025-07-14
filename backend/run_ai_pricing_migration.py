#!/usr/bin/env python3
"""
AI Pricing Recommendations Table Migration Script
தமிழ் - AI விலை பரிந்துரைகள் அட்டவணை மைக்கிரேஷன் ஸ்கிரிப்ட்
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db import EnhancedJyotiFlowDatabase

async def run_ai_pricing_migration():
    """Run the AI pricing recommendations table migration"""
    print("🕉️ Starting AI Pricing Recommendations Table Migration...")
    print("தமிழ் - AI விலை பரிந்துரைகள் அட்டவணை மைக்கிரேஷன் தொடங்குகிறது...")
    
    try:
        # Initialize database connection
        db = EnhancedJyotiFlowDatabase()
        await db.connect()
        
        print("✅ Database connected successfully")
        print("✅ தரவுத்தளம் வெற்றிகரமாக இணைக்கப்பட்டது")
        
        # Read and execute the migration SQL
        migration_file = backend_dir / "migrations" / "add_pricing_tables.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("📄 Executing migration SQL...")
        print("📄 மைக்கிரேஷன் SQL இயக்கப்படுகிறது...")
        
        # Split SQL by semicolon and execute each statement
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    await db.execute(statement)
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"⚠️ Statement {i} warning (may already exist): {e}")
        
        # Verify the table was created
        print("🔍 Verifying table creation...")
        print("🔍 அட்டவணை உருவாக்கம் சரிபார்க்கப்படுகிறது...")
        
        table_exists = await db.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_pricing_recommendations'
            )
        """)
        
        if table_exists:
            print("✅ ai_pricing_recommendations table created successfully")
            print("✅ ai_pricing_recommendations அட்டவணை வெற்றிகரமாக உருவாக்கப்பட்டது")
            
            # Check sample data
            sample_count = await db.fetchval("""
                SELECT COUNT(*) FROM ai_pricing_recommendations
            """)
            
            print(f"📊 Sample data count: {sample_count}")
            print(f"📊 மாதிரி தரவு எண்ணிக்கை: {sample_count}")
            
            # Show sample recommendations
            sample_recs = await db.fetch("""
                SELECT recommendation_type, service_name, current_value, suggested_value, expected_impact
                FROM ai_pricing_recommendations 
                LIMIT 3
            """)
            
            print("\n📋 Sample Recommendations:")
            print("📋 மாதிரி பரிந்துரைகள்:")
            for rec in sample_recs:
                print(f"  - {rec['recommendation_type']}: {rec['service_name']} "
                      f"(${rec['current_value']} → ${rec['suggested_value']}, "
                      f"Impact: ${rec['expected_impact']})")
            
        else:
            print("❌ Table creation failed")
            print("❌ அட்டவணை உருவாக்கம் தோல்வியடைந்தது")
            return False
        
        print("\n🎉 AI Pricing Recommendations Migration Completed Successfully!")
        print("🎉 AI விலை பரிந்துரைகள் மைக்கிரேஷன் வெற்றிகரமாக முடிந்தது!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"❌ மைக்கிரேஷன் தோல்வியடைந்தது: {e}")
        return False
    
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    success = asyncio.run(run_ai_pricing_migration())
    sys.exit(0 if success else 1) 