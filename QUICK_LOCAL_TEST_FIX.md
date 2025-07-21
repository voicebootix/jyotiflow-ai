# 🚀 QUICK LOCAL TEST (If You Have PostgreSQL Locally)

## 🎯 IF YOU WANT TO TEST LOCALLY FIRST:

### Step 1: Set DATABASE_URL
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://username:password@localhost:5432/your_database"

# Or create .env file in backend/
echo "DATABASE_URL=postgresql://username:password@localhost:5432/your_database" > backend/.env
```

### Step 2: Run the Fix
```bash
cd backend
python apply_schema_fix.py
```

### Step 3: Test Locally
```bash
# Start backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Then test admin dashboard at http://localhost:3000
```

---

## 🎯 BUT PRODUCTION FIX IS PRIORITY!

**Your users are seeing the error right now on your live site!**

**Use RENDER_DATABASE_FIX_GUIDE.md to fix production immediately.**

---

## 🔍 WHY THIS FIXES THE PROBLEM:

### Current Error Chain:
1. **Frontend saves YouTube config** → POST request
2. **Backend tries:** `SELECT value FROM platform_settings WHERE key = 'youtube_credentials'`
3. **Database error:** Column "key" doesn't exist (table has "platform_name" instead)
4. **Backend returns error response** 
5. **Frontend shows:** "Failed to save configuration"

### After Fix:
1. **Frontend saves YouTube config** → POST request
2. **Backend executes:** `SELECT value FROM platform_settings WHERE key = 'youtube_credentials'` ✅
3. **Database returns:** `{"api_key": "...", "channel_id": "...", "status": "not_connected"}`
4. **Backend saves successfully** → Returns `{"success": true, "message": "Youtube configuration saved successfully"}`
5. **Frontend shows:** Green success notification ✅

**This is the complete root cause fix!** 