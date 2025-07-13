from fastapi import APIRouter, Depends
from db import get_db

router = APIRouter(prefix="/api/admin", tags=["Admin Overview"])

@router.get("/overview")
async def get_admin_overview(db=Depends(get_db)):
    """Get admin dashboard overview - redirects to analytics overview"""
    try:
        # Get basic stats
        total_users = await db.fetchval("SELECT COUNT(*) FROM users")
        active_users = await db.fetchval("SELECT COUNT(*) FROM users WHERE last_login_at >= NOW() - INTERVAL '7 days'")
        total_revenue = await db.fetchval("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='completed'")
        monthly_revenue = await db.fetchval("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='completed' AND created_at >= NOW() - INTERVAL '30 days'")
        total_sessions = await db.fetchval("SELECT COUNT(*) FROM sessions")
        total_donations = await db.fetchval("SELECT COALESCE(SUM(amount), 0) FROM donation_transactions WHERE status='completed'")
        
        # Get recent activity
        recent_users = await db.fetch("""
            SELECT email, full_name, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        recent_sessions = await db.fetch("""
            SELECT session_id, user_email, service_type, start_time 
            FROM sessions 
            ORDER BY start_time DESC 
            LIMIT 5
        """)
        
        recent_payments = await db.fetch("""
            SELECT user_email, amount, created_at 
            FROM payments 
            WHERE status = 'completed'
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        return {
            "success": True,
            "data": {
                "statistics": {
                    "total_users": total_users or 0,
                    "active_users": active_users or 0,
                    "total_revenue": float(total_revenue or 0),
                    "monthly_revenue": float(monthly_revenue or 0),
                    "total_sessions": total_sessions or 0,
                    "total_donations": float(total_donations or 0)
                },
                "recent_activity": {
                    "recent_users": [dict(user) for user in recent_users],
                    "recent_sessions": [dict(session) for session in recent_sessions],
                    "recent_payments": [dict(payment) for payment in recent_payments]
                }
            }
        }
        
    except Exception as e:
        print(f"Admin overview error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "statistics": {
                    "total_users": 0,
                    "active_users": 0,
                    "total_revenue": 0,
                    "monthly_revenue": 0,
                    "total_sessions": 0,
                    "total_donations": 0
                },
                "recent_activity": {
                    "recent_users": [],
                    "recent_sessions": [],
                    "recent_payments": []
                }
            }
        }