from fastapi import APIRouter, Depends, HTTPException, Request
from db import get_db
import jwt
import os
import time
from datetime import datetime, timezone
import uuid
from typing import Dict, Any
import asyncio
import logging

# Import the enhanced birth chart logic from spiritual.py to avoid duplication
from .spiritual import get_prokerala_birth_chart_data, create_south_indian_chart_structure

# OPENAI INTEGRATION
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

# SECURITY FIX: Remove hardcoded fallback
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required for security. Please set it before starting the application.")
JWT_ALGORITHM = "HS256"

logger = logging.getLogger(__name__)

def get_user_id_from_token(request: Request) -> str:
    """Extract user ID from JWT token"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # SURGICAL FIX: Use 'sub' field to match livechat and deps.py
        return payload.get("sub") or payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_email_from_token(request: Request) -> str:
    """Extract user email from JWT token"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("email") or payload.get("user_email")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def generate_spiritual_guidance_with_ai(question: str, astrology_data: Dict[str, Any]) -> str:
    """Generate spiritual guidance using OpenAI with enhanced birth chart data"""
    try:
        openai.api_key = OPENAI_API_KEY
        
        # Extract key astrological information
        birth_details = astrology_data.get("birth_details", {})
        chart_viz = astrology_data.get("chart_visualization", {})
        
        # Build enhanced astrological context
        astro_context = []
        if birth_details:
            if birth_details.get("nakshatra"):
                astro_context.append(f"Nakshatra: {birth_details['nakshatra'].get('name', 'N/A')}")
            if birth_details.get("chandra_rasi"):
                astro_context.append(f"Moon Sign: {birth_details['chandra_rasi'].get('name', 'N/A')}")
            if birth_details.get("soorya_rasi"):
                astro_context.append(f"Sun Sign: {birth_details['soorya_rasi'].get('name', 'N/A')}")
        
        astro_summary = "; ".join(astro_context) if astro_context else "Basic astrological data available"
        
        prompt = f"""You are Swami Jyotirananthan, a revered Tamil spiritual master and Vedic astrologer.

User's Question: {question}
Astrological Context: {astro_summary}

Provide compassionate spiritual guidance that includes:
1. Direct response to their question with astrological insights
2. Specific guidance based on their birth chart (South Indian style)
3. Tamil spiritual wisdom and traditional remedies
4. Practical steps they can take
5. Mantras or spiritual practices

Write in English with Tamil spiritual concepts. Be warm, wise, and specific."""

        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are Swami Jyotirananthan, a compassionate Tamil spiritual guide with deep knowledge of Vedic astrology."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI guidance generation failed: {str(e)}")
        # Enhanced fallback guidance with astrological context
        astro_info = ""
        if astrology_data.get("birth_details"):
            bd = astrology_data["birth_details"]
            if bd.get("nakshatra"):
                astro_info += f"Your birth nakshatra {bd['nakshatra'].get('name', '')} "
            if bd.get("chandra_rasi"):
                astro_info += f"and moon sign {bd['chandra_rasi'].get('name', '')} "
            astro_info += "indicate "
        
        return f"""🕉️ Divine Guidance from Swami Jyotirananthan

Your Question: {question}

{astro_info}a soul seeking divine wisdom. The ancient Tamil tradition teaches us that every sincere question arises from the soul's journey toward truth.

From your birth chart, I can see that you are blessed with spiritual sensitivity. The cosmic energies surrounding your birth suggest:

• Regular meditation and prayer will bring clarity
• Serving others with compassion aligns with your dharma  
• Trust in divine timing - the universe responds to pure intention
• Cultivate gratitude and humility in your spiritual practice

May the divine light of Lord Shiva illuminate your path forward.

Om Namah Shivaya 🙏

🌟 Specific Spiritual Practices:
- Chant "Om Namah Shivaya" 108 times daily
- Light a diya (oil lamp) during your evening prayers
- Practice pranayama (breath control) for mental clarity
- Offer water to the rising sun with gratitude"""

async def schedule_session_followup(session_id: str, user_email: str, service_type: str, db):
    """Schedule automatic follow-up after session completion"""
    try:
        # Import here to avoid circular imports
        from utils.followup_service import FollowUpService
        from schemas.followup import FollowUpRequest, FollowUpChannel
        
        followup_service = FollowUpService(db)
        
        # Get default session follow-up template
        conn = await db.get_connection()
        try:
            if hasattr(db, 'is_sqlite') and db.is_sqlite:
                template = await conn.fetchrow("""
                    SELECT id FROM follow_up_templates 
                    WHERE template_type = 'session_followup' AND is_active = 1 
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
        
        if template:
            # Schedule follow-up
            request = FollowUpRequest(
                user_email=user_email,
                session_id=session_id,
                template_id=template['id'],
                channel=FollowUpChannel.EMAIL
            )
            
            # Schedule asynchronously to not block session response
            asyncio.create_task(followup_service.schedule_followup(request))
            
    except Exception as e:
        # Log error but don't fail the session
        logger.error(f"Failed to schedule follow-up for session {session_id}: {e}")

@router.post("/start")
async def start_session(request: Request, session_data: Dict[str, Any], db=Depends(get_db)):
    """Start a spiritual guidance session with enhanced birth chart integration"""
    user_id = get_user_id_from_token(request)
    user_email = await get_user_email_from_token(request)
    
    # Get service details first
    service_type = session_data.get("service_type")
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type is required")
    
    # Use transaction to ensure atomicity - check credits and deduct in same transaction
    async with db.transaction():
        # Get user with FOR UPDATE to prevent race conditions
        user = await db.fetchrow("""
            SELECT id, email, credits FROM users 
            WHERE id = $1 FOR UPDATE
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get service details
        service = await db.fetchrow("""
            SELECT id, name, credits_required, price_usd 
            FROM service_types 
            WHERE name = $1 AND enabled = TRUE
        """, service_type)
        
        if not service:
            raise HTTPException(status_code=400, detail="Invalid or disabled service type")
        
        # Check credits within transaction
        if user["credits"] < service["credits_required"]:
            raise HTTPException(
                status_code=402, 
                detail=f"போதிய கிரெடிட்கள் இல்லை. தேவை: {service['credits_required']}, கிடைக்கும்: {user['credits']}"
            )
        
        # Deduct credits atomically
        result = await db.execute("""
            UPDATE users SET credits = credits - $1 
            WHERE id = $2 AND credits >= $1
        """, service["credits_required"], user_id)
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=402, 
                detail="Credit deduction failed - insufficient credits or concurrent transaction"
            )
        
        # Initialize cache tracking variables
        cache_used = False
        endpoints_used = []
        
        # Create session record with cache tracking (will be updated later with actual cache info)
        session_id = str(uuid.uuid4())
        await db.execute("""
            INSERT INTO sessions (id, user_email, service_type, question, guidance, 
                                avatar_video_url, credits_used, original_price, status, 
                                prokerala_cache_used, prokerala_endpoints_used, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed', $9, $10, NOW())
        """, 
            session_id, 
            user["email"], 
            service_type, 
            session_data.get("question", ""),
            f"Divine guidance for: {session_data.get('question', '')}",
            None,  # avatar_video_url
            service["credits_required"],
            service["price_usd"],
            cache_used,
            endpoints_used
        )
        
        # Calculate remaining credits
        remaining_credits = user["credits"] - service["credits_required"]
    
    # ENHANCED: Use unified birth chart logic from spiritual.py
    birth_details = session_data.get("birth_details")
    astrology_data = {}
    guidance_text = ""
    
    try:
        # Import and use the RAG-enhanced spiritual guidance system
        from enhanced_rag_knowledge_engine import get_rag_enhanced_guidance
        
        # Get enhanced guidance with RAG + Prokerala integration
        rag_result = await get_rag_enhanced_guidance(
            user_query=session_data.get("question", ""),
            birth_details=birth_details,
            service_type=service_type
        )
        
        guidance_text = rag_result.get("enhanced_guidance", "")
        
        # Extract astrology data from enhanced birth details if available
        enhanced_birth_details = rag_result.get("enhanced_birth_details", {})
        if enhanced_birth_details and "prokerala_response" in enhanced_birth_details:
            astrology_data = enhanced_birth_details["prokerala_response"]
        else:
            astrology_data = {"data": {"message": "Enhanced spiritual guidance provided"}}
        
        logger.info(f"[RAG] Enhanced guidance generated: {len(guidance_text)} chars")
        logger.info(f"[RAG] Knowledge sources used: {len(rag_result.get('knowledge_sources', []))}")
        logger.info(f"[RAG] Persona mode: {rag_result.get('persona_mode', 'general')}")
        
    except Exception as e:
        logger.warning(f"[RAG] Enhanced guidance failed, falling back to enhanced birth chart: {e}")
        
        # Fallback to enhanced birth chart logic from spiritual.py
        if birth_details and all(birth_details.get(key) for key in ["date", "time", "location"]):
            try:
                # Use the enhanced birth chart logic from spiritual.py
                logger.info(f"[Session] Using enhanced birth chart logic for {user_email}")
                
                # Get comprehensive birth chart data with South Indian chart
                chart_response = await get_prokerala_birth_chart_data(user_email, birth_details)
                
                if chart_response.get("success"):
                    astrology_data = chart_response.get("birth_chart", {})
                    
                    # Generate spiritual guidance based on enhanced chart data
                    guidance_text = await generate_spiritual_guidance_with_ai(
                        session_data.get("question", ""), 
                        astrology_data
                    )
                    
                    logger.info(f"[Session] ✅ Enhanced birth chart generated successfully")
                else:
                    # Fallback with basic guidance
                    astrology_data = {
                        "data": {
                            "nakshatra": {"name": "Unable to calculate"},
                            "chandra_rasi": {"name": "Please check birth details"}
                        },
                        "error": chart_response.get("message", "Birth chart generation failed")
                    }
                    guidance_text = await generate_spiritual_guidance_with_ai(
                        session_data.get("question", ""), 
                        astrology_data
                    )
                    
            except Exception as e:
                logger.error(f"Enhanced birth chart API error for session {session_id}: {e}")
                # Final fallback to basic guidance
                astrology_data = {
                    "data": {
                        "nakshatra": {"name": "Unable to calculate"},
                        "chandra_rasi": {"name": "Please check birth details"}
                    },
                    "error": str(e)
                }
                guidance_text = await generate_spiritual_guidance_with_ai(
                    session_data.get("question", ""), 
                    astrology_data
                )
        else:
            # No birth details provided
            astrology_data = {"data": {"message": "Birth details required for astrological analysis"}}
            guidance_text = await generate_spiritual_guidance_with_ai(
                session_data.get("question", ""), 
                astrology_data
            )
    
    # Update session with cache tracking information
    if birth_details:
        try:
            # BUG FIX: Handle location as both string and dict to prevent AttributeError
            location = birth_details.get('location', '')
            if isinstance(location, dict):
                location_name = location.get('name', '')
            elif isinstance(location, str):
                location_name = location
            else:
                location_name = str(location) if location else ''
            
            cache_key = f"birth_chart:{birth_details.get('date', '')}:{birth_details.get('time', '')}:{location_name}"
            cached_data = await db.fetchrow("""
                SELECT created_at FROM api_cache 
                WHERE cache_key = $1 AND created_at > NOW() - INTERVAL '30 days'
            """, cache_key)
            
            if cached_data:
                cache_used = True
                logger.info(f"[Session] Cache hit detected for session {session_id}")
                
                # Get service endpoint configuration
                service_config = await db.fetchrow("""
                    SELECT prokerala_endpoints FROM service_types WHERE name = $1
                """, service_type)
                
                if service_config and service_config['prokerala_endpoints']:
                    endpoints_used = service_config['prokerala_endpoints']
                
                # Update session with cache information
                await db.execute("""
                    UPDATE sessions 
                    SET prokerala_cache_used = $1, prokerala_endpoints_used = $2
                    WHERE id = $3
                """, cache_used, endpoints_used, session_id)
                
                logger.info(f"[Session] Updated session {session_id} with cache info: used={cache_used}, endpoints={len(endpoints_used)}")
        except Exception as e:
            logger.warning(f"[Session] Cache tracking failed for session {session_id}: {e}")
    
    # Schedule automatic follow-up (non-blocking)
    asyncio.create_task(schedule_session_followup(session_id, user["email"], service_type, db))
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "guidance": guidance_text,  # Enhanced guidance with real astrology
            "astrology": astrology_data,  # Enhanced birth chart data with South Indian chart
            "birth_chart": astrology_data,  # Complete chart data
            "birth_details": birth_details,  # Echo back for verification
            "credits_deducted": service["credits_required"],
            "remaining_credits": remaining_credits,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "enhanced_birth_chart": True,
                "south_indian_chart": True,
                "prokerala_integration": True,
                "service_type": service_type,
                "data_source": "Enhanced Prokerala API v2 (birth-details + chart + planetary-positions)"
            }
        }
    } 