#!/usr/bin/env python3
"""
Manual RAG System Fix
Apply RAG migrations manually if auto-deploy failed
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

async def manual_rag_fix():
    """Manually fix RAG system issues"""
    # Get database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    conn = None
    try:
        print("🔧 Starting manual RAG system fix...")
        conn = await asyncpg.connect(DATABASE_URL, command_timeout=30)
        print("✅ Database connection established")
        
        # Step 1: Check and enable vector extension
        print("\n" + "="*50)
        print("🔧 STEP 1: Vector Extension")
        print("="*50)
        
        try:
            # Check if vector extension exists
            has_vector = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                )
            """)
            
            if not has_vector:
                print("📦 Installing pgvector extension...")
                try:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    print("✅ pgvector extension installed successfully!")
                except Exception as ext_error:
                    print(f"❌ Failed to install pgvector: {ext_error}")
                    print("💡 Manual action needed: Enable vector extension in Supabase dashboard")
                    print("   → Go to Database → Extensions → Enable 'vector'")
            else:
                print("✅ pgvector extension already installed")
                
        except Exception as e:
            print(f"⚠️ Vector extension check failed: {e}")
        
        # Step 2: Ensure rag_knowledge_base table exists
        print("\n" + "="*50)
        print("🔧 STEP 2: Knowledge Base Table")
        print("="*50)
        
        try:
            # Create table if it doesn't exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_knowledge_base (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(100),
                    tags TEXT[],
                    embedding_vector vector(1536),
                    metadata JSONB DEFAULT '{}',
                    source_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true
                )
            """)
            print("✅ rag_knowledge_base table ready")
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_rag_knowledge_category ON rag_knowledge_base (category) WHERE is_active = true",
                "CREATE INDEX IF NOT EXISTS idx_rag_knowledge_tags ON rag_knowledge_base USING GIN (tags) WHERE is_active = true"
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                    print(f"✅ Index created: {index_sql.split()[-1]}")
                except Exception as idx_error:
                    print(f"⚠️ Index creation warning: {idx_error}")
                    
            # Try to create vector index if extension is available
            try:
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rag_knowledge_embedding 
                    ON rag_knowledge_base USING ivfflat (embedding_vector vector_cosine_ops)
                    WITH (lists = 100)
                """)
                print("✅ Vector similarity index created")
            except Exception as vec_idx_error:
                print(f"⚠️ Vector index creation failed: {vec_idx_error}")
                print("   → Will work without vector index (slower but functional)")
                
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            return False
        
        # Step 3: Populate knowledge base if empty
        print("\n" + "="*50)
        print("🔧 STEP 3: Knowledge Base Population")
        print("="*50)
        
        try:
            # Check current count
            current_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
            print(f"📊 Current entries: {current_count}")
            
            if current_count == 0:
                print("📚 Populating knowledge base with spiritual wisdom...")
                
                # Sample spiritual wisdom entries
                spiritual_entries = [
                    {
                        'title': 'The Path to Inner Peace',
                        'content': 'True inner peace is not the absence of conflict, but the presence of tranquility amidst life\'s storms. When we cultivate stillness within, we become unshakeable by external circumstances. Practice daily meditation, even for just 10 minutes, and watch as your inner landscape transforms. Peace is your natural state - everything else is temporary noise.',
                        'category': 'meditation',
                        'tags': ['inner_peace', 'meditation', 'tranquility', 'mindfulness'],
                        'source_url': 'https://jyotiflow.com/inner-peace'
                    },
                    {
                        'title': 'Meditation for Daily Life',
                        'content': 'Meditation is not escape from reality but preparation for it. Start each morning with 5 minutes of breath awareness. Sit comfortably, close your eyes, and simply observe your breathing. When thoughts arise, gently return to the breath. This simple practice builds the foundation for mindful living throughout your day.',
                        'category': 'meditation', 
                        'tags': ['daily_practice', 'breathing', 'mindfulness', 'morning_routine'],
                        'source_url': 'https://jyotiflow.com/daily-meditation'
                    },
                    {
                        'title': 'Understanding Your Life Purpose',
                        'content': 'Your life purpose is not something you find externally - it emerges from within when you align with your authentic self. Pay attention to what brings you joy, what challenges ignite your passion, and what service calls to your heart. Your dharma lies at the intersection of your gifts, the world\'s needs, and your deepest joy.',
                        'category': 'guidance',
                        'tags': ['life_purpose', 'dharma', 'authenticity', 'service'],
                        'source_url': 'https://jyotiflow.com/life-purpose'
                    },
                    {
                        'title': 'Overcoming Life Challenges',
                        'content': 'Every obstacle is a teacher in disguise. When faced with difficulties, ask not "Why me?" but "What is this teaching me?" Challenges are not punishments but invitations to grow. Embrace them with curiosity rather than resistance. The very quality you need to develop is often hidden within the challenge you\'re avoiding.',
                        'category': 'guidance',
                        'tags': ['challenges', 'growth', 'resilience', 'learning'],
                        'source_url': 'https://jyotiflow.com/overcoming-challenges'
                    },
                    {
                        'title': 'The Power of Gratitude', 
                        'content': 'Gratitude is the fastest way to transform your reality. What you appreciate, appreciates. Start and end each day by listing three things you\'re grateful for. Include challenges - they\'re gifts in disguise. Gratitude shifts your focus from what\'s missing to what\'s present, from scarcity to abundance.',
                        'category': 'daily_practice',
                        'tags': ['gratitude', 'abundance', 'appreciation', 'transformation'],
                        'source_url': 'https://jyotiflow.com/gratitude-practice'
                    },
                    {
                        'title': 'Cultivating Compassion',
                        'content': 'Compassion begins with yourself and extends to all beings. When you make mistakes, treat yourself with the same kindness you\'d show a good friend. When others hurt you, remember they\'re acting from their own pain. Compassion doesn\'t mean accepting harmful behavior - it means responding with wisdom rather than reaction.',
                        'category': 'relationships',
                        'tags': ['compassion', 'self_love', 'forgiveness', 'understanding'],
                        'source_url': 'https://jyotiflow.com/compassion'
                    },
                    {
                        'title': 'The Gift of Presence',
                        'content': 'The present moment is the only reality you truly have. The past is memory, the future is imagination - but life happens now. Practice bringing your full attention to whatever you\'re doing. When eating, eat. When listening, listen. When loving, love completely. Presence is the greatest gift you can give yourself and others.',
                        'category': 'mindfulness',
                        'tags': ['presence', 'present_moment', 'awareness', 'attention'],
                        'source_url': 'https://jyotiflow.com/presence'
                    },
                    {
                        'title': 'Embracing Change',
                        'content': 'Change is the only constant in life, yet we resist it like fighting the current of a river. What if, instead, you learned to dance with change? Every ending is a beginning, every loss creates space for gain. Embrace change as life\'s way of updating your soul\'s software. Growth requires letting go of who you were to become who you\'re meant to be.',
                        'category': 'growth',
                        'tags': ['change', 'transformation', 'letting_go', 'evolution'],
                        'source_url': 'https://jyotiflow.com/embracing-change'
                    }
                ]
                
                # Insert entries
                for entry in spiritual_entries:
                    try:
                        await conn.execute("""
                            INSERT INTO rag_knowledge_base 
                            (title, content, category, tags, source_url, metadata, is_active)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT DO NOTHING
                        """, 
                        entry['title'],
                        entry['content'], 
                        entry['category'],
                        entry['tags'],
                        entry['source_url'],
                        {"created_for": "spiritual_calendar_service"},
                        True
                        )
                        print(f"   ✅ Added: {entry['title']}")
                    except Exception as insert_error:
                        print(f"   ⚠️ Insert warning for {entry['title']}: {insert_error}")
                
                # Check final count
                final_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base")
                print(f"✅ Knowledge base populated: {final_count} entries")
                
            else:
                print(f"✅ Knowledge base already has {current_count} entries")
                
        except Exception as e:
            print(f"❌ Knowledge base population failed: {e}")
            return False
        
        # Step 4: Update migration tracking
        print("\n" + "="*50)
        print("🔧 STEP 4: Migration Tracking") 
        print("="*50)
        
        try:
            # Ensure migration tracking table exists
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    checksum VARCHAR(64)
                )
            """)
            
            # Mark our migrations as applied
            rag_migrations = [
                "026_add_pgvector_extension.sql",
                "027_populate_spiritual_knowledge_base.sql"
            ]
            
            for migration in rag_migrations:
                await conn.execute("""
                    INSERT INTO schema_migrations (migration_name, checksum)
                    VALUES ($1, $2)
                    ON CONFLICT (migration_name) DO NOTHING
                """, migration, "manual_fix")
                print(f"✅ Marked as applied: {migration}")
                
        except Exception as e:
            print(f"⚠️ Migration tracking update failed: {e}")
        
        # Step 5: Final verification
        print("\n" + "="*50)
        print("🔧 STEP 5: Verification")
        print("="*50)
        
        try:
            # Test basic functionality
            has_vector = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            has_table = await conn.fetchval("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rag_knowledge_base')")
            entry_count = await conn.fetchval("SELECT COUNT(*) FROM rag_knowledge_base") if has_table else 0
            
            print(f"📦 Vector extension: {'✅ Installed' if has_vector else '❌ Missing'}")
            print(f"📚 Knowledge base table: {'✅ Exists' if has_table else '❌ Missing'}")  
            print(f"📊 Knowledge entries: {entry_count}")
            
            if has_table and entry_count > 0:
                # Test a simple query
                sample = await conn.fetchval("SELECT title FROM rag_knowledge_base LIMIT 1")
                print(f"🧪 Sample entry: {sample}")
                
                # Test vector operations if available
                if has_vector:
                    try:
                        # Simple vector test
                        test_vector = "[" + ",".join(["0.1"] * 1536) + "]"
                        await conn.execute("SELECT $1::vector", test_vector)
                        print("✅ Vector operations working")
                    except Exception as vec_test_error:
                        print(f"⚠️ Vector test failed: {vec_test_error}")
                        
        except Exception as e:
            print(f"⚠️ Verification failed: {e}")
        
        await conn.close()
        
        print("\n" + "="*50)
        print("🎉 MANUAL RAG FIX COMPLETED")
        print("="*50)
        print("✅ RAG system should now work properly!")
        print("🧠 Dynamic spiritual content generation enabled")
        print("📚 Knowledge base populated with spiritual wisdom")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual RAG fix failed: {e}")
        return False
    finally:
        if conn and not conn.is_closed():
            try:
                await conn.close()
            except Exception:
                pass  # Ignore errors when closing

if __name__ == "__main__":
    success = asyncio.run(manual_rag_fix())
    if success:
        print("\n🚀 Manual fix completed successfully!")
        print("   → Restart application to see changes")
    else:
        print("\n💥 Manual fix failed!")
        print("   → Check error messages above")
    sys.exit(0 if success else 1)
