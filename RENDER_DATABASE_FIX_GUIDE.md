# 🚨 RENDER.COM DATABASE FIX GUIDE

## 🎯 ACCESS YOUR PRODUCTION DATABASE

### Method 1: Render Dashboard
1. **Login to Render.com**
2. **Find your PostgreSQL service** (not the web service)
3. **Click "Connect"** → **"External Connection"**
4. **Copy the connection details**

### Method 2: Direct Database URL
1. **Go to your web service dashboard**
2. **Environment** tab
3. **Find DATABASE_URL** value
4. **Copy it** (starts with `postgresql://`)

## 🔧 APPLY THE FIX

### Option A: Using psql (Recommended)
```bash
# Use the DATABASE_URL from Render
psql "postgresql://your_user:password@hostname:port/database_name"

# Then paste the entire SQL fix:
```

```sql
-- 🚨 CRITICAL FIX: Copy this entire block and paste in psql

-- Backup existing data (if any)
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'platform_name'
    ) THEN
        CREATE TABLE platform_settings_backup AS 
        SELECT * FROM platform_settings;
        RAISE NOTICE '📦 Backup created: platform_settings_backup';
    END IF;
END $$;

-- Drop wrong table structure
DROP TABLE IF EXISTS platform_settings CASCADE;

-- Create correct table structure
CREATE TABLE platform_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial platform credentials
INSERT INTO platform_settings (key, value) VALUES
    ('facebook_credentials', '{"status": "not_connected"}'),
    ('instagram_credentials', '{"status": "not_connected"}'),
    ('youtube_credentials', '{"status": "not_connected"}'),
    ('twitter_credentials', '{"status": "not_connected"}'),
    ('tiktok_credentials', '{"status": "not_connected"}')
ON CONFLICT (key) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_platform_settings_key ON platform_settings(key);

-- Verify fix
SELECT key, value->>'status' as status FROM platform_settings ORDER BY key;
```

### Option B: Using pgAdmin or DBeaver
1. **Install pgAdmin** or **DBeaver**
2. **Create new connection** using Render DATABASE_URL
3. **Open Query Editor**
4. **Paste the SQL fix above**
5. **Execute**

## ✅ VERIFICATION

After applying fix, run this query:
```sql
-- This should return rows without error
SELECT key, value FROM platform_settings WHERE key = 'youtube_credentials';
```

## 🚀 RESTART YOUR APP

1. **Go to Render dashboard**
2. **Find your web service**
3. **Manual Deploy** → **Deploy latest commit**
4. **Wait for deployment to complete**

## 🧪 TEST THE FIX

1. **Go to your live app URL**
2. **Admin Dashboard → Social Media → Platform Configuration**
3. **Try saving YouTube credentials**
4. **Should show GREEN success message!**

---

## 📋 EXPECTED RESULTS:

### BEFORE Fix:
- ❌ "Failed to save configuration"
- ❌ SQL errors in logs
- ❌ Frontend shows error despite 200 OK

### AFTER Fix:
- ✅ "Youtube configuration saved successfully!"
- ✅ Green success notification
- ✅ Data actually saved in database 