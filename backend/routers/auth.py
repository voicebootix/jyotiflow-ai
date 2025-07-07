from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr
from db import get_db
import bcrypt
import jwt
import os
import uuid
from datetime import datetime, timedelta

# தமிழ் - ரகசியம் (SECRET)
JWT_SECRET = os.getenv("JWT_SECRET", "jyotiflow_secret")
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
async def create_jwt_token(user_id: uuid.UUID, email: str):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# தமிழ் - உள்நுழைவு
@router.post("/login")
async def login(form: LoginForm, db=Depends(get_db)):
    user = await db.fetchrow("SELECT * FROM users WHERE email=$1", form.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(form.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = await create_jwt_token(user["id"], user["email"])
    return {"access_token": token, "user": {"id": str(user["id"]), "email": user["email"], "full_name": user.get("full_name", "")}}

# தமிழ் - பதிவு
@router.post("/register")
async def register(form: RegisterForm, db=Depends(get_db)):
    try:
        exists = await db.fetchval("SELECT 1 FROM users WHERE email=$1", form.email)
        if exists:
            raise HTTPException(status_code=400, detail="இந்த மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது")
        
        password_hash = bcrypt.hashpw(form.password.encode(), bcrypt.gensalt()).decode()
        user_id = uuid.uuid4()
        
        # Give new users 5 free credits
        free_credits = 5
        
        await db.execute("""
            INSERT INTO users (id, email, password_hash, name, full_name, credits, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """, user_id, form.email, password_hash, form.full_name, form.full_name, free_credits)
        
        token = await create_jwt_token(user_id, form.email)
        return {
            "access_token": token, 
            "user": {
                "id": str(user_id), 
                "email": form.email, 
                "full_name": form.full_name,
                "credits": free_credits
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="பதிவு தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்")

# தமிழ் - வெளியேறு
@router.post("/logout")
async def logout():
    return {"message": "Logged out"} 