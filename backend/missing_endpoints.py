#!/usr/bin/env python3
"""
Missing API Endpoints for JyotiFlow
Implements the missing endpoints that were causing 404 errors
"""

from fastapi import APIRouter, Request, Depends
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
from backend.deps import get_db

logger = logging.getLogger(__name__)

# Create routers for missing endpoints
ai_router = APIRouter(prefix="/api/ai", tags=["ai"])
user_router = APIRouter(prefix="/api/user", tags=["user"])
sessions_router = APIRouter(prefix="/api/sessions", tags=["sessions"])
community_router = APIRouter(prefix="/api/community", tags=["community"])

def get_user_email_from_token(request: Request) -> Optional[str]:
    """Extract user email from JWT token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        # Import here to avoid circular imports
        from backend.core_foundation_enhanced import EnhancedSecurityManager
        user_data = EnhancedSecurityManager.verify_access_token(token)
        return user_data.get("email")
    except Exception as e:
        logger.error(f"Error extracting user email: {e}")
        return None

@ai_router.get("/user-recommendations")
async def get_user_recommendations(request: Request, db=Depends(get_db)):
    """
    Get AI-powered recommendations for the user
    Previously missing endpoint causing 404 errors
    """
    try:
        user_email = get_user_email_from_token(request)
        if not user_email:
            return {"success": False, "message": "Authentication required", "data": []}
        
        # Get user's recent sessions to provide personalized recommendations
        recent_sessions = await db.fetch("""
            SELECT service_type, question, created_at 
            FROM sessions 
            WHERE user_email = $1 
            ORDER BY created_at DESC 
            LIMIT 5
        """, user_email)
        
        # Get user's credit balance
        user_credits = await db.fetchval("""
            SELECT credits FROM users WHERE email = $1
        """, user_email)
        
        # Generate AI recommendations based on user history
        recommendations = []
        
        if recent_sessions:
            # Analyze user's most used service types
            service_usage = {}
            for session in recent_sessions:
                service_type = session['service_type']
                service_usage[service_type] = service_usage.get(service_type, 0) + 1
            
            # Get most used service type
            most_used_service = max(service_usage, key=service_usage.get)
            
            # Recommend next level service
            service_progression = {
                'clarity': 'love',
                'love': 'premium',
                'premium': 'elite',
                'elite': 'premium'  # Premium is good for regular use
            }
            
            recommended_service = service_progression.get(most_used_service, 'clarity')
            
            recommendations.append({
                "type": "service_upgrade",
                "title": f"Try {recommended_service.title()} Guidance",
                "description": f"Based on your {most_used_service} sessions, you might enjoy {recommended_service} guidance",
                "service_type": recommended_service,
                "confidence": 0.8,
                "credits_required": {"clarity": 10, "love": 15, "premium": 25, "elite": 50}.get(recommended_service, 10)
            })
        
        # Always recommend topping up credits if low
        if user_credits and user_credits < 25:
            recommendations.append({
                "type": "credit_topup",
                "title": "Top Up Your Credits",
                "description": f"You have {user_credits} credits remaining. Top up to continue your spiritual journey",
                "action": "buy_credits",
                "confidence": 0.9,
                "suggested_amount": 100
            })
        
        # Recommend based on time of day
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 10:
            recommendations.append({
                "type": "daily_wisdom",
                "title": "Morning Spiritual Guidance",
                "description": "Start your day with spiritual clarity and positive energy",
                "service_type": "clarity",
                "confidence": 0.7,
                "credits_required": 10
            })
        elif 20 <= current_hour <= 23:
            recommendations.append({
                "type": "evening_reflection",
                "title": "Evening Reflection Session",
                "description": "Reflect on your day and gain insights for tomorrow",
                "service_type": "love",
                "confidence": 0.6,
                "credits_required": 15
            })
        
        return {
            "success": True,
            "message": "AI recommendations generated",
            "data": recommendations[:3]  # Limit to top 3 recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating user recommendations: {e}")
        return {
            "success": False,
            "message": "Failed to generate recommendations",
            "error": str(e),
            "data": []
        }

@user_router.get("/credit-history")
async def get_credit_history(request: Request, db=Depends(get_db)):
    """
    Get user's credit transaction history
    Previously missing endpoint causing 404 errors
    """
    try:
        user_email = get_user_email_from_token(request)
        if not user_email:
            return {"success": False, "message": "Authentication required", "data": []}
        
        # Get user's credit transactions
        transactions = await db.fetch("""
            SELECT 
                transaction_type,
                amount,
                credits,
                balance_after,
                description,
                created_at
            FROM user_purchases 
            WHERE user_email = $1 
            ORDER BY created_at DESC 
            LIMIT 50
        """, user_email)
        
        # Get sessions that used credits
        session_transactions = await db.fetch("""
            SELECT 
                'session_usage' as transaction_type,
                -credits_used as credits,
                service_type,
                'Spiritual guidance session' as description,
                created_at
            FROM sessions 
            WHERE user_email = $1 AND credits_used > 0
            ORDER BY created_at DESC 
            LIMIT 20
        """, user_email)
        
        # Combine and sort all transactions
        all_transactions = []
        
        for transaction in transactions:
            all_transactions.append({
                "type": transaction['transaction_type'],
                "amount": float(transaction['amount']) if transaction['amount'] else 0,
                "credits": transaction['credits'],
                "balance_after": transaction['balance_after'],
                "description": transaction['description'],
                "created_at": transaction['created_at'].isoformat(),
                "source": "purchase"
            })
        
        for session in session_transactions:
            all_transactions.append({
                "type": "session_usage",
                "amount": 0,
                "credits": session['credits'],
                "balance_after": None,
                "description": f"{session['service_type']} - {session['description']}",
                "created_at": session['created_at'].isoformat(),
                "source": "session"
            })
        
        # Sort by date
        all_transactions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "success": True,
            "message": "Credit history retrieved",
            "data": all_transactions[:30]  # Limit to last 30 transactions
        }
        
    except Exception as e:
        logger.error(f"Error getting credit history: {e}")
        return {
            "success": False,
            "message": "Failed to retrieve credit history",
            "error": str(e),
            "data": []
        }

@sessions_router.get("/analytics")
async def get_sessions_analytics(request: Request, db=Depends(get_db)):
    """
    Get session analytics for the user
    Previously missing endpoint causing 404 errors
    """
    try:
        user_email = get_user_email_from_token(request)
        if not user_email:
            return {"success": False, "message": "Authentication required", "data": {}}
        
        # Get session count by service type
        service_stats = await db.fetch("""
            SELECT 
                service_type,
                COUNT(*) as session_count,
                SUM(credits_used) as total_credits_used,
                AVG(credits_used) as avg_credits_per_session
            FROM sessions 
            WHERE user_email = $1 
            GROUP BY service_type
            ORDER BY session_count DESC
        """, user_email)
        
        # Get monthly session trend
        monthly_trend = await db.fetch("""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as sessions,
                SUM(credits_used) as credits_used
            FROM sessions 
            WHERE user_email = $1 
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
            LIMIT 12
        """, user_email)
        
        # Get total stats
        total_stats = await db.fetchrow("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(credits_used) as total_credits_used,
                MIN(created_at) as first_session,
                MAX(created_at) as last_session
            FROM sessions 
            WHERE user_email = $1
        """, user_email)
        
        analytics = {
            "total_sessions": total_stats['total_sessions'] if total_stats else 0,
            "total_credits_used": total_stats['total_credits_used'] if total_stats else 0,
            "first_session": total_stats['first_session'].isoformat() if total_stats and total_stats['first_session'] else None,
            "last_session": total_stats['last_session'].isoformat() if total_stats and total_stats['last_session'] else None,
            "service_breakdown": [
                {
                    "service_type": row['service_type'],
                    "session_count": row['session_count'],
                    "total_credits_used": row['total_credits_used'],
                    "avg_credits_per_session": float(row['avg_credits_per_session']) if row['avg_credits_per_session'] else 0
                }
                for row in service_stats
            ],
            "monthly_trend": [
                {
                    "month": row['month'].isoformat(),
                    "sessions": row['sessions'],
                    "credits_used": row['credits_used']
                }
                for row in monthly_trend
            ]
        }
        
        return {
            "success": True,
            "message": "Session analytics retrieved",
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        return {
            "success": False,
            "message": "Failed to retrieve session analytics",
            "error": str(e),
            "data": {}
        }

@community_router.get("/my-participation")
async def get_my_participation(request: Request, db=Depends(get_db)):
    """
    Get user's community participation data
    Previously missing endpoint causing 404 errors
    """
    try:
        user_email = get_user_email_from_token(request)
        if not user_email:
            return {"success": False, "message": "Authentication required", "data": {}}
        
        # Check if satsang_attendees table exists
        try:
            satsang_participation = await db.fetch("""
                SELECT 
                    sa.satsang_id,
                    sa.attended,
                    sa.duration_minutes,
                    sa.questions_asked,
                    sa.chat_messages_sent,
                    sa.engagement_score,
                    sa.rating,
                    sa.created_at
                FROM satsang_attendees sa
                WHERE sa.user_email = $1
                ORDER BY sa.created_at DESC
                LIMIT 20
            """, user_email)
        except Exception:
            # Table doesn't exist, return empty data
            satsang_participation = []
        
        # Get user's sessions as a form of participation
        recent_sessions = await db.fetch("""
            SELECT 
                service_type,
                question,
                created_at
            FROM sessions 
            WHERE user_email = $1 
            ORDER BY created_at DESC 
            LIMIT 10
        """, user_email)
        
        participation_data = {
            "satsang_events": [
                {
                    "satsang_id": row['satsang_id'],
                    "attended": row['attended'],
                    "duration_minutes": row['duration_minutes'],
                    "questions_asked": row['questions_asked'],
                    "chat_messages_sent": row['chat_messages_sent'],
                    "engagement_score": float(row['engagement_score']) if row['engagement_score'] else 0,
                    "rating": row['rating'],
                    "date": row['created_at'].isoformat()
                }
                for row in satsang_participation
            ],
            "recent_sessions": [
                {
                    "service_type": row['service_type'],
                    "question": row['question'][:100] + "..." if len(row['question']) > 100 else row['question'],
                    "created_at": row['created_at'].isoformat()
                }
                for row in recent_sessions
            ],
            "participation_summary": {
                "total_satsang_events": len(satsang_participation),
                "total_sessions": len(recent_sessions),
                "avg_engagement_score": sum(float(row['engagement_score']) if row['engagement_score'] else 0 for row in satsang_participation) / len(satsang_participation) if satsang_participation else 0,
                "total_questions_asked": sum(row['questions_asked'] for row in satsang_participation),
                "total_chat_messages": sum(row['chat_messages_sent'] for row in satsang_participation)
            }
        }
        
        return {
            "success": True,
            "message": "Community participation retrieved",
            "data": participation_data
        }
        
    except Exception as e:
        logger.error(f"Error getting community participation: {e}")
        return {
            "success": False,
            "message": "Failed to retrieve community participation",
            "error": str(e),
            "data": {}
        }

# Export the routers so they can be included in main.py
__all__ = ["ai_router", "user_router", "sessions_router", "community_router"]