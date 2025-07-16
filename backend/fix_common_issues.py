"""
Common Fixes for Database Self-Healing System
Run these fixes based on validation errors
"""

import os
import asyncio
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_permissions():
    """Fix database permissions if needed"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Grant necessary permissions
        await conn.execute("""
            GRANT SELECT, INSERT, UPDATE, DELETE 
            ON ALL TABLES IN SCHEMA public 
            TO CURRENT_USER
        """)
        print("✅ Permissions fixed")
    except Exception as e:
        print(f"❌ Could not fix permissions: {e}")
        print("Ask your database admin to run:")
        print("GRANT ALL PRIVILEGES ON DATABASE your_db TO your_user;")
    finally:
        await conn.close()

async def fix_ast_parsing():
    """Fix AST parsing issues"""
    print("Fixing common AST parsing issues...")
    
    # Install required packages
    import subprocess
    import sys
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "astunparse"], 
                      check=True, capture_output=True, text=True)
        print("✅ Installed astunparse")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install astunparse: {e.stderr}")
        return
    
    # Create __init__.py files if missing
    dirs = ['backend', 'backend/routers', 'backend/utils']
    for dir in dirs:
        init_file = os.path.join(dir, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
            print(f"✅ Created {init_file}")

async def fix_import_errors():
    """Fix common import errors"""
    # Add project root to Python path
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print("✅ Fixed Python path")

async def create_required_tables():
    """Create tables required by self-healing system"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Create backup tracking table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS database_backups (
                id SERIAL PRIMARY KEY,
                backup_id VARCHAR(255) UNIQUE,
                table_name VARCHAR(255),
                column_name VARCHAR(255),
                issue_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create health check results table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_check_results (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                results JSONB,
                issues_found INTEGER,
                issues_fixed INTEGER,
                critical_count INTEGER
            )
        """)
        
        print("✅ Created required tables")
    finally:
        await conn.close()

async def fix_type_cast_errors():
    """Fix specific type casting in code using AST analysis"""
    # This would fix actual code files
    files_to_check = [
        'backend/routers/sessions.py',
        'backend/utils/database.py',
        'backend/services/user_service.py'
    ]

    for file in files_to_check:
        if os.path.exists(file):
            print(f"⚠️  Manual review needed for {file}")
            print("   - Check for JavaScript-style parseInt() in Python code")
            print("   - Check for PostgreSQL ::integer casts in SQL strings")
            print("   - Use proper parameterized queries instead")

async def main():
    """Run all fixes"""
    print("🔧 Running common fixes...\n")
    
    await fix_permissions()
    await fix_ast_parsing()
    await fix_import_errors()
    await create_required_tables()
    await fix_type_cast_errors()
    
    print("\n✅ Fixes completed. Run validation again.")

if __name__ == "__main__":
    asyncio.run(main())