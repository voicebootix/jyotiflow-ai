import hmac
import hashlib
import struct
import time
import json
import secrets
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncio
from fastapi import HTTPException
import sqlite3
import aiosqlite
import logging

logger = logging.getLogger(__name__)

class AgoraTokenGenerator:
    """Agora RTC Token Generator for secure channel access"""
    
    def __init__(self, app_id: str, app_certificate: str):
        self.app_id = app_id
        self.app_certificate = app_certificate
        
    def generate_rtc_token(self, channel_name: str, uid: int, role: int = 1, expire_time: int = 3600) -> str:
        """Generate Agora RTC token for channel access
        
        Args:
            channel_name: Unique channel identifier
            uid: User identifier (0 for string-based UIDs)
            role: 1 for publisher, 2 for subscriber
            expire_time: Token expiration in seconds
            
        Returns:
            Generated Agora RTC token
        """
        try:
            # Build token with current timestamp
            current_timestamp = int(time.time())
            expire_timestamp = current_timestamp + expire_time
            
            # Create token signature
            token_data = {
                'appId': self.app_id,
                'channelName': channel_name,
                'uid': uid,
                'role': role,
                'expireTime': expire_timestamp
            }
            
            # Generate signature using HMAC-SHA256
            message = f"{self.app_id}{channel_name}{uid}{role}{expire_timestamp}"
            signature = hmac.new(
                self.app_certificate.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Create token (simplified version for demo)
            token = f"agora_token_{self.app_id}_{channel_name}_{uid}_{signature[:16]}"
            
            return token
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise HTTPException(status_code=500, detail="Token generation failed")


class AgoraChannelManager:
    """Manage Agora channels and sessions"""
    
    def __init__(self, db_path: str = "backend/jyotiflow.db"):
        self.db_path = db_path
        
    async def create_session_channel(self, user_id: int, session_type: str = "spiritual_guidance") -> Dict:
        """Create new Agora channel for live session
        
        Args:
            user_id: User requesting the session
            session_type: Type of session (spiritual_guidance, satsang, etc.)
            
        Returns:
            Session details with Agora credentials
        """
        try:
            # Generate unique channel name
            channel_name = f"jyotiflow_{session_type}_{user_id}_{int(time.time())}"
            session_id = secrets.token_urlsafe(16)
            
            # Create session record
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'channel_name': channel_name,
                'session_type': session_type,
                'status': 'created',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO live_chat_sessions 
                    (session_id, user_id, channel_name, session_type, status, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, user_id, channel_name, session_type, 
                    'created', session_data['created_at'], session_data['expires_at']
                ))
                await conn.commit()
                
            logger.info(f"Session created: {session_id} for user {user_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Channel creation failed: {e}")
            raise HTTPException(status_code=500, detail="Channel creation failed")
    
    async def join_channel(self, session_id: str, user_id: int) -> Dict:
        """Generate credentials for user to join existing channel
        
        Args:
            session_id: Session to join
            user_id: User requesting to join
            
        Returns:
            Agora credentials for joining
        """
        try:
            # Get session details
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT channel_name, session_type, status, expires_at
                    FROM live_chat_sessions
                    WHERE session_id = ?
                """, (session_id,))
                session = await cursor.fetchone()
                
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
                
            channel_name, session_type, status, expires_at = session
            
            # Check if session is still active
            if status != 'active':
                raise HTTPException(status_code=400, detail="Session not active")
                
            # Check expiration
            if datetime.fromisoformat(expires_at) < datetime.now():
                raise HTTPException(status_code=400, detail="Session expired")
            
            # Record participant join
            await self._record_participant_join(session_id, user_id)
            
            return {
                'session_id': session_id,
                'channel_name': channel_name,
                'session_type': session_type,
                'user_id': user_id,
                'status': 'ready_to_join'
            }
            
        except Exception as e:
            logger.error(f"Join channel failed: {e}")
            raise HTTPException(status_code=500, detail="Join channel failed")
    
    async def _record_participant_join(self, session_id: str, user_id: int):
        """Record user joining session"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO session_participants 
                    (session_id, user_id, joined_at, status)
                    VALUES (?, ?, ?, ?)
                """, (session_id, user_id, datetime.now().isoformat(), 'joined'))
                await conn.commit()
        except Exception as e:
            logger.error(f"Failed to record participant join: {e}")
    
    async def end_session(self, session_id: str, user_id: int) -> Dict:
        """End live chat session
        
        Args:
            session_id: Session to end
            user_id: User ending the session
            
        Returns:
            Session end confirmation
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Update session status
                await conn.execute("""
                    UPDATE live_chat_sessions 
                    SET status = 'ended', ended_at = ?
                    WHERE session_id = ? AND user_id = ?
                """, (datetime.now().isoformat(), session_id, user_id))
                
                # Update participant status
                await conn.execute("""
                    UPDATE session_participants 
                    SET status = 'left', left_at = ?
                    WHERE session_id = ? AND user_id = ?
                """, (datetime.now().isoformat(), session_id, user_id))
                
                await conn.commit()
                
            logger.info(f"Session ended: {session_id}")
            return {
                'session_id': session_id,
                'status': 'ended',
                'ended_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"End session failed: {e}")
            raise HTTPException(status_code=500, detail="End session failed")
    
    async def get_session_status(self, session_id: str) -> Dict:
        """Get current session status and participants
        
        Args:
            session_id: Session to check
            
        Returns:
            Session status and participant info
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Get session details
                cursor = await conn.execute("""
                    SELECT session_id, user_id, channel_name, session_type, 
                           status, created_at, expires_at, ended_at
                    FROM live_chat_sessions
                    WHERE session_id = ?
                """, (session_id,))
                session = await cursor.fetchone()
                
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                # Get participants
                cursor = await conn.execute("""
                    SELECT user_id, joined_at, left_at, status
                    FROM session_participants
                    WHERE session_id = ?
                """, (session_id,))
                participants = await cursor.fetchall()
                
            session_data = {
                'session_id': session[0],
                'user_id': session[1],
                'channel_name': session[2],
                'session_type': session[3],
                'status': session[4],
                'created_at': session[5],
                'expires_at': session[6],
                'ended_at': session[7],
                'participants': [
                    {
                        'user_id': p[0],
                        'joined_at': p[1],
                        'left_at': p[2],
                        'status': p[3]
                    } for p in participants
                ]
            }
            
            return session_data
            
        except Exception as e:
            logger.error(f"Get session status failed: {e}")
            raise HTTPException(status_code=500, detail="Get session status failed")


class AgoraServiceManager:
    """Main Agora service manager"""
    
    def __init__(self, app_id: str, app_certificate: str, db_path: str = "backend/jyotiflow.db"):
        self.app_id = app_id
        self.app_certificate = app_certificate
        self.token_generator = AgoraTokenGenerator(app_id, app_certificate)
        self.channel_manager = AgoraChannelManager(db_path)
        
    async def initiate_live_session(self, user_id: int, session_type: str = "spiritual_guidance") -> Dict:
        """Complete flow to initiate live session with Agora
        
        Args:
            user_id: User requesting session
            session_type: Type of session
            
        Returns:
            Complete session data with Agora credentials
        """
        try:
            # Create channel
            session_data = await self.channel_manager.create_session_channel(user_id, session_type)
            
            # Generate token
            token = self.token_generator.generate_rtc_token(
                session_data['channel_name'], 
                user_id, 
                role=1,  # Publisher role
                expire_time=3600  # 1 hour
            )
            
            # Update session with token
            session_data.update({
                'agora_app_id': self.app_id,
                'agora_token': token,
                'agora_channel': session_data['channel_name'],
                'user_role': 'publisher',
                'token_expires_in': 3600
            })
            
            # Update session status to active
            async with aiosqlite.connect(self.channel_manager.db_path) as conn:
                await conn.execute("""
                    UPDATE live_chat_sessions 
                    SET status = 'active', agora_token = ?
                    WHERE session_id = ?
                """, (token, session_data['session_id']))
                await conn.commit()
            
            logger.info(f"Live session initiated: {session_data['session_id']}")
            return session_data
            
        except Exception as e:
            logger.error(f"Live session initiation failed: {e}")
            raise HTTPException(status_code=500, detail="Live session initiation failed")
    
    async def create_database_tables(self):
        """Create necessary database tables for Agora integration"""
        try:
            async with aiosqlite.connect(self.channel_manager.db_path) as conn:
                # Live chat sessions table
                await conn.execute("""
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
                await conn.execute("""
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
                await conn.execute("""
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
                
                await conn.commit()
                logger.info("Agora database tables created successfully")
                
        except Exception as e:
            logger.error(f"Database table creation failed: {e}")
            raise


# Global Agora service instance
agora_service = None

async def get_agora_service() -> AgoraServiceManager:
    """Get global Agora service instance"""
    global agora_service
    if agora_service is None:
        # Load from configuration
        try:
            from core_foundation_enhanced import get_settings
            settings = get_settings()
            agora_service = AgoraServiceManager(
                app_id=settings.agora_app_id,
                app_certificate=settings.agora_app_certificate
            )
            await agora_service.create_database_tables()
        except Exception as e:
            logger.error(f"Failed to initialize Agora service: {e}")
            # Fallback with demo credentials
            agora_service = AgoraServiceManager(
                app_id="demo_app_id",
                app_certificate="demo_app_certificate"
            )
    return agora_service