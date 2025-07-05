"""
Follow-up Service for JyotiFlow.ai
Handles sending follow-up messages via different channels with credit-based pricing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..core_foundation_enhanced import get_db
from ..schemas.content import FollowUpTemplate, FollowUpSchedule
from ..utils.analytics_utils import track_user_engagement
from ..utils.stripe_utils import deduct_user_credits

logger = logging.getLogger(__name__)

class FollowUpService:
    """Service for managing follow-up communications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_email_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send email follow-up - FREE
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            # Get session details
            session = self.db.execute(
                "SELECT s.*, u.email, u.name FROM sessions s "
                "JOIN users u ON s.user_id = u.id "
                "WHERE s.id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            # Check if email follow-up already sent
            if session.follow_up_email_sent:
                return {"success": False, "message": "Email follow-up already sent for this session"}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'email' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No email template found"}
            
            # Prepare email content
            email_content = self._prepare_email_content(template, session)
            
            # Send email (using existing notification system)
            from ..utils.analytics_utils import send_notification
            email_result = send_notification(
                channel="email",
                to=session.email,
                subject=email_content["subject"],
                message=email_content["body"]
            )
            
            if email_result.get("success"):
                # Mark email as sent
                self.db.execute(
                    "UPDATE sessions SET follow_up_email_sent = true, "
                    "follow_up_count = follow_up_count + 1, "
                    "updated_at = :now WHERE id = :session_id",
                    {"now": datetime.utcnow(), "session_id": session_id}
                )
                
                # Track analytics
                track_user_engagement(
                    user_id=session.user_id,
                    event_type="followup_email_sent",
                    session_id=session_id,
                    metadata={"template_id": template.id}
                )
                
                self.db.commit()
                logger.info(f"Email follow-up sent successfully for session {session_id}")
                
                return {
                    "success": True,
                    "message": "Email follow-up sent successfully",
                    "credits_charged": 0,
                    "channel": "email"
                }
            else:
                return {"success": False, "message": "Failed to send email follow-up"}
                
        except Exception as e:
            logger.error(f"Error sending email follow-up for session {session_id}: {str(e)}")
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def send_sms_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send SMS follow-up - 1 CREDIT
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            # Get session details
            session = self.db.execute(
                "SELECT s.*, u.phone, u.name FROM sessions s "
                "JOIN users u ON s.user_id = u.id "
                "WHERE s.id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            if not session.phone:
                return {"success": False, "message": "User phone number not available"}
            
            # Check if SMS follow-up already sent
            if session.follow_up_sms_sent:
                return {"success": False, "message": "SMS follow-up already sent for this session"}
            
            # Check user credits
            user_credits = self.db.execute(
                "SELECT credits FROM users WHERE id = :user_id",
                {"user_id": session.user_id}
            ).fetchone()
            
            if not user_credits or user_credits.credits < 1:
                return {"success": False, "message": "Insufficient credits. SMS follow-up costs 1 credit."}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'sms' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No SMS template found"}
            
            # Prepare SMS content
            sms_content = self._prepare_sms_content(template, session)
            
            # Send SMS (using existing notification system)
            from ..utils.analytics_utils import send_notification
            sms_result = send_notification(
                channel="sms",
                to=session.phone,
                message=sms_content["body"]
            )
            
            if sms_result.get("success"):
                # Deduct credits
                deduct_result = deduct_user_credits(session.user_id, 1, "SMS follow-up")
                
                if not deduct_result.get("success"):
                    return {"success": False, "message": "Failed to deduct credits"}
                
                # Mark SMS as sent
                self.db.execute(
                    "UPDATE sessions SET follow_up_sms_sent = true, "
                    "follow_up_count = follow_up_count + 1, "
                    "updated_at = :now WHERE id = :session_id",
                    {"now": datetime.utcnow(), "session_id": session_id}
                )
                
                # Track analytics
                track_user_engagement(
                    user_id=session.user_id,
                    event_type="followup_sms_sent",
                    session_id=session_id,
                    metadata={"template_id": template.id, "credits_charged": 1}
                )
                
                self.db.commit()
                logger.info(f"SMS follow-up sent successfully for session {session_id}")
                
                return {
                    "success": True,
                    "message": "SMS follow-up sent successfully",
                    "credits_charged": 1,
                    "channel": "sms"
                }
            else:
                return {"success": False, "message": "Failed to send SMS follow-up"}
                
        except Exception as e:
            logger.error(f"Error sending SMS follow-up for session {session_id}: {str(e)}")
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def send_whatsapp_followup(self, session_id: int) -> Dict[str, Any]:
        """
        Send WhatsApp follow-up - 2 CREDITS
        
        Args:
            session_id: ID of the session to send follow-up for
            
        Returns:
            Dict with success status and message
        """
        try:
            # Get session details
            session = self.db.execute(
                "SELECT s.*, u.phone, u.name FROM sessions s "
                "JOIN users u ON s.user_id = u.id "
                "WHERE s.id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            if not session.phone:
                return {"success": False, "message": "User phone number not available"}
            
            # Check if WhatsApp follow-up already sent
            if session.follow_up_whatsapp_sent:
                return {"success": False, "message": "WhatsApp follow-up already sent for this session"}
            
            # Check user credits
            user_credits = self.db.execute(
                "SELECT credits FROM users WHERE id = :user_id",
                {"user_id": session.user_id}
            ).fetchone()
            
            if not user_credits or user_credits.credits < 2:
                return {"success": False, "message": "Insufficient credits. WhatsApp follow-up costs 2 credits."}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'whatsapp' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No WhatsApp template found"}
            
            # Prepare WhatsApp content
            whatsapp_content = self._prepare_whatsapp_content(template, session)
            
            # Send WhatsApp (using existing notification system)
            from ..utils.analytics_utils import send_notification
            whatsapp_result = send_notification(
                channel="whatsapp",
                to=session.phone,
                message=whatsapp_content["body"]
            )
            
            if whatsapp_result.get("success"):
                # Deduct credits
                deduct_result = deduct_user_credits(session.user_id, 2, "WhatsApp follow-up")
                
                if not deduct_result.get("success"):
                    return {"success": False, "message": "Failed to deduct credits"}
                
                # Mark WhatsApp as sent
                self.db.execute(
                    "UPDATE sessions SET follow_up_whatsapp_sent = true, "
                    "follow_up_count = follow_up_count + 1, "
                    "updated_at = :now WHERE id = :session_id",
                    {"now": datetime.utcnow(), "session_id": session_id}
                )
                
                # Track analytics
                track_user_engagement(
                    user_id=session.user_id,
                    event_type="followup_whatsapp_sent",
                    session_id=session_id,
                    metadata={"template_id": template.id, "credits_charged": 2}
                )
                
                self.db.commit()
                logger.info(f"WhatsApp follow-up sent successfully for session {session_id}")
                
                return {
                    "success": True,
                    "message": "WhatsApp follow-up sent successfully",
                    "credits_charged": 2,
                    "channel": "whatsapp"
                }
            else:
                return {"success": False, "message": "Failed to send WhatsApp follow-up"}
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp follow-up for session {session_id}: {str(e)}")
            self.db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _prepare_email_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare email content with session-specific data"""
        subject = template.subject.replace("{user_name}", session.name or "Dear User")
        body = template.content.replace("{user_name}", session.name or "Dear User")
        body = body.replace("{session_date}", session.created_at.strftime("%B %d, %Y"))
        body = body.replace("{session_type}", session.session_type or "Spiritual Guidance")
        
        return {
            "subject": subject,
            "body": body
        }
    
    def _prepare_sms_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare SMS content with session-specific data"""
        body = template.content.replace("{user_name}", session.name or "User")
        body = body.replace("{session_date}", session.created_at.strftime("%B %d"))
        body = body.replace("{session_type}", session.session_type or "Guidance")
        
        return {
            "body": body
        }
    
    def _prepare_whatsapp_content(self, template: Any, session: Any) -> Dict[str, str]:
        """Prepare WhatsApp content with session-specific data"""
        body = template.content.replace("{user_name}", session.name or "Dear User")
        body = body.replace("{session_date}", session.created_at.strftime("%B %d, %Y"))
        body = body.replace("{session_type}", session.session_type or "Spiritual Guidance")
        
        return {
            "body": body
        }
    
    def get_followup_status(self, session_id: int) -> Dict[str, Any]:
        """Get follow-up status for a session"""
        try:
            session = self.db.execute(
                "SELECT follow_up_email_sent, follow_up_sms_sent, follow_up_whatsapp_sent, "
                "follow_up_count FROM sessions WHERE id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            return {
                "success": True,
                "email_sent": session.follow_up_email_sent,
                "sms_sent": session.follow_up_sms_sent,
                "whatsapp_sent": session.follow_up_whatsapp_sent,
                "total_followups": session.follow_up_count
            }
            
        except Exception as e:
            logger.error(f"Error getting follow-up status for session {session_id}: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}


# Convenience functions for easy access
def send_email_followup(session_id: int) -> Dict[str, Any]:
    """Send email follow-up - FREE"""
    db = next(get_db())
    service = FollowUpService(db)
    return service.send_email_followup(session_id)

def send_sms_followup(session_id: int) -> Dict[str, Any]:
    """Send SMS follow-up - 1 CREDIT"""
    db = next(get_db())
    service = FollowUpService(db)
    return service.send_sms_followup(session_id)

def send_whatsapp_followup(session_id: int) -> Dict[str, Any]:
    """Send WhatsApp follow-up - 2 CREDITS"""
    db = next(get_db())
    service = FollowUpService(db)
    return service.send_whatsapp_followup(session_id) 