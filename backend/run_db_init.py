#!/usr/bin/env python3
"""
🎯 JyotiFlow Database Initialization Runner
Run this script to manually initialize the database tables
"""

import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_database import initialize_jyotiflow_database

async def main():
    """Main function to run database initialization"""
    print("🚀 Starting JyotiFlow Database Initialization...")
    print("=" * 50)
    
    try:
        success = await initialize_jyotiflow_database()
        
        if success:
            print("=" * 50)
            print("✅ Database initialization completed successfully!")
            print("🎉 All tables have been created and initial data inserted.")
            print("🚀 JyotiFlow is ready to run!")
        else:
            print("=" * 50)
            print("❌ Database initialization failed!")
            print("Please check the error messages above and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 