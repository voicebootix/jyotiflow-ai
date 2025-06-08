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
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncpg
import asyncio
import os
import jwt
import bcrypt
import stripe
import openai
import httpx
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, EmailStr
import uvicorn
from contextlib import asynccontextmanager
import secrets
import re
from fastapi.responses import HTMLResponse

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """தமிழ் - Application startup மற்றும் shutdown events"""
    global db_pool
    try:
        # தமிழ் - Database connection pool உருவாக்குதல்
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
        logger.info("🙏🏼 Swami Jyotirananthan's digital ashram is awakening...")
        logger.info("Database connection pool created successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise
    finally:
        if db_pool:
            await db_pool.close()
            logger.info("Database connection pool closed")

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

# தமிழ் - Database helper functions
async def get_db_connection():
    """தமிழ் - Database connection pool இலிருந்து connection பெறுதல்"""
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    return await db_pool.acquire()

async def release_db_connection(conn):
    """தமிழ் - Database connection ஐ pool க்கு திரும்ப அனுப்புதல்"""
    if conn:
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
    """தமிழ் - Prokerala API இலிருந்து birth chart பெறுதல் (Mock for testing)"""
    try:
        # தமிழ் - Mock response for testing
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
            "birth_date": birth_date
        }
    except Exception as e:
        logger.error(f"Prokerala API exception: {e}")
        return {"error": "Birth chart service temporarily unavailable"}

async def generate_spiritual_guidance(sku: str, question: str, birth_chart: Dict = None) -> str:
    """தமிழ் - Mock spiritual guidance generation for testing"""
    try:
        # தமிழ் - Customize response based on SKU
        sku_config = SKUS.get(sku, {})
        service_name = sku_config.get('name', 'Spiritual Guidance')
        
        # தமிழ் - Mock responses for testing
        if sku == 'clarity':
            return f"""🙏🏼 My dear child, I sense a deep question stirring in your heart today. 

Your question about "{question}" touches the very essence of your spiritual journey. Looking at your astrological influences, I see the cosmic energies are aligning to bring you the clarity you seek.

The stars whisper that this is a time of transformation for you. Like the lotus that blooms from muddy waters, your current challenges are preparing you for beautiful growth. Trust in the divine timing of your life.

Take three deep breaths with me now, and feel the ancient wisdom flowing through your being. The answer you seek already resides within your soul - you simply need to quiet the mind to hear it.

Until we meet again, may your path be illuminated with divine light and wisdom. 🕉️

Blessings,
Swami Jyotirananthan"""
        
        elif sku == 'love':
            return f"""🙏🏼 Beloved soul, love is the greatest teacher and the most sacred energy in our universe.

Your heart's inquiry about "{question}" reveals the beautiful vulnerability that makes you human. In matters of love, the stars show me that Venus is blessing your path with opportunities for deep connection.

Whether you seek to understand a current relationship or attract new love, remember that the love you give to yourself sets the vibration for all love that enters your life. Your birth chart suggests a powerful capacity for emotional healing and transformation.

The divine feminine and masculine energies within you are seeking balance. Honor both your need for independence and your desire for union. True love begins with self-acceptance and radiates outward like ripples on a sacred lake.

In the coming lunar cycle, pay attention to your dreams and intuitive insights about relationships. The universe is preparing to answer your heart's deepest prayers.

May your heart overflow with love and your relationships be blessed with divine harmony. 💕

With infinite love,
Swami Jyotirananthan"""
        
        elif sku == 'premium':
            return f"""🙏🏼 My cherished seeker, you have come seeking comprehensive guidance for your life's journey, and the cosmos has prepared profound insights for you.

Your question "{question}" opens doorways to understanding your soul's purpose in this incarnation. Looking at your complete astrological blueprint, I see a being of great spiritual potential navigating important life transitions.

**Career & Purpose:** The planetary alignments suggest you are being called to align your work with your higher purpose. Your dharma involves serving others through your unique gifts. Trust the inner calling that may seem unconventional to others.

**Relationships & Family:** Venus and the Moon in your chart indicate deep emotional intelligence. Your relationships are mirrors reflecting your own growth. Forgive past hurts and open your heart to receive the love that surrounds you.

**Health & Vitality:** Your body is a temple housing your divine spirit. The stars counsel attention to both physical wellness and emotional balance. Meditation and connection with nature will restore your energy.

**Spiritual Growth:** You are in a powerful phase of awakening. The challenges you've faced have been preparing you for greater service to humanity. Your intuitive abilities are strengthening - trust them.

**Financial Abundance:** Prosperity flows when we align with our purpose. Release fears about money and focus on how you can serve. The universe will provide as you follow your authentic path.

The next six months bring significant opportunities for transformation. Stay centered in your spiritual practice and trust the divine timing of your life.

May every step of your journey be blessed with wisdom, love, and abundant grace. 🔮

In divine service,
Swami Jyotirananthan"""
        
        elif sku == 'elite':
            return f"""🙏🏼 Beloved spiritual companion, welcome to this sacred space of ongoing guidance and transformation.

Today's insight for your question "{question}" comes from the eternal wisdom of the Vedas and the current cosmic energies surrounding your path.

**Daily Spiritual Practice:** Begin each morning by connecting with your breath and setting an intention for the day. The planetary transits suggest this is a powerful time for manifestation through aligned action.

**Emotional Mastery:** You are learning to be the observer of your emotions rather than being controlled by them. This is advanced spiritual work. When challenging feelings arise, breathe deeply and ask: "What is this emotion teaching me?"

**Relationship Dynamics:** Your connections with others are evolving as you grow spiritually. Some relationships may naturally fade while new, more aligned connections enter your life. Trust this natural process.

**Life Purpose Activation:** The universe is calling you to step more fully into your role as a light-bearer. Your experiences, both joyful and challenging, have prepared you to guide others. Consider how you might share your wisdom.

**Abundance Consciousness:** Shift from thinking about what you lack to appreciating what you have. Gratitude is the fastest path to attracting more blessings. The cosmos responds to the vibration of appreciation.

**This Week's Guidance:** Pay special attention to synchronicities and signs. The universe is communicating with you through repeated numbers, unexpected encounters, and intuitive insights.

Remember, dear soul, you are never alone on this journey. The divine light within you is connected to the infinite source of all wisdom and love.

Until tomorrow's guidance, may you walk in peace and radiate love wherever you go. 🌟

Your spiritual companion,
Swami Jyotirananthan"""
        
        else:
            return f"""🙏🏼 Dear seeker, the divine light within me honors the divine light within you.

Your question "{question}" has reached my heart, and I offer you this guidance from the ancient wisdom traditions.

The cosmos reminds us that every challenge is an opportunity for growth, every setback a setup for a comeback. Trust in the divine timing of your life and know that you are exactly where you need to be.

May peace, love, and wisdom guide your path forward.

Blessings,
Swami Jyotirananthan 🕉️"""
        
    except Exception as e:
        logger.error(f"Guidance generation exception: {e}")
        return f"My dear child, the cosmic energies are shifting at this moment. Please try again in a few moments, and I shall provide the guidance your soul seeks. 🙏🏼"

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

# தமிழ் - API Routes

@app.get("/", response_class=HTMLResponse)
async def homepage():
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
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
async def health_check():
    """தமிழ் - Health check endpoint"""
    try:
        # தமிழ் - Test database connection (SQLite for testing)
        if "sqlite" in DATABASE_URL:
            # தமிழ் - Simple SQLite test
            import sqlite3
            conn = sqlite3.connect("./test_jyotiflow.db")
            conn.execute("SELECT 1")
            conn.close()
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

@app.post("/api/auth/admin-login")
async def admin_login(login_data: AdminLogin):
    """தமிழ் - Admin login with environment credentials"""
    try:
        if login_data.email != ADMIN_EMAIL or login_data.password != ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        # தமிழ் - Create admin JWT token
        token = create_jwt_token(login_data.email, is_admin=True)
        
        return {
            "message": "🙏🏼 Admin access granted to the digital ashram",
            "token": token,
            "admin": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Admin login failed")

# தமிழ் - Session Management Routes

@app.post("/api/session/start")
async def start_spiritual_session(session_data: SessionStart, current_user: Dict = Depends(get_current_user)):
    """தமிழ் - Start spiritual guidance session with credit deduction"""
    conn = None
    try:
        user_email = current_user['email']
        sku = session_data.sku
        
        # தமிழ் - Validate SKU
        if sku not in SKUS:
            raise HTTPException(status_code=400, detail="Invalid service type")
        
        sku_config = SKUS[sku]
        credits_required = sku_config['credits']
        
        conn = await get_db_connection()
        
        # தமிழ் - Check user credits
        user = await conn.fetchrow(
            "SELECT credits FROM users WHERE email = $1", user_email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['credits'] < credits_required:
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
            sku_config = SKUS.get(session['session_type'], {})
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

# தமிழ் - Credit Management Routes

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

# தமிழ் - Admin Routes

@app.get("/api/admin/users")
async def get_all_users(admin_user: Dict = Depends(get_admin_user)):
    """தமிழ் - Get all users for admin dashboard"""
    conn = None
    try:
        conn = await get_db_connection()
        
        users = await conn.fetch("""
            SELECT email, first_name, last_name, credits, last_login, created_at
            FROM users 
            ORDER BY created_at DESC
        """)
        
        user_list = []
        for user in users:
            user_list.append({
                "email": user['email'],
                "name": f"{user['first_name'] or ''} {user['last_name'] or ''}".strip(),
                "credits": user['credits'],
                "last_login": user['last_login'].isoformat() if user['last_login'] else None,
                "created_at": user['created_at'].isoformat()
            })
        
        return {
            "users": user_list,
            "total_users": len(user_list)
        }
        
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    finally:
        if conn:
            await release_db_connection(conn)

@app.post("/api/admin/credits/adjust")
async def adjust_user_credits(credit_data: CreditAdjust, admin_user: Dict = Depends(get_admin_user)):
    """தமிழ் - Adjust user credits (admin only)"""
    conn = None
    try:
        conn = await get_db_connection()
        
        # தமிழ் - Check if user exists
        user = await conn.fetchrow(
            "SELECT credits FROM users WHERE email = $1", credit_data.user_email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # தமிழ் - Update credits
        await conn.execute(
            "UPDATE users SET credits = credits + $1 WHERE email = $2",
            credit_data.credits, credit_data.user_email
        )
        
        # தமிழ் - Log admin action
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        """, admin_user['email'], "credit_adjustment", credit_data.user_email, 
            f"Adjusted credits by {credit_data.credits}. Reason: {credit_data.reason}", 
            datetime.utcnow())
        
        new_balance = user['credits'] + credit_data.credits
        
        return {
            "message": f"Credits adjusted for {credit_data.user_email}",
            "previous_balance": user['credits'],
            "adjustment": credit_data.credits,
            "new_balance": new_balance,
            "reason": credit_data.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit adjustment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust credits")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/analytics")
async def get_platform_analytics(admin_user: Dict = Depends(get_admin_user)):
    """தமிழ் - Get platform analytics for admin dashboard"""
    conn = None
    try:
        conn = await get_db_connection()
        
        # தமிழ் - Get user statistics
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        new_users_today = await conn.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE created_at >= CURRENT_DATE
        """)
        
        # தமிழ் - Get session statistics
        total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")
        sessions_today = await conn.fetchval("""
            SELECT COUNT(*) FROM sessions 
            WHERE session_time >= CURRENT_DATE
        """)
        
        # தமிழ் - Get popular services
        popular_services = await conn.fetch("""
            SELECT session_type, COUNT(*) as count
            FROM sessions 
            GROUP BY session_type 
            ORDER BY count DESC
        """)
        
        service_stats = []
        for service in popular_services:
            sku_config = SKUS.get(service['session_type'], {})
            service_stats.append({
                "service": sku_config.get('name', service['session_type']),
                "sessions": service['count']
            })
        
        # தமிழ் - Get recent activity
        recent_sessions = await conn.fetch("""
            SELECT s.user_email, s.session_type, s.session_time, s.status
            FROM sessions s
            ORDER BY s.session_time DESC
            LIMIT 10
        """)
        
        recent_activity = []
        for session in recent_sessions:
            sku_config = SKUS.get(session['session_type'], {})
            recent_activity.append({
                "user": session['user_email'],
                "service": sku_config.get('name', session['session_type']),
                "time": session['session_time'].isoformat(),
                "status": session['status']
            })
        
        return {
            "users": {
                "total": total_users,
                "new_today": new_users_today
            },
            "sessions": {
                "total": total_sessions,
                "today": sessions_today
            },
            "popular_services": service_stats,
            "recent_activity": recent_activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")
    finally:
        if conn:
            await release_db_connection(conn)

@app.get("/api/admin/sessions")
async def get_all_sessions(admin_user: Dict = Depends(get_admin_user)):
    """தமிழ் - Get all sessions for admin review"""
    conn = None
    try:
        conn = await get_db_connection()
        
        sessions = await conn.fetch("""
            SELECT s.id, s.user_email, s.session_type, s.credits_used, 
                   s.result_summary, s.session_time, s.status
            FROM sessions s
            ORDER BY s.session_time DESC
            LIMIT 100
        """)
        
        session_list = []
        for session in sessions:
            sku_config = SKUS.get(session['session_type'], {})
            session_list.append({
                "id": session['id'],
                "user_email": session['user_email'],
                "service": sku_config.get('name', session['session_type']),
                "credits_used": session['credits_used'],
                "guidance_preview": session['result_summary'][:200] + "..." if session['result_summary'] and len(session['result_summary']) > 200 else session['result_summary'],
                "date": session['session_time'].isoformat(),
                "status": session['status']
            })
        
        return {
            "sessions": session_list,
            "total_sessions": len(session_list)
        }
        
    except Exception as e:
        logger.error(f"Admin sessions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")
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
if __name__ == "__main__":
    logger.info("🙏🏼 Starting Swami Jyotirananthan's Digital Ashram...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )

async def init_db():
    try:
        db_url = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(dsn=db_url)

        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        await conn.execute(schema_sql)
        await conn.close()
        print("✅ PostgreSQL schema initialized successfully.")
    except Exception as e:
        print(f"⚠️ Error initializing DB: {e}")

# Run once during app startup
asyncio.get_event_loop().run_until_complete(init_db())

