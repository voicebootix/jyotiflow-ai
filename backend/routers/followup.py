from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import uuid
import json

from schemas.followup import (
    FollowUpRequest, FollowUpResponse, FollowUpTemplate, 
    FollowUpSchedule, FollowUpAnalytics, FollowUpSettings, FollowUpChannel
)
from utils.followup_service import FollowUpService
from deps import get_current_user, get_admin_user
from core_foundation_enhanced import get_database
from database_timezone_fixer import safe_utc_now

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/followup", tags=["Follow-up System"])

# Initialize follow-up service
async def get_followup_service():
    try:
        db = await get_database()
        return FollowUpService(db)
    except Exception as e:
        logger.error(f"Failed to initialize followup service: {e}")
        # Return a fallback service or raise appropriate error
        raise HTTPException(status_code=500, detail="Followup service unavailable")

# =============================================================================
# USER ENDPOINTS
# =============================================================================

@router.post("/schedule", response_model=FollowUpResponse)
async def schedule_followup(
    request: FollowUpRequest,
    current_user: dict = Depends(get_current_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Schedule a follow-up for the current user"""
    try:
        # Ensure user can only schedule for themselves
        if request.user_email != current_user['email']:
            raise HTTPException(status_code=403, detail="Can only schedule follow-ups for yourself")
        
        response = await followup_service.schedule_followup(request)
        return response
        
    except Exception as e:
        logger.error(f"Failed to schedule follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-followups")
async def get_my_followups(
    current_user: dict = Depends(get_admin_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Get all follow-ups for the current user"""
    try:
        followups = await followup_service.get_user_followups(current_user['email'])
        return {
            "success": True,
            "data": followups,
            "count": len(followups)
        }
    except Exception as e:
        logger.error(f"Failed to get user follow-ups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{followup_id}")
async def cancel_my_followup(
    followup_id: str,
    current_user: dict = Depends(get_current_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Cancel a follow-up for the current user"""
    try:
        success = await followup_service.cancel_followup(followup_id, current_user['email'])
        if success:
            return {"success": True, "message": "Follow-up cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Follow-up not found or cannot be cancelled")
    except Exception as e:
        logger.error(f"Failed to cancel follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@router.get("/admin/templates")
async def get_followup_templates(
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Get all follow-up templates (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                rows = await conn.fetch("SELECT * FROM follow_up_templates ORDER BY created_at DESC")
            else:
                rows = await conn.fetch("SELECT * FROM follow_up_templates ORDER BY created_at DESC")
            
            templates = [dict(row) for row in rows]
            return {
                "success": True,
                "data": templates,
                "count": len(templates)
            }
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get follow-up templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/templates")
async def create_followup_template(
    template_data: FollowUpTemplate,
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Create a new follow-up template (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                template_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO follow_up_templates (
                        id, name, tamil_name, description, template_type, channel,
                        subject, content, tamil_content, variables, credits_cost, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_id, template_data.name, template_data.tamil_name,
                    template_data.description, template_data.template_type.value,
                    template_data.channel.value, template_data.subject, template_data.content,
                    template_data.tamil_content, json.dumps(template_data.variables),
                    template_data.credits_cost, template_data.is_active
                ))
            else:
                template_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO follow_up_templates (
                        id, name, tamil_name, description, template_type, channel,
                        subject, content, tamil_content, variables, credits_cost, is_active
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, (
                    template_id, template_data.name, template_data.tamil_name,
                    template_data.description, template_data.template_type.value,
                    template_data.channel.value, template_data.subject, template_data.content,
                    template_data.tamil_content, json.dumps(template_data.variables),
                    template_data.credits_cost, template_data.is_active
                ))
            
            return {
                "success": True,
                "message": "Template created successfully",
                "template_id": template_id
            }
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to create follow-up template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/templates/{template_id}")
async def update_followup_template(
    template_id: str,
    template_data: FollowUpTemplate,
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Update a follow-up template (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                result = await conn.execute("""
                    UPDATE follow_up_templates SET
                        name = ?, tamil_name = ?, description = ?, template_type = ?,
                        channel = ?, subject = ?, content = ?, tamil_content = ?,
                        variables = ?, credits_cost = ?, is_active = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    template_data.name, template_data.tamil_name, template_data.description,
                    template_data.template_type.value, template_data.channel.value,
                    template_data.subject, template_data.content, template_data.tamil_content,
                    json.dumps(template_data.variables), template_data.credits_cost,
                    template_data.is_active, safe_utc_now(), template_id
                ))
            else:
                result = await conn.execute("""
                    UPDATE follow_up_templates SET
                        name = $1, tamil_name = $2, description = $3, template_type = $4,
                        channel = $5, subject = $6, content = $7, tamil_content = $8,
                        variables = $9, credits_cost = $10, is_active = $11, updated_at = NOW()
                    WHERE id = $12
                """, (
                    template_data.name, template_data.tamil_name, template_data.description,
                    template_data.template_type.value, template_data.channel.value,
                    template_data.subject, template_data.content, template_data.tamil_content,
                    json.dumps(template_data.variables), template_data.credits_cost,
                    template_data.is_active, template_id
                ))
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Template not found")
            
            return {"success": True, "message": "Template updated successfully"}
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to update follow-up template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/templates/{template_id}")
async def delete_followup_template(
    template_id: str,
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Delete a follow-up template (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                result = await conn.execute("DELETE FROM follow_up_templates WHERE id = ?", (template_id,))
            else:
                result = await conn.execute("DELETE FROM follow_up_templates WHERE id = $1", template_id)
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Template not found")
            
            return {"success": True, "message": "Template deleted successfully"}
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to delete follow-up template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/schedules")
async def get_all_followup_schedules(
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database),
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all follow-up schedules (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            query = """
                SELECT fs.*, ft.name as template_name, ft.tamil_name as template_tamil_name,
                       u.name as user_name
                FROM follow_up_schedules fs
                JOIN follow_up_templates ft ON fs.template_id = ft.id
                LEFT JOIN users u ON fs.user_email = u.email
            """
            params = []
            
            if status:
                if db.is_sqlite:
                    query += " WHERE fs.status = ?"
                    params.append(status)
                else:
                    query += " WHERE fs.status = $1"
                    params.append(status)
            
            query += " ORDER BY fs.scheduled_at DESC"
            
            if db.is_sqlite:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            else:
                query += " LIMIT $2 OFFSET $3"
                params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)
            schedules = [dict(row) for row in rows]
            
            return {
                "success": True,
                "data": schedules,
                "count": len(schedules)
            }
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get follow-up schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/analytics")
async def get_followup_analytics(
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get follow-up analytics (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            # Build date filter
            date_filter = ""
            params = []
            if start_date and end_date:
                if db.is_sqlite:
                    date_filter = " WHERE date BETWEEN ? AND ?"
                    params = [start_date, end_date]
                else:
                    date_filter = " WHERE date BETWEEN $1 AND $2"
                    params = [start_date, end_date]
            
            # Get analytics data
            if db.is_sqlite:
                rows = await conn.fetch(f"""
                    SELECT 
                        SUM(total_sent) as total_sent,
                        SUM(total_delivered) as total_delivered,
                        SUM(total_read) as total_read,
                        SUM(total_failed) as total_failed,
                        SUM(credits_charged) as total_credits_charged,
                        SUM(revenue_generated) as total_revenue
                    FROM follow_up_analytics
                    {date_filter}
                """, *params)
            else:
                rows = await conn.fetch(f"""
                    SELECT 
                        SUM(total_sent) as total_sent,
                        SUM(total_delivered) as total_delivered,
                        SUM(total_read) as total_read,
                        SUM(total_failed) as total_failed,
                        SUM(credits_charged) as total_credits_charged,
                        SUM(revenue_generated) as total_revenue
                    FROM follow_up_analytics
                    {date_filter}
                """, *params)
            
            analytics = dict(rows[0]) if rows else {
                'total_sent': 0, 'total_delivered': 0, 'total_read': 0,
                'total_failed': 0, 'total_credits_charged': 0, 'total_revenue': 0
            }
            
            # Calculate rates
            total_sent = analytics['total_sent'] or 0
            analytics['delivery_rate'] = (analytics['total_delivered'] or 0) / total_sent * 100 if total_sent > 0 else 0
            analytics['read_rate'] = (analytics['total_read'] or 0) / total_sent * 100 if total_sent > 0 else 0
            
            # Get top templates
            if db.is_sqlite:
                top_templates = await conn.fetch(f"""
                    SELECT ft.name, ft.tamil_name, SUM(fa.total_sent) as total_sent
                    FROM follow_up_analytics fa
                    JOIN follow_up_templates ft ON fa.template_id = ft.id
                    {date_filter.replace('date', 'fa.date')}
                    GROUP BY ft.id, ft.name, ft.tamil_name
                    ORDER BY total_sent DESC
                    LIMIT 5
                """, *params)
            else:
                top_templates = await conn.fetch(f"""
                    SELECT ft.name, ft.tamil_name, SUM(fa.total_sent) as total_sent
                    FROM follow_up_analytics fa
                    JOIN follow_up_templates ft ON fa.template_id = ft.id
                    {date_filter.replace('date', 'fa.date')}
                    GROUP BY ft.id, ft.name, ft.tamil_name
                    ORDER BY total_sent DESC
                    LIMIT 5
                """, *params)
            
            analytics['top_templates'] = [dict(row) for row in top_templates]
            
            return {
                "success": True,
                "data": analytics
            }
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get follow-up analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/settings")
async def get_followup_settings(
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Get follow-up system settings (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                rows = await conn.fetch("SELECT * FROM follow_up_settings WHERE is_active = TRUE")
            else:
                rows = await conn.fetch("SELECT * FROM follow_up_settings WHERE is_active = TRUE")
            
            settings = {}
            for row in rows:
                key = row['setting_key']
                value = row['setting_value']
                value_type = row['setting_type']
                
                if value_type == 'boolean':
                    settings[key] = value.lower() == 'true'
                elif value_type == 'integer':
                    settings[key] = int(value)
                else:
                    settings[key] = value
            
            return {
                "success": True,
                "data": settings
            }
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to get follow-up settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/settings")
async def update_followup_settings(
    settings: FollowUpSettings,
    admin_user: dict = Depends(get_admin_user),
    db = Depends(get_database)
):
    """Update follow-up system settings (admin only)"""
    try:
        conn = await db.get_connection()
        try:
            settings_dict = settings.dict()
            
            for key, value in settings_dict.items():
                if db.is_sqlite:
                    await conn.execute("""
                        UPDATE follow_up_settings 
                        SET setting_value = ?, updated_at = ?
                        WHERE setting_key = ?
                    """, (str(value), safe_utc_now(), key))
                else:
                    await conn.execute("""
                        UPDATE follow_up_settings 
                        SET setting_value = $1, updated_at = NOW()
                        WHERE setting_key = $2
                    """, str(value), key)
            
            return {"success": True, "message": "Settings updated successfully"}
        finally:
            await db.release_connection(conn)
    except Exception as e:
        logger.error(f"Failed to update follow-up settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# AUTOMATIC FOLLOW-UP ENDPOINTS
# =============================================================================

@router.post("/auto/session-complete")
async def auto_schedule_session_followup(
    session_id: str = Body(...),
    user_email: str = Body(...),
    service_type: str = Body(...),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Automatically schedule follow-up after session completion"""
    try:
        # Get default session follow-up template
        db = await get_database()
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                template = await conn.fetchrow("""
                    SELECT id FROM follow_up_templates 
                    WHERE template_type = 'session_followup' AND is_active = TRUE 
                    ORDER BY created_at ASC LIMIT 1
                """)
            else:
                template = await conn.fetchrow("""
                    SELECT id FROM follow_up_templates 
                    WHERE template_type = 'session_followup' AND is_active = TRUE 
                    ORDER BY created_at ASC LIMIT 1
                """)
        finally:
            await db.release_connection(conn)
        
        if not template:
            logger.warning("No session follow-up template found")
            return {"success": False, "message": "No follow-up template available"}
        
        # Schedule follow-up
        request = FollowUpRequest(
            user_email=user_email,
            session_id=session_id,
            template_id=template['id'],
            channel=FollowUpChannel.EMAIL
        )
        
        response = await followup_service.schedule_followup(request)
        return response
        
    except Exception as e:
        logger.error(f"Failed to auto-schedule session follow-up: {e}")
        return {"success": False, "message": str(e)}

# =============================================================================
# DIRECT FOLLOW-UP ENDPOINTS
# =============================================================================

@router.post("/email/{session_id}")
async def send_email_followup_endpoint(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Send email follow-up for a session - FREE"""
    try:
        # Verify user owns the session
        db = await get_database()
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = ?
                """, session_id)
            else:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = $1
                """, session_id)
        finally:
            await db.release_connection(conn)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = await followup_service.send_email_followup(session_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sms/{session_id}")
async def send_sms_followup_endpoint(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Send SMS follow-up for a session - 1 CREDIT"""
    try:
        # Verify user owns the session
        db = await get_database()
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = ?
                """, session_id)
            else:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = $1
                """, session_id)
        finally:
            await db.release_connection(conn)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = await followup_service.send_sms_followup(session_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send SMS follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp/{session_id}")
async def send_whatsapp_followup_endpoint(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Send WhatsApp follow-up for a session - 2 CREDITS"""
    try:
        # Verify user owns the session
        db = await get_database()
        conn = await db.get_connection()
        try:
            if db.is_sqlite:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = ?
                """, session_id)
            else:
                session = await conn.fetchrow("""
                    SELECT user_id FROM sessions WHERE id = $1
                """, session_id)
        finally:
            await db.release_connection(conn)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = await followup_service.send_whatsapp_followup(session_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send WhatsApp follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/health")
async def followup_health_check(
    followup_service: FollowUpService = Depends(get_followup_service)
):
    """Health check for follow-up system"""
    try:
        # Check if settings are loaded
        if not followup_service.settings:
            return {"status": "unhealthy", "message": "Settings not loaded"}
        
        return {
            "status": "healthy",
            "message": "Follow-up system is operational",
            "settings_loaded": len(followup_service.settings) > 0
        }
    except Exception as e:
        logger.error(f"Follow-up health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)} 