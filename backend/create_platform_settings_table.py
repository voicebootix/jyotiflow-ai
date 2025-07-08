import sqlite3
import json
from datetime import datetime

def create_platform_settings_table():
    """Create the missing platform_settings table"""
    print("🔧 Creating platform_settings table...")
    
    conn = sqlite3.connect('jyotiflow.db')
    cursor = conn.cursor()
    
    # Create platform_settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create initial placeholder entries
    initial_settings = [
        ('facebook_credentials', '{}'),
        ('instagram_credentials', '{}'),
        ('youtube_credentials', '{}'),
        ('twitter_credentials', '{}'),
        ('tiktok_credentials', '{}'),
        ('ai_model_config', '{}')
    ]
    
    for key, value in initial_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO platform_settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        print(f"✅ Created setting: {key}")
    
    conn.commit()
    
    # Verify table creation
    cursor.execute("SELECT COUNT(*) FROM platform_settings")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT key FROM platform_settings")
    keys = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"✅ Platform settings table created successfully!")
    print(f"📊 Total settings: {count}")
    print(f"🔑 Available keys: {', '.join(keys)}")
    
    return True

def verify_table_creation():
    """Verify that the table was created successfully"""
    print("\n🔍 Verifying table creation...")
    
    conn = sqlite3.connect('jyotiflow.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='platform_settings'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        print("✅ Table exists in database")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(platform_settings)")
        columns = cursor.fetchall()
        print(f"📋 Table columns: {[col[1] for col in columns]}")
        
        # Check initial data
        cursor.execute("SELECT key, value FROM platform_settings")
        rows = cursor.fetchall()
        
        print("📝 Initial settings:")
        for key, value in rows:
            print(f"   - {key}: {'configured' if value != '{}' else 'empty'}")
    else:
        print("❌ Table creation failed!")
        
    conn.close()
    return table_exists

if __name__ == "__main__":
    print("🚀 JyotiFlow Platform Settings Database Fix")
    print("=" * 50)
    
    try:
        # Create the table
        success = create_platform_settings_table()
        
        if success:
            # Verify creation
            verify_table_creation()
            
            print("\n🎯 NEXT STEPS:")
            print("1. Configure your Facebook credentials")
            print("2. Test the Facebook service")
            print("3. Test social media posting")
            print("\nSee SOCIAL_MEDIA_AUTOMATION_ROOT_CAUSE_ANALYSIS.md for detailed instructions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your database file and try again")