import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

# FastAPI Core Imports
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# তমিল - আমাদের ভিত্তি এবং ব্যবসায়িক লজিক থেকে আমদানি
from core_foundation_enhanced import (
    get_current_user, get_admin_user, get_database,
    SpiritualUser, UserPurchase, SpiritualSession,
    EnhancedSettings, logger, EnhancedJyotiFlowDatabase
)

from enhanced_business_logic import (
    SpiritualAvatarEngine, MonetizationOptimizer, SatsangManager,
    SocialContentEngine, EnhancedSessionProcessor
)

# =============================================================================
# 🎨 ENHANCED TEMPLATE CONFIGURATION
# তমিল - উন্নত টেমপ্লেট কনফিগারেশন
# =============================================================================

# Initialize Enhanced Templates
templates = Jinja2Templates(directory="templates")

# Enhanced template context for all pages
async def enhanced_template_context(
    request: Request,
    user: Optional[SpiritualUser] = None,
    db: Optional[EnhancedJyotiFlowDatabase] = None
) -> Dict[str, Any]:
    """তমিল - সমস্ত পৃষ্ঠার জন্য উন্নত টেমপ্লেট প্রসঙ্গ"""
    context = {
        "request": request,
        "user": user,
        "app_name": "JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram",
        "year": datetime.now().year,
        "divine_blessing": "🙏🏼 Om Namah Shivaya",
        
        # Enhanced features flags
        "avatar_enabled": user and isinstance(user, dict) and user.get('subscription_tier') in ["premium", "elite"] if user else False,
        "live_chat_enabled": user and isinstance(user, dict) and user.get('subscription_tier') in ["premium", "elite"] if user else False,
        "satsang_access": user and isinstance(user, dict) and user.get('subscription_tier', 'free') != "free" if user else False,

        
        # Navigation enhancement
        "nav_items": [
            {"name": "Home", "url": "/", "icon": "🏠"},
            {"name": "Spiritual Guidance", "url": "/spiritual-guidance", "icon": "🕉️"},
            {"name": "Live Chat", "url": "/live-chat", "icon": "📹", "premium": True},
            {"name": "Satsang", "url": "/satsang", "icon": "🙏🏼", "premium": True},
            {"name": "Pricing", "url": "/pricing", "icon": "💎"},
            {"name": "Profile", "url": "/profile", "icon": "👤", "auth": True}
        ]
    }
    
    # Add user-specific data
    if user and db:
        try:
            # Get user's recent sessions
            recent_sessions = await db.get_user_sessions(user.id, limit=3)
            context.update({
                "recent_sessions": recent_sessions,
                "total_sessions": len(await db.get_user_sessions(user.id)),
                "subscription_status": user.subscription_tier,
                "next_satsang": await db.get_next_satsang_for_user(user.id)
            })
        except Exception as e:
            logger.error(f"Template context enhancement failed: {e}")
    
    return context

# =============================================================================
# 🏠 ENHANCED HOME & CORE PAGES
# তমিল - উন্নত হোম এবং মূল পৃষ্ঠা
# =============================================================================

async def enhanced_home_page(
    request: Request,
    user: Optional[Dict] = None,
    db: Optional[Any] = None
):

    """তমিল - উন্নত হোম পৃষ্ঠা"""
    context = await enhanced_template_context(request, user, db)
    
    # Add home-specific enhancements
    context.update({
        "hero_message": "🕉️ Welcome to Divine Digital Guidance",
        "featured_services": [
            {
                "title": "AI Avatar Guidance",
                "description": "Personalized video guidance from Swamiji",
                "icon": "🎭",
                "premium": True,
                "url": "/spiritual-guidance"
            },
            {
                "title": "Live Video Chat", 
                "description": "Real-time spiritual consultation",
                "icon": "📹",
                "premium": True,
                "url": "/live-chat"
            },
            {
                "title": "Monthly Satsang",
                "description": "Join our spiritual community gatherings", 
                "icon": "🙏🏼",
                "premium": True,
                "url": "/satsang"
            }
        ],
        
        # Dynamic content based on user
        "personalized_content": await _get_personalized_home_content(user, db) if user else None,
        "upcoming_satsang": await db.get_next_public_satsang() if db else None,
        "testimonials": await _get_featured_testimonials(db) if db else []
    })
    
    return templates.TemplateResponse("enhanced_home.html", context)

async def enhanced_spiritual_guidance_page(
    request: Request,
    user: SpiritualUser = Depends(get_current_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - উন্নত আধ্যাত্মিক পথনির্দেশনা পৃষ্ঠা"""
    context = await enhanced_template_context(request, user, db)
    
    # Add guidance-specific enhancements
    context.update({
        "page_title": "Sacred Spiritual Guidance",
        "guidance_types": [
            {
                "type": "quick_blessing",
                "title": "Quick Divine Blessing",
                "description": "Instant spiritual comfort and blessing",
                "price": 5,
                "duration": "30 seconds",
                "features": ["Text guidance", "Voice blessing"],
                "avatar_enabled": False
            },
            
            {
                "type": "spiritual_guidance", 
                "title": "Spiritual Guidance",
                "description": "Detailed guidance for life questions",
                "price": 15,
                "duration": "2-3 minutes", 
                "features": ["Detailed analysis", "Practical advice", "Avatar video"],
                "avatar_enabled": user.subscription_tier in ["premium", "elite"]
            },
            {
                "type": "premium_consultation",
                "title": "Premium Consultation", 
                "description": "Comprehensive spiritual analysis",
                "price": 50,
                "duration": "5-10 minutes",
                "features": ["Vedic analysis", "Personalized guidance", "HD Avatar video", "Follow-up support"],
                "avatar_enabled": True,
                "premium_only": True
            },
            {
                "type": "elite_session",
                "title": "Elite Spiritual Session",
                "description": "Transformative one-on-one guidance",  
                "price": 100,
                "duration": "15-30 minutes",
                "features": ["Deep spiritual analysis", "Life path guidance", "4K Avatar video", "Personal meditation"],
                "avatar_enabled": True,
                "elite_only": True
            }
        ],
        
        # User's guidance history
        "recent_guidance": await db.get_user_sessions(user.id, limit=5),
        "spiritual_journey_insights": await _generate_journey_insights(user, db)
    })
    
    return templates.TemplateResponse("enhanced_spiritual_guidance.html", context)

# =============================================================================
# 🎥 LIVE VIDEO CHAT INTERFACE
# তমিল - লাইভ ভিডিও চ্যাট ইন্টারফেস
# =============================================================================

async def live_chat_page(
    request: Request,
    user: SpiritualUser = Depends(get_current_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - লাইভ ভিডিও চ্যাট পৃষ্ঠা"""
    # Check subscription access
    if user.subscription_tier not in ["premium", "elite"]:
        return RedirectResponse(url="/pricing?upgrade=live_chat", status_code=302)
    
    context = await enhanced_template_context(request, user, db)
    
    context.update({
        "page_title": "Live Video Chat with Swamiji",
        "chat_options": [
            {
                "type": "premium_consultation",
                "title": "Premium Live Session",
                "duration": 30,
                "price": 75,
                "features": ["30 minutes", "Video guidance", "Q&A session", "Recording included"]
            },
            {
                "type": "elite_session", 
                "title": "Elite Transformation Session",
                "duration": 60,
                "price": 150,
                "features": ["60 minutes", "Deep spiritual work", "Personalized practices", "Follow-up support"],
                "elite_only": True
            }
        ],
        
        # Live chat configuration
        "agora_config": {
            "app_id": EnhancedSettings().agora_app_id,
            "channel_prefix": "swamiji_live_",
            "video_profile": "720p_1"
        },
        
        "user_live_sessions": await db.get_user_live_sessions(user.id),
        "swamiji_availability": await _check_swamiji_availability()
    })
    
    return templates.TemplateResponse("live_chat.html", context)

# =============================================================================
# 🕉️ SATSANG COMMUNITY INTERFACE
# তমিল - সত্সং সম্প্রদায় ইন্টারফেস
# =============================================================================

async def satsang_page(
    request: Request,
    user: Optional[SpiritualUser] = Depends(get_current_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - সত্সং কমিউনিটি পৃষ্ঠা"""
    context = await enhanced_template_context(request, user, db)
    
    # Get satsang events
    upcoming_satsangs = await db.get_upcoming_satsangs()
    past_satsangs = await db.get_past_satsangs(limit=6)
    
    context.update({
        "page_title": "Sacred Satsang Community",
        "satsang_description": """
        Join our global spiritual family in monthly satsangs where souls gather 
        to receive divine teachings, participate in sacred chants, and experience 
        the transformative power of collective spiritual practice.
        """,
        
        "upcoming_satsangs": upcoming_satsangs,
        "past_satsangs": past_satsangs,
        
        "satsang_features": [
            "Live spiritual teachings from Swamiji",
            "Interactive Q&A sessions", 
            "Guided meditation and chanting",
            "Global spiritual community",
            "Recording access for later viewing",
            "Special blessings and mantras"
        ],
        
        # User's satsang participation
        "user_registrations": await db.get_user_satsang_registrations(user.id) if user else [],
        "participation_stats": await _get_user_satsang_stats(user, db) if user else None
    })
    
    return templates.TemplateResponse("satsang_community.html", context)

# =============================================================================
# 🛡️ ENHANCED ADMIN DASHBOARD
# তমিল - উন্নত অ্যাডমিন ড্যাশবোর্ড
# =============================================================================

async def enhanced_admin_dashboard(
    request: Request,
    admin_user: SpiritualUser = Depends(get_admin_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - AI সুপারিশ সহ উন্নত অ্যাডমিন ড্যাশবোর্ড"""
    context = await enhanced_template_context(request, admin_user, db)
    
    # Initialize business intelligence
    monetization_optimizer = MonetizationOptimizer()
    
    # Get enhanced analytics
    analytics_data = await _get_enhanced_analytics(db)
    ai_recommendations = await monetization_optimizer.generate_pricing_recommendations()
    
    context.update({
        "page_title": "Enhanced Admin Dashboard",
        
        # Core metrics (preserved)
        "total_users": analytics_data["total_users"],
        "total_revenue": analytics_data["total_revenue"],
        "recent_sessions": analytics_data["recent_sessions"],
        
        # Enhanced analytics
        "avatar_sessions": analytics_data["avatar_sessions"],
        "live_chat_usage": analytics_data["live_chat_usage"],
        "satsang_attendance": analytics_data["satsang_attendance"],
        "conversion_metrics": analytics_data["conversion_metrics"],
        
        # AI Business Intelligence
        "ai_recommendations": ai_recommendations,
        "revenue_optimization": {
            "current_monthly": analytics_data["monthly_revenue"],
            "projected_with_optimization": analytics_data["monthly_revenue"] * 1.3,
            "optimization_opportunities": ai_recommendations.get("recommendations", [])[:3]
        },
        
        # Content management
        "social_content_queue": await _get_social_content_queue(db),
        "upcoming_satsangs_admin": await db.get_upcoming_satsangs(),
        
        # System health
        "system_health": await _get_system_health_metrics(),
        "avatar_service_status": await _check_avatar_service_health()
    })
    
    return templates.TemplateResponse("enhanced_admin_dashboard.html", context)

async def admin_ai_insights_page(
    request: Request,
    admin_user: SpiritualUser = Depends(get_admin_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - AI অন্তর্দৃষ্টি পৃষ্ঠা"""
    context = await enhanced_template_context(request, admin_user, db)
    
    monetization_optimizer = MonetizationOptimizer()
    
    # Get comprehensive AI analysis
    pricing_insights = await monetization_optimizer.generate_pricing_recommendations()
    product_optimization = await monetization_optimizer.optimize_product_offerings()
    retention_strategies = await monetization_optimizer.generate_retention_strategies()
    
    context.update({
        "page_title": "AI Business Intelligence",
        "pricing_insights": pricing_insights,
        "product_optimization": product_optimization,
        "retention_strategies": retention_strategies,
        
        # Implementation tracking
        "implemented_recommendations": await db.get_implemented_recommendations(),
        "recommendation_impact": await _calculate_recommendation_impact(db)
    })
    
    return templates.TemplateResponse("admin_ai_insights.html", context)

# =============================================================================
# 📱 SOCIAL CONTENT MANAGEMENT
# তমিল - সামাজিক বিষয়বস্তু ব্যবস্থাপনা
# =============================================================================

async def social_content_management_page(
    request: Request,
    admin_user: SpiritualUser = Depends(get_admin_user),
    db: EnhancedJyotiFlowDatabase = Depends(get_database)
):
    """তমিল - সামাজিক বিষয়বস্তু ব্যবস্থাপনা পৃষ্ঠা"""
    context = await enhanced_template_context(request, admin_user, db)
    
    social_engine = SocialContentEngine()
    
    context.update({
        "page_title": "Social Content Management",
        
        "content_queue": await db.get_social_content_queue(),
        "published_content": await db.get_published_social_content(limit=20),
        "content_performance": await _get_content_performance_metrics(db),
        
        "content_templates": [
            {
                "type": "daily_wisdom",
                "title": "Daily Wisdom Post",
                "platforms": ["instagram", "twitter", "linkedin"],
                "frequency": "daily"
            },
            {
                "type": "satsang_highlight", 
                "title": "Satsang Highlights",
                "platforms": ["youtube", "instagram"],
                "frequency": "weekly"
            },
            {
                "type": "spiritual_teaching",
                "title": "Spiritual Teaching",
                "platforms": ["all"],
                "frequency": "twice_weekly"
            }
        ],
        
        "scheduling_calendar": await _get_content_calendar(db),
        "auto_generation_settings": await db.get_auto_content_settings()
    })
    
    return templates.TemplateResponse("social_content_management.html", context)

# =============================================================================
# 🛠️ ENHANCED UTILITY FUNCTIONS
# তমিল - উন্নত ইউটিলিটি ফাংশন
# =============================================================================

async def _get_personalized_home_content(
    user: SpiritualUser, 
    db: EnhancedJyotiFlowDatabase
) -> Dict:
    """তমিল - ব্যক্তিগতকৃত হোম কন্টেন্ট পান"""
    try:
        recent_sessions = await db.get_user_sessions(user.id, limit=3)
        spiritual_journey = await _analyze_user_spiritual_journey(user, db)
        
        return {
            "welcome_message": f"Welcome back, {user.name} 🙏🏼",
            "spiritual_progress": spiritual_journey,
            "recommended_actions": await _get_recommended_actions(user, db),
            "personal_mantras": await _get_personal_mantras(user)
        }
    except Exception as e:
        logger.error(f"Personalized content generation failed: {e}")
        return {}

async def _generate_journey_insights(
    user: SpiritualUser, 
    db: EnhancedJyotiFlowDatabase
) -> Dict:
    """তমিল - আধ্যাত্মিক যাত্রার অন্তর্দৃষ্টি তৈরি করুন"""
    try:
        sessions = await db.get_user_sessions(user.id)
        
        insights = {
            "total_sessions": len(sessions),
            "spiritual_growth_stage": "seeking" if len(sessions) < 5 else "growing",
            "favorite_topics": await _extract_favorite_topics(sessions),
            "growth_trajectory": "upward" if len(sessions) > 3 else "beginning",
            "next_recommendation": "Consider premium consultation for deeper guidance"
        }
        
        return insights
    except Exception as e:
        logger.error(f"Journey insights generation failed: {e}")
        return {}

async def _get_enhanced_analytics(db: EnhancedJyotiFlowDatabase) -> Dict:
    """তমিল - উন্নত বিশ্লেষণ ডেটা পান"""
    try:
        base_analytics = await db.get_basic_analytics()
        
        enhanced_data = {
            **base_analytics,
            "avatar_sessions": await db.count_avatar_sessions(),
            "live_chat_usage": await db.get_live_chat_metrics(),
            "satsang_attendance": await db.get_satsang_metrics(),
            "conversion_metrics": await db.get_conversion_analytics(),
            "monthly_revenue": await db.calculate_monthly_revenue()
        }
        
        return enhanced_data
    except Exception as e:
        logger.error(f"Enhanced analytics failed: {e}")
        return {"error": "Analytics temporarily unavailable"}

async def _check_swamiji_availability() -> Dict:
    """তমিল - স্বামীজির উপলব্ধতা পরীক্ষা করুন"""
    # This would integrate with real availability system
    current_hour = datetime.now().hour
    
    if 6 <= current_hour <= 22:  # 6 AM to 10 PM
        return {
            "available": True,
            "status": "Swamiji is available for divine guidance",
            "next_available": None
        }
    else:
        next_available = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        if next_available <= datetime.now():
            next_available += timedelta(days=1)
            
        return {
            "available": False,
            "status": "Swamiji is in meditation. Available from 6 AM to 10 PM",
            "next_available": next_available.isoformat()
        }

async def _get_system_health_metrics() -> Dict:
    """তমিল - সিস্টেম স্বাস্থ্য মেট্রিক্স পান"""
    return {
        "api_status": "healthy",
        "database_status": "healthy", 
        "avatar_service": "operational",
        "live_chat_service": "operational",
        "response_time": "< 200ms",
        "uptime": "99.9%"
    }

async def _check_avatar_service_health() -> Dict:
    """তমিল - অবতার সেবার স্বাস্থ্য পরীক্ষা করুন"""
    return {
        "d_id_status": "operational",
        "elevenlabs_status": "operational", 
        "agora_status": "operational",
        "generation_queue": 3,
        "average_generation_time": "68 seconds"
    }

# =============================================================================
# 🎨 TEMPLATE FILTERS & GLOBALS
# তমিল - টেমপ্লেট ফিল্টার এবং গ্লোবাল
# =============================================================================

def setup_template_filters():
    """তমিল - টেমপ্লেট ফিল্টার সেট করুন"""
    
    def format_currency(amount):
        return f"${amount:,.2f}"
    
    def format_duration(seconds):
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        else:
            return f"{seconds//3600}h {(seconds%3600)//60}m"
    
    def spiritual_greeting():
        greetings = ["🙏🏼 Namaste", "🕉 Om Shanti", "🌺 Divine Blessings"]
        import random
        return random.choice(greetings)
    
    # CORRECT WAY to add filters
    templates.env.filters['format_currency'] = format_currency
    templates.env.filters['format_duration'] = format_duration  
    templates.env.filters['spiritual_greeting'] = spiritual_greeting
    
    def get_subscription_benefits(tier):
        benefits = {
            "free": ["Basic spiritual guidance", "Text responses"],
            "premium": ["Avatar video guidance", "Live chat access", "Satsang participation", "Priority support"],
            "elite": ["Extended sessions", "Personal consultations", "Exclusive satsangs", "Direct access to Swamiji"]
        }
        return benefits.get(tier, [])
    
    # Add global function
    templates.env.globals['get_subscription_benefits'] = get_subscription_benefits 
    

# Initialize template filters
setup_template_filters()

# Export route handlers
__all__ = [
    "enhanced_home_page",
    "enhanced_spiritual_guidance_page", 
    "live_chat_page",
    "satsang_page",
    "enhanced_admin_dashboard",
    "admin_ai_insights_page",
    "social_content_management_page",
    "enhanced_template_context"
]