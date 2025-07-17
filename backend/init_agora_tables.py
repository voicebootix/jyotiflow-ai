#!/usr/bin/env python3
"""
Initialize Agora tables for JyotiFlow video chat system
"""
import asyncpg
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

def _parse_affected_rows(command_tag: str) -> int:
    """
    Parse asyncpg command tag to extract the number of affected rows.
    
    Command tag formats:
    - UPDATE: "UPDATE n" where n = affected rows
    - DELETE: "DELETE n" where n = affected rows  
    - INSERT: "INSERT oid n" where n = affected rows
    - SELECT: "SELECT n" where n = selected rows
    
    Args:
        command_tag: Command tag string returned by asyncpg.execute()
        
    Returns:
        Number of affected rows, or 0 if parsing fails
    """
    try:
        parts = command_tag.strip().split()
        
        if not parts:
            logger.warning(f"Empty command tag received: '{command_tag}'")
            return 0
        
        command = parts[0].upper()
        
        if command in ('UPDATE', 'DELETE', 'SELECT'):
            # Format: "COMMAND n"
            if len(parts) >= 2:
                return int(parts[1])
            else:
                logger.warning(f"Unexpected {command} command tag format: '{command_tag}'")
                return 0
                
        elif command == 'INSERT':
            # Format: "INSERT oid n" where we want n
            if len(parts) >= 3:
                return int(parts[2])
            else:
                logger.warning(f"Unexpected INSERT command tag format: '{command_tag}'")
                return 0
                
        else:
            # Unknown command type
            logger.warning(f"Unknown command type in tag: '{command_tag}'")
            return 0
            
    except (ValueError, IndexError) as e:
        logger.error(f"Failed to parse command tag '{command_tag}': {e}")
        return 0

async def init_agora_tables():
    """Initialize all Agora-related tables in PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    # Validate DATABASE_URL is set
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is missing or empty. "
            "Please set the DATABASE_URL environment variable before running this script. "
            "Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'"
        )
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Create video_chat_sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS video_chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER,
                channel_name VARCHAR(255) NOT NULL,
                user_token TEXT NOT NULL,
                app_id VARCHAR(255) NOT NULL,
                service_type VARCHAR(100) DEFAULT 'video_chat',
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """)
        
        # Create video_chat_recordings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS video_chat_recordings (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                recording_sid VARCHAR(255) UNIQUE,
                resource_id VARCHAR(255),
                recording_url TEXT,
                status VARCHAR(50) DEFAULT 'processing',
                file_size INTEGER DEFAULT 0,
                duration INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES video_chat_sessions(session_id)
            )
        """)
        
        # Create video_chat_analytics table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS video_chat_analytics (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id INTEGER,
                join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                leave_time TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0,
                quality_score INTEGER DEFAULT 0,
                network_quality VARCHAR(50) DEFAULT 'unknown',
                platform VARCHAR(50) DEFAULT 'web',
                metadata JSONB DEFAULT '{}'::jsonb,
                FOREIGN KEY (session_id) REFERENCES video_chat_sessions(session_id)
            )
        """)
        
        # Create indexes for better performance
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_video_sessions_user_id ON video_chat_sessions(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_video_sessions_status ON video_chat_sessions(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_video_sessions_created_at ON video_chat_sessions(created_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_video_recordings_session_id ON video_chat_recordings(session_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_video_analytics_session_id ON video_chat_analytics(session_id)")
        
        print("✅ Agora tables initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing Agora tables: {e}")
        
    finally:
        await conn.close()

async def populate_sample_data():
    """Populate sample data for testing"""
    database_url = os.getenv("DATABASE_URL")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Insert sample video chat session
        await conn.execute("""
            INSERT INTO video_chat_sessions (session_id, user_id, channel_name, user_token, app_id, service_type)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (session_id) DO NOTHING
        """, 
        'test_session_001', 
        1, 
        'jyotiflow_test_channel', 
        'test_token_123', 
        'your_agora_app_id',
        'video_chat'
        )
        
        print("✅ Sample data populated successfully")
        
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        
    finally:
        await conn.close()

async def cleanup_expired_sessions():
    """Clean up expired video chat sessions"""
    database_url = os.getenv("DATABASE_URL")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Update expired sessions
        result = await conn.execute("""
            UPDATE video_chat_sessions 
            SET status = 'expired' 
            WHERE expires_at < NOW() 
            AND status = 'active'
        """)
        
        # Get count of updated rows using robust parsing
        updated_count = _parse_affected_rows(result)
        
        if updated_count > 0:
            print(f"✅ Cleaned up {updated_count} expired sessions")
        else:
            print("✅ No expired sessions to clean up")
            
    except Exception as e:
        print(f"❌ Error cleaning up expired sessions: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_agora_tables())
    asyncio.run(populate_sample_data())
    asyncio.run(cleanup_expired_sessions())