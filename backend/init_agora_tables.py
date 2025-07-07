#!/usr/bin/env python3
"""
Initialize Agora database tables for live chat functionality
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = "backend/jyotiflow.db"

def create_agora_tables():
    """Create all necessary tables for Agora live chat functionality"""
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            print("🎥 Creating Agora live chat tables...")
            
            # Live chat sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    session_type TEXT DEFAULT 'spiritual_guidance',
                    agora_token TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ended_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Session participants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    joined_at TEXT NOT NULL,
                    left_at TEXT,
                    status TEXT DEFAULT 'joined',
                    FOREIGN KEY (session_id) REFERENCES live_chat_sessions(session_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Agora usage tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agora_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    duration_minutes INTEGER DEFAULT 0,
                    cost_credits REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES live_chat_sessions(session_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_user_id 
                ON live_chat_sessions(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_status 
                ON live_chat_sessions(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_participants_session_id 
                ON session_participants(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_agora_usage_logs_user_id 
                ON agora_usage_logs(user_id)
            """)
            
            conn.commit()
            
            print("✅ Agora tables created successfully!")
            
            # Verify tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%live_chat%' OR name LIKE '%session_participants%' OR name LIKE '%agora_usage%'
            """)
            tables = cursor.fetchall()
            
            print(f"📋 Created tables: {[table[0] for table in tables]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating Agora tables: {e}")
        return False

def verify_agora_setup():
    """Verify that all Agora tables are properly set up"""
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            required_tables = [
                'live_chat_sessions',
                'session_participants', 
                'agora_usage_logs'
            ]
            
            for table in required_tables:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table,))
                
                if not cursor.fetchone():
                    print(f"❌ Table {table} not found!")
                    return False
                else:
                    print(f"✅ Table {table} verified")
            
            # Check table schemas
            cursor.execute("PRAGMA table_info(live_chat_sessions)")
            session_columns = [col[1] for col in cursor.fetchall()]
            
            required_session_columns = [
                'id', 'session_id', 'user_id', 'channel_name', 
                'session_type', 'agora_token', 'status', 
                'created_at', 'expires_at', 'ended_at'
            ]
            
            for col in required_session_columns:
                if col not in session_columns:
                    print(f"❌ Column {col} missing in live_chat_sessions!")
                    return False
                    
            print("✅ All Agora tables and schemas verified successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying Agora setup: {e}")
        return False

def add_demo_data():
    """Add some demo data for testing"""
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Check if users table exists and has data
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                print("⚠️ No users found - cannot add demo data")
                return
                
            # Get first user ID
            cursor.execute("SELECT id FROM users LIMIT 1")
            user_id = cursor.fetchone()[0]
            
            # Add demo live chat session
            demo_session_id = "demo_session_12345"
            demo_channel = "jyotiflow_spiritual_guidance_demo"
            
            cursor.execute("""
                INSERT OR REPLACE INTO live_chat_sessions 
                (session_id, user_id, channel_name, session_type, status, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                demo_session_id,
                user_id,
                demo_channel,
                'spiritual_guidance',
                'ended',
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Add demo usage log
            cursor.execute("""
                INSERT OR REPLACE INTO agora_usage_logs
                (session_id, user_id, duration_minutes, cost_credits, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                demo_session_id,
                user_id,
                30,
                15.0,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            print("✅ Demo data added successfully!")
            
    except Exception as e:
        print(f"❌ Error adding demo data: {e}")

if __name__ == "__main__":
    print("🚀 Initializing Agora Live Chat Database...")
    
    if create_agora_tables():
        if verify_agora_setup():
            add_demo_data()
            print("\n🎉 Agora integration database setup complete!")
            print("You can now use the live chat functionality.")
        else:
            print("\n❌ Agora setup verification failed!")
    else:
        print("\n❌ Agora table creation failed!")