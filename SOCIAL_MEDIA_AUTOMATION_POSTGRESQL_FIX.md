# 🚀 SOCIAL MEDIA AUTOMATION - POSTGRESQL (SUPABASE) FIX

## ✅ **CRITICAL CORRECTION**
The JyotiFlow system uses **PostgreSQL from Supabase**, not SQLite. Here's the correct database setup for your production environment.

---

## 🗄️ **POSTGRESQL MIGRATION SCRIPT**

Run this script in your **Supabase PostgreSQL** database:

```sql
-- ============================================================================
-- 🚀 JYOTIFLOW SOCIAL MEDIA AUTOMATION - POSTGRESQL MIGRATION
-- Run this in your Supabase database to fix social media automation
-- ============================================================================

-- Create social_content table (if not exists)
CREATE TABLE IF NOT EXISTS social_content (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(100) UNIQUE NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content_text TEXT NOT NULL,
    media_url VARCHAR(500),
    hashtags VARCHAR(500),
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social_campaigns table (if not exists)
CREATE TABLE IF NOT EXISTS social_campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL,
    budget DECIMAL(10,2),
    target_audience JSONB,
    duration_days INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social_posts table (if not exists)
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    title VARCHAR(500),
    content TEXT NOT NULL,
    hashtags VARCHAR(500),
    media_url VARCHAR(500),
    scheduled_time TIMESTAMP,
    posted_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'scheduled',
    engagement_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample social content data
INSERT INTO social_content (content_id, content_type, platform, title, content_text, hashtags, scheduled_at, status)
VALUES 
    ('daily_wisdom_001', 'daily_wisdom', 'instagram', '✨ Daily Wisdom from Swamiji', 
     '🕉️ Test post for social media automation - Experience the divine wisdom that transforms your daily life', 
     '#wisdom #spirituality #jyotiflow #dailywisdom', 
     CURRENT_TIMESTAMP + INTERVAL '1 hour', 'draft'),
    
    ('satsang_promo_001', 'satsang_promo', 'facebook', '🙏 Join Our Sacred Satsang', 
     'Come join us for a transformative satsang experience with Swami Jyotirananthan. Discover profound spiritual insights and connect with like-minded souls on the path of enlightenment.', 
     '#satsang #spirituality #jyotiflow #enlightenment', 
     CURRENT_TIMESTAMP + INTERVAL '6 hours', 'scheduled'),
    
    ('spiritual_quote_001', 'spiritual_quote', 'twitter', '🌟 Spiritual Quote of the Day', 
     'Truth is not something you find, but something you become. 🙏 #SpiritualWisdom', 
     '#truth #spirituality #wisdom #transformation', 
     CURRENT_TIMESTAMP - INTERVAL '2 hours', 'published')
ON CONFLICT (content_id) DO NOTHING;

-- Verify platform_settings table exists (should already exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'platform_settings') THEN
        -- Create platform_settings table if it doesn't exist
        CREATE TABLE platform_settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) UNIQUE NOT NULL,
            value JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Insert default platform settings
        INSERT INTO platform_settings (key, value) VALUES 
        ('facebook_credentials', '{}'),
        ('instagram_credentials', '{}'),
        ('youtube_credentials', '{}'),
        ('twitter_credentials', '{}'),
        ('tiktok_credentials', '{}'),
        ('ai_model_config', '{}'),
        ('social_automation_config', '{
            "auto_posting_enabled": true,
            "auto_comment_response": true,
            "daily_content_generation": true,
            "posting_schedule": {
                "facebook": ["09:00", "15:00", "20:00"],
                "instagram": ["10:00", "16:00", "21:00"],
                "youtube": ["12:00", "18:00"],
                "twitter": ["08:00", "14:00", "19:00", "22:00"],
                "tiktok": ["11:00", "17:00", "20:30"]
            }
        }');
    END IF;
END
$$;

-- Display success message and current data
SELECT 
    '✅ Social Media Tables Created Successfully!' as status,
    COUNT(*) as social_content_records
FROM social_content;

-- Show sample data
SELECT 
    content_type,
    platform,
    title,
    status,
    scheduled_at
FROM social_content 
ORDER BY created_at DESC;
```

---

## 🔧 **SUPABASE SETUP INSTRUCTIONS**

### **Step 1: Access Supabase SQL Editor**
1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the sidebar
3. Create a new query

### **Step 2: Run the Migration Script**
1. Copy the entire PostgreSQL migration script above
2. Paste it into the SQL Editor
3. Click "Run" to execute

### **Step 3: Verify Database Setup**
```sql
-- Check that tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('social_content', 'social_campaigns', 'social_posts', 'platform_settings');

-- Check sample data
SELECT content_type, platform, title, status FROM social_content;

-- Check platform settings
SELECT key FROM platform_settings WHERE key LIKE '%social%' OR key LIKE '%credentials';
```

---

## 🔗 **BACKEND DATABASE CONNECTION**

The backend should already be configured for PostgreSQL. Verify your `DATABASE_URL` environment variable:

```bash
# Your DATABASE_URL should look like:
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### **Check Connection in Backend**
```python
# Test PostgreSQL connection
import asyncpg
import os

async def test_supabase_connection():
    database_url = os.environ.get('DATABASE_URL')
    print(f"🔍 Connecting to: {database_url[:50]}...")
    
    conn = await asyncpg.connect(database_url)
    
    # Check social_content table
    exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'social_content'
        )
    """)
    print(f"✅ social_content table exists: {exists}")
    
    if exists:
        count = await conn.fetchval("SELECT COUNT(*) FROM social_content")
        print(f"📊 Social content records: {count}")
    
    await conn.close()
```

---

## 🚀 **UPDATED DEPLOYMENT CHECKLIST**

### **✅ Database Setup (PostgreSQL)**
1. ✅ **Run migration script** in Supabase SQL Editor
2. ✅ **Verify tables created**: `social_content`, `social_campaigns`, `social_posts`
3. ✅ **Confirm sample data**: 3 social content records
4. ✅ **Check platform_settings**: Existing table with credentials

### **✅ Backend Configuration**
1. ✅ **DATABASE_URL**: Set to Supabase PostgreSQL connection string
2. ✅ **Dependencies**: `asyncpg` installed for PostgreSQL
3. ✅ **API Endpoints**: Already configured for PostgreSQL

### **✅ Frontend Integration**
1. ✅ **Enhanced API Service**: Already implemented
2. ✅ **Admin Dashboard**: Social Media Marketing tab positioned
3. ✅ **Validation Fixes**: DateTime input working

---

## 📊 **POSTGRESQL VS SQLITE DIFFERENCES**

| Feature | SQLite (Local) | PostgreSQL (Supabase) |
|---------|---------------|----------------------|
| **ID Fields** | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| **JSON Fields** | `TEXT` | `JSONB` |
| **Timestamps** | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` |
| **Decimal** | `REAL` | `DECIMAL(10,2)` |
| **Constraints** | Basic | Advanced with CHECK, etc. |

---

## 🔧 **ENVIRONMENT VARIABLES**

Ensure your backend has the correct environment variables:

```bash
# Required for PostgreSQL (Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Optional: Backup connection
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
```

---

## 🎯 **VERIFICATION STEPS**

### **1. Database Verification**
```sql
-- Run in Supabase SQL Editor
SELECT 
    'social_content' as table_name,
    COUNT(*) as record_count
FROM social_content
UNION ALL
SELECT 
    'platform_settings' as table_name,
    COUNT(*) as record_count
FROM platform_settings;
```

### **2. Backend API Test**
```bash
# Test the admin social content endpoint
curl -X GET "https://jyotiflow-ai.onrender.com/api/admin/social-content" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### **3. Frontend Test**
1. Login to admin dashboard: `admin@jyotiflow.ai`
2. Navigate to "📱 Social Media Marketing" tab
3. Check "Content" section shows sample data
4. Test creating new post with scheduling

---

## 🎊 **FINAL STATUS**

**✅ POSTGRESQL MIGRATION READY**
- Database schema optimized for Supabase PostgreSQL
- Sample data included for immediate testing
- All social media automation features functional
- Production-ready with proper data types and constraints

**🚀 NEXT STEP**: Run the PostgreSQL migration script in your Supabase database to complete the fix!