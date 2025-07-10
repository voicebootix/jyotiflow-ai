#!/usr/bin/env python3
"""
Auto-apply migrations during deployment
This script runs automatically when the backend starts
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def apply_migrations():
    """Apply database migrations automatically"""
    try:
        from run_migrations import MigrationRunner
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️ DATABASE_URL not set, skipping migrations")
            return True
        
        print("🚀 Starting automatic migration process...")
        
        # Run migrations
        runner = MigrationRunner(database_url)
        success = await runner.run_migrations()
        
        if success:
            print("✅ Migrations applied successfully")
            return True
        else:
            print("❌ Migration process failed")
            return False
            
    except Exception as e:
        print(f"💥 Migration error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run migrations
    success = asyncio.run(apply_migrations())
    
    if not success:
        print("⚠️ Migrations failed, but continuing with startup...")
        # Don't fail the deployment if migrations fail
        # This ensures the app still starts even if there are migration issues
    
    sys.exit(0)  # Always exit successfully to allow app startup

