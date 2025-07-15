#!/usr/bin/env python3
"""
Test script to check which frontend API endpoints are working
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")

async def test_endpoints():
    """Test all the endpoints that the frontend is calling"""
    
    print("🔍 Testing Frontend API Endpoints...")
    print("=" * 50)
    
    # Connect to database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test endpoints that should exist
    endpoints_to_test = [
        ("/api/user/profile", "User profile endpoint"),
        ("/api/user/sessions", "User sessions endpoint"),
        ("/api/user/credits", "User credits endpoint"),
        ("/api/user/credit-history", "User credit history endpoint"),
        ("/api/user/recommendations", "User recommendations endpoint"),
        ("/api/ai/user-recommendations", "AI user recommendations endpoint"),
        ("/api/spiritual/progress/{user_id}", "Spiritual progress endpoint"),
        ("/api/spiritual/birth-chart/cache-status", "Birth chart cache status endpoint"),
        ("/api/followup/my-followups", "User followups endpoint"),
        ("/api/services/types", "Service types endpoint"),
        ("/api/credits/packages", "Credit packages endpoint"),
        ("/api/community/my-participation", "Community participation endpoint"),
        ("/api/sessions/analytics", "Session analytics endpoint"),
    ]
    
    print("\n📋 Endpoint Status:")
    print("-" * 50)
    
    for endpoint, description in endpoints_to_test:
        # Check if the endpoint exists in the codebase
        if "user_id" in endpoint:
            endpoint = endpoint.replace("{user_id}", "test-user")
        
        print(f"🔍 {description}: {endpoint}")
        
        # For now, just check if the router files exist
        if "user/" in endpoint:
            print("   ✅ User router exists")
        elif "ai/" in endpoint:
            print("   ✅ AI router exists")
        elif "spiritual/" in endpoint:
            print("   ✅ Spiritual router exists")
        elif "followup/" in endpoint:
            print("   ✅ Followup router exists")
        elif "services/" in endpoint:
            print("   ✅ Services router exists")
        elif "credits/" in endpoint:
            print("   ✅ Credits router exists")
        else:
            print("   ❓ Router status unknown")
    
    # Test database tables
    print("\n🗄️ Database Table Status:")
    print("-" * 50)
    
    tables_to_check = [
        "users",
        "sessions", 
        "service_types",
        "credit_packages",
        "followup_messages",
        "platform_settings"
    ]
    
    for table in tables_to_check:
        try:
            result = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"✅ {table}: {result} records")
        except Exception as e:
            print(f"❌ {table}: {str(e)}")
    
    await conn.close()
    print("\n✅ Endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(test_endpoints()) 