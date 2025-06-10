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
        
    except Exception as e:
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

@app.get('/admin')
def admin_page():
    ADMIN_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🙏🏼 Admin Dashboard - JyotiFlow.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                min-height: 100vh;
                color: white;
            }
            
            .header {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .logo {
                font-size: 2rem;
                margin-bottom: 5px;
            }
            
            .title {
                font-size: 1.8rem;
                background: linear-gradient(45deg, #FFD700, #FFA500);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 30px 20px;
            }
            
            .login-section {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .dashboard-section {
                display: none;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
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
            
            .stat-label {
                font-size: 1rem;
                opacity: 0.8;
            }
            
            .data-section {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .section-title {
                color: #FFD700;
                font-size: 1.3rem;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .table th,
            .table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .table th {
                background: rgba(255, 215, 0, 0.1);
                color: #FFD700;
                font-weight: bold;
            }
            
            .table tr:hover {
                background: rgba(255, 255, 255, 0.05);
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #FFD700;
            }
            
            .form-input {
                width: 100%;
                max-width: 300px;
                padding: 10px;
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 1rem;
            }
            
            .btn {
                background: linear-gradient(45deg, #FFD700, #FFA500);
                color: #333;
                border: none;
                padding: 10px 25px;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
            }
            
            .btn-danger {
                background: linear-gradient(45deg, #e74c3c, #c0392b);
                color: white;
            }
            
            .btn-success {
                background: linear-gradient(45deg, #27ae60, #2ecc71);
                color: white;
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
                text-align: center;
                margin-top: 30px;
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
                .stats-grid {
                    grid-template-columns: 1fr;
                }
                
                .table {
                    font-size: 0.9rem;
                }
                
                .table th,
                .table td {
                    padding: 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🙏🏼</div>
            <h1 class="title">JyotiFlow.ai Admin Dashboard</h1>
        </div>
        
        <div class="container">
            <!-- Login Section -->
            <div id="loginSection" class="login-section">
                <h2 style="color: #FFD700; margin-bottom: 20px;">Admin Access</h2>
                
                <div id="errorMessage" class="error-message"></div>
                
                <form id="adminLoginForm">
                    <div class="form-group">
                        <label class="form-label">Admin Email:</label>
                        <input type="email" class="form-input" id="adminUsername" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Admin Password:</label>
                        <input type="password" class="form-input" id="adminPassword" required>
                    </div>
                    
                    <button type="submit" class="btn">🔐 Access Dashboard</button>
                </form>
            </div>
            
            <!-- Dashboard Section -->
            <div id="dashboardSection" class="dashboard-section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-value" id="totalUsers">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🔮</div>
                        <div class="stat-value" id="totalSessions">0</div>
                        <div class="stat-label">Total Sessions</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">💰</div>
                        <div class="stat-value" id="totalRevenue">$0</div>
                        <div class="stat-label">Total Revenue</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-value" id="todaySessions">0</div>
                        <div class="stat-label">Today's Sessions</div>
                    </div>
                </div>
                
                <div class="data-section">
                    <h3 class="section-title">👥 User Management</h3>
                    <div id="successMessage" class="success-message"></div>
                    
                    <button class="btn" onclick="loadUsers()">🔄 Refresh Users</button>
                    
                    <table class="table" id="usersTable">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Credits</th>
                                <th>Joined</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="usersTableBody">
                            <tr>
                                <td colspan="6" style="text-align: center; opacity: 0.7;">Loading users...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="data-section">
                    <h3 class="section-title">🔮 Recent Sessions</h3>
                    
                    <button class="btn" onclick="loadSessions()">🔄 Refresh Sessions</button>
                    
                    <table class="table" id="sessionsTable">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Service</th>
                                <th>Question</th>
                                <th>Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="sessionsTableBody">
                            <tr>
                                <td colspan="6" style="text-align: center; opacity: 0.7;">Loading sessions...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="data-section">
                    <h3 class="section-title">⚙️ System Health</h3>
                    
                    <button class="btn" onclick="checkSystemHealth()">🔄 Check Health</button>
                    
                    <div id="systemHealth" style="margin-top: 15px;">
                        <p>Click "Check Health" to view system status...</p>
                    </div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/login">🔐 User Login</a>
                <button class="btn btn-danger" onclick="adminLogout()" style="display: none;" id="logoutBtn">🚪 Logout</button>
            </div>
        </div>
        
        <script>
            // Admin login
            document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const username = document.getElementById('adminUsername').value;
                const password = document.getElementById('adminPassword').value;
                
                const errorDiv = document.getElementById('errorMessage');
                errorDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/admin/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: username,  // ← Change 'username' to 'email'
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        localStorage.setItem('admin_token', data.token);
                        showDashboard();
                        loadDashboardData();
                    } else {
                        errorDiv.textContent = data.message || 'Invalid admin credentials.';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Connection error. Please try again.';
                    errorDiv.style.display = 'block';
                }
            });
            
            function showDashboard() {
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('dashboardSection').style.display = 'block';
                document.getElementById('logoutBtn').style.display = 'inline-block';
            }
            
            function adminLogout() {
                localStorage.removeItem('admin_token');
                document.getElementById('loginSection').style.display = 'block';
                document.getElementById('dashboardSection').style.display = 'none';
                document.getElementById('logoutBtn').style.display = 'none';
            }
            
            async function loadDashboardData() {
                await loadStats();
                await loadUsers();
                await loadSessions();
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/admin_stats', {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('totalUsers').textContent = data.stats.total_users;
                        document.getElementById('totalSessions').textContent = data.stats.total_sessions;
                        document.getElementById('totalRevenue').textContent = '$' + data.stats.total_revenue;
                        document.getElementById('todaySessions').textContent = data.stats.today_sessions;
                    }
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            async function loadUsers() {
                try {
                    const response = await fetch('/api/admin/users', {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const tbody = document.getElementById('usersTableBody');
                        tbody.innerHTML = '';
                        
                        data.users.forEach(user => {
                            const row = tbody.insertRow();
                            row.innerHTML = `
                                <td>${user.id}</td>
                                <td>${user.first_name} ${user.last_name}</td>
                                <td>${user.email}</td>
                                <td>${user.credits}</td>
                                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-success" onclick="addCredits(${user.id})">💰 Add Credits</button>
                                </td>
                            `;
                        });
                    }
                } catch (error) {
                    console.error('Error loading users:', error);
                }
            }
            
            async function loadSessions() {
                try {
                    const response = await fetch('/admin_sessions', {
                        headers: {
                            'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const tbody = document.getElementById('sessionsTableBody');
                        tbody.innerHTML = '';
                        
                        data.sessions.forEach(session => {
                            const row = tbody.insertRow();
                            row.innerHTML = `
                                <td>${session.id}</td>
                                <td>${session.user_email}</td>
                                <td>${session.service_type}</td>
                                <td>${session.question.substring(0, 50)}...</td>
                                <td>${new Date(session.created_at).toLocaleDateString()}</td>
                                <td><span style="color: #27ae60;">✅ Complete</span></td>
                            `;
                        });
                    }
                } catch (error) {
                    console.error('Error loading sessions:', error);
                }
            }
            
            async function addCredits(userId) {
                const credits = prompt('How many credits to add?');
                if (credits && !isNaN(credits)) {
                    try {
                        const response = await fetch('/admin_add_credits', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
                            },
                            body: JSON.stringify({
                                user_id: userId,
                                credits: parseInt(credits)
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            const successDiv = document.getElementById('successMessage');
                            successDiv.textContent = `Successfully added ${credits} credits!`;
                            successDiv.style.display = 'block';
                            setTimeout(() => successDiv.style.display = 'none', 3000);
                            loadUsers();
                        }
                    } catch (error) {
                        console.error('Error adding credits:', error);
                    }
                }
            }
            
            async function checkSystemHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    const healthDiv = document.getElementById('systemHealth');
                    healthDiv.innerHTML = `
                        <p><strong>Status:</strong> <span style="color: #27ae60;">✅ ${data.status}</span></p>
                        <p><strong>Database:</strong> <span style="color: #27ae60;">✅ Connected</span></p>
                        <p><strong>Timestamp:</strong> ${data.timestamp}</p>
                        <p><strong>Version:</strong> JyotiFlow.ai v3.3</p>
                    `;
                } catch (error) {
                    const healthDiv = document.getElementById('systemHealth');
                    healthDiv.innerHTML = `
                        <p><strong>Status:</strong> <span style="color: #e74c3c;">❌ Error</span></p>
                        <p><strong>Message:</strong> Unable to connect to system</p>
                    `;
                }
            }
            
            // Check if already logged in
            if (localStorage.getItem('admin_token')) {
                showDashboard();
                loadDashboardData();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=ADMIN_TEMPLATE)
    
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

@app.get("/api/admin/users")
async def get_admin_users(admin: Dict = Depends(get_admin_user)):
    """தமிழ் - Get all users for admin dashboard"""
    conn = None
    try:
        conn = await get_db_connection()
        
        users = await conn.fetch("""
            SELECT id, first_name, last_name, email, credits, created_at, last_login
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users_list = []
        for user in users:
            users_list.append({
                "id": user['id'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "email": user['email'],
                "credits": user['credits'],
                "created_at": user['created_at'].isoformat() if user['created_at'] else None,
                "last_login": user['last_login'].isoformat() if user['last_login'] else None
            })
        
        return {
            "success": True,
            "users": users_list
        }
        
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load users")
    finally:
        if conn:
            await release_db_connection(conn)

# Helper function for admin authentication
async def get_admin_user(request: Request):
    """தமிழ் - Verify admin JWT token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return {"email": payload.get("email"), "is_admin": True}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
    """தமிழ் - Get all sessions for admin dashboard"""
    conn = None
    try:
        conn = await get_db_connection()
        
        sessions = await conn.fetch("""
            SELECT s.id, s.user_email, s.session_type, s.credits_used, 
                   s.session_time, s.status, s.result_summary
            FROM sessions s
            ORDER BY s.session_time DESC
            LIMIT 100
        """)
        
        sessions_list = []
        for session in sessions:
            sessions_list.append({
                "id": session['id'],
                "user_email": session['user_email'],
                "service_type": session['session_type'],
                "credits_used": session['credits_used'],
                "session_time": session['session_time'].isoformat() if session['session_time'] else None,
                "status": session['status'],
                "question": session['result_summary'][:100] + "..." if session['result_summary'] else "No question"
            })
        
        return {
            "success": True,
            "sessions": sessions_list
        }
        
    except Exception as e:
        logger.error(f"Admin sessions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load sessions")
    finally:
        if conn:
            await release_db_connection(conn)

@app.post("/admin_add_credits")
async def add_user_credits(request: Request, admin: Dict = Depends(get_admin_user)):
    """தமிழ் - Add credits to user account"""
    conn = None
    try:
        data = await request.json()
        user_id = data.get('user_id')
        credits = data.get('credits')
        
        if not user_id or not credits or credits <= 0:
            raise HTTPException(status_code=400, detail="Invalid user ID or credits amount")
        
        conn = await get_db_connection()
        
        # Get user info
        user = await conn.fetchrow("SELECT email, credits FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add credits
        await conn.execute(
            "UPDATE users SET credits = credits + $1 WHERE id = $2",
            credits, user_id
        )
        
        # Log the transaction
        await conn.execute("""
            INSERT INTO admin_logs (admin_email, action, target_user, details, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        """, admin['email'], "add_credits", user['email'], 
            f"Added {credits} credits (admin action)", datetime.utcnow())
        
        return {
            "success": True,
            "message": f"Successfully added {credits} credits to {user['email']}",
            "new_balance": user['credits'] + credits
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add credits error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add credits")
    finally:
        if conn:
            await release_db_connection(conn)

# Helper function for admin authentication
async def get_admin_user(request: Request):
    """தமிழ் - Verify admin JWT token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return {"email": payload.get("email"), "is_admin": True}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
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

