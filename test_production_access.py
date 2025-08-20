#!/usr/bin/env python3
"""
Test Production Database Access
Quick check of what we can do in the Supabase environment
"""

import asyncio
import asyncpg
import os

async def test_production_access():
    """Test production database capabilities"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Try to get from Render environment (they might have set it)
        DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DB_URL")
    
    if not DATABASE_URL:
        print("❌ No database URL found in environment")
        print("💡 Available DB environment variables:")
        # Securely list environment variables without exposing values
        for var in sorted(k for k in os.environ if 'DB' in k.upper() or 'DATABASE' in k.upper()):
            print(f"   {var}: ********")
        return False
    
    conn = None
    try:
        print("🔌 Testing database connection...")
        print("📍 Target: ********")  # Don't expose any part of connection string
        
        conn = await asyncpg.connect(DATABASE_URL, command_timeout=10)
        print("✅ Connected successfully!")
        
        # Test basic permissions
        print("\n🔐 Testing Permissions:")
        
        # Can we select?
        try:
            result = await conn.fetchval("SELECT 1")
            print(f"   ✅ SELECT: {result}")
        except Exception as e:
            print(f"   ❌ SELECT: {e}")
        
        # Can we create temp tables?
        try:
            await conn.execute("CREATE TEMP TABLE test_temp (id int)")
            await conn.execute("DROP TABLE test_temp")
            print("   ✅ CREATE/DROP TEMP: Working")
        except Exception as e:
            print(f"   ❌ CREATE/DROP TEMP: {e}")
        
        # Can we create extensions?
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("   ✅ CREATE EXTENSION vector: Success!")
        except Exception as e:
            print(f"   ❌ CREATE EXTENSION vector: {e}")
            
            # Check if it's already installed
            has_vector = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            if has_vector:
                print("   ✅ Vector extension already installed!")
        
        # Check available extensions
        print("\n📦 Available Extensions:")
        try:
            available = await conn.fetch("SELECT name FROM pg_available_extensions WHERE name LIKE '%vector%' OR name LIKE '%embed%'")
            if available:
                for ext in available:
                    print(f"   📦 {ext['name']}")
            else:
                print("   ⚠️ No vector/embedding extensions found")
        except Exception as e:
            print(f"   ❌ Extension check failed: {e}")
        
        # Check current extensions  
        print("\n🔧 Current Extensions:")
        extensions = await conn.fetch("SELECT extname FROM pg_extension ORDER BY extname")
        for ext in extensions[:15]:  # Show first 15
            print(f"   ✅ {ext['extname']}")
        if len(extensions) > 15:
            print(f"   ... and {len(extensions) - 15} more")
        
        # Test vector operations if available
        has_vector = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
        if has_vector:
            print("\n🧠 Testing Vector Operations:")
            try:
                # Test vector creation
                test_vector = "[" + ",".join(["0.1"] * 1536) + "]"
                result = await conn.fetchval("SELECT $1::vector", test_vector)
                print("   ✅ Vector creation: Working")
                
                # Test vector similarity
                await conn.fetchval("SELECT $1::vector <=> $2::vector", test_vector, test_vector)
                print("   ✅ Vector similarity: Working")
                
            except Exception as e:
                print(f"   ❌ Vector operations: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    finally:
        if conn and not conn.is_closed():
            try:
                await conn.close()
            except Exception:
                pass  # Ignore errors when closing

if __name__ == "__main__":
    success = asyncio.run(test_production_access())
    print(f"\n{'✅ Production access test passed!' if success else '❌ Production access test failed!'}")
