# 🔍 How to Check Your JyotiFlow Database

## Database Connection Details

**Your Database URL (found in code):**
```
postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db
```

**Breakdown:**
- **User:** jyotiflow_db_user
- **Password:** em0MmaZmvPzASryvzLHpR5g5rRZTQqpw
- **Host:** dpg-d12ohqemcj7s73fjbqtg-a
- **Database:** jyotiflow_db

## Method 1: Using psql (Command Line) - RECOMMENDED

### Install psql
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# MacOS
brew install postgresql

# Or use Docker
docker run -it --rm postgres:13 psql "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
```

### Connect to Database
```bash
psql "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
```

### Check Database State
Once connected, run these SQL commands:

```sql
-- 1. Check what tables exist
\dt

-- 2. Check users table
SELECT COUNT(*) FROM users;
SELECT id, email, role, credits, full_name FROM users;

-- 3. Check admin user specifically  
SELECT id, email, role, credits, full_name FROM users WHERE email = 'admin@jyotiflow.ai';

-- 4. Check credit packages
SELECT COUNT(*) FROM credit_packages;
SELECT id, name, credits_amount, price_usd, bonus_credits FROM credit_packages;

-- 5. Check service types
SELECT COUNT(*) FROM service_types;
SELECT id, name, description, base_credits, enabled FROM service_types LIMIT 5;

-- 6. Check if any sessions exist
SELECT COUNT(*) FROM sessions;

-- 7. Exit
\q
```

## Method 2: Using pgAdmin (GUI Tool)

### Install pgAdmin
1. Download from: https://www.pgadmin.org/download/
2. Install and open pgAdmin

### Connect to Database
1. Right-click "Servers" → "Create" → "Server"
2. **General Tab:**
   - Name: JyotiFlow Database
3. **Connection Tab:**
   - Host: `dpg-d12ohqemcj7s73fjbqtg-a`
   - Port: `5432`
   - Database: `jyotiflow_db`
   - Username: `jyotiflow_db_user`
   - Password: `em0MmaZmvPzASryvzLHpR5g5rRZTQqpw`

### Check Tables
1. Navigate: Servers → JyotiFlow Database → Databases → jyotiflow_db → Schemas → public → Tables
2. Right-click tables → "View/Edit Data" → "All Rows"

## Method 3: Online PostgreSQL Client

### Using Adminer (Web-based)
1. Go to: https://www.adminer.org/
2. Download `adminer.php`
3. Upload to a web server or run locally with PHP
4. Enter connection details:
   - System: PostgreSQL
   - Server: `dpg-d12ohqemcj7s73fjbqtg-a`
   - Username: `jyotiflow_db_user`
   - Password: `em0MmaZmvPzASryvzLHpR5g5rRZTQqpw`
   - Database: `jyotiflow_db`

## Method 4: Using Python Script (If Dependencies Available)

### Install Dependencies
```bash
pip install asyncpg
```

### Quick Check Script
```python
import asyncio
import asyncpg

async def quick_db_check():
    DATABASE_URL = "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check tables
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        print(f"📊 Tables: {[t['tablename'] for t in tables]}")
        
        # Check users
        if 'users' in [t['tablename'] for t in tables]:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"👤 Total users: {user_count}")
            
            if user_count > 0:
                users = await conn.fetch("SELECT id, email, role, credits FROM users")
                for user in users:
                    print(f"   - {user['email']}: {user['role']}, {user['credits']} credits")
        
        # Check admin user
        admin = await conn.fetchrow("SELECT * FROM users WHERE email = 'admin@jyotiflow.ai'")
        if admin:
            print(f"🔑 Admin user found: {admin['credits']} credits, role: {admin['role']}")
        else:
            print("❌ Admin user not found")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

# Run the check
asyncio.run(quick_db_check())
```

## Method 5: Using DBeaver (Universal Database Tool)

### Install DBeaver
1. Download from: https://dbeaver.io/download/
2. Install and open DBeaver

### Connect to Database
1. Click "New Database Connection"
2. Select "PostgreSQL"
3. Enter details:
   - Server Host: `dpg-d12ohqemcj7s73fjbqtg-a`
   - Port: `5432`
   - Database: `jyotiflow_db`
   - Username: `jyotiflow_db_user`
   - Password: `em0MmaZmvPzASryvzLHpR5g5rRZTQqpw`

## 🎯 What to Look For

### 1. Check if Database is Empty
```sql
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
```
- **0 tables:** Database is completely empty
- **20+ tables:** Database is initialized

### 2. Check Admin User
```sql
SELECT id, email, role, credits, full_name, created_at 
FROM users 
WHERE email = 'admin@jyotiflow.ai';
```
**Expected Result:**
- Email: admin@jyotiflow.ai
- Role: admin
- Credits: 1000
- Full_name: Admin User

### 3. Check User ID Type
```sql
SELECT data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'id';
```
- **integer:** Uses SERIAL (current schema)
- **uuid:** Uses UUID (would need auth.py fix)

### 4. Check Credit Packages
```sql
SELECT name, credits_amount, price_usd, bonus_credits 
FROM credit_packages 
ORDER BY id;
```
**Expected 4 packages:**
- Starter Pack: 10 credits, $9.99
- Spiritual Seeker: 25 credits, $19.99  
- Divine Wisdom: 50 credits, $34.99
- Enlightened Master: 100 credits, $59.99

## 🚨 Common Issues

### Connection Refused
- Database server might be down
- Network issues
- Wrong credentials

### Access Denied  
- Wrong username/password
- Database doesn't exist
- User doesn't have permissions

### SSL Required
Try adding `?sslmode=require` to the connection string:
```
postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db?sslmode=require
```

## 🎯 Quick Test Commands

### Test Connection
```bash
psql "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db" -c "SELECT 1;"
```

### Count All Tables
```bash
psql "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

### Check Admin User
```bash
psql "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db" -c "SELECT email, role, credits FROM users WHERE email = 'admin@jyotiflow.ai';"
```

Choose the method that works best for your environment. **psql (Method 1) is usually the fastest and most reliable.**