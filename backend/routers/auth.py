from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr
from db import get_db
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

# தமிழ் - ரகசியம் (SECRET) - SECURITY FIX: Remove hardcoded fallback
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required for security. Please set it before starting the application.")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60 * 24

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# தமிழ் - உள்நுழைவு படிவம்
class LoginForm(BaseModel):
    email: EmailStr
    password: str

# தமிழ் - பதிவு படிவம்
class RegisterForm(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

# தமிழ் - JWT உருவாக்கம்
async def create_jwt_token(user_id: int, email: str, role: str = "user"):
    payload = {
        "sub": str(user_id),  # Changed from "user_id" to "sub" for standard JWT format
        "email": email,
        "role": role,  # Added missing role field
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Password hash validation function
def validate_password_hash(password_hash: str) -> bool:
    """Validate that password hash is in correct bcrypt format"""
    if not password_hash:
        return False
    if len(password_hash) != 60:
        return False  
    if not password_hash.startswith('$2b$'):
        return False
    return True

# தமிழ் - உள்நுழைவு
@router.post("/login")
async def login(form: LoginForm, db=Depends(get_db)):
    print(f"🔍 Login attempt for: {form.email}")
    
    user = await db.fetchrow("SELECT * FROM users WHERE email=$1", form.email)
    if not user:
        print(f"❌ User not found: {form.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print(f"✅ User found: {user['email']}")
    print(f"📝 Password hash: {user['password_hash'][:20]}...")
    
    # Validate password hash format
    if not validate_password_hash(user["password_hash"]):
        print(f"❌ Invalid password hash format for user: {form.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # FIXED: Use consistent UTF-8 encoding for password verification
    try:
        password_check = bcrypt.checkpw(form.password.encode('utf-8'), user["password_hash"].encode('utf-8'))
        print(f"🔐 Password check result: {password_check}")
    except Exception as e:
        print(f"❌ Password verification error for {form.email}: {e}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not password_check:
        print(f"❌ Password verification failed for: {form.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print(f"✅ Password verified for: {form.email}")
    
    # Generate JWT token
    try:
        token = await create_jwt_token(user["id"], user["email"], user.get("role", "user"))
        print(f"✅ JWT token generated for: {form.email}")
    except Exception as e:
        print(f"❌ JWT token generation failed for {form.email}: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")
    
    return {
        "access_token": token, 
        "user": {
            "id": str(user["id"]), 
            "email": user["email"], 
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "user"),
            "credits": user.get("credits", 0)
        }
    }

# தமிழ் - பதிவு
@router.post("/register")
async def register(form: RegisterForm, db=Depends(get_db)):
    try:
        print(f"🔍 Registration attempt for: {form.email}")
        
        exists = await db.fetchval("SELECT 1 FROM users WHERE email=$1", form.email)
        if exists:
            print(f"❌ User already exists: {form.email}")
            raise HTTPException(status_code=400, detail="இந்த மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது")
        
        # FIXED: Use consistent UTF-8 encoding for password hashing
        password_hash = bcrypt.hashpw(form.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"📝 Generated password hash: {password_hash[:20]}...")
        
        # Validate generated hash
        if not validate_password_hash(password_hash):
            print(f"❌ Generated password hash is invalid for: {form.email}")
            raise HTTPException(status_code=500, detail="Password hashing failed")
        
        # Give new users 5 free credits
        free_credits = 5
        
        # ✅ FIXED: Let database auto-generate integer ID
        user_id = await db.fetchval("""
            INSERT INTO users (email, password_hash, full_name, credits, role, is_active, created_at)
            VALUES ($1, $2, $3, $4, 'user', true, NOW())
            RETURNING id
        """, form.email, password_hash, form.full_name, free_credits)
        
        print(f"✅ User registered successfully: {form.email} with ID: {user_id}")
        
        token = await create_jwt_token(user_id, form.email, "user")
        print(f"✅ JWT token generated for new user: {form.email}")
        
        return {
            "access_token": token, 
            "user": {
                "id": str(user_id), 
                "email": form.email, 
                "full_name": form.full_name,
                "role": "user",
                "credits": free_credits
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error for {form.email}: {e}")
        raise HTTPException(status_code=500, detail="பதிவு தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்")

# தமிழ் - வெளியேறு
@router.post("/logout")
async def logout():
    return {"message": "Logged out"} 