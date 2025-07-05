"""
Follow-up Service for JyotiFlow.ai
Handles sending follow-up messages via different channels with credit-based pricing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio

from ..core_foundation_enhanced import get_database
from ..utils.analytics_utils import track_user_engagement, send_notification

logger = logging.getLogger(__name__)

class FollowUpService:
    """Service for managing follow-up communications"""
    
    def __init__(self, db=None):
        self.db = db
        self.settings = {}
    
    async def send_email_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send email follow-up - FREE
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            if not self.db:
                self.db = await get_database()
            
            conn = await self.db.get_connection()
            try:
                # Get session details
                if self.db.is_sqlite:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.email, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = ?
                    """, session_id)
                else:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.email, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = $1
                    """, session_id)
                
                if not session:
                    return {"success": False, "message": "Session not found"}
                
                # Check if email follow-up already sent
                if session['follow_up_email_sent']:
                    return {"success": False, "message": "Email follow-up already sent for this session"}
                
                # Get follow-up template
                if self.db.is_sqlite:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'email' AND is_active = 1 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                else:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'email' AND is_active = true 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                
                if not template:
                    return {"success": False, "message": "No email template found"}
                
                # Prepare email content
                email_content = self._prepare_email_content(template, session)
                
                # Send email
                email_result = await send_notification(
                    channel="email",
                    to=session['email'],
                    subject=email_content["subject"],
                    message=email_content["body"]
                )
                
                if email_result.get("success"):
                    # Mark email as sent
                    if self.db.is_sqlite:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_email_sent = 1, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = ? WHERE id = ?
                        """, datetime.utcnow(), session_id)
                    else:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_email_sent = true, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = NOW() WHERE id = $1
                        """, session_id)
                    
                    # Track analytics
                    await track_user_engagement(
                        user_id=session['user_id'],
                        event_type="followup_email_sent",
                        session_id=session_id,
                        metadata={"template_id": template['id']}
                    )
                    
                    logger.info(f"Email follow-up sent successfully for session {session_id}")
                    
                    return {
                        "success": True,
                        "message": "Email follow-up sent successfully",
                        "credits_charged": 0,
                        "channel": "email"
                    }
                else:
                    return {"success": False, "message": "Failed to send email follow-up"}
                    
            finally:
                await self.db.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Error sending email follow-up for session {session_id}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def send_sms_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send SMS follow-up - 1 CREDIT (Automatic deduction)
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            if not self.db:
                self.db = await get_database()
            
            conn = await self.db.get_connection()
            try:
                # Get session details
                if self.db.is_sqlite:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.phone, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = ?
                    """, session_id)
                else:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.phone, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = $1
                    """, session_id)
                
                if not session:
                    return {"success": False, "message": "Session not found"}
                
                if not session['phone']:
                    return {"success": False, "message": "User phone number not available"}
                
                # Check if SMS follow-up already sent
                if session['follow_up_sms_sent']:
                    return {"success": False, "message": "SMS follow-up already sent for this session"}
                
                # Check user credits
                if self.db.is_sqlite:
                    user_credits = await conn.fetchrow("""
                        SELECT credits FROM users WHERE id = ?
                    """, session['user_id'])
                else:
                    user_credits = await conn.fetchrow("""
                        SELECT credits FROM users WHERE id = $1
                    """, session['user_id'])
                
                if not user_credits or user_credits['credits'] < 1:
                    return {"success": False, "message": "Insufficient credits. SMS follow-up costs 1 credit."}
                
                # Get follow-up template
                if self.db.is_sqlite:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'sms' AND is_active = 1 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                else:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'sms' AND is_active = true 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                
                if not template:
                    return {"success": False, "message": "No SMS template found"}
                
                # Prepare SMS content
                sms_content = self._prepare_sms_content(template, session)
                
                # Send SMS
                sms_result = await send_notification(
                    channel="sms",
                    to=session['phone'],
                    message=sms_content["body"]
                )
                
                if sms_result.get("success"):
                    # AUTOMATIC CREDIT DEDUCTION
                    try:
                        if self.db.is_sqlite:
                            # Direct credit deduction for SQLite
                            result = await conn.execute("""
                                UPDATE users SET credits = credits - ? 
                                WHERE id = ? AND credits >= ?
                            """, (1, session['user_id'], 1))
                            
                            if result.rowcount == 0:
                                return {"success": False, "message": "Failed to deduct credits - insufficient balance"}
                        else:
                            # Direct credit deduction for PostgreSQL
                            result = await conn.execute("""
                                UPDATE users SET credits = credits - $1 
                                WHERE id = $2 AND credits >= $1
                            """, (1, session['user_id']))
                            
                            if result.rowcount == 0:
                                return {"success": False, "message": "Failed to deduct credits - insufficient balance"}
                        
                        # Log credit deduction
                        logger.info(f"Credits deducted: 1 credit from user {session['user_id']} for SMS follow-up")
                        
                    except Exception as credit_error:
                        logger.error(f"Credit deduction failed: {credit_error}")
                        return {"success": False, "message": "Failed to deduct credits"}
                    
                    # Mark SMS as sent
                    if self.db.is_sqlite:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_sms_sent = 1, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = ? WHERE id = ?
                        """, datetime.utcnow(), session_id)
                    else:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_sms_sent = true, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = NOW() WHERE id = $1
                        """, session_id)
                    
                    # Track analytics
                    await track_user_engagement(
                        user_id=session['user_id'],
                        event_type="followup_sms_sent",
                        session_id=session_id,
                        metadata={"template_id": template['id'], "credits_charged": 1}
                    )
                    
                    logger.info(f"SMS follow-up sent successfully for session {session_id}")
                    
                    return {
                        "success": True,
                        "message": "SMS follow-up sent successfully",
                        "credits_charged": 1,
                        "channel": "sms"
                    }
                else:
                    return {"success": False, "message": "Failed to send SMS follow-up"}
                    
            finally:
                await self.db.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Error sending SMS follow-up for session {session_id}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def send_whatsapp_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send WhatsApp follow-up - 2 CREDITS (Automatic deduction)
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            if not self.db:
                self.db = await get_database()
            
            conn = await self.db.get_connection()
            try:
                # Get session details
                if self.db.is_sqlite:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.phone, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = ?
                    """, session_id)
                else:
                    session = await conn.fetchrow("""
                        SELECT s.*, u.phone, u.name, u.id as user_id 
                        FROM sessions s 
                        JOIN users u ON s.user_id = u.id 
                        WHERE s.id = $1
                    """, session_id)
                
                if not session:
                    return {"success": False, "message": "Session not found"}
                
                if not session['phone']:
                    return {"success": False, "message": "User phone number not available"}
                
                # Check if WhatsApp follow-up already sent
                if session['follow_up_whatsapp_sent']:
                    return {"success": False, "message": "WhatsApp follow-up already sent for this session"}
                
                # Check user credits
                if self.db.is_sqlite:
                    user_credits = await conn.fetchrow("""
                        SELECT credits FROM users WHERE id = ?
                    """, session['user_id'])
                else:
                    user_credits = await conn.fetchrow("""
                        SELECT credits FROM users WHERE id = $1
                    """, session['user_id'])
                
                if not user_credits or user_credits['credits'] < 2:
                    return {"success": False, "message": "Insufficient credits. WhatsApp follow-up costs 2 credits."}
                
                # Get follow-up template
                if self.db.is_sqlite:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'whatsapp' AND is_active = 1 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                else:
                    template = await conn.fetchrow("""
                        SELECT * FROM follow_up_templates 
                        WHERE channel = 'whatsapp' AND is_active = true 
                        ORDER BY created_at DESC LIMIT 1
                    """)
                
                if not template:
                    return {"success": False, "message": "No WhatsApp template found"}
                
                # Prepare WhatsApp content
                whatsapp_content = self._prepare_whatsapp_content(template, session)
                
                # Send WhatsApp
                whatsapp_result = await send_notification(
                    channel="whatsapp",
                    to=session['phone'],
                    message=whatsapp_content["body"]
                )
                
                if whatsapp_result.get("success"):
                    # AUTOMATIC CREDIT DEDUCTION
                    try:
                        if self.db.is_sqlite:
                            # Direct credit deduction for SQLite
                            result = await conn.execute("""
                                UPDATE users SET credits = credits - ? 
                                WHERE id = ? AND credits >= ?
                            """, (2, session['user_id'], 2))
                            
                            if result.rowcount == 0:
                                return {"success": False, "message": "Failed to deduct credits - insufficient balance"}
                        else:
                            # Direct credit deduction for PostgreSQL
                            result = await conn.execute("""
                                UPDATE users SET credits = credits - $1 
                                WHERE id = $2 AND credits >= $1
                            """, (2, session['user_id']))
                            
                            if result.rowcount == 0:
                                return {"success": False, "message": "Failed to deduct credits - insufficient balance"}
                        
                        # Log credit deduction
                        logger.info(f"Credits deducted: 2 credits from user {session['user_id']} for WhatsApp follow-up")
                        
                    except Exception as credit_error:
                        logger.error(f"Credit deduction failed: {credit_error}")
                        return {"success": False, "message": "Failed to deduct credits"}
                    
                    # Mark WhatsApp as sent
                    if self.db.is_sqlite:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_whatsapp_sent = 1, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = ? WHERE id = ?
                        """, datetime.utcnow(), session_id)
                    else:
                        await conn.execute("""
                            UPDATE sessions SET follow_up_whatsapp_sent = true, 
                            follow_up_count = follow_up_count + 1, 
                            updated_at = NOW() WHERE id = $1
                        """, session_id)
                    
                    # Track analytics
                    await track_user_engagement(
                        user_id=session['user_id'],
                        event_type="followup_whatsapp_sent",
                        session_id=session_id,
                        metadata={"template_id": template['id'], "credits_charged": 2}
                    )
                    
                    logger.info(f"WhatsApp follow-up sent successfully for session {session_id}")
                    
                    return {
                        "success": True,
                        "message": "WhatsApp follow-up sent successfully",
                        "credits_charged": 2,
                        "channel": "whatsapp"
                    }
                else:
                    return {"success": False, "message": "Failed to send WhatsApp follow-up"}
                    
            finally:
                await self.db.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp follow-up for session {session_id}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _prepare_email_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare email content with session-specific data"""
        subject = template['subject'].replace("{user_name}", session['name'] or "Dear User")
        body = template['content'].replace("{user_name}", session['name'] or "Dear User")
        body = body.replace("{session_date}", session['created_at'].strftime("%B %d, %Y"))
        body = body.replace("{session_type}", session.get('session_type', 'Spiritual Guidance'))
        
        return {
            "subject": subject,
            "body": body
        }
    
    def _prepare_sms_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare SMS content with session-specific data"""
        body = template['content'].replace("{user_name}", session['name'] or "User")
        body = body.replace("{session_date}", session['created_at'].strftime("%B %d"))
        body = body.replace("{session_type}", session.get('session_type', 'Guidance'))
        
        return {
            "body": body
        }
    
    def _prepare_whatsapp_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare WhatsApp content with session-specific data"""
        body = template['content'].replace("{user_name}", session['name'] or "Dear User")
        body = body.replace("{session_date}", session['created_at'].strftime("%B %d, %Y"))
        body = body.replace("{session_type}", session.get('session_type', 'Spiritual Guidance'))
        
        return {
            "body": body
        }
    
    async def get_followup_status(self, session_id: int) -> Dict[str, Any]:
        """Get follow-up status for a session"""
        try:
            if not self.db:
                self.db = await get_database()
            
            conn = await self.db.get_connection()
            try:
                if self.db.is_sqlite:
                    session = await conn.fetchrow("""
                        SELECT follow_up_email_sent, follow_up_sms_sent, follow_up_whatsapp_sent, 
                        follow_up_count FROM sessions WHERE id = ?
                    """, session_id)
                else:
                    session = await conn.fetchrow("""
                        SELECT follow_up_email_sent, follow_up_sms_sent, follow_up_whatsapp_sent, 
                        follow_up_count FROM sessions WHERE id = $1
                    """, session_id)
                
                if not session:
                    return {"success": False, "message": "Session not found"}
                
                return {
                    "success": True,
                    "email_sent": session['follow_up_email_sent'],
                    "sms_sent": session['follow_up_sms_sent'],
                    "whatsapp_sent": session['follow_up_whatsapp_sent'],
                    "total_followups": session['follow_up_count']
                }
                
            finally:
                await self.db.release_connection(conn)
                
        except Exception as e:
            logger.error(f"Error getting follow-up status for session {session_id}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}


# Convenience functions for easy access
async def send_email_followup(session_id: int) -> Dict[str, Any]:
    """Send email follow-up - FREE"""
    service = FollowUpService()
    return await service.send_email_followup(session_id)

async def send_sms_followup(session_id: int) -> Dict[str, Any]:
    """Send SMS follow-up - 1 CREDIT (Automatic deduction)"""
    service = FollowUpService()
    return await service.send_sms_followup(session_id)

async def send_whatsapp_followup(session_id: int) -> Dict[str, Any]:
    """Send WhatsApp follow-up - 2 CREDITS (Automatic deduction)"""
    service = FollowUpService()
    return await service.send_whatsapp_followup(session_id) 