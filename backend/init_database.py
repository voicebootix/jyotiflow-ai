import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment")

# Set default values for required environment variables if not present
if not os.getenv('JWT_SECRET'):
    os.environ['JWT_SECRET'] = 'test_jwt_secret_key_for_development_only'
    print("⚠️ Using default JWT_SECRET for development")

if not os.getenv('OPENAI_API_KEY'):
    os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-development'
    print("⚠️ Using placeholder OPENAI_API_KEY")

if not os.getenv('STRIPE_SECRET_KEY'):
    os.environ['STRIPE_SECRET_KEY'] = 'sk_test_placeholder'
    print("⚠️ Using placeholder STRIPE_SECRET_KEY")

try:
    from core_foundation_enhanced import db_manager, security_manager, settings, logger
except ImportError as e:
    print(f"❌ Cannot import core foundation: {e}")
    print("Please ensure core_foundation_enhanced.py exists and all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading core foundation: {e}")
    print("Check your environment variables and configuration.")
    sys.exit(1)

async def initialize_database():
    """Initialize database and create tables"""
    print("🗄️ JyotiFlow.ai Database Initialization")
    print("=" * 50)
    
    try:
        # Initialize database manager
        print("📊 Initializing database manager...")
        await db_manager.initialize()
        print("✅ Database manager initialized")
        
        # Check database health
        print("🏥 Checking database health...")
        health = await db_manager.health_check()
        print(f"✅ Database status: {health['status']}")
        
        # Create sample data
        print("📝 Creating sample data...")
        await create_sample_data()
        print("✅ Sample data created")
        
        print("\n🎉 Database initialization complete!")
        print("🙏🏼 Your spiritual platform database is ready")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def create_sample_data():
    """Create sample data for testing"""
    conn = await db_manager.get_connection()
    
    try:
        # Create admin user
        admin_exists = await check_user_exists(conn, settings.admin_email)
        if not admin_exists:
            await create_admin_user(conn)
            print(f"👑 Admin user created: {settings.admin_email}")
        else:
            print(f"👑 Admin user already exists: {settings.admin_email}")
        
        # Create sample users
        sample_users = [
            {
                "email": "test@jyotiflow.ai",
                "password": "test123",
                "name": "Test User",
                "credits": 10
            },
            {
                "email": "spiritual.seeker@example.com",
                "password": "spiritual123", 
                "name": "Spiritual Seeker",
                "credits": 25
            }
        ]
        
        for user_data in sample_users:
            user_exists = await check_user_exists(conn, user_data["email"])
            if not user_exists:
                await create_sample_user(conn, user_data)
                print(f"👤 Sample user created: {user_data['email']}")
            else:
                print(f"👤 User already exists: {user_data['email']}")
        
        # Create sample satsang event
        await create_sample_satsang(conn)
        print("🕉️ Sample satsang event created")
        
    finally:
        await db_manager.release_connection(conn)

async def check_user_exists(conn, email: str) -> bool:
    """Check if user exists in database"""
    if db_manager.is_sqlite:
        result = await conn.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return (await result.fetchone()) is not None
    else:
        return await conn.fetchval("SELECT 1 FROM users WHERE email = $1", email) is not None

async def create_admin_user(conn):
    """Create admin user"""
    password_hash = security_manager.hash_password(settings.admin_password)
    now = datetime.now(timezone.utc)
    
    if db_manager.is_sqlite:
        await conn.execute("""
            INSERT INTO users (
                email, password_hash, name, credits, role,
                preferred_avatar_style, voice_preference, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            settings.admin_email, password_hash, "Admin Swami", 1000, "admin",
            "traditional", "wise", now.isoformat(), now.isoformat()
        ))
        await conn.commit()
    else:
        await conn.execute("""
            INSERT INTO users (
                email, password_hash, name, credits, role,
                preferred_avatar_style, voice_preference,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        """, settings.admin_email, password_hash, "Admin Swami", 1000, "admin",
             "traditional", "wise")

async def create_sample_user(conn, user_data: dict):
    """Create sample user"""
    password_hash = security_manager.hash_password(user_data["password"])
    now = datetime.now(timezone.utc)
    
    if db_manager.is_sqlite:
        await conn.execute("""
            INSERT INTO users (
                email, password_hash, name, credits, role,
                preferred_avatar_style, voice_preference,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data["email"], password_hash, user_data["name"], 
            user_data["credits"], "user", "traditional", "compassionate",
            now.isoformat(), now.isoformat()
        ))
        await conn.commit()
    else:
        await conn.execute("""
            INSERT INTO users (
                email, password_hash, name, credits, role,
                preferred_avatar_style, voice_preference,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        """, user_data["email"], password_hash, user_data["name"],
             user_data["credits"], "user", "traditional", "compassionate")

async def create_sample_satsang(conn):
    """Create sample satsang event"""
    from datetime import timedelta
    
    # Create next month's satsang
    next_month = datetime.now(timezone.utc) + timedelta(days=30)
    next_month = next_month.replace(hour=19, minute=0, second=0, microsecond=0)  # 7 PM
    
    if db_manager.is_sqlite:
        await conn.execute("""
            INSERT OR IGNORE INTO satsang_events (
                title, description, scheduled_date, max_attendees,
                spiritual_theme, created_by
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Monthly Divine Satsang",
            "Join Swami Jyotirananthan for spiritual guidance and community connection",
            next_month.isoformat(), 500,
            "Divine Love and Compassion", "system"
        ))
        await conn.commit()
    else:
        await conn.execute("""
            INSERT INTO satsang_events (
                title, description, scheduled_date, max_attendees,
                spiritual_theme, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT DO NOTHING
        """, "Monthly Divine Satsang",
             "Join Swami Jyotirananthan for spiritual guidance and community connection",
             next_month, 500, "Divine Love and Compassion", "system")

async def verify_database():
    """Verify database setup"""
    print("\n🔍 Verifying database setup...")
    
    conn = await db_manager.get_connection()
    
    try:
        # Check tables exist
        if db_manager.is_sqlite:
            result = await conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in await result.fetchall()]
        else:
            result = await conn.fetch("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row['tablename'] for row in result]
        
        print(f"📊 Tables found: {len(tables)}")
        for table in sorted(tables):
            print(f"   ✅ {table}")
        
        # Check user count
        if db_manager.is_sqlite:
            result = await conn.execute("SELECT COUNT(*) FROM users")
            user_count = (await result.fetchone())[0]
        else:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        print(f"👥 Total users: {user_count}")
        
        # Check admin user
        admin_exists = await check_user_exists(conn, settings.admin_email)
        print(f"👑 Admin user exists: {'✅' if admin_exists else '❌'}")
        
    finally:
        await db_manager.release_connection(conn)

def check_environment():
    """Check environment setup"""
    print("🔧 Checking environment...")
    
    required_vars = ['OPENAI_API_KEY', 'STRIPE_SECRET_KEY', 'JWT_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('sk-test') or 'placeholder' in os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"⚠️ Using placeholder values for: {', '.join(missing)}")
        print("💡 Please update your .env file with real API keys for production use")
    else:
        print("✅ All required environment variables found")

async def main():
    """Main initialization function"""
    print("🙏🏼 JyotiFlow.ai Database Initialization")
    print("✨ Swami Jyotirananthan's Digital Ashram")
    print("=" * 60)
    
    # Check environment
    check_environment()
    
    # Initialize database
    await initialize_database()
    
    # Verify setup
    await verify_database()
    
    print("\n🎉 Database initialization complete!")
    print("🚀 Your JyotiFlow.ai platform is ready!")
    print("🙏🏼 Run 'python main.py --dev' to start the server")

if __name__ == "__main__":
    asyncio.run(main())