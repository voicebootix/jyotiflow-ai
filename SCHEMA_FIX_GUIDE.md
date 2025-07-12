# 🔧 Schema Mismatch Fix Guide

## Current Problem

**Authentication Router (`auth.py`):**
```python
user_id = uuid.uuid4()  # Creates: "123e4567-e89b-12d3-a456-426614174000"
```

**Database Schema:**
```sql
id SERIAL PRIMARY KEY,  -- Creates: 1, 2, 3, 4, 5...
```

**Result:** User registration and login fail because UUID strings can't be stored in integer columns.

## 🚀 **OPTION A: Fix auth.py to use integers (RECOMMENDED)**

**Why recommended:**
- ✅ Simpler to implement
- ✅ Admin user already works (ID=1)
- ✅ No database changes needed
- ✅ More efficient (integers vs UUIDs)

### Step 1: Backup Current Files
```bash
cd /workspace/backend
cp routers/auth.py routers/auth.py.backup
```

### Step 2: Fix auth.py Registration
Edit `routers/auth.py` and replace the registration function:

**BEFORE:**
```python
@router.post("/register")
async def register(form: RegisterForm, db=Depends(get_db)):
    try:
        exists = await db.fetchval("SELECT 1 FROM users WHERE email=$1", form.email)
        if exists:
            raise HTTPException(status_code=400, detail="இந்த மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது")
        
        password_hash = bcrypt.hashpw(form.password.encode(), bcrypt.gensalt()).decode()
        user_id = uuid.uuid4()  # ❌ THIS IS THE PROBLEM
        
        # Give new users 5 free credits
        free_credits = 5
        
        await db.execute("""
            INSERT INTO users (id, email, password_hash, name, full_name, credits, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """, user_id, form.email, password_hash, form.full_name, form.full_name, free_credits)
```

**AFTER:**
```python
@router.post("/register")
async def register(form: RegisterForm, db=Depends(get_db)):
    try:
        exists = await db.fetchval("SELECT 1 FROM users WHERE email=$1", form.email)
        if exists:
            raise HTTPException(status_code=400, detail="இந்த மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது")
        
        password_hash = bcrypt.hashpw(form.password.encode(), bcrypt.gensalt()).decode()
        # ✅ FIXED: Let database auto-generate integer ID
        
        # Give new users 5 free credits
        free_credits = 5
        
        # ✅ FIXED: Remove id from INSERT, let SERIAL auto-increment
        user_id = await db.fetchval("""
            INSERT INTO users (email, password_hash, full_name, credits, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            RETURNING id
        """, form.email, password_hash, form.full_name, free_credits)
```

### Step 3: Remove UUID import
At the top of `routers/auth.py`, remove:
```python
import uuid  # ❌ Remove this line
```

### Step 4: Test the Fix
1. **Test admin login:** Should still work with `admin@jyotiflow.ai` / `Jyoti@2024!`
2. **Test user registration:** Should now work without UUID errors
3. **Test user login:** Should work after successful registration

---

## 🔄 **OPTION B: Change database to use UUIDs**

**Why not recommended:**
- ⚠️ More complex migration
- ⚠️ Need to update admin user ID
- ⚠️ May break existing references

### Step 1: Create Migration Script
```sql
-- migrate_to_uuid.sql

-- Add UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create new UUID column
ALTER TABLE users ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();

-- Update admin user with specific UUID
UPDATE users SET new_id = '00000000-0000-0000-0000-000000000001' WHERE id = 1;

-- Drop old id column and rename new_id
ALTER TABLE users DROP CONSTRAINT users_pkey;
ALTER TABLE users DROP COLUMN id;
ALTER TABLE users RENAME COLUMN new_id TO id;
ALTER TABLE users ADD PRIMARY KEY (id);
```

### Step 2: Run Migration
```bash
psql 'postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db' -f migrate_to_uuid.sql
```

---

## 🔗 **OPTION C: Add conversion layer**

**Most complex - not recommended for this case**

---

## 🎯 **RECOMMENDED IMPLEMENTATION (Option A)**

Here's the exact code to fix your `routers/auth.py`:

```python
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr
from db import get_db
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
# Removed: import uuid  ❌

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
async def create_jwt_token(user_id: int, email: str, role: str = "user"):  # ✅ Changed to int
    payload = {
        "sub": str(user_id),  # Convert to string for JWT
        "email": email,
        "role": role,
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
    token = await create_jwt_token(user["id"], user["email"], user.get("role", "user"))
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

# தமிழ் - பதிவு  ✅ FIXED VERSION
@router.post("/register")
async def register(form: RegisterForm, db=Depends(get_db)):
    try:
        exists = await db.fetchval("SELECT 1 FROM users WHERE email=$1", form.email)
        if exists:
            raise HTTPException(status_code=400, detail="இந்த மின்னஞ்சல் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது")
        
        password_hash = bcrypt.hashpw(form.password.encode(), bcrypt.gensalt()).decode()
        
        # Give new users 5 free credits
        free_credits = 5
        
        # ✅ FIXED: Let database auto-generate integer ID
        user_id = await db.fetchval("""
            INSERT INTO users (email, password_hash, full_name, credits, role, is_active, created_at)
            VALUES ($1, $2, $3, $4, 'user', true, NOW())
            RETURNING id
        """, form.email, password_hash, form.full_name, free_credits)
        
        token = await create_jwt_token(user_id, form.email, "user")
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
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="பதிவு தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்")

# தமிழ் - வெளியேறு
@router.post("/logout")
async def logout():
    return {"message": "Logged out"}
```

## 🧪 **Testing the Fix**

### Test 1: Admin Login (Should Still Work)
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@jyotiflow.ai", "password": "Jyoti@2024!"}'
```

### Test 2: User Registration (Should Now Work)
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass", "full_name": "Test User"}'
```

### Test 3: User Login (Should Work After Registration)
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'
```

## 🎯 **Expected Results After Fix**

✅ **Admin authentication:** Still works perfectly
✅ **User registration:** Now works with integer IDs  
✅ **User login:** Now works properly
✅ **No more Guest fallback:** Users will authenticate correctly
✅ **Database consistency:** All users use integer IDs

## 📊 **Verification Commands**

After implementing the fix, check your database:

```sql
-- Should show admin + new users
SELECT id, email, role, credits FROM users;

-- All IDs should be integers
SELECT data_type FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'id';

-- Test user count after registration
SELECT COUNT(*) FROM users;
```

**Choose Option A (recommended) and your authentication system will be fully operational!**