#!/usr/bin/env python3
"""
Debug RAG Migration Issues
Check what specific migrations failed and database state
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def debug_rag_migrations():
    """Debug RAG migration failures"""
    conn = None
    try:
        # Get database URL
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        print(f"🔌 Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL, command_timeout=30)
        print("✅ Database connection established")
        
        print("\n" + "="*60)
        print("📋 MIGRATION STATUS CHECK")
        print("="*60)
        
        # Check if schema_migrations table exists
        migrations_table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'schema_migrations'
            )
        """)
        
        if migrations_table_exists:
            print("✅ schema_migrations table exists")
            
            # Get applied migrations
            applied_migrations = await conn.fetch("""
                SELECT migration_name, applied_at 
                FROM schema_migrations 
                ORDER BY applied_at DESC
            """)
            
            print(f"📊 Total applied migrations: {len(applied_migrations)}")
            print("\n🗂️  Recent Applied Migrations:")
            for row in applied_migrations[:10]:  # Show last 10
                print(f"   ✅ {row['migration_name']} - {row['applied_at']}")
            
            # Check if our RAG migrations are applied
            rag_migrations = ['026_add_pgvector_extension.sql', '027_populate_spiritual_knowledge_base.sql']
            applied_set = {row['migration_name'] for row in applied_migrations}
            
            print("\n🧠 RAG Migration Status:")
            for migration in rag_migrations:
                status = "✅ APPLIED" if migration in applied_set else "❌ NOT APPLIED"
                print(f"   {status} - {migration}")
                
        else:
            print("❌ schema_migrations table does not exist")
        
        print("\n" + "="*60)
        print("🔧 DATABASE EXTENSIONS CHECK")
        print("="*60)
        
        # Check available extensions
        extensions = await conn.fetch("SELECT extname FROM pg_extension ORDER BY extname")
        print(f"📊 Total extensions: {len(extensions)}")
        
        extension_names = [row['extname'] for row in extensions]
        if 'vector' in extension_names:
            print("✅ pgvector extension is installed")
        else:
            print("❌ pgvector extension is NOT installed")
            
        # Check if vector extension is available for installation
        try:
            available_extensions = await conn.fetch("""
                SELECT name FROM pg_available_extensions 
                WHERE name = 'vector'
            """)
            if available_extensions:
                print("✅ pgvector extension is available for installation")
            else:
                print("❌ pgvector extension is NOT available in this database")
        except Exception as e:
            print(f"⚠️ Could not check available extensions: {e}")
            
        print("\n📋 Current Extensions:")
        for ext in extension_names[:10]:  # Show first 10
            print(f"   📦 {ext}")
        
        print("\n" + "="*60)
        print("📚 RAG KNOWLEDGE BASE CHECK")
        print("="*60)
        
        # Check if rag_knowledge_base table exists
        rag_table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'rag_knowledge_base'
            )
        """)
        
        if rag_table_exists:
            print("✅ rag_knowledge_base table exists")
            
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'rag_knowledge_base'
                ORDER BY ordinal_position
            """)
            
            print(f"📊 Table has {len(columns)} columns:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   📝 {col['column_name']} - {col['data_type']} - {nullable}")
            
            # Check data count
            total_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            print(f"\n📊 Total entries: {total_count}")
            
            if total_count > 0:
                # Check categories
                categories = await conn.fetch("""
                    SELECT category, COUNT(*) as count 
                    FROM rag_knowledge_base 
                    GROUP BY category 
                    ORDER BY count DESC
                """)
                
                print("📋 Content by category:")
                for cat in categories:
                    print(f"   📚 {cat['category']}: {cat['count']} entries")
                    
                # Check if is_active column exists
                has_is_active = any(col['column_name'] == 'is_active' for col in columns)
                if has_is_active:
                    active_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base WHERE is_active = true")
                    print(f"✅ Active entries: {active_count}")
                else:
                    print("⚠️ No is_active column found")
            else:
                print("❌ Table is EMPTY - no spiritual content available")
        else:
            print("❌ rag_knowledge_base table does NOT exist")
        
        print("\n" + "="*60)
        print("🧪 RAG FUNCTIONALITY TEST")
        print("="*60)
        
        if rag_table_exists and 'vector' in extension_names:
            print("🧠 Testing RAG vector operations...")
            try:
                # Test vector similarity if we have data
                if total_count > 0:
                    # Create proper 1536-dimensional test vector
                    test_values = [0.1] * 1536
                    test_embedding = "[" + ", ".join(map(str, test_values)) + "]"
                    
                    # Test vector similarity search
                    test_query = f"""
                        SELECT title, category 
                        FROM rag_knowledge_base 
                        WHERE embedding_vector IS NOT NULL
                        ORDER BY embedding_vector <=> '[{test_embedding}]'::vector
                        LIMIT 3
                    """
                    
                    results = await conn.fetch(test_query)
                    if results:
                        print("✅ Vector similarity search working!")
                        for result in results:
                            print(f"   📖 {result['title']} ({result['category']})")
                    else:
                        print("⚠️ No vectors found for similarity search")
                else:
                    print("⚠️ Cannot test - missing table or extension")
            except Exception as e:
                print(f"❌ Vector operation failed: {e}")
        else:
            print("⚠️ Cannot test RAG - missing requirements")
            
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        
        issues = []
        if not migrations_table_exists:
            issues.append("Migration tracking system not set up")
        if 'vector' not in extension_names:
            issues.append("pgvector extension not installed")
        if not rag_table_exists:
            issues.append("rag_knowledge_base table missing")
        elif total_count == 0:
            issues.append("rag_knowledge_base table empty")
            
        if issues:
            print("❌ Issues found:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ All RAG components appear to be working!")
            
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Debug script failed: {e}")
        return False
    finally:
        if conn and not conn.is_closed():
            try:
                await conn.close()
            except Exception:
                pass  # Ignore errors when closing

if __name__ == "__main__":
    success = asyncio.run(debug_rag_migrations())
    sys.exit(0 if success else 1)
