"""
Follow-up Service - PostgreSQL Only Version
Handles follow-up message scheduling and delivery for JyotiFlow.ai
"""

import asyncio
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from enum import Enum

# Import schemas if available, otherwise define here
try:
    from schemas.followup import (
        FollowUpTemplate, FollowUpSchedule, FollowUpRequest, 
        FollowUpResponse, FollowUpStatus, FollowUpChannel, FollowUpType
    )
except ImportError:
    # Define minimal required classes if schemas not available
    class FollowUpChannel(Enum):
        EMAIL = "email"
        SMS = "sms"
        WHATSAPP = "whatsapp"
        PUSH = "push"

# Import notification functions if available
try:
    from utils.notification_utils import send_email, send_sms, send_whatsapp, send_push_notification
except ImportError:
    # Define stubs if notification utils not available
    async def send_email(to: str, subject: str, content: str):
        pass
    def send_sms(to: str, content: str):
        pass
    def send_whatsapp(to: str, content: str):
        pass
    def send_push_notification(to: str, content: str):
        pass

logger = logging.getLogger(__name__)

class FollowUpService:
    """
    Follow-up system service for JyotiFlow.ai - PostgreSQL Only
    
    USAGE PATTERN:
    --------------
    # Option 1: Explicit initialization (recommended for long-lived services)
    service = FollowUpService(db_manager)
    await service.initialize()  # Load settings from database
    
    # Option 2: Lazy initialization (automatic on first use)
    service = FollowUpService(db_manager)
    # Settings will be loaded automatically when schedule_followup() is called
    
    IMPORTANT NOTES:
    ---------------
    - Settings are loaded from the database on first use or explicit initialization
    - If database loading fails, service falls back to safe default settings
    - All failures are logged with clear error messages (no silent failures)
    - Service remains functional even if settings table is missing/corrupted
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.settings = {}
        self._settings_loaded = False
    
    async def initialize(self):
        """Initialize the service by loading settings from database"""
        if not self._settings_loaded:
            await self._load_settings()
            self._settings_loaded = True
    
    async def _ensure_settings_loaded(self):
        """Ensure settings are loaded before proceeding with operations"""
        if not self._settings_loaded:
            await self._load_settings()
            self._settings_loaded = True
    
    async def _load_settings(self):
        """Load follow-up system settings"""
        try:
            conn = await self.db.get_connection()
            try:
                rows = await conn.fetch("SELECT setting_key, setting_value, setting_type FROM follow_up_settings WHERE is_active = TRUE")
                
                # Start with default settings
                default_settings = {
                    'auto_followup_enabled': True,
                    'default_credits_cost': 5,
                    'max_followups_per_session': 3,
                    'min_interval_hours': 24,
                    'max_interval_days': 30,
                    'enable_credit_charging': True
                }
                self.settings = default_settings.copy()
                
                # Override with database settings
                for row in rows:
                    key = row['setting_key']
                    value = row['setting_value']
                    value_type = row['setting_type']
                    
                    try:
                        if value_type == 'boolean':
                            self.settings[key] = value.lower() == 'true'
                        elif value_type == 'integer':
                            self.settings[key] = int(value)
                        else:
                            self.settings[key] = value
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Invalid setting value for {key}: {value} ({value_type}). Using default. Error: {e}")
                
                logger.info(f"Successfully loaded {len(rows)} follow-up settings from database")
                
            finally:
                await self.db.release_connection(conn)
                
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to load follow-up settings from database: {e}")
            logger.warning("⚠️ Follow-up service will operate with DEFAULT SETTINGS ONLY")
            logger.warning("⚠️ This may result in unexpected behavior. Please check database connectivity and follow_up_settings table.")
            
            # Set default settings to ensure service remains functional
            self.settings = {
                'auto_followup_enabled': True,
                'default_credits_cost': 5,
                'max_followups_per_session': 3,
                'min_interval_hours': 24,
                'max_interval_days': 30,
                'enable_credit_charging': True
            }
            
            # Mark that settings loading failed for monitoring
            self.settings['_settings_load_failed'] = True
            self.settings['_settings_load_error'] = str(e)
    
    async def schedule_followup(self, request) -> Dict[str, Any]:
        """Schedule a follow-up for a user"""
        try:
            # Ensure settings are loaded
            await self._ensure_settings_loaded()
            
            # Validate user exists and has enough credits
            user = await self._get_user_by_email(request.user_email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get template
            template = await self._get_template_by_id(request.template_id)
            if not template or not template.get('is_active', True):
                raise HTTPException(status_code=404, detail="Template not found or inactive")
            
            # Check if user has enough credits
            credits_needed = getattr(request, 'credits_to_charge', None) or template.get('credits_cost', 5)
            if self.settings.get('enable_credit_charging', True) and user['credits'] < credits_needed:
                raise HTTPException(
                    status_code=402, 
                    detail=f"Insufficient credits. Required: {credits_needed}, Available: {user['credits']}"
                )
            
            # Validate scheduling constraints
            await self._validate_scheduling_constraints(request, template)
            
            # Determine scheduled time
            scheduled_at = getattr(request, 'scheduled_at', None) or await self._calculate_optimal_time(request.user_email, template)
            
            # Create follow-up schedule
            followup_id = str(uuid.uuid4())
            conn = await self.db.get_connection()
            try:
                async with conn.transaction():
                    # Deduct credits if enabled
                    if self.settings.get('enable_credit_charging', True):
                        await conn.execute(
                            "UPDATE users SET credits = credits - $1 WHERE email = $2",
                            credits_needed, request.user_email
                        )
                    
                    # Create follow-up schedule
                    channel_value = request.channel.value if hasattr(request.channel, 'value') else str(request.channel)
                    await conn.execute("""
                        INSERT INTO follow_up_schedules (
                            id, user_email, session_id, template_id, channel, 
                            scheduled_at, status, credits_charged, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7, NOW(), NOW())
                    """, (
                        followup_id, request.user_email, getattr(request, 'session_id', None), 
                        request.template_id, channel_value, scheduled_at, credits_needed
                    ))
                    
                    # Update session follow-up count if session_id provided
                    if getattr(request, 'session_id', None):
                        await conn.execute("""
                            UPDATE sessions SET follow_up_count = follow_up_count + 1 
                            WHERE id = $1
                        """, request.session_id)
            finally:
                await self.db.release_connection(conn)
            
            # Schedule the actual sending
            asyncio.create_task(self._schedule_sending(followup_id, scheduled_at))
            
            return {
                'success': True,
                'message': "Follow-up scheduled successfully",
                'followup_id': followup_id,
                'credits_charged': credits_needed,
                'scheduled_at': scheduled_at
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule follow-up: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to schedule follow-up: {str(e)}")
    
    async def _schedule_sending(self, followup_id: str, scheduled_at: datetime):
        """Schedule the actual sending of follow-up"""
        try:
            # Calculate delay until scheduled time
            now = datetime.now(timezone.utc)
            delay = (scheduled_at - now).total_seconds()
            
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Send the follow-up
            await self._send_followup(followup_id)
            
        except Exception as e:
            logger.error(f"Failed to send scheduled follow-up {followup_id}: {e}")
            await self._mark_followup_failed(followup_id, str(e))
    
    async def _send_followup(self, followup_id: str):
        """Send a follow-up message"""
        try:
            # Get follow-up details
            followup = await self._get_followup_by_id(followup_id)
            if not followup:
                logger.error(f"Follow-up {followup_id} not found")
                return
            
            if followup['status'] != 'pending':
                logger.info(f"Follow-up {followup_id} is not pending (status: {followup['status']})")
                return
            
            # Get template and user details
            template = await self._get_template_by_id(followup['template_id'])
            user = await self._get_user_by_email(followup['user_email'])
            
            if not template or not user:
                await self._mark_followup_failed(followup_id, "Template or user not found")
                return
            
            # Prepare message content
            subject, content = await self._prepare_message_content(template, user, followup)
            
            # Send message based on channel
            success = await self._send_message(
                channel=followup['channel'],
                to=followup['user_email'],
                subject=subject,
                content=content
            )
            
            if success:
                await self._mark_followup_sent(followup_id)
                await self._track_analytics(template.get('id', template.get('template_id')), followup['channel'], 'sent')
            else:
                await self._mark_followup_failed(followup_id, "Failed to send message")
                
        except Exception as e:
            logger.error(f"Failed to send follow-up {followup_id}: {e}")
            await self._mark_followup_failed(followup_id, str(e))
    
    async def _prepare_message_content(self, template: Dict, user: Dict, followup: Dict) -> tuple:
        """Prepare message content with variable substitution"""
        try:
            # Get session details if available
            session_data = {}
            if followup.get('session_id'):
                session = await self._get_session_by_id(followup['session_id'])
                if session:
                    session_data = {
                        'session_date': session['created_at'].strftime('%Y-%m-%d'),
                        'service_type': session.get('service_type', 'Unknown'),
                        'guidance_summary': session.get('guidance', '')[:100] + '...' if len(session.get('guidance', '')) > 100 else session.get('guidance', '')
                    }
            
            # Prepare variables for substitution
            variables = {
                'user_name': user.get('name', user.get('full_name', 'User')),
                'user_email': user['email'],
                **session_data
            }
            
            # Get content based on user's preferred language
            user_language = user.get('preferred_language', 'en')
            
            if user_language == 'ta' and template.get('tamil_content'):
                content = template['tamil_content']
                subject = template.get('tamil_subject', template.get('subject', 'Follow-up'))
            else:
                content = template.get('content', 'Thank you for using JyotiFlow!')
                subject = template.get('subject', 'Follow-up')
            
            # Substitute variables
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                content = content.replace(placeholder, str(var_value))
                subject = subject.replace(placeholder, str(var_value))
            
            return subject, content
            
        except Exception as e:
            logger.error(f"Failed to prepare message content: {e}")
            return template.get('subject', 'Follow-up'), template.get('content', 'Thank you for using JyotiFlow!')
    
    async def _send_message(self, channel: str, to: str, subject: str, content: str) -> bool:
        """Send message through specified channel"""
        try:
            if channel == 'email':
                await send_email(to, subject, content)
            elif channel == 'sms':
                await asyncio.get_event_loop().run_in_executor(None, send_sms, to, content)
            elif channel == 'whatsapp':
                await asyncio.get_event_loop().run_in_executor(None, send_whatsapp, to, content)
            elif channel == 'push':
                logger.warning("Push notifications not fully implemented")
                return False
            else:
                logger.error(f"Unsupported channel: {channel}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send {channel} message: {e}")
            return False
    
    async def _mark_followup_sent(self, followup_id: str):
        """Mark follow-up as sent and update session tracking"""
        conn = await self.db.get_connection()
        try:
            # Get follow-up details to update session tracking
            followup = await self._get_followup_by_id(followup_id)
            
            # Update follow-up schedule
            await conn.execute("""
                UPDATE follow_up_schedules 
                SET status = 'sent', sent_at = NOW(), updated_at = NOW()
                WHERE id = $1
            """, followup_id)
            
            # Update session tracking if session_id exists
            if followup and followup.get('session_id'):
                channel = followup.get('channel', '').lower()
                if channel == 'email':
                    await conn.execute("""
                        UPDATE sessions 
                        SET follow_up_email_sent = TRUE 
                        WHERE id = $1
                    """, followup['session_id'])
                elif channel == 'sms':
                    await conn.execute("""
                        UPDATE sessions 
                        SET follow_up_sms_sent = TRUE 
                        WHERE id = $1
                    """, followup['session_id'])
                elif channel == 'whatsapp':
                    await conn.execute("""
                        UPDATE sessions 
                        SET follow_up_whatsapp_sent = TRUE 
                        WHERE id = $1
                    """, followup['session_id'])
        finally:
            await self.db.release_connection(conn)
    
    async def _mark_followup_failed(self, followup_id: str, reason: str):
        """Mark follow-up as failed"""
        conn = await self.db.get_connection()
        try:
            await conn.execute("""
                UPDATE follow_up_schedules 
                SET status = 'failed', failure_reason = $1, updated_at = NOW()
                WHERE id = $2
            """, reason, followup_id)
        finally:
            await self.db.release_connection(conn)
    
    async def _track_analytics(self, template_id: str, channel: str, event: str):
        """Track follow-up analytics"""
        try:
            today = datetime.now(timezone.utc).date()
            conn = await self.db.get_connection()
            try:
                # PostgreSQL UPSERT
                await conn.execute("""
                    INSERT INTO follow_up_analytics (
                        date, template_id, channel, total_sent, created_at, updated_at
                    ) VALUES ($1, $2, $3, 1, NOW(), NOW())
                    ON CONFLICT (date, template_id, channel) 
                    DO UPDATE SET total_sent = follow_up_analytics.total_sent + 1, updated_at = NOW()
                """, today, template_id, channel)
            finally:
                await self.db.release_connection(conn)
        except Exception as e:
            logger.error(f"Failed to track analytics: {e}")
    
    async def _validate_scheduling_constraints(self, request, template: Dict):
        """Validate scheduling constraints"""
        # Ensure settings are loaded
        await self._ensure_settings_loaded()
        
        # Check max follow-ups per session
        session_id = getattr(request, 'session_id', None)
        if session_id:
            count = await self._get_followup_count_for_session(session_id)
            max_count = self.settings.get('max_followups_per_session', 3)
            if count >= max_count:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Maximum follow-ups ({max_count}) already scheduled for this session"
                )
        
        # Check minimum interval
        scheduled_at = getattr(request, 'scheduled_at', None)
        if scheduled_at:
            min_interval = timedelta(hours=self.settings.get('min_interval_hours', 24))
            last_followup = await self._get_last_followup_for_user(request.user_email)
            if last_followup and (scheduled_at - last_followup['scheduled_at']) < min_interval:
                raise HTTPException(
                    status_code=400,
                    detail=f"Minimum interval of {min_interval} required between follow-ups"
                )
    
    async def _calculate_optimal_time(self, user_email: str, template: Dict) -> datetime:
        """Calculate optimal time for follow-up based on user behavior"""
        try:
            # Get user's last activity time
            user = await self._get_user_by_email(user_email)
            if not user:
                return datetime.now(timezone.utc) + timedelta(days=1)
            
            # Simple logic: schedule for next day at 10 AM user's timezone
            optimal_time = datetime.now(timezone.utc) + timedelta(days=1)
            optimal_time = optimal_time.replace(hour=10, minute=0, second=0, microsecond=0)
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal time: {e}")
            return datetime.now(timezone.utc) + timedelta(days=1)
    
    # Database helper methods - PostgreSQL only
    async def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def _get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get template by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM follow_up_templates WHERE id = $1", template_id)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def _get_followup_by_id(self, followup_id: str) -> Optional[Dict]:
        """Get follow-up by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM follow_up_schedules WHERE id = $1", followup_id)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def _get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM sessions WHERE id = $1", session_id)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def _get_followup_count_for_session(self, session_id: str) -> int:
        """Get follow-up count for a session"""
        conn = await self.db.get_connection()
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM follow_up_schedules WHERE session_id = $1", session_id)
            return count or 0
        finally:
            await self.db.release_connection(conn)
    
    async def _get_last_followup_for_user(self, user_email: str) -> Optional[Dict]:
        """Get last follow-up for user"""
        conn = await self.db.get_connection()
        try:
            row = await conn.fetchrow("""
                SELECT * FROM follow_up_schedules 
                WHERE user_email = $1 
                ORDER BY scheduled_at DESC 
                LIMIT 1
            """, user_email)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def get_user_followups(self, user_email: str) -> List[Dict]:
        """Get all follow-ups for a user"""
        conn = await self.db.get_connection()
        try:
            rows = await conn.fetch("""
                SELECT fs.*, ft.name as template_name, ft.tamil_name as template_tamil_name
                FROM follow_up_schedules fs
                JOIN follow_up_templates ft ON fs.template_id = ft.id
                WHERE fs.user_email = $1
                ORDER BY fs.scheduled_at DESC
            """, user_email)
            return [dict(row) for row in rows]
        finally:
            await self.db.release_connection(conn)
    
    async def cancel_followup(self, followup_id: str, user_email: str) -> bool:
        """Cancel a follow-up"""
        conn = await self.db.get_connection()
        try:
            result = await conn.execute("""
                UPDATE follow_up_schedules 
                SET status = 'cancelled', updated_at = NOW()
                WHERE id = $1 AND user_email = $2 AND status = 'pending'
            """, followup_id, user_email)
            
            # Parse asyncpg command tag to get affected row count
            return self._parse_affected_rows(result) > 0
        finally:
            await self.db.release_connection(conn)
    
    def _parse_affected_rows(self, command_tag: str) -> int:
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