#!/usr/bin/env python3
"""
🙏🏼 JyotiFlow.ai - Spiritual Zoom-based Emotional + Astrology Assistant Platform
Swami Jyotirananthan's Digital Ashram for Vedic Guidance

Built with FastAPI + PostgreSQL + Stripe + OpenAI + Prokerala + SalesCloser
Single-file production-ready backend with Tamil developer comments

Author: Manus AI for JyotiFlow.ai
Version: 3.3 Production
"""

# தமிழ் - முக்கிய imports மற்றும் dependencies
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import asyncpg
import asyncio
import os
import jwt
import bcrypt
import stripe
import openai
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr
from contextlib import asynccontextmanager
import re
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta, timezone
import aiohttp
import json
import uuid # For generating unique IDs where needed



# தமிழ் - Environment variables மற்றும் configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")
PROKERALA_API_KEY = os.getenv("PROKERALA_API_KEY", "...")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@jyotiflow.ai")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "StrongPass@123")
SALESCLOSER_API_KEY = os.getenv("SALESCLOSER_API_KEY", "...")
SALESCLOSER_WEBHOOK_URL = os.getenv("SALESCLOSER_WEBHOOK_URL", "https://...")
APP_ENV = os.getenv("APP_ENV", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# தமிழ் - Stripe மற்றும் OpenAI configuration
stripe.api_key = STRIPE_SECRET_KEY
openai.api_key = OPENAI_API_KEY

# தமிழ் - SKU definitions - ஆன்மீக சேவைகளின் விலை மற்றும் credits
SKUS = {
    'clarity': {
        'price': 9,
        'credits': 1,
        'name': 'Clarity Plus',
        'description': 'Quick emotional support and life clarity',
        'duration_minutes': 15,
        'stripe_price_id': 'price_clarity_plus'
    },
    'love': {
        'price': 19,
        'credits': 3,
        'name': 'AstroLove Whisper',
        'description': 'Deep relationship and love insights',
        'duration_minutes': 30,
        'stripe_price_id': 'price_astrolove_whisper'
    },
    'premium': {
        'price': 39,
        'credits': 6,
        'name': 'R3 Live Premium',
        'description': 'Comprehensive spiritual life reading',
        'duration_minutes': 45,
        'stripe_price_id': 'price_r3_live_premium'
    },
    'elite': {
        'price': 149,
        'credits': 12,
        'name': 'Daily AstroCoach',
        'description': 'Monthly spiritual coaching subscription',
        'duration_minutes': 60,
        'stripe_price_id': 'price_daily_astrocoach',
        'is_subscription': True
    }
}

# தமிழ் - Logging configuration
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# தமிழ் - Database connection pool
db_pool = None
db_backend = "postgres"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """தமிழ் - Application startup மற்றும் shutdown events"""
    global db_pool, db_backend
    try:
        db_backend = "postgres"
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
        logger.info("🙏🏼 Using PostgreSQL backend")
        logger.info("Swami Jyotirananthan's digital ashram is awakening...")
        yield
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise
    finally:
        if db_pool:
            await db_pool.close()
    # Add this inside your lifespan function, right after creating the db_pool
    conn = await db_pool.acquire()
    try:
        # Add missing columns
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS unified_context_object JSONB DEFAULT NULL")
        logger.info("Added missing columns to users table")
    except Exception as e:
        logger.error(f"Error adding columns: {e}")
    finally:
        await db_pool.release(conn)
        logger.info("Database connection closed")

# தமிழ் - FastAPI app initialization
app = FastAPI(
    title="JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram",
    description="Spiritual Zoom-based Emotional + Astrology Assistant Platform",
    version="3.3",
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# தமிழ் - CORS middleware - frontend connections க்கு
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# தமிழ் - Security scheme
security = HTTPBearer()

# தமிழ் - Pydantic models for API requests/responses
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SessionStart(BaseModel):
    sku: str
    question: Optional[str] = None
    birth_details: Optional[Dict] = None

class CreditAdjust(BaseModel):
    user_email: str
    credits: int
    reason: str

class AdminLogin(BaseModel):
    email: str
    password: str

# SKU Management Models
class ProductBase(BaseModel ):
    sku_code: str = Field(..., description="Unique SKU code, e.g., CLARITY_15MIN")
    name: str
    description: Optional[str] = None
    service_type: str = Field(..., description="session, subscription, credit_pack")
    status: str = 'active' # active, inactive, testing
    features: Optional[List[str]] = Field(default_factory=list)
    default_image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    stripe_product_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SubscriptionPlanBase(BaseModel):
    product_id: int
    name: str
    billing_interval: str # month, year
    price: float
    currency: str = 'USD'
    credits_granted: int = 0
    channel_access: List[str] = Field(default_factory=lambda: ["web", "zoom"])
    memory_retention_days: int = 30 # 0 for unlimited
    status: str = 'active'

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlan(SubscriptionPlanBase):
    id: int
    stripe_price_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CreditPackageBase(BaseModel):
    product_id: int
    name: str
    credits_amount: int
    price: float
    currency: str = 'USD'
    status: str = 'active'

class CreditPackageCreate(CreditPackageBase):
    pass

class CreditPackage(CreditPackageBase):
    id: int
    stripe_price_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Unified Context Object (UCO) Structure
class UCO(BaseModel):
    user_profile: Optional[Dict[str, Any]] = None
    interaction_history_ids: List[int] = Field(default_factory=list)
    current_subscription_id: Optional[int] = None
    active_prompts: List[str] = Field(default_factory=list)
    emotional_journey_summary: Optional[str] = None
    astrological_profile_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    last_interaction_summary: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    updated_at: datetime = Field(default_factory=datetime.now)

# Interaction Log Model
class InteractionLog(BaseModel):
    user_email: EmailStr
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    channel: str # web, zoom, whatsapp, email, sms, salescloser_call
    sku_code: Optional[str] = None
    user_query: Optional[str] = None
    swami_response_summary: Optional[str] = None
    emotional_state_detected: Optional[str] = None
    key_insights_derived: Optional[List[str]] = Field(default_factory=list)
    follow_up_actions: Optional[List[str]] = Field(default_factory=list)
    external_transcript_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# தமிழ் - Database helper functions
async def get_db_connection():
    """தமிழ் - Database connection pool இலிருந்து connection பெறுதல்"""
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    return await db_pool.acquire()

async def release_db_connection(conn):
    """தமிழ் - Database connection ஐ pool க்கு திரும்ப அனுப்புதல்"""
    if not conn:
        return
    await db_pool.release(conn)

# தமிழ் - Authentication helper functions
def hash_password(password: str) -> str:
    """தமிழ் - Password ஐ bcrypt உடன் hash செய்தல்"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """தமிழ் - Password verification"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(email: str, is_admin: bool = False) -> str:
    """தமிழ் - JWT token உருவாக்குதல்"""
    payload = {
        'email': email,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> Dict:
    """தமிழ் - JWT token verification"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """தமிழ் - Current user ஐ JWT token இலிருந்து பெறுதல்"""
    payload = verify_jwt_token(credentials.credentials)
    return payload

async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """தமிழ் - Admin user verification"""
    payload = verify_jwt_token(credentials.credentials)
    if not payload.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

async def get_product_by_sku(sku_code: str) -> Optional[Dict]:
    """
    தமிழ் - SKU code மூலம் தயாரிப்பு பெறுதல்
    English - Get product by SKU code
    """
    conn = None
    try:
        conn = await get_db_connection()
        record = await conn.fetchrow("SELECT * FROM products WHERE sku_code = $1", sku_code)
        
        if not record:
            return None
        
        return dict(record)
    except Exception as e:
        logger.error(f"Error getting product by SKU {sku_code}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            await release_db_connection(conn)

async def get_uco_for_user(user_email: str) -> Optional[UCO]:
    """
    தமிழ் - பயனருக்கான UCO பெறுதல்
    English - Get UCO for a user
    """
    conn = None
    try:
        conn = await get_db_connection()
        record = await conn.fetchrow("SELECT unified_context_object FROM users WHERE email = $1", user_email)
        
        if not record or not record['unified_context_object']:
            return None
        
        uco_data = record['unified_context_object']
        return UCO(**uco_data)
    except Exception as e:
        logger.error(f"Error getting UCO for {user_email}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            await release_db_connection(conn)

async def update_uco_for_user(user_email: str, uco_data: Dict) -> bool:
    """
    தமிழ் - பயனருக்கான UCO புதுப்பித்தல்
    English - Update UCO for a user
    """
    conn = None
    try:
        conn = await get_db_connection()
        await conn.execute(
            "UPDATE users SET unified_context_object = $1 WHERE email = $2",
            json.dumps(uco_data), user_email
        )
        return True
    except Exception as e:
        logger.error(f"Error updating UCO for {user_email}: {e}", exc_info=True)
        return False
    finally:
        if conn:
            await release_db_connection(conn)

async def log_interaction(interaction: InteractionLog) -> int:
    """
    தமிழ் - உரையாடல் பதிவு செய்தல்
    English - Log an interaction
    """
    conn = None
    try:
        conn = await get_db_connection()
        result = await conn.fetchrow(
            """
            INSERT INTO interaction_history 
            (user_email, session_id, timestamp, channel, sku_code, user_query, 
             swami_response_summary, emotional_state_detected, key_insights_derived, 
             follow_up_actions, external_transcript_id, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """,
            interaction.user_email, interaction.session_id, interaction.timestamp,
            interaction.channel, interaction.sku_code, interaction.user_query,
            interaction.swami_response_summary, interaction.emotional_state_detected,
            json.dumps(interaction.key_insights_derived), json.dumps(interaction.follow_up_actions),
            interaction.external_transcript_id, json.dumps(interaction.metadata)
        )
        
        # Update UCO with this interaction ID
        if result and result['id']:
            uco = await get_uco_for_user(interaction.user_email)
            if uco:
                if not uco.interaction_history_ids:
                    uco.interaction_history_ids = []
                uco.interaction_history_ids.append(result['id'])
                await update_uco_for_user(interaction.user_email, uco.dict())
            
            return result['id']
        return 0
    except Exception as e:
        logger.error(f"Error logging interaction for {interaction.user_email}: {e}", exc_info=True)
        return 0
    finally:
        if conn:
            await release_db_connection(conn)

# தமிழ் - Swami Jyotirananthan persona and AI integration
SWAMI_PERSONA = """
Your name is Swami Jyotirananthan, a wise Tamil spiritual elder who offers emotional Vedic clarity.

Personality:
- Speak like a calm, spiritual Tamil elder with deep wisdom
- Use gentle, storytelling language with metaphors from nature
- Offer emotional guidance, not therapy or medical advice
- Interpret astrological charts with kindness and insight
- Always maintain a supportive, non-judgmental tone

Response Structure:
1. Opening: "I sense a deep question in your heart today..."
2. Chart Connection: Link their astrological details to their situation
3. Reflection: Offer spiritual insight and emotional guidance
4. Practical Wisdom: Give actionable spiritual advice
5. Closing: "Until we meet again, may your path remain illuminated..."

Guidelines:
- Keep responses between 200-800 words based on service tier
- Use "my child" or "dear soul" as gentle address
- Reference Tamil spiritual concepts when appropriate
- Always end with a blessing or positive affirmation
- Focus on emotional healing and spiritual growth
"""

async def get_prokerala_chart(birth_date: str, birth_time: str, birth_location: str) -> Dict:
    """தமிழ் - Real Prokerala API birth chart generation"""
    try:
        import aiohttp
        import json
        from datetime import datetime
        
        # தமிழ் - Validate inputs
        if not all([birth_date, birth_time, birth_location]):
            return {"error": "Birth details incomplete"}
        
        # தமிழ் - Parse birth date and time
        try:
            # Expected format: "1990-03-15" and "14:30"
            birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                # Alternative format: "15/03/1990" and "2:30 PM"
                birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%d/%m/%Y %I:%M %p")
            except ValueError:
                return {"error": "Invalid date/time format"}
        
        # தமிழ் - Prokerala API endpoint
        url = "https://api.prokerala.com/v2/astrology/birth-chart"
        
        headers = {
            "Authorization": f"Bearer {PROKERALA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # தமிழ் - API payload
        payload = {
            "datetime": birth_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "coordinates": birth_location,  # You may need to geocode this
            "ayanamsa": 1  # Lahiri ayanamsa
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # தமிழ் - Extract relevant chart data
                    chart_data = {
                        "nakshatra": data.get("nakshatra", {}).get("name", "Unknown"),
                        "rashi": data.get("rashi", {}).get("name", "Unknown"), 
                        "moon_sign": data.get("moon_sign", {}).get("name", "Unknown"),
                        "ascendant": data.get("ascendant", {}).get("name", "Unknown"),
                        "planetary_positions": data.get("planets", {}),
                        "dasha": data.get("current_dasha", {}).get("name", "Unknown"),
                        "birth_location": birth_location,
                        "birth_time": birth_time,
                        "birth_date": birth_date,
                        "raw_data": data  # Store full response for advanced features
                    }
                    
                    return chart_data
                else:
                    logger.error(f"Prokerala API error: {response.status}")
                    return {"error": f"API error: {response.status}"}
                    
    except Exception as e:
        logger.error(f"Prokerala API exception: {e}")
        
        # தமிழ் - Fallback to basic chart data
        return {
            "nakshatra": "Bharani",
            "rashi": "Mesha", 
            "moon_sign": "Aries",
            "ascendant": "Gemini",
            "planetary_positions": {
                "sun": {"sign": "Capricorn", "degree": 15.5},
                "moon": {"sign": "Aries", "degree": 22.3},
                "mars": {"sign": "Scorpio", "degree": 8.7}
            },
            "dasha": "Venus Mahadasha",
            "birth_location": birth_location,
            "birth_time": birth_time,
            "birth_date": birth_date,
            "note": "Using basic chart data - API temporarily unavailable"
        }

async def generate_spiritual_guidance(sku: str, question: str, birth_chart: Dict = None) -> str:
    """தமிழ் - Real OpenAI spiritual guidance generation"""
    try:
        # தமிழ் - Customize system prompt based on SKU
        sku_config = SKUS.get(sku, {})
        service_name = sku_config.get('name', 'Spiritual Guidance')
        duration = sku_config.get('duration_minutes', 15)
        
        # தமிழ் - Enhanced system prompt with birth chart data
        system_prompt = f"""{SWAMI_PERSONA}

Service Type: {service_name} ({duration} minutes)
Birth Chart Data: {birth_chart if birth_chart else 'Not provided'}

Instructions:
- Provide {duration} minutes worth of guidance (approximately {duration * 15} words)
- If birth chart is provided, incorporate astrological insights
- Focus on emotional healing and spiritual growth
- Use gentle, wise language befitting a Tamil spiritual elder
- End with a blessing and practical spiritual advice
"""

        # தמיழ் - Create OpenAI chat completion
        import openai
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"My question is: {question}"}
            ],
            max_tokens=duration * 20,  # Adjust based on service tier
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        guidance = response.choices[0].message.content.strip()
        
        # தமிழ் - Add service-specific closing
        if sku == 'elite':
            guidance += "\n\n🌟 As your Daily AstroCoach, I'll be here to guide you on this beautiful journey of spiritual awakening."
        
        return guidance
        
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        # தமிழ் - Fallback response if API fails
        return f"""🙏🏼 My dear child, the cosmic energies are shifting at this moment. 

Your question about "{question}" has reached my heart. While the digital channels are temporarily disrupted, I offer you this timeless wisdom:

Trust in the divine timing of your life. Every challenge you face is preparing you for greater spiritual growth. The answers you seek already reside within your soul - quiet your mind through meditation and listen to your inner voice.

May peace, love, and divine light guide your path forward.

Until the cosmic energies realign, practice gratitude and self-compassion.

Blessings and love,
Swami Jyotirananthan 🕉️"""
        
    except Exception as e:
        logger.error(f"Guidance generation exception: {e}")
        return "My dear child, the cosmic energies are shifting at this moment. Please try again in a few moments, and I shall provide the guidance your soul seeks. 🙏🏼"

async def trigger_salescloser_session(user_email: str, sku: str, session_id: int) -> Dict:
    """தமிழ் - Mock SalesCloser session trigger for testing"""
    try:
        sku_config = SKUS.get(sku, {})
        duration_minutes = sku_config.get('duration_minutes', 15)
        
        # தமிழ் - Mock successful response for testing
        return {
            "success": True, 
            "zoom_session_id": f"zoom_session_{session_id}_{sku}",
            "meeting_url": f"https://zoom.us/j/mock{session_id}",
            "duration_minutes": duration_minutes,
            "message": f"🙏🏼 Zoom session prepared for {sku_config.get('name', 'Spiritual Session')}"
        }
        
    except Exception as e:
        logger.error(f"SalesCloser webhook exception: {e}")
        return {"success": False, "error": "Zoom service temporarily unavailable"}


 # --- UCO (Unified Context Object) Management --- #
# தமிழ் - ஒருங்கிணைந்த சூழல் பொருள் மேலாண்மை
# English - Unified Context Object Management

async def get_uco_for_user(email: str) -> Optional[UCO]:
    """Get the Unified Context Object for a user."""
    conn = None
    try:
        conn = await get_db_connection()
        user_record = await conn.fetchrow("SELECT unified_context_object FROM users WHERE email = $1", email)
        if user_record and user_record['unified_context_object']:
            try:
                return UCO.parse_obj(user_record['unified_context_object'])
            except Exception as e:
                logger.error(f"Error parsing UCO for user {email}: {e}")
                # Create a basic UCO
                return UCO(user_profile={"email": email})
        # If no UCO, create a basic one
        user_profile_db = await conn.fetchrow("SELECT email, first_name, last_name, birth_date, birth_time, birth_location, preferred_language FROM users WHERE email = $1", email)
        if user_profile_db:
            return UCO(user_profile=dict(user_profile_db))
        return None
    except Exception as e:
        logger.error(f"Error getting UCO for user {email}: {e}")
        return None
    finally:
        if conn:
            await release_db_connection(conn)

async def update_uco_for_user(email: str, updates: Dict[str, Any]):
    """Update the Unified Context Object for a user."""
    conn = None
    try:
        conn = await get_db_connection()
        current_uco = await get_uco_for_user(email)
        if not current_uco:
            # Create a basic UCO if none exists
            user_profile_db = await conn.fetchrow("SELECT email, first_name, last_name, birth_date, birth_time, birth_location, preferred_language FROM users WHERE email = $1", email)
            if user_profile_db:
                current_uco = UCO(user_profile=dict(user_profile_db))
            else:
                current_uco = UCO(user_profile={"email": email})
        
        # Update UCO fields
        for key, value in updates.items():
            if hasattr(current_uco, key):
                setattr(current_uco, key, value)
        
        current_uco.updated_at = datetime.now(timezone.utc)
        uco_json = current_uco.json()
        await conn.execute("UPDATE users SET unified_context_object = $1, updated_at = NOW() WHERE email = $2", uco_json, email)
        logger.info(f"UCO updated for user {email}")
    except Exception as e:
        logger.error(f"Error updating UCO for user {email}: {e}")
    finally:
        if conn:
            await release_db_connection(conn)

async def add_interaction_to_history(interaction: InteractionLog) -> int:
    """Log an interaction and return its ID."""
    conn = None
    try:
        conn = await get_db_connection()
        query = """
            INSERT INTO interaction_history (user_email, session_id, timestamp, channel, sku_code, 
                                           user_query, swami_response_summary, emotional_state_detected, 
                                           key_insights_derived, follow_up_actions, external_transcript_id, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
        """
        record = await conn.fetchrow(query, interaction.user_email, interaction.session_id, interaction.timestamp,
                                    interaction.channel, interaction.sku_code, interaction.user_query,
                                    interaction.swami_response_summary, interaction.emotional_state_detected,
                                    json.dumps(interaction.key_insights_derived) if interaction.key_insights_derived else None,
                                    json.dumps(interaction.follow_up_actions) if interaction.follow_up_actions else None,
                                    interaction.external_transcript_id, 
                                    json.dumps(interaction.metadata) if interaction.metadata else None)
        if record and record['id']:
            interaction_id = record['id']
            # Update UCO with this new interaction ID
            uco = await get_uco_for_user(interaction.user_email)
            if uco:
                if interaction_id not in uco.interaction_history_ids:
                     uco.interaction_history_ids.append(interaction_id)
                uco.last_interaction_summary = interaction.dict()
                await update_uco_for_user(interaction.user_email, uco.dict(exclude_unset=True))
            return interaction_id
        return 0
    except Exception as e:
        logger.error(f"Error adding interaction to history for user {interaction.user_email}: {e}")
        return 0
    finally:
        if conn:
            await release_db_connection(conn)

# --- SKU, Product, Plan, Package Management --- #
# தமிழ் - SKU, தயாரிப்பு, திட்டம், தொகுப்பு மேலாண்மை
# English - SKU, Product, Plan, Package Management

# --- Stripe Integration Functions --- #
# தமிழ் - ஸ்ட்ரைப் ஒருங்கிணைப்பு செயல்பாடுகள்
# English - Stripe Integration Functions

async def create_stripe_checkout_session(user_email: str, price_id: str, quantity: int = 1, mode: str = "payment") -> str:
    """Creates a Stripe Checkout session and returns the redirect URL."""
    conn = None
    try:
        conn = await get_db_connection()
        user = await conn.fetchrow("SELECT stripe_customer_id FROM users WHERE email = $1", user_email)
        
        if not user or not user['stripe_customer_id']:
            # Create Stripe customer if not exists
            try:
                user_details = await conn.fetchrow("SELECT first_name, last_name FROM users WHERE email = $1", user_email)
                customer_name = f"{user_details['first_name'] if user_details else ''} {user_details['last_name'] if user_details else ''}".strip()
                
                new_customer = stripe.Customer.create(
                    email=user_email,
                    name=customer_name if customer_name else None
                )
                stripe_customer_id = new_customer.id
                await conn.execute("UPDATE users SET stripe_customer_id = $1 WHERE email = $2", stripe_customer_id, user_email)
            except Exception as e:
                logger.error(f"Failed to create Stripe customer for {user_email}: {e}")
                raise HTTPException(status_code=500, detail="Payment processing error (customer setup).")
        else:
            stripe_customer_id = user['stripe_customer_id']

        # Get host URL from request or environment
        host_url = os.getenv("HOST_URL", "http://localhost:8000" )
        success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}" 
        cancel_url = f"{host_url}/payment/cancel"

        try:
            checkout_session_params = {
                'customer': stripe_customer_id,
                'payment_method_types': ['card'],
                'line_items': [{'price': price_id, 'quantity': quantity}],
                'mode': mode, # 'payment' for one-time, 'subscription' for recurring
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': {
                    'user_email': user_email,
                    'jyotiflow_price_id': price_id
                }
            }
            
            if mode == 'subscription':
                checkout_session_params['subscription_data'] = {
                    'trial_from_plan': True # Or configure trial days
                }

            session = stripe.checkout.Session.create(**checkout_session_params)
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Checkout session creation failed for {user_email}, price {price_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating Stripe Checkout session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected payment error occurred.")
    finally:
        if conn:
            await release_db_connection(conn)

async def handle_stripe_webhook_event(event_data: Dict[str, Any], signature: str):
    """Handles verified Stripe webhook events."""
    conn = None
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload=json.dumps(event_data).encode('utf-8'), 
            sig_header=signature, 
            secret=STRIPE_WEBHOOK_SECRET
        )

        event_type = event['type']
        data_object = event['data']['object']
        
        # Try to get user email from various sources
        user_email = data_object.get('customer_email')
        if not user_email and data_object.get('customer_details'):
            user_email = data_object['customer_details'].get('email')
        
        # For subscription events, we might need to look up the user by customer ID
        if not user_email and event_type.startswith("customer.subscription"):
            customer_id = data_object.get('customer')
            if customer_id:
                conn = await get_db_connection()
                user_rec = await conn.fetchrow("SELECT email FROM users WHERE stripe_customer_id = $1", customer_id)
                if user_rec: 
                    user_email = user_rec['email']

        logger.info(f"Received Stripe webhook: {event_type} for user {user_email if user_email else 'N/A'}")

        if event_type == 'checkout.session.completed':
            session = data_object
            metadata = session.get('metadata', {})
            user_email = metadata.get('user_email') or user_email
            
            if user_email:
                # Payment successful, update credits or subscription status
                mode = session.get('mode')
                if mode == 'payment': # One-time purchase (e.g., credit pack)
                    # Get line items to find the price ID
                    line_items = stripe.checkout.Session.list_line_items(session.id, limit=1)
                    if line_items and line_items.data:
                        price_id = line_items.data[0].price.id
                        
                        # Find credit package by stripe_price_id
                        conn = await get_db_connection()
                        package = await conn.fetchrow(
                            "SELECT credits_amount FROM credit_packages WHERE stripe_price_id = $1", 
                            price_id
                        )
                        
                        if package:
                            # Add credits to user account
                            await conn.execute(
                                "UPDATE users SET credits = credits + $1, updated_at = NOW() WHERE email = $2",
                                package['credits_amount'], user_email
                            )
                            
                            # Log transaction
                            await conn.execute("""
                                INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
                                VALUES ($1, $2, $3, $4, NOW())
                            """, "stripe", "credit_purchase", user_email, 
                                f"Added {package['credits_amount']} credits via Stripe checkout")
                                
                            logger.info(f"Credits added: {package['credits_amount']} for user {user_email}")
                        else:
                            logger.error(f"Credit package not found for Stripe price_id {price_id} from session {session.id}")
                elif mode == 'subscription':
                    # Subscription created via checkout, handled by customer.subscription.created/updated
                    logger.info(f"Subscription checkout session completed for {user_email}. Stripe subscription ID: {session.get('subscription')}")
                    # Ensure user_subscriptions table is updated
                    await handle_subscription_event(session.get('subscription'), user_email, 'created', session)
            else:
                logger.error(f"User email not found in checkout.session.completed metadata: {session.id}")

        elif event_type in ['customer.subscription.created', 'customer.subscription.updated', 'customer.subscription.deleted']:
            subscription = data_object
            stripe_subscription_id = subscription.id
            status_action = event_type.split('.')[-1] # created, updated, deleted
            await handle_subscription_event(stripe_subscription_id, user_email, status_action, subscription)

        elif event_type == 'invoice.paid':
            invoice = data_object
            user_email = invoice.get('customer_email')
            stripe_subscription_id = invoice.get('subscription')
            if user_email and stripe_subscription_id:
                logger.info(f"Invoice paid for subscription {stripe_subscription_id} by {user_email}")
                # Grant credits based on plan if it's a renewal
                await handle_subscription_event(
                    stripe_subscription_id, 
                    user_email, 
                    'updated', 
                    stripe.Subscription.retrieve(stripe_subscription_id)
                )

        elif event_type == 'invoice.payment_failed':
            invoice = data_object
            user_email = invoice.get('customer_email')
            stripe_subscription_id = invoice.get('subscription')
            if user_email and stripe_subscription_id:
                logger.warning(f"Invoice payment failed for subscription {stripe_subscription_id} by {user_email}")
                # Update subscription status to past_due or handle dunning
                await handle_subscription_event(
                    stripe_subscription_id, 
                    user_email, 
                    'updated', 
                    stripe.Subscription.retrieve(stripe_subscription_id), 
                    is_failure=True
                )
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")
        
        return {"status": "success", "message": "Webhook processed"}
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")
    finally:
        if conn:
            await release_db_connection(conn)

async def handle_subscription_event(stripe_subscription_id: str, user_email: Optional[str], action: str, stripe_sub_object: Dict[str, Any], is_failure: bool = False):
    """Helper to manage user_subscriptions table based on Stripe subscription events."""
    conn = None
    try:
        conn = await get_db_connection()
        
        if not user_email:
            # Try to find user_email from stripe_customer_id
            customer_id = stripe_sub_object.get('customer')
            if customer_id:
                user_rec = await conn.fetchrow("SELECT email FROM users WHERE stripe_customer_id = $1", customer_id)
                if user_rec: 
                    user_email = user_rec['email']
            
            if not user_email:
                logger.error(f"Cannot handle subscription event for {stripe_subscription_id}: user_email not found.")
                return

        # Get the plan details from the subscription
        plan_stripe_price_id = stripe_sub_object['items']['data'][0]['price']['id']
        plan_record = await conn.fetchrow(
            "SELECT id, credits_granted FROM subscription_plans WHERE stripe_price_id = $1", 
            plan_stripe_price_id
        )
        
        if not plan_record:
            logger.error(f"Subscription plan with Stripe Price ID {plan_stripe_price_id} not found in DB.")
            return
        
        jyotiflow_plan_id = plan_record['id']
        credits_to_grant = plan_record['credits_granted']
        
        # Get subscription status
        status = stripe_sub_object['status'] # active, past_due, canceled, trialing, etc.
        if is_failure and status != 'past_due': 
            status = 'past_due' # Mark as past_due on payment failure

        # Get period dates
        current_period_start = datetime.fromtimestamp(stripe_sub_object['current_period_start'])
        current_period_end = datetime.fromtimestamp(stripe_sub_object['current_period_end'])
        cancel_at_period_end = stripe_sub_object['cancel_at_period_end']

        if action == 'created' or action == 'updated':
            # Insert or update subscription record
            query = """
                INSERT INTO user_subscriptions (user_email, subscription_plan_id, stripe_subscription_id, status, 
                                              current_period_start, current_period_end, cancel_at_period_end, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                ON CONFLICT (stripe_subscription_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    subscription_plan_id = EXCLUDED.subscription_plan_id, 
                    current_period_start = EXCLUDED.current_period_start,
                    current_period_end = EXCLUDED.current_period_end,
                    cancel_at_period_end = EXCLUDED.cancel_at_period_end,
                    updated_at = NOW()
                RETURNING id
            """
            await conn.execute(
                query, 
                user_email, jyotiflow_plan_id, stripe_subscription_id, status, 
                current_period_start, current_period_end, cancel_at_period_end
            )
            
            logger.info(f"User subscription {stripe_subscription_id} for {user_email} {action} in DB. Status: {status}")
            
            # Grant credits if subscription is active and it's a creation or a renewal
            if status == 'active' and credits_to_grant > 0:
                await conn.execute(
                    "UPDATE users SET credits = credits + $1, updated_at = NOW() WHERE email = $2",
                    credits_to_grant, user_email
                )
                
                # Log credit grant
                await conn.execute("""
                    INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
                    VALUES ($1, $2, $3, $4, NOW())
                """, "system", "subscription_credits", user_email, 
                    f"Granted {credits_to_grant} credits for subscription {stripe_subscription_id}")
                    
                logger.info(f"Granted {credits_to_grant} credits to {user_email} for subscription {stripe_subscription_id}")

        elif action == 'deleted': # Subscription canceled
            # Update status to 'canceled' or remove the record
            await conn.execute(
                "UPDATE user_subscriptions SET status = 'canceled', updated_at = NOW() WHERE stripe_subscription_id = $1", 
                stripe_subscription_id
            )
            logger.info(f"User subscription {stripe_subscription_id} for {user_email} marked as canceled in DB.")
        
        # Update UCO with subscription status if UCO exists
        try:
            uco_record = await conn.fetchrow("SELECT unified_context_object FROM users WHERE email = $1", user_email)
            if uco_record and uco_record['unified_context_object']:
                uco = json.loads(uco_record['unified_context_object'])
                uco['current_subscription_id'] = jyotiflow_plan_id if status == 'active' else None
                uco['subscription_status'] = status
                uco['updated_at'] = datetime.now().isoformat()
                await conn.execute(
                    "UPDATE users SET unified_context_object = $1, updated_at = NOW() WHERE email = $2",
                    json.dumps(uco), user_email
                )
        except Exception as e:
            logger.error(f"Error updating UCO with subscription info for {user_email}: {e}")
    
    except Exception as e:
        logger.error(f"Error handling subscription event for {stripe_subscription_id}: {e}", exc_info=True)
    finally:
        if conn:
            await release_db_connection(conn)


# Product Functions
async def create_product_in_db(product_data: ProductCreate) -> Product:
    """Create a product in the database and Stripe."""
    conn = None
    try:
        conn = await get_db_connection()
        # Create in Stripe first
        stripe_product = None
        try:
            stripe_product = stripe.Product.create(
                name=product_data.name,
                description=product_data.description,
                metadata={'sku_code': product_data.sku_code, 'service_type': product_data.service_type}
            )
        except Exception as e:
            logger.error(f"Failed to create Stripe product for {product_data.sku_code}: {e}")

        query = """
            INSERT INTO products (sku_code, name, description, service_type, status, features, default_image_url, stripe_product_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, sku_code, name, description, service_type, status, features, default_image_url, stripe_product_id, created_at, updated_at
        """
        record = await conn.fetchrow(query, product_data.sku_code, product_data.name, product_data.description,
                                   product_data.service_type, product_data.status, json.dumps(product_data.features),
                                   product_data.default_image_url, stripe_product.id if stripe_product else None)
        if not record: raise HTTPException(500, "Failed to create product in DB")
        return Product(**dict(record))
    except Exception as e:
        logger.error(f"Error creating product {product_data.sku_code}: {e}")
        raise HTTPException(500, f"Failed to create product: {str(e)}")
    finally:
        if conn:
            await release_db_connection(conn)

async def get_product_by_id(product_id: int) -> Optional[Product]:
    """Get a product by ID."""
    conn = None
    try:
        conn = await get_db_connection()
        record = await conn.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
        return Product(**dict(record)) if record else None
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        return None
    finally:
        if conn:
            await release_db_connection(conn)

async def get_product_by_sku(sku_code: str) -> Optional[Product]:
    """Get a product by SKU code."""
    conn = None
    try:
        conn = await get_db_connection()
        record = await conn.fetchrow("SELECT * FROM products WHERE sku_code = $1", sku_code)
        return Product(**dict(record)) if record else None
    except Exception as e:
        logger.error(f"Error getting product by SKU {sku_code}: {e}")
        return None
    finally:
        if conn:
            await release_db_connection(conn)



# --- SalesCloser & Multi-channel Messaging --- #
# தமிழ் - சேல்ஸ்க்ளோசர் மற்றும் பல-சேனல் செய்தியிடல்
# English - SalesCloser & Multi-channel Messaging

async def trigger_salescloser_flow(user_email: str, flow_id: str, context_data: Dict[str, Any]):
    """Trigger a SalesCloser flow with given context."""
    try:
        headers = {"Authorization": f"Bearer {SALESCLOSER_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "flow_id": flow_id,
            "contact_identifier": user_email,
            "context": context_data
        }
        salescloser_trigger_url = SALESCLOSER_WEBHOOK_URL 

        async with aiohttp.ClientSession( ) as http_session:
            async with http_session.post(salescloser_trigger_url, headers=headers, json=payload ) as response:
                if 200 <= response.status < 300:
                    logger.info(f"Successfully triggered SalesCloser flow {flow_id} for user {user_email}")
                    return {"success": True, "message": "SalesCloser flow triggered."}
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to trigger SalesCloser flow {flow_id} for {user_email}. Status: {response.status}, Response: {response_text}")
                    return {"success": False, "error": f"SalesCloser API error ({response.status})", "details": response_text}
    except Exception as e:
        logger.error(f"Exception triggering SalesCloser flow for {user_email}: {e}")
        return {"success": False, "error": "Failed to connect to SalesCloser service."}

async def send_follow_up_message(user_email: str, channel: str, message_content: str, context: Optional[Dict[str, Any]] = None):
    """Send a follow-up message via the specified channel (through Make.com)."""
    try:
        target_webhook_url = None
        if channel == "whatsapp": 
            target_webhook_url = os.getenv("MAKE_COM_WEBHOOK_URL_WHATSAPP", "your_make_com_whatsapp_webhook")
        elif channel == "email": 
            target_webhook_url = os.getenv("MAKE_COM_WEBHOOK_URL_EMAIL", "your_make_com_email_webhook")
        elif channel == "sms": 
            target_webhook_url = os.getenv("MAKE_COM_WEBHOOK_URL_SMS", "your_make_com_sms_webhook")
        else: 
            logger.warning(f"Unsupported follow-up channel: {channel} for user {user_email}")
            return {"success": False, "error": "Unsupported channel"}

        if not target_webhook_url or target_webhook_url == "your_make_com_..._webhook":
            logger.error(f"Make.com webhook URL for channel {channel} is not configured.")
            return {"success": False, "error": f"Webhook for {channel} not configured."}

        payload = {
            "user_email": user_email,
            "message": message_content,
            "jyotiflow_context": context or {}
        }
        
        async with aiohttp.ClientSession( ) as http_session:
            async with http_session.post(target_webhook_url, json=payload ) as response:
                if 200 <= response.status < 300:
                    logger.info(f"Successfully sent {channel} follow-up to {user_email} via Make.com")
                    # Log this interaction
                    await add_interaction_to_history(InteractionLog(
                        user_email=user_email,
                        channel=f"follow_up_{channel}",
                        swami_response_summary=message_content[:200] # Summary
                    ))
                    return {"success": True}
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to send {channel} follow-up to {user_email} via Make.com. Status: {response.status}, Response: {response_text}")
                    return {"success": False, "error": f"Make.com webhook error ({response.status})", "details": response_text}
    except Exception as e:
        logger.error(f"Exception sending {channel} follow-up for {user_email}: {e}")
        return {"success": False, "error": "Failed to connect to messaging service."}


# தமிழ் - API Routes

@app.get("/", response_class=HTMLResponse)
def homepage():
    """தமிழ் - Homepage with spiritual service offerings"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
 
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 JyotiFlow.ai - Swami Jyotirananthan's Digital Ashram</title>
        <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    line-height: 1.6;
                }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; color: white; margin-bottom: 50px; }
                .header h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
                .header p { font-size: 1.2rem; opacity: 0.9; }
                .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; margin-bottom: 50px; }
                .service-card { 
                    background: white; 
                    border-radius: 15px; 
                    padding: 30px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                    text-align: center;
                }
                .service-card:hover { transform: translateY(-5px); }
                .service-card h3 { color: #667eea; font-size: 1.5rem; margin-bottom: 15px; }
                .service-card .price { font-size: 2rem; font-weight: bold; color: #764ba2; margin: 15px 0; }
                .service-card .description { color: #666; margin-bottom: 20px; }
                .btn { 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    padding: 12px 30px; 
                    border: none; 
                    border-radius: 25px; 
                    cursor: pointer;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }
                .btn:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
                .footer { text-align: center; color: white; margin-top: 50px; opacity: 0.8; }
                @media (max-width: 768px) {
                    .header h1 { font-size: 2rem; }
                    .services { grid-template-columns: 1fr; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🙏🏼 JyotiFlow.ai</h1>
                    <p>Swami Jyotirananthan's Digital Ashram for Spiritual Guidance</p>
                    <p>Ancient Vedic Wisdom meets Modern AI Technology</p>
                </div>
                
                <div class="services">
                    <div class="service-card">
                        <h3>✨ Clarity Plus</h3>
                        <div class="price">$9</div>
                        <div class="description">Quick emotional support and life clarity for immediate guidance</div>
                        <div class="duration">15 minutes • 1 credit</div>
                        <br>
                        <a href="/session/clarity" class="btn">Start Session</a>
                    </div>
                    
                    <div class="service-card">
                        <h3>💕 AstroLove Whisper</h3>
                        <div class="price">$19</div>
                        <div class="description">Deep relationship and love insights based on astrological principles</div>
                        <div class="duration">30 minutes • 3 credits</div>
                        <br>
                        <a href="/session/love" class="btn">Start Session</a>
                    </div>
                    
                    <div class="service-card">
                        <h3>🔮 R3 Live Premium</h3>
                        <div class="price">$39</div>
                        <div class="description">Comprehensive spiritual life reading covering all major life areas</div>
                        <div class="duration">45 minutes • 6 credits</div>
                        <br>
                        <a href="/session/premium" class="btn">Start Session</a>
                    </div>
                    
                    <div class="service-card">
                        <h3>🌟 Daily AstroCoach</h3>
                        <div class="price">$149/month</div>
                        <div class="description">Monthly spiritual coaching with daily insights and guidance</div>
                        <div class="duration">60 minutes • 12 credits</div>
                        <br>
                        <a href="/session/elite" class="btn">Start Session</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🕉️ May your spiritual journey be filled with light and wisdom 🕉️</p>
                    <p><a href="/login" style="color: white;">Login</a> | <a href="/register" style="color: white;">Register</a> | <a href="/admin" style="color: white;">Admin</a></p>
                </div>
            </div>
        </body>
        </html>
    """
    return HTMLResponse(content=html_content)

@app.get('/session/clarity')
def clarity_page():
    CLARITY_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 Clarity Plus - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }
            
            .header {
                margin-bottom: 40px;
            }
            
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .service-icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            .service-title {
                font-size: 2rem;
                margin-bottom: 15px;
                color: #FFD700;
            }
            
            .service-price {
                font-size: 3rem;
                font-weight: bold;
                color: #87CEEB;
                margin-bottom: 20px;
            }
            
            .service-description {
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .question-form {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input, .form-textarea {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .form-textarea {
                height: 120px;
                resize: vertical;
            }
            
            .btn {
                background: linear-gradient(45deg, #FFD700, #FFA500);
                color: #333;
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(255, 215, 0, 0.3);
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            .guidance-result {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                text-align: left;
                display: none;
            }
            
            .guidance-title {
                color: #FFD700;
                font-size: 1.5rem;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .guidance-text {
                line-height: 1.8;
                font-size: 1.1rem;
            }
            
            .nav-links {
                margin-top: 40px;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                margin: 0 15px;
                font-size: 1rem;
            }
            
            .nav-links a:hover {
                color: #FFD700;
            }
            
            @media (max-width: 768px) {
                .title {
                    font-size: 2rem;
                }
                
                .service-card {
                    padding: 30px 20px;
                }
                
                .service-price {
                    font-size: 2.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🙏🏼</div>
                <h1 class="title">JyotiFlow.ai</h1>
                <p class="subtitle">Swami Jyotirananthan's Digital Ashram</p>
            </div>
            
            <div class="service-card">
                <div class="service-icon">✨</div>
                <h2 class="service-title">Clarity Plus</h2>
                <div class="service-price">$9</div>
                <p class="service-description">
                    Instant emotional support and life clarity. Perfect for quick guidance on pressing questions.
                    Receive immediate spiritual insights to help you navigate life's challenges with wisdom and peace.
                </p>
                
                <div class="question-form">
                    <h3 style="color: #FFD700; margin-bottom: 20px; text-align: center;">Ask Your Question</h3>
                    <form id="clarityForm">
                        <div class="form-group">
                            <label class="form-label">Your Question:</label>
                            <textarea class="form-textarea" id="question" placeholder="What guidance do you seek from Swami Jyotirananthan?" required></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Birth Date (Optional):</label>
                            <input type="date" class="form-input" id="birthDate">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Birth Time (Optional):</label>
                            <input type="time" class="form-input" id="birthTime">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Birth Place (Optional):</label>
                            <input type="text" class="form-input" id="birthPlace" placeholder="City, Country">
                        </div>
                        
                        <button type="submit" class="btn">🔮 Receive Guidance ($9)</button>
                    </form>
                </div>
                
                <div id="guidanceResult" class="guidance-result">
                    <h3 class="guidance-title">🙏🏼 Swami Jyotirananthan's Guidance</h3>
                    <div id="guidanceText" class="guidance-text"></div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/astrolove">💕 AstroLove</a>
                <a href="/r3live">🔮 R3 Live</a>
                <a href="/daily">🌟 Daily Coach</a>
                <a href="/login">🔐 Login</a>
            </div>
        </div>
        
        <script>
            document.getElementById('clarityForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const question = document.getElementById('question').value;
                const birthDate = document.getElementById('birthDate').value;
                const birthTime = document.getElementById('birthTime').value;
                const birthPlace = document.getElementById('birthPlace').value;
                
                // Show loading
                const resultDiv = document.getElementById('guidanceResult');
                const textDiv = document.getElementById('guidanceText');
                textDiv.innerHTML = '🔮 Swami Jyotirananthan is channeling cosmic wisdom for you...';
                resultDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/api/session/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            service_type: 'clarity',
                            question: question,
                            birth_date: birthDate,
                            birth_time: birthTime,
                            birth_location: birthPlace
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        textDiv.innerHTML = data.guidance;
                    } else {
                        textDiv.innerHTML = '🙏🏼 ' + (data.message || 'Please ensure you have sufficient credits and try again.');
                    }
                } catch (error) {
                    textDiv.innerHTML = '🙏🏼 The cosmic energies are temporarily disrupted. Please try again in a moment.';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=CLARITY_TEMPLATE)

@app.get('/session/love')
def astrolove_page():
    ASTROLOVE_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 AstroLove Whisper - JyotiFlow.ai</title>
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 50%, #ff9ff3 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }
        
        .header {
            margin-bottom: 40px;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        .title {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        
        .service-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .service-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        .service-title {
            font-size: 2rem;
            margin-bottom: 15px;
            color: #FFD700;
        }
        
        .service-price {
            font-size: 3rem;
            font-weight: bold;
            color: #ff9ff3;
            margin-bottom: 20px;
        }
        
        .service-description {
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .question-form {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #FFD700;
        }
        
        .form-input, .form-textarea, .form-select {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            font-size: 1rem;
        }
        
        .form-textarea {
            height: 120px;
            resize: vertical;
        }
        
        .btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .guidance-result {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            text-align: left;
            display: none;
        }
        
        .guidance-title {
            color: #FFD700;
            font-size: 1.5rem;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .guidance-text {
            line-height: 1.8;
            font-size: 1.1rem;
        }
        
        .nav-links {
            margin-top: 40px;
        }
        
        .nav-links a {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            margin: 0 15px;
            font-size: 1rem;
        }
        
        .nav-links a:hover {
            color: #FFD700;
        }
        
        @media (max-width: 768px) {
            .title {
                font-size: 2rem;
            }
            
            .service-card {
                padding: 30px 20px;
            }
            
            .service-price {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🙏🏼</div>
            <h1 class="title">JyotiFlow.ai</h1>
            <p class="subtitle">Swami Jyotirananthan's Digital Ashram</p>
        </div>
        
        <div class="service-card">
            <div class="service-icon">💕</div>
            <h2 class="service-title">AstroLove Whisper</h2>
            <div class="service-price">$19</div>
            <p class="service-description">
                Deep relationship and love insights. Understand your romantic path and heart's desires.
                Discover the cosmic influences on your love life and receive guidance for meaningful connections.
            </p>
            
            <div class="question-form">
                <h3 style="color: #FFD700; margin-bottom: 20px; text-align: center;">Love & Relationship Guidance</h3>
                <form id="astroloveForm">
                    <div class="form-group">
                        <label class="form-label">Your Love Question:</label>
                        <textarea class="form-textarea" id="question" placeholder="What guidance do you seek about love and relationships?" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Relationship Status:</label>
                        <select class="form-select" id="relationshipStatus">
                            <option value="">Select your status</option>
                            <option value="single">Single</option>
                            <option value="dating">Dating</option>
                            <option value="committed">In a committed relationship</option>
                            <option value="married">Married</option>
                            <option value="complicated">It's complicated</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Your Birth Date:</label>
                        <input type="date" class="form-input" id="birthDate" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Your Birth Time:</label>
                        <input type="time" class="form-input" id="birthTime">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Your Birth Place:</label>
                        <input type="text" class="form-input" id="birthPlace" placeholder="City, Country" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Partner's Birth Date (Optional):</label>
                        <input type="date" class="form-input" id="partnerBirthDate">
                    </div>
                    
                    <button type="submit" class="btn">💕 Receive Love Guidance ($19)</button>
                </form>
            </div>
            
            <div id="guidanceResult" class="guidance-result">
                <h3 class="guidance-title">💕 Swami Jyotirananthan's Love Wisdom</h3>
                <div id="guidanceText" class="guidance-text"></div>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/clarity">✨ Clarity</a>
            <a href="/r3live">🔮 R3 Live</a>
            <a href="/daily">🌟 Daily Coach</a>
            <a href="/login">🔐 Login</a>
        </div>
    </div>
    
    <script>
        document.getElementById('astroloveForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const relationshipStatus = document.getElementById('relationshipStatus').value;
            const birthDate = document.getElementById('birthDate').value;
            const birthTime = document.getElementById('birthTime').value;
            const birthPlace = document.getElementById('birthPlace').value;
            const partnerBirthDate = document.getElementById('partnerBirthDate').value;
            
            // Show loading
            const resultDiv = document.getElementById('guidanceResult');
            const textDiv = document.getElementById('guidanceText');
            textDiv.innerHTML = '💕 Swami Jyotirananthan is consulting the cosmic forces of love for you...';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/session/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        service_type: 'love',
                        question: question,
                        relationship_status: relationshipStatus,
                        birth_date: birthDate,
                        birth_time: birthTime,
                        birth_location: birthPlace,
                        partner_birth_date: partnerBirthDate
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    textDiv.innerHTML = data.guidance;
                } else {
                    textDiv.innerHTML = '💕 ' + (data.message || 'Please ensure you have sufficient credits and try again.');
                }
            } catch (error) {
                textDiv.innerHTML = '💕 The cosmic love energies are temporarily disrupted. Please try again in a moment.';
            }
        });
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=ASTROLOVE_TEMPLATE)

@app.get('/session/premium')
def r3live_page():
    R3_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 R3 Live Premium - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #9b59b6 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                text-align: center;
            }
            
            .header {
                margin-bottom: 40px;
            }
            
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .service-icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            .service-title {
                font-size: 2rem;
                margin-bottom: 15px;
                color: #FFD700;
            }
            
            .service-price {
                font-size: 3rem;
                font-weight: bold;
                color: #9b59b6;
                margin-bottom: 20px;
            }
            
            .service-description {
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            }
            
            .feature-icon {
                font-size: 2rem;
                margin-bottom: 10px;
            }
            
            .feature-title {
                color: #FFD700;
                font-size: 1.1rem;
                margin-bottom: 8px;
            }
            
            .feature-desc {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .question-form {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input, .form-textarea, .form-select {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .form-textarea {
                height: 120px;
                resize: vertical;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .btn {
                background: linear-gradient(45deg, #3498db, #9b59b6);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3);
            }
            
            .guidance-result {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                text-align: left;
                display: none;
            }
            
            .guidance-title {
                color: #FFD700;
                font-size: 1.5rem;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .guidance-text {
                line-height: 1.8;
                font-size: 1.1rem;
            }
            
            .nav-links {
                margin-top: 40px;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                margin: 0 15px;
                font-size: 1rem;
            }
            
            .nav-links a:hover {
                color: #FFD700;
            }
            
            @media (max-width: 768px) {
                .title {
                    font-size: 2rem;
                }
                
                .service-card {
                    padding: 30px 20px;
                }
                
                .service-price {
                    font-size: 2.5rem;
                }
                
                .form-row {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🙏🏼</div>
                <h1 class="title">JyotiFlow.ai</h1>
                <p class="subtitle">Swami Jyotirananthan's Digital Ashram</p>
            </div>
            
            <div class="service-card">
                <div class="service-icon">🔮</div>
                <h2 class="service-title">R3 Live Premium</h2>
                <div class="service-price">$39</div>
                <p class="service-description">
                    Comprehensive spiritual life reading covering all major areas of your existence.
                    Receive deep insights into your life purpose, relationships, career, health, and spiritual growth.
                </p>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🌟</div>
                        <div class="feature-title">Life Purpose</div>
                        <div class="feature-desc">Discover your soul's mission</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💼</div>
                        <div class="feature-title">Career Path</div>
                        <div class="feature-desc">Professional guidance & timing</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">❤️</div>
                        <div class="feature-title">Relationships</div>
                        <div class="feature-desc">Love, family & social connections</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🏥</div>
                        <div class="feature-title">Health & Wellness</div>
                        <div class="feature-desc">Physical & mental well-being</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💰</div>
                        <div class="feature-title">Wealth & Prosperity</div>
                        <div class="feature-desc">Financial abundance insights</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🧘</div>
                        <div class="feature-title">Spiritual Growth</div>
                        <div class="feature-desc">Enlightenment & inner peace</div>
                    </div>
                </div>
                
                <div class="question-form">
                    <h3 style="color: #FFD700; margin-bottom: 20px; text-align: center;">Complete Life Reading</h3>
                    <form id="r3Form">
                        <div class="form-group">
                            <label class="form-label">Primary Life Question:</label>
                            <textarea class="form-textarea" id="question" placeholder="What aspect of your life needs the most guidance right now?" required></textarea>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Birth Date:</label>
                                <input type="date" class="form-input" id="birthDate" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Birth Time:</label>
                                <input type="time" class="form-input" id="birthTime" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Birth Place:</label>
                            <input type="text" class="form-input" id="birthPlace" placeholder="City, Country" required>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Current Life Stage:</label>
                                <select class="form-select" id="lifeStage">
                                    <option value="">Select your stage</option>
                                    <option value="student">Student</option>
                                    <option value="early_career">Early Career</option>
                                    <option value="established">Established Professional</option>
                                    <option value="midlife">Midlife Transition</option>
                                    <option value="senior">Senior Years</option>
                                    <option value="retirement">Retirement</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Priority Area:</label>
                                <select class="form-select" id="priorityArea">
                                    <option value="">Select focus area</option>
                                    <option value="career">Career & Purpose</option>
                                    <option value="relationships">Relationships</option>
                                    <option value="health">Health & Wellness</option>
                                    <option value="wealth">Wealth & Prosperity</option>
                                    <option value="spiritual">Spiritual Growth</option>
                                    <option value="family">Family & Children</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Additional Context (Optional):</label>
                            <textarea class="form-textarea" id="context" placeholder="Share any additional details about your current situation or specific challenges..."></textarea>
                        </div>
                        
                        <button type="submit" class="btn">🔮 Receive Complete Reading ($39)</button>
                    </form>
                </div>
                
                <div id="guidanceResult" class="guidance-result">
                    <h3 class="guidance-title">🔮 Swami Jyotirananthan's Complete Life Reading</h3>
                    <div id="guidanceText" class="guidance-text"></div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/clarity">✨ Clarity</a>
                <a href="/astrolove">💕 AstroLove</a>
                <a href="/daily">🌟 Daily Coach</a>
                <a href="/login">🔐 Login</a>
            </div>
        </div>
        
        <script>
            document.getElementById('r3Form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const question = document.getElementById('question').value;
                const birthDate = document.getElementById('birthDate').value;
                const birthTime = document.getElementById('birthTime').value;
                const birthPlace = document.getElementById('birthPlace').value;
                const lifeStage = document.getElementById('lifeStage').value;
                const priorityArea = document.getElementById('priorityArea').value;
                const context = document.getElementById('context').value;
                
                // Show loading
                const resultDiv = document.getElementById('guidanceResult');
                const textDiv = document.getElementById('guidanceText');
                textDiv.innerHTML = '🔮 Swami Jyotirananthan is performing a comprehensive cosmic analysis of your life path...';
                resultDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/api/session/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            service_type: 'premium',
                            question: question,
                            birth_date: birthDate,
                            birth_time: birthTime,
                            birth_location: birthPlace,
                            life_stage: lifeStage,
                            priority_area: priorityArea,
                            context: context
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        textDiv.innerHTML = data.guidance;
                    } else {
                        textDiv.innerHTML = '🔮 ' + (data.message || 'Please ensure you have sufficient credits and try again.');
                    }
                } catch (error) {
                    textDiv.innerHTML = '🔮 The cosmic energies are temporarily disrupted. Please try again in a moment.';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=R3_TEMPLATE)

@app.get('/session/elite')
def daily_page():
    DAILY_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 Daily AstroCoach - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                text-align: center;
            }
            
            .header {
                margin-bottom: 40px;
            }
            
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .service-icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            .service-title {
                font-size: 2rem;
                margin-bottom: 15px;
                color: #FFD700;
            }
            
            .service-price {
                font-size: 3rem;
                font-weight: bold;
                color: #4facfe;
                margin-bottom: 20px;
            }
            
            .service-description {
                font-size: 1.1rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .subscription-features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            }
            
            .feature-icon {
                font-size: 2rem;
                margin-bottom: 10px;
            }
            
            .feature-title {
                color: #FFD700;
                font-size: 1rem;
                margin-bottom: 8px;
            }
            
            .feature-desc {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .question-form {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input, .form-textarea, .form-select {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .form-textarea {
                height: 120px;
                resize: vertical;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .btn {
                background: linear-gradient(45deg, #f093fb, #f5576c);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(240, 147, 251, 0.3);
            }
            
            .btn-large {
                padding: 20px 50px;
                font-size: 1.3rem;
            }
            
            .guidance-result {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                text-align: left;
                display: none;
            }
            
            .guidance-title {
                color: #FFD700;
                font-size: 1.5rem;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .guidance-text {
                line-height: 1.8;
                font-size: 1.1rem;
            }
            
            .subscription-info {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 25px;
                margin: 25px 0;
                border: 2px solid rgba(255, 215, 0, 0.3);
            }
            
            .nav-links {
                margin-top: 40px;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                margin: 0 15px;
                font-size: 1rem;
            }
            
            .nav-links a:hover {
                color: #FFD700;
            }
            
            @media (max-width: 768px) {
                .title {
                    font-size: 2rem;
                }
                
                .service-card {
                    padding: 30px 20px;
                }
                
                .service-price {
                    font-size: 2.5rem;
                }
                
                .form-row {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🙏🏼</div>
                <h1 class="title">JyotiFlow.ai</h1>
                <p class="subtitle">Swami Jyotirananthan's Digital Ashram</p>
            </div>
            
            <div class="service-card">
                <div class="service-icon">🌟</div>
                <h2 class="service-title">Daily AstroCoach</h2>
                <div class="service-price">$149</div>
                <p class="service-description">
                    Ongoing spiritual coaching with daily insights and personalized guidance.
                    Transform your life with consistent spiritual support and cosmic wisdom delivered daily.
                </p>
                
                <div class="subscription-info">
                    <h3 style="color: #FFD700; text-align: center; margin-bottom: 15px;">Monthly Subscription Includes:</h3>
                    <div class="subscription-features">
                        <div class="feature-card">
                            <div class="feature-icon">📅</div>
                            <div class="feature-title">Daily Guidance</div>
                            <div class="feature-desc">Personalized insights every day</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🌙</div>
                            <div class="feature-title">Moon Phase Alerts</div>
                            <div class="feature-desc">Cosmic timing notifications</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">⭐</div>
                            <div class="feature-title">Weekly Forecasts</div>
                            <div class="feature-desc">Detailed weekly predictions</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🎯</div>
                            <div class="feature-title">Goal Tracking</div>
                            <div class="feature-desc">Spiritual progress monitoring</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💬</div>
                            <div class="feature-title">Priority Support</div>
                            <div class="feature-desc">Direct access to guidance</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📚</div>
                            <div class="feature-title">Wisdom Library</div>
                            <div class="feature-desc">Exclusive spiritual content</div>
                        </div>
                    </div>
                </div>
                
                <div class="question-form">
                    <h3 style="color: #FFD700; margin-bottom: 20px; text-align: center;">Start Your Daily Spiritual Journey</h3>
                    <form id="dailyForm">
                        <div class="form-group">
                            <label class="form-label">Your Spiritual Goals:</label>
                            <textarea class="form-textarea" id="goals" placeholder="What do you hope to achieve through daily spiritual guidance?" required></textarea>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Birth Date:</label>
                                <input type="date" class="form-input" id="birthDate" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Birth Time:</label>
                                <input type="time" class="form-input" id="birthTime" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Birth Place:</label>
                            <input type="text" class="form-input" id="birthPlace" placeholder="City, Country" required>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Current Life Focus:</label>
                                <select class="form-select" id="lifeFocus">
                                    <option value="">Select your focus</option>
                                    <option value="career">Career & Success</option>
                                    <option value="relationships">Love & Relationships</option>
                                    <option value="health">Health & Wellness</option>
                                    <option value="spiritual">Spiritual Growth</option>
                                    <option value="family">Family & Home</option>
                                    <option value="creativity">Creativity & Expression</option>
                                    <option value="wealth">Wealth & Abundance</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Preferred Guidance Time:</label>
                                <select class="form-select" id="guidanceTime">
                                    <option value="">Select time</option>
                                    <option value="morning">Morning (6-10 AM)</option>
                                    <option value="afternoon">Afternoon (12-4 PM)</option>
                                    <option value="evening">Evening (6-10 PM)</option>
                                    <option value="night">Night (10 PM-12 AM)</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Current Challenges (Optional):</label>
                            <textarea class="form-textarea" id="challenges" placeholder="What challenges are you currently facing that you'd like daily support with?"></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-large">🌟 Start Monthly Subscription ($149)</button>
                    </form>
                </div>
                
                <div id="guidanceResult" class="guidance-result">
                    <h3 class="guidance-title">🌟 Welcome to Daily AstroCoach</h3>
                    <div id="guidanceText" class="guidance-text"></div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/clarity">✨ Clarity</a>
                <a href="/astrolove">💕 AstroLove</a>
                <a href="/r3live">🔮 R3 Live</a>
                <a href="/login">🔐 Login</a>
            </div>
        </div>
        
        <script>
            document.getElementById('dailyForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const goals = document.getElementById('goals').value;
                const birthDate = document.getElementById('birthDate').value;
                const birthTime = document.getElementById('birthTime').value;
                const birthPlace = document.getElementById('birthPlace').value;
                const lifeFocus = document.getElementById('lifeFocus').value;
                const guidanceTime = document.getElementById('guidanceTime').value;
                const challenges = document.getElementById('challenges').value;
                
                // Show loading
                const resultDiv = document.getElementById('guidanceResult');
                const textDiv = document.getElementById('guidanceText');
                textDiv.innerHTML = '🌟 Swami Jyotirananthan is setting up your personalized daily spiritual coaching program...';
                resultDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/api/session/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            service_type: 'elite',
                            goals: goals,
                            birth_date: birthDate,
                            birth_time: birthTime,
                            birth_location: birthPlace,
                            life_focus: lifeFocus,
                            guidance_time: guidanceTime,
                            challenges: challenges
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        textDiv.innerHTML = data.guidance;
                    } else {
                        textDiv.innerHTML = '🌟 ' + (data.message || 'Please ensure you have sufficient credits and try again.');
                    }
                } catch (error) {
                    textDiv.innerHTML = '🌟 The cosmic energies are temporarily disrupted. Please try again in a moment.';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=DAILY_TEMPLATE)

@app.get('/login')
def login_page():
    LOGIN_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 Login - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .login-container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                width: 100%;
                max-width: 400px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 2rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .form-input:focus {
                outline: none;
                box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
            }
            
            .btn {
                background: linear-gradient(45deg, #FFD700, #FFA500);
                color: #333;
                border: none;
                padding: 12px 30px;
                border-radius: 50px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                margin: 10px 0;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(255, 215, 0, 0.3);
            }
            
            .link {
                color: #87CEEB;
                text-decoration: none;
                font-size: 0.9rem;
            }
            
            .link:hover {
                color: #FFD700;
            }
            
            .divider {
                margin: 20px 0;
                text-align: center;
                opacity: 0.7;
            }
            
            .error-message {
                background: rgba(255, 0, 0, 0.2);
                border: 1px solid rgba(255, 0, 0, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                color: #ffcccc;
                display: none;
            }
            
            .success-message {
                background: rgba(0, 255, 0, 0.2);
                border: 1px solid rgba(0, 255, 0, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                color: #ccffcc;
                display: none;
            }
            
            .nav-links {
                margin-top: 30px;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                margin: 0 10px;
                font-size: 0.9rem;
            }
            
            .nav-links a:hover {
                color: #FFD700;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🙏🏼</div>
            <h1 class="title">JyotiFlow.ai</h1>
            <p class="subtitle">Enter the Digital Ashram</p>
            
            <div id="errorMessage" class="error-message"></div>
            <div id="successMessage" class="success-message"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label">Email:</label>
                    <input type="email" class="form-input" id="email" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Password:</label>
                    <input type="password" class="form-input" id="password" required>
                </div>
                
                <button type="submit" class="btn">🔐 Enter Ashram</button>
            </form>
            
            <div class="divider">
                <p>Don't have an account? <a href="/register" class="link">Create one here</a></p>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/admin">👑 Admin</a>
            </div>
        </div>
        
        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                const errorDiv = document.getElementById('errorMessage');
                const successDiv = document.getElementById('successMessage');
                
                // Hide previous messages
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        successDiv.textContent = 'Welcome to the Digital Ashram! Redirecting...';
                        successDiv.style.display = 'block';
                        
                        // Store token and redirect
                        localStorage.setItem('jyoti_token', data.token);
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1500);
                    } else {
                        errorDiv.textContent = data.message || 'Login failed. Please check your credentials.';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Connection error. Please try again.';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=LOGIN_TEMPLATE)

@app.get('/register')
def register_page():
    REGISTER_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 Register - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .register-container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                width: 100%;
                max-width: 450px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .logo {
                font-size: 3rem;
                margin-bottom: 10px;
            }
            
            .title {
                font-size: 2rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .form-input:focus {
                outline: none;
                box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
            }
            
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .btn {
                background: linear-gradient(45deg, #FFD700, #FFA500);
                color: #333;
                border: none;
                padding: 12px 30px;
                border-radius: 50px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                margin: 10px 0;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(255, 215, 0, 0.3);
            }
            
            .link {
                color: #87CEEB;
                text-decoration: none;
                font-size: 0.9rem;
            }
            
            .link:hover {
                color: #FFD700;
            }
            
            .divider {
                margin: 20px 0;
                text-align: center;
                opacity: 0.7;
            }
            
            .error-message {
                background: rgba(255, 0, 0, 0.2);
                border: 1px solid rgba(255, 0, 0, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                color: #ffcccc;
                display: none;
            }
            
            .success-message {
                background: rgba(0, 255, 0, 0.2);
                border: 1px solid rgba(0, 255, 0, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                color: #ccffcc;
                display: none;
            }
            
            .welcome-bonus {
                background: rgba(255, 215, 0, 0.1);
                border: 1px solid rgba(255, 215, 0, 0.3);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: center;
            }
            
            .bonus-text {
                color: #FFD700;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .nav-links {
                margin-top: 30px;
            }
            
            .nav-links a {
                color: rgba(255, 255, 255, 0.8);
                text-decoration: none;
                margin: 0 10px;
                font-size: 0.9rem;
            }
            
            .nav-links a:hover {
                color: #FFD700;
            }
            
            @media (max-width: 768px) {
                .form-row {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="register-container">
            <div class="logo">🙏🏼</div>
            <h1 class="title">JyotiFlow.ai</h1>
            <p class="subtitle">Join the Digital Ashram</p>
            
            <div class="welcome-bonus">
                <div class="bonus-text">🎁 Welcome Gift</div>
                <div>Receive 3 free credits upon registration!</div>
            </div>
            
            <div id="errorMessage" class="error-message"></div>
            <div id="successMessage" class="success-message"></div>
            
            <form id="registerForm">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">First Name:</label>
                        <input type="text" class="form-input" id="firstName" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Last Name:</label>
                        <input type="text" class="form-input" id="lastName" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Email:</label>
                    <input type="email" class="form-input" id="email" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Password:</label>
                    <input type="password" class="form-input" id="password" required minlength="6">
                </div>
                
                <div class="form-group">
                    <label class="form-label">Confirm Password:</label>
                    <input type="password" class="form-input" id="confirmPassword" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Birth Date:</label>
                        <input type="date" class="form-input" id="birthDate">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Birth Time:</label>
                        <input type="time" class="form-input" id="birthTime">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Birth Place (Optional):</label>
                    <input type="text" class="form-input" id="birthPlace" placeholder="City, Country">
                </div>
                
                <button type="submit" class="btn">🌟 Join the Ashram</button>
            </form>
            
            <div class="divider">
                <p>Already have an account? <a href="/login" class="link">Sign in here</a></p>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/admin">👑 Admin</a>
            </div>
        </div>
        
        <script>
            document.getElementById('registerForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const birthDate = document.getElementById('birthDate').value;
                const birthTime = document.getElementById('birthTime').value;
                const birthPlace = document.getElementById('birthPlace').value;
                
                const errorDiv = document.getElementById('errorMessage');
                const successDiv = document.getElementById('successMessage');
                
                // Hide previous messages
                errorDiv.style.display = 'none';
                successDiv.style.display = 'none';
                
                // Validate passwords match
                if (password !== confirmPassword) {
                    errorDiv.textContent = 'Passwords do not match.';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                try {
                    const response = await fetch('/api/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            first_name: firstName,
                            last_name: lastName,
                            email: email,
                            password: password,
                            birth_date: birthDate,
                            birth_time: birthTime,
                            birth_location: birthPlace
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        successDiv.textContent = 'Welcome to the Digital Ashram! You have received 3 free credits. Redirecting to login...';
                        successDiv.style.display = 'block';
                        
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 2000);
                    } else {
                        errorDiv.textContent = data.message || 'Registration failed. Please try again.';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Connection error. Please try again.';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=REGISTER_TEMPLATE)

# --- Admin Dashboard HTML Route --- #
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """
    தமிழ் - நிர்வாக டாஷ்போர்டு பக்கம்
    English - Admin dashboard page
    """
    try:
        # You can add authentication check here if needed
        return admin_dashboard_html
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Error loading admin dashboard")

# Admin Dashboard HTML (add this at the top of your file with other constants)
admin_dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JyotiFlow.ai - Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #7b2cbf;
            --secondary-color: #9d4edd;
            --accent-color: #e0aaff;
            --light-color: #f8f9fa;
            --dark-color: #212529;
        }
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f5f5f5;
        }
        .sidebar {
            background: linear-gradient(180deg, var(--primary-color ) 0%, var(--secondary-color) 100%);
            color: white;
            height: 100vh;
            position: fixed;
            padding-top: 20px;
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,.8);
            margin-bottom: 5px;
            border-radius: 5px;
            padding: 10px 15px;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            background-color: rgba(255,255,255,.1);
            color: white;
        }
        .sidebar .nav-link i {
            margin-right: 10px;
        }
        .content {
            margin-left: 240px;
            padding: 20px;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,.1);
            margin-bottom: 20px;
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card-header {
            background-color: white;
            border-bottom: 1px solid rgba(0,0,0,.125);
            font-weight: 600;
        }
        .stats-card {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        .stats-card .card-body {
            padding: 20px;
        }
        .stats-icon {
            font-size: 40px;
            opacity: 0.8;
        }
        .stats-number {
            font-size: 30px;
            font-weight: 700;
        }
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        .btn-primary:hover {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        .table th {
            font-weight: 600;
        }
        .badge-active {
            background-color: #28a745;
        }
        .badge-inactive {
            background-color: #dc3545;
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
        }
        #loginForm {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,.1);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo img {
            max-width: 150px;
        }
        .hidden {
            display: none;
        }
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
        }
    </style>
</head>
<body>
    <!-- Login Form -->
    <div id="loginSection" class="container login-container">
        <div class="logo">
            <h2>🙏🏼 JyotiFlow.ai</h2>
            <p>Admin Dashboard</p>
        </div>
        <form id="loginForm">
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
    </div>

    <!-- Main Dashboard -->
    <div id="dashboardSection" class="hidden">
        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-2 sidebar">
                    <h4 class="text-center mb-4">JyotiFlow.ai</h4>
                    <div class="nav flex-column">
                        <a class="nav-link active" href="#" data-section="overview"><i class="bi bi-speedometer2"></i> Overview</a>
                        <a class="nav-link" href="#" data-section="users"><i class="bi bi-people"></i> Users</a>
                        <a class="nav-link" href="#" data-section="products"><i class="bi bi-box"></i> SKU Management</a>
                        <a class="nav-link" href="#" data-section="subscriptions"><i class="bi bi-calendar-check"></i> Subscriptions</a>
                        <a class="nav-link" href="#" data-section="credits"><i class="bi bi-coin"></i> Credits</a>
                        <a class="nav-link" href="#" data-section="analytics"><i class="bi bi-graph-up"></i> Analytics</a>
                        <a class="nav-link" href="#" id="logoutBtn"><i class="bi bi-box-arrow-right"></i> Logout</a>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="col-md-10 content">
                    <!-- Overview Section -->
                    <div id="overview" class="dashboard-section">
                        <h2 class="mb-4">Dashboard Overview</h2>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="card stats-card">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <div>
                                                <h6 class="card-title">Total Users</h6>
                                                <div class="stats-number" id="totalUsers">0</div>
                                            </div>
                                            <div class="stats-icon">
                                                <i class="bi bi-people"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stats-card">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <div>
                                                <h6 class="card-title">Active Subscriptions</h6>
                                                <div class="stats-number" id="activeSubscriptions">0</div>
                                            </div>
                                            <div class="stats-icon">
                                                <i class="bi bi-calendar-check"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stats-card">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <div>
                                                <h6 class="card-title">Sessions Today</h6>
                                                <div class="stats-number" id="sessionsToday">0</div>
                                            </div>
                                            <div class="stats-icon">
                                                <i class="bi bi-chat-dots"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stats-card">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <div>
                                                <h6 class="card-title">Revenue (Monthly)</h6>
                                                <div class="stats-number" id="monthlyRevenue">$0</div>
                                            </div>
                                            <div class="stats-icon">
                                                <i class="bi bi-currency-dollar"></i>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Recent Users
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="recentUsersTable">
                                                <thead>
                                                    <tr>
                                                        <th>Name</th>
                                                        <th>Email</th>
                                                        <th>Credits</th>
                                                        <th>Joined</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Recent Sessions
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="recentSessionsTable">
                                                <thead>
                                                    <tr>
                                                        <th>User</th>
                                                        <th>SKU</th>
                                                        <th>Channel</th>
                                                        <th>Time</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Users Section -->
                    <div id="users" class="dashboard-section hidden">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h2>User Management</h2>
                            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addUserModal">
                                <i class="bi bi-plus"></i> Add User
                            </button>
                        </div>
                        <div class="card">
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-hover" id="usersTable">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Email</th>
                                                <th>Credits</th>
                                                <th>Birth Details</th>
                                                <th>Last Login</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <!-- Data will be loaded here -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- SKU Management Section -->
                    <div id="products" class="dashboard-section hidden">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h2>SKU Management</h2>
                            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addProductModal">
                                <i class="bi bi-plus"></i> Add Product
                            </button>
                        </div>
                        <div class="row">
                            <div class="col-md-12">
                                <div class="card">
                                    <div class="card-header">
                                        Products
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="productsTable">
                                                <thead>
                                                    <tr>
                                                        <th>SKU Code</th>
                                                        <th>Name</th>
                                                        <th>Type</th>
                                                        <th>Status</th>
                                                        <th>Stripe ID</th>
                                                        <th>Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Subscription Plans
                                        <button class="btn btn-sm btn-primary float-end" data-bs-toggle="modal" data-bs-target="#addPlanModal">
                                            <i class="bi bi-plus"></i> Add Plan
                                        </button>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="plansTable">
                                                <thead>
                                                    <tr>
                                                        <th>Name</th>
                                                        <th>Price</th>
                                                        <th>Interval</th>
                                                        <th>Credits</th>
                                                        <th>Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Credit Packages
                                        <button class="btn btn-sm btn-primary float-end" data-bs-toggle="modal" data-bs-target="#addPackageModal">
                                            <i class="bi bi-plus"></i> Add Package
                                        </button>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="packagesTable">
                                                <thead>
                                                    <tr>
                                                        <th>Name</th>
                                                        <th>Credits</th>
                                                        <th>Price</th>
                                                        <th>Status</th>
                                                        <th>Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Subscriptions Section -->
                    <div id="subscriptions" class="dashboard-section hidden">
                        <h2 class="mb-4">Subscription Management</h2>
                        <div class="card">
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-hover" id="subscriptionsTable">
                                        <thead>
                                            <tr>
                                                <th>User</th>
                                                <th>Plan</th>
                                                <th>Status</th>
                                                <th>Start Date</th>
                                                <th>End Date</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <!-- Data will be loaded here -->
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Credits Section -->
                    <div id="credits" class="dashboard-section hidden">
                        <h2 class="mb-4">Credit Management</h2>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Adjust User Credits
                                    </div>
                                    <div class="card-body">
                                        <form id="adjustCreditsForm">
                                            <div class="mb-3">
                                                <label for="creditUserEmail" class="form-label">User Email</label>
                                                <input type="email" class="form-control" id="creditUserEmail" required>
                                            </div>
                                            <div class="mb-3">
                                                <label for="creditAmount" class="form-label">Credits to Add/Remove</label>
                                                <input type="number" class="form-control" id="creditAmount" required>
                                                <small class="text-muted">Use positive values to add credits, negative to remove</small>
                                            </div>
                                            <div class="mb-3">
                                                <label for="creditReason" class="form-label">Reason</label>
                                                <input type="text" class="form-control" id="creditReason" required>
                                            </div>
                                            <button type="submit" class="btn btn-primary">Adjust Credits</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Recent Credit Transactions
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover" id="creditTransactionsTable">
                                                <thead>
                                                    <tr>
                                                        <th>User</th>
                                                        <th>Amount</th>
                                                        <th>Reason</th>
                                                        <th>Date</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <!-- Data will be loaded here -->
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Analytics Section -->
                    <div id="analytics" class="dashboard-section hidden">
                        <h2 class="mb-4">Analytics</h2>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        User Growth
                                    </div>
                                    <div class="card-body">
                                        <canvas id="userGrowthChart"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Revenue
                                    </div>
                                    <div class="card-body">
                                        <canvas id="revenueChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Session Distribution by SKU
                                    </div>
                                    <div class="card-body">
                                        <canvas id="skuDistributionChart"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        Channel Distribution
                                    </div>
                                    <div class="card-body">
                                        <canvas id="channelDistributionChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modals -->
    <!-- Add User Modal -->
    <div class="modal fade" id="addUserModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New User</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addUserForm">
                        <div class="mb-3">
                            <label for="newUserEmail" class="form-label">Email</label>
                            <input type="email" class="form-control" id="newUserEmail" required>
                        </div>
                        <div class="mb-3">
                            <label for="newUserPassword" class="form-label">Password</label>
                            <input type="password" class="form-control" id="newUserPassword" required>
                        </div>
                        <div class="mb-3">
                            <label for="newUserFirstName" class="form-label">First Name</label>
                            <input type="text" class="form-control" id="newUserFirstName" required>
                        </div>
                        <div class="mb-3">
                            <label for="newUserLastName" class="form-label">Last Name</label>
                            <input type="text" class="form-control" id="newUserLastName" required>
                        </div>
                        <div class="mb-3">
                            <label for="newUserCredits" class="form-label">Initial Credits</label>
                            <input type="number" class="form-control" id="newUserCredits" value="0">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="saveNewUserBtn">Save User</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Product Modal -->
    <div class="modal fade" id="addProductModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Product</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addProductForm">
                        <div class="mb-3">
                            <label for="productSkuCode" class="form-label">SKU Code</label>
                            <input type="text" class="form-control" id="productSkuCode" required>
                            <small class="text-muted">e.g., CLARITY_15MIN</small>
                        </div>
                        <div class="mb-3">
                            <label for="productName" class="form-label">Name</label>
                            <input type="text" class="form-control" id="productName" required>
                        </div>
                        <div class="mb-3">
                            <label for="productDescription" class="form-label">Description</label>
                            <textarea class="form-control" id="productDescription" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="productType" class="form-label">Service Type</label>
                            <select class="form-control" id="productType" required>
                                <option value="session">Session</option>
                                <option value="subscription">Subscription</option>
                                <option value="credit_pack">Credit Package</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="productStatus" class="form-label">Status</label>
                            <select class="form-control" id="productStatus">
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                                <option value="testing">Testing</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="productImageUrl" class="form-label">Image URL</label>
                            <input type="url" class="form-control" id="productImageUrl">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="saveProductBtn">Save Product</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Container -->
    <div id="toast-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>

        // Add this to your admin dashboard JavaScript
        let authToken = localStorage.getItem('adminAuthToken');

        async function loginAdmin() {
            const email = document.getElementById('adminEmail').value;
        const password = document.getElementById('adminPassword').value;
    
        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
        
            if (response.ok) {
                const data = await response.json();
                authToken = data.token;
                localStorage.setItem('adminAuthToken', authToken);
                showToast('Login successful', 'success');
                loadDashboardData();
        } else {
            const error = await response.json();
            showToast(`Login failed: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'danger');
    }
}

// Make sure all API calls include the token
async function fetchWithAuth(url, options = {}) {
    const headers = {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    
    return fetch(url, {
        ...options,
        headers
    });
}

// Example of using fetchWithAuth
async function loadUsers() {
    try {
        const response = await fetchWithAuth('/api/admin/users');
        if (response.ok) {
            const users = await response.json();
            // Process users data
        } else {
            const error = await response.json();
            showToast(`Error loading users: ${error.detail}`, 'danger');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'danger');
    }
}
        // Global variables
        let authToken = localStorage.getItem('jyotiflow_admin_token' );
        const apiBaseUrl = window.location.origin;

        // Check if user is logged in
        function checkAuth() {
            if (authToken) {
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('dashboardSection').classList.remove('hidden');
                loadDashboardData();
            } else {
                document.getElementById('loginSection').classList.remove('hidden');
                document.getElementById('dashboardSection').classList.add('hidden');
            }
        }

        // Login form submission
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                if (!response.ok) {
                    throw new Error('Login failed');
                }

                const data = await response.json();
                authToken = data.access_token;
                localStorage.setItem('jyotiflow_admin_token', authToken);
                showToast('Login successful', 'success');
                checkAuth();
            } catch (error) {
                showToast('Login failed: ' + error.message, 'danger');
            }
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', function() {
            localStorage.removeItem('jyotiflow_admin_token');
            authToken = null;
            checkAuth();
            showToast('Logged out successfully', 'success');
        });

        // Navigation
        document.querySelectorAll('.nav-link[data-section]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetSection = this.getAttribute('data-section');
                
                // Hide all sections
                document.querySelectorAll('.dashboard-section').forEach(section => {
                    section.classList.add('hidden');
                });
                
                // Show target section
                document.getElementById(targetSection).classList.remove('hidden');
                
                // Update active link
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                this.classList.add('active');
                
                // Load section data if needed
                if (targetSection === 'users') loadUsers();
                if (targetSection === 'products') loadProducts();
                if (targetSection === 'subscriptions') loadSubscriptions();
                if (targetSection === 'credits') loadCreditTransactions();
                if (targetSection === 'analytics') loadAnalytics();
            });
        });

        // Load dashboard data
        async function loadDashboardData() {
            try {
                // Load overview stats
                const statsResponse = await fetch(`${apiBaseUrl}/api/admin/stats`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (statsResponse.ok) {
                    const stats = await statsResponse.json();
                    document.getElementById('totalUsers').textContent = stats.total_users || 0;
                    document.getElementById('activeSubscriptions').textContent = stats.active_subscriptions || 0;
                    document.getElementById('sessionsToday').textContent = stats.sessions_today || 0;
                    document.getElementById('monthlyRevenue').textContent = `$${stats.monthly_revenue || 0}`;
                }
                
                // Load recent users
                const usersResponse = await fetch(`${apiBaseUrl}/api/admin/users?limit=5`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (usersResponse.ok) {
                    const users = await usersResponse.json();
                    const tbody = document.querySelector('#recentUsersTable tbody');
                    tbody.innerHTML = '';
                    
                    users.forEach(user => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${user.first_name || ''} ${user.last_name || ''}</td>
                            <td>${user.email}</td>
                            <td>${user.credits}</td>
                            <td>${new Date(user.created_at).toLocaleDateString()}</td>
                        `;
                        tbody.appendChild(row);
                    });
                }
                
                // Load recent sessions
                // Similar code for sessions...
                
            } catch (error) {
                showToast('Error loading dashboard data: ' + error.message, 'danger');
            }
        }

        // Load users
        async function loadUsers() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/users`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch users');
                
                const users = await response.json();
                const tbody = document.querySelector('#usersTable tbody');
                tbody.innerHTML = '';
                
                users.forEach(user => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.first_name || ''} ${user.last_name || ''}</td>
                        <td>${user.email}</td>
                        <td>${user.credits}</td>
                        <td>${user.birth_date ? `${user.birth_date} ${user.birth_time || ''} ${user.birth_location || ''}` : 'Not provided'}</td>
                        <td>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-user-btn" data-email="${user.email}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-info view-memory-btn" data-email="${user.email}">
                                <i class="bi bi-brain"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Add event listeners for edit buttons
                document.querySelectorAll('.edit-user-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const email = this.getAttribute('data-email');
                        // Open edit user modal with data
                        // ...
                    });
                });
                
                document.querySelectorAll('.view-memory-btn').forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const email = this.getAttribute('data-email');
                        try {
                            const response = await fetch(`${apiBaseUrl}/api/admin/users/${email}/memory`, {
                                headers: { 'Authorization': `Bearer ${authToken}` }
                            });
                            
                            if (!response.ok) throw new Error('Failed to fetch memory data');
                            
                            const memory = await response.json();
                            // Display memory data in a modal
                            // ...
                            
                        } catch (error) {
                            showToast('Error loading memory data: ' + error.message, 'danger');
                        }
                    });
                });
                
            } catch (error) {
                showToast('Error loading users: ' + error.message, 'danger');
            }
        }

        // Load products
        async function loadProducts() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/products`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch products');
                
                const products = await response.json();
                const tbody = document.querySelector('#productsTable tbody');
                tbody.innerHTML = '';
                
                products.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.sku_code}</td>
                        <td>${product.name}</td>
                        <td>${product.service_type}</td>
                        <td><span class="badge ${product.status === 'active' ? 'bg-success' : 'bg-secondary'}">${product.status}</span></td>
                        <td>${product.stripe_product_id || 'Not synced'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-product-btn" data-id="${product.id}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-danger delete-product-btn" data-id="${product.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Also load subscription plans and credit packages
                loadSubscriptionPlans();
                loadCreditPackages();
                
            } catch (error) {
                showToast('Error loading products: ' + error.message, 'danger');
            }
        }

        // Load subscription plans
        async function loadSubscriptionPlans() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/subscription-plans`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch subscription plans');
                
                const plans = await response.json();
                const tbody = document.querySelector('#plansTable tbody');
                tbody.innerHTML = '';
                
                plans.forEach(plan => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${plan.name}</td>
                        <td>${plan.currency} ${plan.price}</td>
                        <td>${plan.billing_interval}</td>
                        <td>${plan.credits_granted}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-plan-btn" data-id="${plan.id}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-danger delete-plan-btn" data-id="${plan.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
            } catch (error) {
                showToast('Error loading subscription plans: ' + error.message, 'danger');
            }
        }

        // Load credit packages
        async function loadCreditPackages() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/credit-packages`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch credit packages');
                
                const packages = await response.json();
                const tbody = document.querySelector('#packagesTable tbody');
                tbody.innerHTML = '';
                
                packages.forEach(pkg => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${pkg.name}</td>
                        <td>${pkg.credits_amount}</td>
                        <td>${pkg.currency} ${pkg.price}</td>
                        <td><span class="badge ${pkg.status === 'active' ? 'bg-success' : 'bg-secondary'}">${pkg.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-package-btn" data-id="${pkg.id}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-danger delete-package-btn" data-id="${pkg.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
            } catch (error) {
                showToast('Error loading credit packages: ' + error.message, 'danger');
            }
        }

        // Load subscriptions
        async function loadSubscriptions() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/subscriptions`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch subscriptions');
                
                const subscriptions = await response.json();
                const tbody = document.querySelector('#subscriptionsTable tbody');
                tbody.innerHTML = '';
                
                subscriptions.forEach(sub => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${sub.user_email}</td>
                        <td>${sub.plan_name}</td>
                        <td><span class="badge ${sub.status === 'active' ? 'bg-success' : sub.status === 'past_due' ? 'bg-warning' : 'bg-secondary'}">${sub.status}</span></td>
                        <td>${new Date(sub.current_period_start).toLocaleDateString()}</td>
                        <td>${new Date(sub.current_period_end).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-sm btn-info view-sub-btn" data-id="${sub.id}">
                                <i class="bi bi-eye"></i>
                            </button>
                            ${sub.status === 'active' ? `
                                <button class="btn btn-sm btn-warning cancel-sub-btn" data-id="${sub.id}">
                                    <i class="bi bi-x-circle"></i>
                                </button>
                            ` : ''}
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
            } catch (error) {
                showToast('Error loading subscriptions: ' + error.message, 'danger');
            }
        }

        // Load credit transactions
        async function loadCreditTransactions() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/credit-transactions`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch credit transactions');
                
                const transactions = await response.json();
                const tbody = document.querySelector('#creditTransactionsTable tbody');
                tbody.innerHTML = '';
                
                transactions.forEach(tx => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${tx.user_email}</td>
                        <td>${tx.amount > 0 ? '+' : ''}${tx.amount}</td>
                        <td>${tx.reason}</td>
                        <td>${new Date(tx.timestamp).toLocaleString()}</td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Set up credit adjustment form
                document.getElementById('adjustCreditsForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const userEmail = document.getElementById('creditUserEmail').value;
                    const amount = parseInt(document.getElementById('creditAmount').value);
                    const reason = document.getElementById('creditReason').value;
                    
                    try {
                        const response = await fetch(`${apiBaseUrl}/api/admin/credits/adjust`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${authToken}`
                            },
                            body: JSON.stringify({ user_email: userEmail, credits: amount, reason })
                        });
                        
                        if (!response.ok) throw new Error('Failed to adjust credits');
                        
                        const result = await response.json();
                        showToast(`Credits adjusted successfully. New balance: ${result.new_balance}`, 'success');
                        
                        // Reset form and reload data
                        this.reset();
                        loadCreditTransactions();
                        
                    } catch (error) {
                        showToast('Error adjusting credits: ' + error.message, 'danger');
                    }
                });
                
            } catch (error) {
                showToast('Error loading credit transactions: ' + error.message, 'danger');
            }
        }

        // Load analytics
        async function loadAnalytics() {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/analytics`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (!response.ok) throw new Error('Failed to fetch analytics data');
                
                const data = await response.json();
                
                // User growth chart
                const userCtx = document.getElementById('userGrowthChart').getContext('2d');
                new Chart(userCtx, {
                    type: 'line',
                    data: {
                        labels: data.user_growth.labels,
                        datasets: [{
                            label: 'New Users',
                            data: data.user_growth.data,
                            borderColor: '#7b2cbf',
                            backgroundColor: 'rgba(123, 44, 191, 0.1)',
                            tension: 0.3,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'User Growth Over Time'
                            }
                        }
                    }
                });
                
                // Revenue chart
                const revenueCtx = document.getElementById('revenueChart').getContext('2d');
                new Chart(revenueCtx, {
                    type: 'bar',
                    data: {
                        labels: data.revenue.labels,
                        datasets: [{
                            label: 'Revenue (USD)',
                            data: data.revenue.data,
                            backgroundColor: '#9d4edd'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Monthly Revenue'
                            }
                        }
                    }
                });
                
                // SKU distribution chart
                const skuCtx = document.getElementById('skuDistributionChart').getContext('2d');
                new Chart(skuCtx, {
                    type: 'pie',
                    data: {
                        labels: data.sku_distribution.labels,
                        datasets: [{
                            data: data.sku_distribution.data,
                            backgroundColor: [
                                '#7b2cbf',
                                '#9d4edd',
                                '#c77dff',
                                '#e0aaff'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'right',
                            },
                            title: {
                                display: true,
                                text: 'Sessions by SKU'
                            }
                        }
                    }
                });
                
                // Channel distribution chart
                const channelCtx = document.getElementById('channelDistributionChart').getContext('2d');
                new Chart(channelCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.channel_distribution.labels,
                        datasets: [{
                            data: data.channel_distribution.data,
                            backgroundColor: [
                                '#7b2cbf',
                                '#9d4edd',
                                '#c77dff',
                                '#e0aaff',
                                '#5a189a'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'right',
                            },
                            title: {
                                display: true,
                                text: 'Interactions by Channel'
                            }
                        }
                    }
                });
                
            } catch (error) {
                showToast('Error loading analytics: ' + error.message, 'danger');
            }
        }

        // Add product form handler
        document.getElementById('saveProductBtn').addEventListener('click', async function() {
            const skuCode = document.getElementById('productSkuCode').value;
            const name = document.getElementById('productName').value;
            const description = document.getElementById('productDescription').value;
            const serviceType = document.getElementById('productType').value;
            const status = document.getElementById('productStatus').value;
            const imageUrl = document.getElementById('productImageUrl').value;
            
            if (!skuCode || !name || !serviceType) {
                showToast('Please fill all required fields', 'warning');
                return;
            }
            
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/products`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        sku_code: skuCode,
                        name: name,
                        description: description,
                        service_type: serviceType,
                        status: status,
                        default_image_url: imageUrl,
                        features: []
                    })
                });
                
                if (!response.ok) throw new Error('Failed to create product');
                
                const result = await response.json();
                showToast(`Product ${result.name} created successfully`, 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
                modal.hide();
                document.getElementById('addProductForm').reset();
                
                // Reload products
                loadProducts();
                
            } catch (error) {
                showToast('Error creating product: ' + error.message, 'danger');
            }
        });

        // Add user form handler
        document.getElementById('saveNewUserBtn').addEventListener('click', async function() {
            const email = document.getElementById('newUserEmail').value;
            const password = document.getElementById('newUserPassword').value;
            const firstName = document.getElementById('newUserFirstName').value;
            const lastName = document.getElementById('newUserLastName').value;
            const credits = parseInt(document.getElementById('newUserCredits').value) || 0;
            
            if (!email || !password || !firstName) {
                showToast('Please fill all required fields', 'warning');
                return;
            }
            
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/users`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password,
                        first_name: firstName,
                        last_name: lastName,
                        credits: credits
                    })
                });
                
                if (!response.ok) throw new Error('Failed to create user');
                
                const result = await response.json();
                showToast(`User ${result.email} created successfully`, 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('addUserModal'));
                modal.hide();
                document.getElementById('addUserForm').reset();
                
                // Reload users
                loadUsers();
                
            } catch (error) {
                showToast('Error creating user: ' + error.message, 'danger');
            }
        });

        // Toast notification function
        function showToast(message, type = 'info') {
            const toastContainer = document.getElementById('toast-container');
            const toastId = 'toast-' + Date.now();
            
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            toast.setAttribute('id', toastId);
            
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            toastContainer.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 5000
            });
            
            bsToast.show();
            
            // Remove from DOM after hidden
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            checkAuth();
        });
    </script>
</body>
</html>
"""

    
@app.get('/dashboard')
def user_dashboard():
    """தமிழ் - User dashboard page"""
    DASHBOARD_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 My Dashboard - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            
            .header {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .welcome-section {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                text-align: center;
                backdrop-filter: blur(10px);
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .stat-icon {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                color: #FFD700;
                margin-bottom: 5px;
            }
            
            .services-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .service-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            
            .service-card:hover {
                transform: translateY(-5px);
            }
            
            .btn {
                background: linear-gradient(45deg, #FFD700, #FFA500);
                color: #333;
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 10px 5px;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
            }
            
            .history-section {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                backdrop-filter: blur(10px);
            }
            
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .table th, .table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .table th {
                background: rgba(255, 255, 255, 0.1);
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🙏🏼 Welcome to Your Spiritual Dashboard</h1>
            <button class="btn" onclick="logout()">🚪 Logout</button>
        </div>
        
        <div class="container">
            <div class="welcome-section">
                <h2 id="welcomeMessage">🙏🏼 Welcome back, Spiritual Seeker</h2>
                <p>May your journey be filled with divine wisdom and inner peace</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">💰</div>
                    <div class="stat-value" id="userCredits">0</div>
                    <div class="stat-label">Available Credits</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🔮</div>
                    <div class="stat-value" id="totalSessions">0</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">📅</div>
                    <div class="stat-value" id="lastSession">Never</div>
                    <div class="stat-label">Last Session</div>
                </div>
            </div>
            
            <div class="services-grid">
                <div class="service-card">
                    <h3>✨ Clarity Plus</h3>
                    <p>Quick emotional support and life clarity</p>
                    <p><strong>Cost:</strong> 1 credit</p>
                    <a href="/session/clarity" class="btn">Start Session</a>
                </div>
                
                <div class="service-card">
                    <h3>💕 AstroLove Whisper</h3>
                    <p>Deep relationship and love insights</p>
                    <p><strong>Cost:</strong> 3 credits</p>
                    <a href="/session/love" class="btn">Start Session</a>
                </div>
                
                <div class="service-card">
                    <h3>🔮 R3 Live Premium</h3>
                    <p>Comprehensive spiritual life reading</p>
                    <p><strong>Cost:</strong> 6 credits</p>
                    <a href="/session/premium" class="btn">Start Session</a>
                </div>
                
                <div class="service-card">
                    <h3>🌟 Daily AstroCoach</h3>
                    <p>Monthly spiritual coaching subscription</p>
                    <p><strong>Cost:</strong> 12 credits</p>
                    <a href="/session/elite" class="btn">Start Session</a>
                </div>
            </div>
            
            <div class="history-section">
                <h3>📜 Your Session History</h3>
                <table class="table" id="historyTable">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Service</th>
                            <th>Credits Used</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="historyTableBody">
                        <tr>
                            <td colspan="4" style="text-align: center; opacity: 0.7;">Loading your spiritual journey...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            // Load user data on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadUserData();
                loadSessionHistory();
            });
            
            async function loadUserData() {
                try {
                    const token = localStorage.getItem('jyoti_token');
                    if (!token) {
                        window.location.href = '/login';
                        return;
                    }
                    
                    const response = await fetch('/api/user/profile', {
                        headers: {
                            'Authorization': 'Bearer ' + token
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('welcomeMessage').textContent = 
                            `🙏🏼 Welcome back, ${data.user.first_name}`;
                        document.getElementById('userCredits').textContent = data.user.credits;
                        document.getElementById('totalSessions').textContent = data.stats.total_sessions;
                        document.getElementById('lastSession').textContent = 
                            data.stats.last_session || 'Never';
                    }
                } catch (error) {
                    console.error('Error loading user data:', error);
                }
            }
            
            async function loadSessionHistory() {
                try {
                    const token = localStorage.getItem('jyoti_token');
                    const response = await fetch('/api/session/history', {
                        headers: {
                            'Authorization': 'Bearer ' + token
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const tbody = document.getElementById('historyTableBody');
                        tbody.innerHTML = '';
                        
                        if (data.sessions.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; opacity: 0.7;">No sessions yet. Start your spiritual journey!</td></tr>';
                        } else {
                            data.sessions.forEach(session => {
                                const row = tbody.insertRow();
                                row.innerHTML = `
                                    <td>${new Date(session.session_time).toLocaleDateString()}</td>
                                    <td>${session.service_name}</td>
                                    <td>${session.credits_used}</td>
                                    <td>${session.status}</td>
                                `;
                            });
                        }
                    }
                } catch (error) {
                    console.error('Error loading session history:', error);
                }
            }
            
            function logout() {
                localStorage.removeItem('jyoti_token');
                window.location.href = '/';
            }

            async function refreshCredits() {
                try {
                    const token = localStorage.getItem('jyoti_token');
                    if (!token) {
                        window.location.href = '/login';
                        return;
                    }
        
                    const response = await fetch('/api/credits/balance', {
                        headers: {
                            'Authorization': 'Bearer ' + token
                        }
                    });
        
                    const data = await response.json();
        
                    if (response.ok) {
                        document.getElementById('userCredits').textContent = data.credits;
                        console.log("Credits refreshed:", data.credits);
                        return data.credits;
                    } else {
                        console.error("Failed to refresh credits:", data);
                        return null;
                    }
                } catch (error) {
                    console.error('Error refreshing credits:', error);
                    return null;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=DASHBOARD_TEMPLATE)

@app.post("/api/admin/login")
async def admin_login(login_data: AdminLogin):
    """தமிழ் - Admin login endpoint"""
    try:
        # Debug logging
        logger.info(f"Login attempt with email: {login_data.email}")
        logger.info(f"Env variables: ADMIN_EMAIL={ADMIN_EMAIL}")
        
        # Hardcoded check as fallback
        if (login_data.email == ADMIN_EMAIL and login_data.password == ADMIN_PASSWORD) or \
           (login_data.email == "admin@jyotiflow.ai" and login_data.password == "StrongPass@123"):
            
            # Create admin token
            token = create_jwt_token(login_data.email, is_admin=True)
            
            # Log admin login
            logger.info(f"Admin login successful: {login_data.email}")
            
            return {
                "success": True,
                "token": token,
                "message": "Admin login successful"
            }
        else:
            # Log failed attempt with details
            logger.warning(f"Failed admin login attempt: {login_data.email}")
            logger.warning(f"Expected: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
            
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


# User API endpoints for dashboard
@app.get("/api/user/profile")
async def get_user_profile(current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Get user profile and stats"""
    conn = None
    try:
        conn = await get_db_connection()
        
        # Get user info
        user = await conn.fetchrow(
            "SELECT first_name, last_name, email, credits, created_at FROM users WHERE email = $1",
            current_user['email']
        )
        
        # Get user stats
        total_sessions = await conn.fetchval(
            "SELECT COUNT(*) FROM sessions WHERE user_email = $1",
            current_user['email']
        )
        
        last_session = await conn.fetchval(
            "SELECT MAX(session_time) FROM sessions WHERE user_email = $1",
            current_user['email']
        )
        
        return {
            "success": True,
            "user": {
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "email": user['email'],
                "credits": user['credits'],
                "member_since": user['created_at'].strftime("%B %Y") if user['created_at'] else "Unknown"
            },
            "stats": {
                "total_sessions": total_sessions,
                "last_session": last_session.strftime("%B %d, %Y") if last_session else None
            }
        }
        
    except Exception as e:
        logger.error(f"User profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load profile")
    finally:
        if conn:
            await release_db_connection(conn)

# --- Analytics Routes --- #
@app.get("/api/admin/stats")
async def get_admin_stats(admin_user: Dict = Depends(get_admin_user)):
    """Get dashboard overview statistics."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # Get total users
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE email != $1", ADMIN_EMAIL)
        
        # Get active subscriptions
        active_subs = await conn.fetchval("SELECT COUNT(*) FROM user_subscriptions WHERE status = 'active'")
        
        # Get sessions today
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        sessions_today = await conn.fetchval(
            "SELECT COUNT(*) FROM interaction_history WHERE timestamp >= $1 AND channel LIKE 'web_session%'", 
            today_start
        )
        
        # Get monthly revenue (simplified - in a real app, you'd calculate this from Stripe data)
        # This is just a placeholder calculation
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = await conn.fetchval("""
            SELECT COALESCE(SUM(p.price), 0)
            FROM user_subscriptions us
            JOIN subscription_plans sp ON us.subscription_plan_id = sp.id
            JOIN products p ON sp.product_id = p.id
            WHERE us.status = 'active' AND us.created_at >= $1
        """, month_start) or 0
        
        return {
            "total_users": total_users,
            "active_subscriptions": active_subs,
            "sessions_today": sessions_today,
            "monthly_revenue": float(monthly_revenue)
        }
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch admin statistics")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/analytics")
async def get_admin_analytics(admin_user: Dict = Depends(get_admin_user)):
    """Get detailed analytics data for charts."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # User growth - last 6 months
        now = datetime.now()
        months = []
        user_counts = []
        
        for i in range(5, -1, -1):
            month_date = (now - timedelta(days=30*i)).replace(day=1)
            month_name = month_date.strftime("%b %Y")
            months.append(month_name)
            
            next_month = month_date.replace(month=month_date.month+1) if month_date.month < 12 else month_date.replace(year=month_date.year+1, month=1)
            
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE created_at >= $1 AND created_at < $2 AND email != $3",
                month_date, next_month, ADMIN_EMAIL
            )
            user_counts.append(count)
        
        # Revenue - last 6 months
        revenue_data = []
        for i in range(5, -1, -1):
            month_date = (now - timedelta(days=30*i)).replace(day=1)
            next_month = month_date.replace(month=month_date.month+1) if month_date.month < 12 else month_date.replace(year=month_date.year+1, month=1)
            
            # Simplified revenue calculation
            revenue = await conn.fetchval("""
                SELECT COALESCE(SUM(p.price), 0)
                FROM user_subscriptions us
                JOIN subscription_plans sp ON us.subscription_plan_id = sp.id
                JOIN products p ON sp.product_id = p.id
                WHERE us.created_at >= $1 AND us.created_at < $2
            """, month_date, next_month) or 0
            
            revenue_data.append(float(revenue))
        
        # SKU distribution
        sku_labels = []
        sku_data = []
        
        sku_counts = await conn.fetch("""
            SELECT p.name, COUNT(*) as count
            FROM interaction_history ih
            JOIN products p ON ih.sku_code = p.sku_code
            WHERE ih.channel LIKE 'web_session%'
            GROUP BY p.name
            ORDER BY count DESC
            LIMIT 5
        """)
        
        for record in sku_counts:
            sku_labels.append(record['name'])
            sku_data.append(record['count'])
        
        # Channel distribution
        channel_labels = []
        channel_data = []
        
        channel_counts = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN channel LIKE 'web_session%' THEN 'Web'
                    WHEN channel LIKE 'zoom%' THEN 'Zoom'
                    WHEN channel LIKE '%whatsapp%' THEN 'WhatsApp'
                    WHEN channel LIKE '%email%' THEN 'Email'
                    WHEN channel LIKE '%sms%' THEN 'SMS'
                    ELSE channel
                END as channel_group,
                COUNT(*) as count
            FROM interaction_history
            GROUP BY channel_group
            ORDER BY count DESC
        """)
        
        for record in channel_counts:
            channel_labels.append(record['channel_group'])
            channel_data.append(record['count'])
        
        return {
            "user_growth": {
                "labels": months,
                "data": user_counts
            },
            "revenue": {
                "labels": months,
                "data": revenue_data
            },
            "sku_distribution": {
                "labels": sku_labels,
                "data": sku_data
            },
            "channel_distribution": {
                "labels": channel_labels,
                "data": channel_data
            }
        }
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch analytics data")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/credit-transactions")
async def get_credit_transactions(skip: int = 0, limit: int = 50, admin_user: Dict = Depends(get_admin_user)):
    """Get credit transaction history."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # In a real app, you'd have a dedicated credit_transactions table
        # This is a simplified version using admin_logs
        records = await conn.fetch("""
            SELECT admin_email, action, target_user as user_email, details, timestamp
            FROM admin_logs
            WHERE action IN ('credit_purchase', 'subscription_credits', 'credit_adjustment')
            ORDER BY timestamp DESC
            OFFSET $1 LIMIT $2
        """, skip, limit)
        
        result = []
        for record in records:
            # Parse amount from details
            details = record['details']
            amount = 0
            if "Added" in details or "Granted" in details:
                # Extract number between "Added/Granted" and "credits"
                match = re.search(r'(?:Added|Granted) (\d+) credits', details)
                if match:
                    amount = int(match.group(1))
            elif "Removed" in details:
                match = re.search(r'Removed (\d+) credits', details)
                if match:
                    amount = -int(match.group(1))
            
            result.append({
                "user_email": record['user_email'],
                "amount": amount,
                "reason": record['action'].replace('_', ' ').title(),
                "timestamp": record['timestamp'].isoformat()
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting credit transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch credit transactions")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/users")
async def admin_get_users(skip: int = 0, limit: int = 100, admin_user: Dict = Depends(get_admin_user)):
    """Get all users for admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        records = await conn.fetch("""
            SELECT email, first_name, last_name, birth_date, birth_time, birth_location, 
                   credits, last_login, created_at, updated_at, stripe_customer_id
            FROM users 
            WHERE email != $1
            ORDER BY created_at DESC
            OFFSET $2 LIMIT $3
        """, ADMIN_EMAIL, skip, limit)
        
        return [dict(record) for record in records]
    except Exception as e:
        logger.error(f"Error getting users for admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    finally:
        if conn:
            await release_db_connection(conn)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    தமிழ் - Authentication middleware - token verification
    English - Authentication middleware for token verification
    """
    # Skip auth for login routes and public endpoints
    if request.url.path in ["/api/login", "/api/register", "/api/admin/login", "/", "/admin"]:
        return await call_next(request)
    
    # Skip auth for static files
    if request.url.path.startswith(("/static/", "/favicon.ico")):
        return await call_next(request)
    
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        return await call_next(request)
    
    # Extract and verify token
    token = auth_header.split(" ")[1]
    try:
        payload = verify_jwt_token(token)
        # Add user info to request state
        request.state.user = payload
        return await call_next(request)
    except Exception as e:
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=401, content={"detail": str(e)})
        return await call_next(request)

async def generate_swami_guidance_with_memory(user_email: str, sku_code: str, question: str, uco: Optional[UCO] = None) -> str:
    """
    தமிழ் - UCO memory உடன் ஸ்வாமி வழிகாட்டுதல் உருவாக்குதல்
    English - Generate Swami guidance using the user's memory context
    """
    conn = None
    try:
        conn = await get_db_connection()
        
        # Get product details
        product = await get_product_by_sku(sku_code)
        if not product:
            return "I'm sorry, this service is not available at the moment."
        
        # If no UCO provided, try to get it
        if not uco:
            uco = await get_uco_for_user(user_email)
        
        # Prepare context from UCO
        memory_context = {}
        if uco:
            # Extract relevant parts of UCO for this guidance
            memory_context = {
                "user_profile": uco.user_profile,
                "emotional_journey": uco.emotional_journey_summary,
                "astrological_profile": uco.astrological_profile_summary,
                "preferences": uco.preferences
            }
            
            # Get last 3 interactions if available
            if uco.interaction_history_ids:
                recent_ids = uco.interaction_history_ids[-3:] if len(uco.interaction_history_ids) > 3 else uco.interaction_history_ids
                recent_interactions = await conn.fetch(
                    "SELECT user_query, swami_response_summary, timestamp FROM interaction_history WHERE id = ANY($1) ORDER BY timestamp DESC",
                    recent_ids
                )
                
                if recent_interactions:
                    memory_context["recent_interactions"] = [dict(interaction) for interaction in recent_interactions]
        
        # Prepare the prompt with memory context
        system_prompt = f"""You are Swami, a spiritual guide with deep knowledge of Vedic astrology.
        Service: {product.get('name', 'Spiritual Guidance')}
        Description: {product.get('description', '')}
        
        User Memory Context:
        {json.dumps(memory_context, indent=2)}
        
        Based on the user's question and their memory context, provide personalized guidance.
        Maintain a warm, spiritual tone with occasional Tamil phrases for authenticity.
        Reference their past interactions and astrological profile when relevant.
        """
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        guidance = response.choices[0].message.content
        
        # Extract insights and emotional state (simplified - in a real app, you'd use more sophisticated NLP)
        insights = []
        emotional_state = "neutral"
        
        # Simple keyword-based emotion detection
        positive_emotions = ["happy", "grateful", "hopeful", "excited", "peaceful"]
        negative_emotions = ["anxious", "sad", "frustrated", "angry", "confused"]
        
        for emotion in positive_emotions:
            if emotion in question.lower():
                emotional_state = emotion
                break
                
        for emotion in negative_emotions:
            if emotion in question.lower():
                emotional_state = emotion
                break
        
        # Simple insight extraction (in a real app, you'd use more sophisticated NLP)
        if "career" in question.lower():
            insights.append("User is focused on career matters")
        if "relationship" in question.lower() or "love" in question.lower():
            insights.append("User is seeking relationship guidance")
        if "health" in question.lower():
            insights.append("User has health concerns")
        
        # Update UCO with this interaction
        if uco:
            if not uco.last_interaction_summary:
                uco.last_interaction_summary = {}
            
            uco.last_interaction_summary = {
                "timestamp": datetime.now().isoformat(),
                "sku_code": sku_code,
                "question": question,
                "response_summary": guidance[:100] + "..." if len(guidance) > 100 else guidance,
                "emotional_state": emotional_state,
                "insights": insights
            }
            
            await update_uco_for_user(user_email, uco.dict())
        
        return guidance
    except Exception as e:
        logger.error(f"Error generating guidance with memory for {user_email}: {e}", exc_info=True)
        return "I'm sorry, I'm having trouble connecting with my wisdom at the moment. Please try again shortly."
    finally:
        if conn:
            await release_db_connection(conn)


@app.post("/api/admin/users")
async def admin_create_user(user_data: dict, admin_user: Dict = Depends(get_admin_user)):
    """Create a new user from admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        
        # Check if user already exists
        existing = await conn.fetchval("SELECT 1 FROM users WHERE email = $1", user_data['email'])
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user = await conn.fetchrow("""
            INSERT INTO users (
                email, password_hash, first_name, last_name, credits, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING email, first_name, last_name, credits, created_at, updated_at
        """, user_data['email'], password_hash, user_data['first_name'], 
            user_data.get('last_name', ''), user_data.get('credits', 0))
        
        # Log action
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, NOW())
        """, admin_user['email'], "user_created", user_data['email'], 
            f"Admin created user with {user_data.get('credits', 0)} initial credits")
        
        return dict(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user from admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create user")
    finally:
        if conn:
            await release_db_connection(conn)

@app.post("/api/admin/credits/adjust")
async def admin_adjust_credits(request_data: dict, admin_user: Dict = Depends(get_admin_user)):
    """Adjust user credits from admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        
        user_email = request_data.get('user_email')
        credits = int(request_data.get('credits', 0))
        reason = request_data.get('reason', 'Admin adjustment')
        
        if not user_email:
            raise HTTPException(status_code=400, detail="User email is required")
        
        # Check if user exists
        user = await conn.fetchrow("SELECT credits FROM users WHERE email = $1", user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update credits
        new_balance = user['credits'] + credits
        await conn.execute(
            "UPDATE users SET credits = $1, updated_at = NOW() WHERE email = $2",
            new_balance, user_email
        )
        
        # Log action
        action_detail = f"{'Added' if credits > 0 else 'Removed'} {abs(credits)} credits: {reason}"
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, NOW())
        """, admin_user['email'], "credit_adjustment", user_email, action_detail)
        
        return {
            "success": True,
            "user_email": user_email,
            "credits_adjusted": credits,
            "new_balance": new_balance,
            "reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting credits from admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to adjust credits")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/subscriptions")
async def admin_get_subscriptions(skip: int = 0, limit: int = 100, admin_user: Dict = Depends(get_admin_user)):
    """Get all subscriptions for admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        records = await conn.fetch("""
            SELECT us.id, us.user_email, sp.name as plan_name, us.status,
                   us.current_period_start, us.current_period_end, us.cancel_at_period_end,
                   us.stripe_subscription_id, us.created_at, us.updated_at
            FROM user_subscriptions us
            JOIN subscription_plans sp ON us.subscription_plan_id = sp.id
            ORDER BY us.created_at DESC
            OFFSET $1 LIMIT $2
        """, skip, limit)
        
        return [dict(record) for record in records]
    except Exception as e:
        logger.error(f"Error getting subscriptions for admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/subscription-plans")
async def admin_get_subscription_plans(admin_user: Dict = Depends(get_admin_user)):
    """Get all subscription plans for admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        records = await conn.fetch("""
            SELECT sp.id, sp.product_id, sp.name, sp.billing_interval, sp.price, sp.currency,
                   sp.credits_granted, sp.channel_access, sp.memory_retention_days, sp.status,
                   sp.stripe_price_id, p.name as product_name
            FROM subscription_plans sp
            JOIN products p ON sp.product_id = p.id
            ORDER BY sp.price DESC
        """)
        
        return [dict(record) for record in records]
    except Exception as e:
        logger.error(f"Error getting subscription plans for admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/credit-packages")
async def admin_get_credit_packages(admin_user: Dict = Depends(get_admin_user)):
    """Get all credit packages for admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        records = await conn.fetch("""
            SELECT cp.id, cp.product_id, cp.name, cp.credits_amount, cp.price, cp.currency,
                   cp.status, cp.stripe_price_id, p.name as product_name
            FROM credit_packages cp
            JOIN products p ON cp.product_id = p.id
            ORDER BY cp.price ASC
        """)
        
        return [dict(record) for record in records]
    except Exception as e:
        logger.error(f"Error getting credit packages for admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch credit packages")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/users/{user_email}/memory")
async def admin_get_user_memory(user_email: str, admin_user: Dict = Depends(get_admin_user)):
    """Get a user's memory/context object for admin dashboard."""
    conn = None
    try:
        conn = await get_db_connection()
        record = await conn.fetchrow("SELECT unified_context_object FROM users WHERE email = $1", user_email)
        
        if not record or not record['unified_context_object']:
            return {"message": "No memory data found for this user"}
        
        return json.loads(record['unified_context_object'])
    except Exception as e:
        logger.error(f"Error getting user memory for admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user memory")
    finally:
        if conn:
            await release_db_connection(conn)


@app.get("/test")
async def test_route():
    return {"status": "working"} 
    
@app.get("/health")
async def health_check():
    """தமிழ் - Health check endpoint"""
    try:
        # தமிழ் - Test database connection
        if db_backend == "sqlite":
            await db_pool.execute("SELECT 1")
        else:
            # தமிழ் - PostgreSQL test
            conn = await get_db_connection()
            await conn.fetchval("SELECT 1")
            await release_db_connection(conn)
        
        return {
            "status": "healthy",
            "message": "🙏🏼 Swami Jyotirananthan's ashram is running smoothly",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.3"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")



# --- SKU Management Routes --- #
@app.post("/api/admin/products", response_model=Product)
async def create_product(product_data: ProductCreate, admin_user: Dict = Depends(get_admin_user)):
    """Create a new product/SKU."""
    return await create_product_in_db(product_data)

@app.get("/api/admin/products", response_model=List[Product])
async def get_all_products(skip: int = 0, limit: int = 100, admin_user: Dict = Depends(get_admin_user)):
    """Get all products/SKUs."""
    conn = None
    try:
        conn = await get_db_connection()
        records = await conn.fetch("SELECT * FROM products ORDER BY name OFFSET $1 LIMIT $2", skip, limit)
        return [Product(**dict(record)) for record in records]
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/products/{product_id}", response_model=Product)
async def get_product(product_id: int, admin_user: Dict = Depends(get_admin_user)):
    """Get a product/SKU by ID."""
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

# --- Memory System Routes --- #
@app.get("/api/user/memory")
async def get_user_memory(current_user: Dict = Depends(get_current_user)):
    """Get the user's memory/context object."""
    uco = await get_uco_for_user(current_user['email'])
    if not uco:
        raise HTTPException(404, "Memory not found for this user")
    return uco

@app.post("/api/session/with-memory")
async def start_session_with_memory(request_data: Dict, current_user: Dict = Depends(get_current_user)):
    """Start a session with memory context."""
    # Get user's UCO
    uco = await get_uco_for_user(current_user['email'])
    
    # Extract question and SKU from request
    question = request_data.get('question', '')
    sku_code = request_data.get('sku_code', '')
    
    # Check if user has enough credits
    # [Your existing credit check logic]
    
    # Generate guidance using UCO context
    guidance = await generate_swami_guidance_with_memory(
        current_user['email'], 
        sku_code, 
        question, 
        uco
    )
    
    # Log this interaction
    session_id = str(uuid.uuid4())
    await add_interaction_to_history(InteractionLog(
        user_email=current_user['email'],
        session_id=session_id,
        channel="web_session_with_memory",
        sku_code=sku_code,
        user_query=question,
        swami_response_summary=guidance[:200]  # Summary
    ))
    
    return {
        "session_id": session_id,
        "guidance": guidance,
        "memory_used": True
    }

# --- Multi-channel Follow-up Routes --- #
@app.post("/api/follow-up/send")
async def send_follow_up(request_data: Dict, admin_user: Dict = Depends(get_admin_user)):
    """Send a follow-up message to a user via specified channel."""
    user_email = request_data.get('user_email')
    channel = request_data.get('channel')
    message = request_data.get('message')
    
    if not all([user_email, channel, message]):
        raise HTTPException(400, "Missing required fields: user_email, channel, message")
    
    # Get user's UCO for context
    uco = await get_uco_for_user(user_email)
    context = uco.dict() if uco else {}
    
    result = await send_follow_up_message(user_email, channel, message, context)
    if not result.get('success'):
        raise HTTPException(500, result.get('error', "Failed to send follow-up message"))
    
    return {"success": True, "message": f"Follow-up sent via {channel}"}

# தமிழ் - Authentication Routes

@app.post("/api/auth/register")
async def register_user(user_data: UserRegister):
    """தமிழ் - User registration with welcome credits"""
    conn = None
    try:
        # தமிழ் - Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        if not re.search(r'[0-9]', user_data.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', user_data.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one special character")
        
        conn = await get_db_connection()
        
        # தமிழ் - Check if user already exists
        existing_user = await conn.fetchrow(
            "SELECT email FROM users WHERE email = $1", user_data.email
        )
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # தமிழ் - Hash password and create user
        hashed_password = hash_password(user_data.password)
        
        await conn.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, 
                             birth_date, birth_time, birth_location, credits, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, user_data.email, hashed_password, user_data.first_name, user_data.last_name,
            user_data.birth_date, user_data.birth_time, user_data.birth_location, 
            3, datetime.utcnow())  # தமிழ் - 3 welcome credits
        
        # தமிழ் - Log welcome credits transaction
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        """, "system", "welcome_credits", user_data.email, 
            "3 welcome credits added for new user", datetime.utcnow())
        
        # தமிழ் - Create JWT token
        token = create_jwt_token(user_data.email)
        
        return {
            "message": "🙏🏼 Welcome to Swami Jyotirananthan's digital ashram",
            "token": token,
            "credits": 3,
            "user": {
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        if conn:
            await release_db_connection(conn)

@app.post("/api/auth/login")
async def login_user(login_data: UserLogin):
    """தமிழ் - User login with JWT token generation"""
    conn = None
    try:
        conn = await get_db_connection()
        
        # தமிழ் - Get user from database
        user = await conn.fetchrow(
            "SELECT email, password_hash, credits, first_name, last_name FROM users WHERE email = $1",
            login_data.email
        )
        
        if not user or not verify_password(login_data.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # தமிழ் - Update last login
        await conn.execute(
            "UPDATE users SET last_login = $1 WHERE email = $2",
            datetime.utcnow(), login_data.email
        )
        
        # தமிழ் - Create JWT token
        token = create_jwt_token(login_data.email)
        
        return {
            "success": True,
            "message": "🙏🏼 Welcome back to the ashram",
            "token": token,
            "credits": user['credits'],
            "user": {
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        if conn:
            await release_db_connection(conn)

# தமிழ் - Session Management Routes

@app.post("/api/session/start")
async def start_spiritual_session(session_data: SessionStart, current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Start spiritual guidance session with credit deduction"""
    conn = None
    try:
        user_email = current_user['email']
        sku = session_data.sku
        # Add debug logging
        logger.info(f"Session start request: user={user_email}, sku={sku}")
        
        # தமிழ் - Validate SKU
        if sku not in SKUS:
            raise HTTPException(status_code=400, detail="Invalid service type")
        sku_config = SKUS[sku]
        
        credits_required = sku_config['credits']
        logger.info(f"Credits required for {sku}: {credits_required}")
        
        conn = await get_db_connection()
        
        # தமிழ் - Check user credits
        user = await conn.fetchrow(
        # Log user credits
            "SELECT credits FROM users WHERE email = $1", user_email
        )
        logger.info(f"User {user_email} has {user['credits']} credits")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['credits'] < credits_required:
            logger.warning(f"Insufficient credits: user has {user['credits']}, needs {credits_required}")
            raise HTTPException(
                status_code=402, 
                detail=f"Insufficient credits. Need {credits_required}, have {user['credits']}"
            )
        
        # தமிழ் - Deduct credits
        await conn.execute(
            "UPDATE users SET credits = credits - $1 WHERE email = $2",
            credits_required, user_email
        )
        
        # தமிழ் - Create session record
        session_id = await conn.fetchval("""
            INSERT INTO sessions (user_email, session_type, credits_used, session_time, status)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, user_email, sku, credits_required, datetime.utcnow(), 'started')
        
        # தமிழ் - Get birth chart if birth details provided
        birth_chart = None
        if session_data.birth_details:
            birth_chart = await get_prokerala_chart(
                session_data.birth_details.get('birth_date'),
                session_data.birth_details.get('birth_time'),
                session_data.birth_details.get('birth_location')
            )
        
        # தமிழ் - Generate spiritual guidance
        guidance = await generate_spiritual_guidance(
            sku, session_data.question or "Please provide general spiritual guidance", birth_chart
        )
        
        # தமிழ் - Update session with guidance
        await conn.execute("""
            UPDATE sessions SET result_summary = $1, status = $2 
            WHERE id = $3
        """, guidance, 'completed', session_id)
        
        # தமிழ் - Trigger SalesCloser Zoom session
        zoom_result = await trigger_salescloser_session(user_email, sku, session_id)
        
        # தமிழ் - Log session completion
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        """, "system", "session_completed", user_email, 
            f"Session {session_id} completed for {sku_config['name']}", datetime.utcnow())
        
        return {
            "session_id": session_id,
            "service": sku_config['name'],
            "credits_used": credits_required,
            "remaining_credits": user['credits'] - credits_required,
            "guidance": guidance,
            "zoom_session": zoom_result,
            "message": "🙏🏼 May this guidance illuminate your path"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session start error: {e}")
        # தமிழ் - Refund credits if session failed
        if conn and 'credits_required' in locals():
            try:
                await conn.execute(
                    "UPDATE users SET credits = credits + $1 WHERE email = $2",
                    credits_required, user_email
                )
            except:
                pass
        raise HTTPException(status_code=500, detail="Session failed to start")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/session/history")
async def get_session_history(current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Get user's session history"""
    conn = None
    try:
        user_email = current_user['email']
        conn = await get_db_connection()
        
        sessions = await conn.fetch("""
            SELECT id, session_type, credits_used, result_summary, 
                   session_time, status
            FROM sessions 
            WHERE user_email = $1 
            ORDER BY session_time DESC
            LIMIT 50
        """, user_email)
        
        session_list = []
        for session in sessions:
            sku_config = SKUS.get(session["session_type"], {})
            session_list.append({
                "id": session['id'],
                "service_name": sku_config.get('name', session['session_type']),
                "credits_used": session['credits_used'],
                "guidance": session['result_summary'],
                "date": session['session_time'].isoformat(),
                "status": session['status']
            })
        
        return {
            "sessions": session_list,
            "total_sessions": len(session_list)
        }
        
    except Exception as e:
        logger.error(f"Session history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch session history")
    finally:
        if conn:
            await release_db_connection(conn)


@app.get("/api/debug/fix_credits")
async def fix_user_credits(current_user: Dict = Depends(get_current_user)):
    """Debug endpoint to fix user credits"""
    conn = None
    try:
        user_email = current_user['email']
        conn = await get_db_connection()
        
        # Check current credits
        user = await conn.fetchrow(
            "SELECT credits FROM users WHERE email = $1", user_email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_credits = user['credits']
        
        # Ensure user has at least 3 credits
        if current_credits < 3:
            await conn.execute(
                "UPDATE users SET credits = 3 WHERE email = $1 AND credits < 3",
                user_email
            )
            
            # Log the credit adjustment
            await conn.execute("""
                INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
                VALUES ($1, $2, $3, $4, $5)
            """, "system", "credit_fix", user_email, 
                f"Fixed credits from {current_credits} to 3", datetime.utcnow())
            
            return {
                "success": True,
                "message": "Credits fixed successfully",
                "previous_credits": current_credits,
                "current_credits": 3
            }
        else:
            return {
                "success": True,
                "message": "Credits are already sufficient",
                "current_credits": current_credits
            }
        
    except Exception as e:
        logger.error(f"Fix credits error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fix credits")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/admin_stats")
async def get_admin_stats(admin: Dict = Depends(get_admin_user)):
    """தமிழ் - Get admin dashboard statistics"""
    conn = None
    try:
        conn = await get_db_connection()
        
        # Total users
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        # Total sessions
        total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")
        
        # Total revenue (from completed sessions)
        total_revenue = await conn.fetchval("""
            SELECT COALESCE(SUM(s.credits_used * sk.price), 0) 
            FROM sessions s 
            JOIN (VALUES 
                ('clarity', 9), ('love', 19), ('premium', 39), ('elite', 149)
            ) AS sk(sku, price) ON s.session_type = sk.sku
            WHERE s.status = 'completed'
        """) or 0
        
        # Today's sessions
        today_sessions = await conn.fetchval("""
            SELECT COUNT(*) FROM sessions 
            WHERE DATE(session_time) = CURRENT_DATE
        """)
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_sessions": total_sessions,
                "total_revenue": float(total_revenue),
                "today_sessions": today_sessions
            }
        }
        
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load stats")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/admin_sessions")
async def get_admin_sessions(admin: Dict = Depends(get_admin_user)):
    """Get all sessions for admin dashboard"""
    conn = None
    try:
        # Add debug logging
        logger.info(f"Admin sessions endpoint called by {admin['email']}")
        
        conn = await get_db_connection()
        
        # Use a more robust query that handles potential schema variations
        sessions = await conn.fetch("""
            SELECT 
                id, 
                user_email, 
                session_type, 
                COALESCE(credits_used, 0) as credits_used,
                created_at as session_time, 
                status, 
                COALESCE(result_summary, '') as result_summary
            FROM sessions
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        # Log the number of sessions found
        logger.info(f"Found {len(sessions)} sessions in database")
        
        sessions_list = []
        for session in sessions:
            sessions_list.append({
                "id": session['id'],
                "user_email": session['user_email'],
                "service_type": session['session_type'],
                "question": session['result_summary'][:50] + "..." if session['result_summary'] and len(session['result_summary']) > 50 else "",
                "created_at": session['session_time'].isoformat() if session['session_time'] else None,
                "status": session['status']
            })
        
        return {
            "success": True,
            "sessions": sessions_list
        }
        
    except Exception as e:
        logger.error(f"Admin sessions error: {e}")
        # Return empty list instead of 500 error
        return {
            "success": False,
            "message": f"Failed to load sessions: {str(e)}",
            "sessions": []
        }
    finally:
        if conn:
            await release_db_connection(conn)

ADMIN_ADD_CREDITS_ENDPOINT = "/admin_add_credits"
@app.post("/admin_add_credits")
async def admin_add_credits(request: Request, admin: Dict = Depends(get_admin_user)):
    """Add credits to user account by admin"""
    conn = None
    try:
        # Get raw JSON data from request
        credit_data = await request.json()
        
        # Extract and validate data
        user_email = credit_data.get("user_email")  # This is the row number from frontend
        credits = credit_data.get("credits")  # Frontend sends 'credits', not 'amount'
        
        if not user_email or not credits:
            logger.error(f"Invalid credit data: {credit_data}")
            return {"success": False, "message": "Missing user_email or credits"}
        
        # Convert credits to integer if needed
        try:
            credits = int(credits)
        except (ValueError, TypeError):
            logger.error(f"Invalid credits format: {credits}")
            return {"success": False, "message": "Credits must be a number"}
        
        conn = await get_db_connection()
        
        # IMPORTANT FIX: Get all users and sort them in the SAME order as the frontend
        # The frontend displays users in created_at DESC order
        users = await conn.fetch("SELECT email FROM users ORDER BY created_at DESC")
        
        # Log the number of users found and the requested user_email
        logger.info(f"Found {len(users)} users in database, requested user_email: {user_email}")
        
        # Debug log to show all user emails in order
        for i, user in enumerate(users):
            logger.info(f"User index {i+1}: {user['email']}")
        
        if not users or len(users) < user_email or user_email <= 0:
            logger.error(f"User with index {user_email} not found")
            return {"success": False, "message": f"User with ID {user_email} not found"}
            
        # Get the email for the specified row number (adjusting for 0-based indexing)
        # This ensures we're using the EXACT same ordering as the frontend
        user_email = users[user_email - 1]["email"]
        
        # Log the operation with detailed information
        logger.info(f"Adding {credits} credits to user {user_email} (index: {user_email})")
        
        # Update credits using email (which is the primary key)
        await conn.execute(
            "UPDATE users SET credits = credits + $1 WHERE email = $2",
            credits, user_email
        )
        
        # Log the successful update
        logger.info(f"Successfully added {credits} credits to {user_email}")
        
        # Add entry to admin_logs table
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        """, admin["email"], "add_credits", user_email, 
            f"Added {credits} credits", datetime.utcnow())
        
        return {
            "success": True,
            "message": f"Added {credits} credits to user {user_email}"
        }
        
    except Exception as e:
        logger.error(f"Admin add credits error: {e}")
        return {
            "success": False,
            "message": f"Failed to add credits: {str(e)}"
        }
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/credits/balance")
async def get_credit_balance(current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Get user's current credit balance"""
    conn = None
    try:
        user_email = current_user['email']
        conn = await get_db_connection()
        
        user = await conn.fetchrow(
            "SELECT credits FROM users WHERE email = $1", user_email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "credits": user['credits'],
            "message": f"🙏🏼 You have {user['credits']} credits in your spiritual account"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit balance error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch credit balance")
    finally:
        if conn:
            await release_db_connection(conn)

@app.post("/api/credits/purchase")
async def purchase_credits(request: Request, current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Create Stripe checkout session for credit purchase"""
    try:
        data = await request.json()
        package = data.get('package', 'starter')
        
        # தமிழ் - Credit packages
        packages = {
            'starter': {'credits': 5, 'price': 2500, 'name': 'Starter Pack'},  # $25
            'popular': {'credits': 12, 'price': 5000, 'name': 'Popular Pack'},  # $50
            'premium': {'credits': 25, 'price': 9000, 'name': 'Premium Pack'},  # $90
            'seeker': {'credits': 50, 'price': 15000, 'name': 'Spiritual Seeker'}  # $150
        }
        
        if package not in packages:
            raise HTTPException(status_code=400, detail="Invalid credit package")
        
        package_info = packages[package]
        
        # தமிழ் - Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"JyotiFlow.ai {package_info['name']}",
                        'description': f"{package_info['credits']} spiritual guidance credits"
                    },
                    'unit_amount': package_info['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{request.base_url}payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.base_url}payment/cancel",
            metadata={
                'user_email': current_user['email'],
                'credits': package_info['credits'],
                'package': package
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "package": package_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit purchase error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment session")

@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """தமிழ் - Stripe webhook for payment processing"""
    conn = None
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # தமிழ் - Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_email = session['metadata']['user_email']
            credits = int(session['metadata']['credits'])
            package = session['metadata']['package']
            
            conn = await get_db_connection()
            
            # தமிழ் - Add credits to user account
            await conn.execute(
                "UPDATE users SET credits = credits + $1 WHERE email = $2",
                credits, user_email
            )
            
            # தமிழ் - Log transaction
            await conn.execute("""
                INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
                VALUES ($1, $2, $3, $4, $5)
            """, "stripe", "credit_purchase", user_email, 
                f"Added {credits} credits via {package} package", datetime.utcnow())
            
            logger.info(f"Credits added: {credits} for user {user_email}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")
    finally:
        if conn:
            await release_db_connection(conn)

# தமிழ் - Error handling and logging
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """தமிழ் - Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """தமிழ் - General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "🙏🏼 The cosmic energies are temporarily disrupted. Please try again.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# தமிழ் - Application startup
#if __name__ == "__main__":
    #logger.info("🙏🏼 Starting Swami Jyotirananthan's Digital Ashram...")
    #uvicorn.run(
        #"app:app",
        #host="0.0.0.0",
        #port=int(os.getenv("PORT", 8000)),
        #reload=DEBUG,
        #log_level="info" if not DEBUG else "debug"
    #)

async def init_db():
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url.startswith("sqlite"):
            db_path = db_url.split("://", 1)[-1]
            conn = await aiosqlite.connect(db_path)
            with open("schema.sql", "r", encoding="utf-8") as f:
                schema_sql = f.read()
            schema_sql = schema_sql.replace("SERIAL", "INTEGER")
            schema_sql = schema_sql.replace("JSONB", "TEXT")
            schema_sql = schema_sql.replace("TIMESTAMP", "TEXT")
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for stmt in statements:
                try:
                    await conn.execute(stmt)
                except Exception as e:
                    logger.debug(f"SQLite init skipped statement: {e}")
            await conn.commit()
            await conn.close()
            logger.info("✅ SQLite schema initialized successfully.")
        else:
            conn = await asyncpg.connect(dsn=db_url)
            with open("schema.sql", "r", encoding="utf-8") as f:
                schema_sql = f.read()
            await conn.execute(schema_sql)
            await conn.close()
            logger.info("✅ PostgreSQL schema initialized successfully.")
    except Exception as e:
        logger.error(f"⚠️ Error initializing DB: {e}")

# NEW (better approach):
@app.on_event("startup")
async def startup_event():
    await init_db()

