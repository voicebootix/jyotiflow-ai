"""
Follow-up Service for JyotiFlow.ai
Handles sending follow-up messages via different channels with credit-based pricing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json

from ..core_foundation_enhanced import get_db
from ..schemas.content import FollowUpTemplate, FollowUpSchedule
from ..utils.analytics_utils import track_user_engagement
from ..utils.stripe_utils import deduct_user_credits

logger = logging.getLogger(__name__)

class FollowUpService:
    """Service for handling follow-up communications (email, SMS, WhatsApp)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def convert_user_id_to_int(self, user_id):
        """Convert string user_id to integer for database queries"""
        if not user_id:
            return None
        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None

    def send_email_followup(self, session_id: int) -> Dict[str, Any]:
        """Send follow-up email to user after session completion"""
        try:
            # Get session details
            session = self.db.execute(
                "SELECT * FROM sessions WHERE id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            # Check if email follow-up already sent
            if session.follow_up_email_sent:
                return {"success": False, "message": "Email follow-up already sent for this session"}
            
            # Check user credits
            user_id_int = self.convert_user_id_to_int(session.user_id)
            if user_id_int is None:
                return {"success": False, "message": "Invalid user ID"}
            
            user_credits = self.db.execute(
                "SELECT credits FROM users WHERE id = :user_id",
                {"user_id": user_id_int}
            ).fetchone()
            
            if not user_credits or user_credits.credits < 1:
                return {"success": False, "message": "Insufficient credits. Email follow-up costs 1 credit."}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'email' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No active email template found"}
            
            # Prepare email content
            email_content = self._prepare_email_content(template, session)
            
            # Send email (simulate sending)
            # TODO: Integrate with actual email service (SendGrid, SES, etc.)
            print(f"Sending email to {session.user_email}")
            print(f"Subject: {email_content['subject']}")
            print(f"Body: {email_content['body']}")
            
            # Deduct credits
            self.db.execute(
                "UPDATE users SET credits = credits - 1 WHERE id = :user_id",
                {"user_id": user_id_int}
            )
            
            # Mark follow-up as sent
            self.db.execute(
                "UPDATE sessions SET follow_up_email_sent = true, follow_up_email_sent_at = NOW() WHERE id = :session_id",
                {"session_id": session_id}
            )
            
            # Record the follow-up
            self.db.execute("""
                INSERT INTO follow_up_logs (session_id, user_id, channel, template_id, content, cost_credits, status, created_at)
                VALUES (:session_id, :user_id, 'email', :template_id, :content, 1, 'sent', NOW())
            """, {
                "session_id": session_id,
                "user_id": user_id_int,
                "template_id": template.id,
                "content": json.dumps(email_content)
            })
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Email follow-up sent successfully",
                "cost_credits": 1,
                "remaining_credits": user_credits.credits - 1
            }
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Email follow-up failed: {str(e)}"}

    def send_sms_followup(self, session_id: int) -> Dict[str, Any]:
        """Send follow-up SMS to user after session completion"""
        try:
            # Get session details
            session = self.db.execute(
                "SELECT * FROM sessions WHERE id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            # Check if SMS follow-up already sent
            if session.follow_up_sms_sent:
                return {"success": False, "message": "SMS follow-up already sent for this session"}
            
            # Check user credits
            user_id_int = self.convert_user_id_to_int(session.user_id)
            if user_id_int is None:
                return {"success": False, "message": "Invalid user ID"}
            
            user_credits = self.db.execute(
                "SELECT credits FROM users WHERE id = :user_id",
                {"user_id": user_id_int}
            ).fetchone()
            
            if not user_credits or user_credits.credits < 1:
                return {"success": False, "message": "Insufficient credits. SMS follow-up costs 1 credit."}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'sms' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No active SMS template found"}
            
            # Prepare SMS content
            sms_content = self._prepare_sms_content(template, session)
            
            # Send SMS (simulate sending)
            # TODO: Integrate with actual SMS service (Twilio, etc.)
            print(f"Sending SMS to {session.user_phone}")
            print(f"Message: {sms_content['message']}")
            
            # Deduct credits
            self.db.execute(
                "UPDATE users SET credits = credits - 1 WHERE id = :user_id",
                {"user_id": user_id_int}
            )
            
            # Mark follow-up as sent
            self.db.execute(
                "UPDATE sessions SET follow_up_sms_sent = true, follow_up_sms_sent_at = NOW() WHERE id = :session_id",
                {"session_id": session_id}
            )
            
            # Record the follow-up
            self.db.execute("""
                INSERT INTO follow_up_logs (session_id, user_id, channel, template_id, content, cost_credits, status, created_at)
                VALUES (:session_id, :user_id, 'sms', :template_id, :content, 1, 'sent', NOW())
            """, {
                "session_id": session_id,
                "user_id": user_id_int,
                "template_id": template.id,
                "content": json.dumps(sms_content)
            })
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "SMS follow-up sent successfully",
                "cost_credits": 1,
                "remaining_credits": user_credits.credits - 1
            }
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"SMS follow-up failed: {str(e)}"}

    def send_whatsapp_followup(self, session_id: int) -> Dict[str, Any]:
        """Send follow-up WhatsApp message to user after session completion"""
        try:
            # Get session details
            session = self.db.execute(
                "SELECT * FROM sessions WHERE id = :session_id",
                {"session_id": session_id}
            ).fetchone()
            
            if not session:
                return {"success": False, "message": "Session not found"}
            
            # Check if WhatsApp follow-up already sent
            if session.follow_up_whatsapp_sent:
                return {"success": False, "message": "WhatsApp follow-up already sent for this session"}
            
            # Check user credits
            user_id_int = self.convert_user_id_to_int(session.user_id)
            if user_id_int is None:
                return {"success": False, "message": "Invalid user ID"}
            
            user_credits = self.db.execute(
                "SELECT credits FROM users WHERE id = :user_id",
                {"user_id": user_id_int}
            ).fetchone()
            
            if not user_credits or user_credits.credits < 2:
                return {"success": False, "message": "Insufficient credits. WhatsApp follow-up costs 2 credits."}
            
            # Get follow-up template
            template = self.db.execute(
                "SELECT * FROM follow_up_templates WHERE channel = 'whatsapp' AND is_active = true "
                "ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            
            if not template:
                return {"success": False, "message": "No active WhatsApp template found"}
            
            # Prepare WhatsApp content
            whatsapp_content = self._prepare_whatsapp_content(template, session)
            
            # Send WhatsApp message (simulate sending)
            # TODO: Integrate with actual WhatsApp Business API
            print(f"Sending WhatsApp to {session.user_phone}")
            print(f"Message: {whatsapp_content['message']}")
            
            # Deduct credits (WhatsApp costs 2 credits)
            self.db.execute(
                "UPDATE users SET credits = credits - 2 WHERE id = :user_id",
                {"user_id": user_id_int}
            )
            
            # Mark follow-up as sent
            self.db.execute(
                "UPDATE sessions SET follow_up_whatsapp_sent = true, follow_up_whatsapp_sent_at = NOW() WHERE id = :session_id",
                {"session_id": session_id}
            )
            
            # Record the follow-up
            self.db.execute("""
                INSERT INTO follow_up_logs (session_id, user_id, channel, template_id, content, cost_credits, status, created_at)
                VALUES (:session_id, :user_id, 'whatsapp', :template_id, :content, 2, 'sent', NOW())
            """, {
                "session_id": session_id,
                "user_id": user_id_int,
                "template_id": template.id,
                "content": json.dumps(whatsapp_content)
            })
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "WhatsApp follow-up sent successfully",
                "cost_credits": 2,
                "remaining_credits": user_credits.credits - 2
            }
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"WhatsApp follow-up failed: {str(e)}"}
    
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