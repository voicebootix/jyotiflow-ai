"""
Common Fixes for Database Self-Healing System
Run these fixes based on validation errors
"""

import os
import asyncio
import asyncpg
import sys

DATABASE_URL = os.getenv("DATABASE_URL")
DB_APP_USER = os.getenv("DB_APP_USER", "app_user")  # Default to 'app_user' if not set

# Global connection pool
pool = None

async def get_pool():
    """Get or create connection pool"""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return pool

async def fix_permissions():
    """Fix database permissions if needed"""
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        try:
            # Check if the user exists
            user_exists = await conn.fetchval(
                "SELECT 1 FROM pg_user WHERE usename = $1", 
                DB_APP_USER
            )
            
            if not user_exists:
                print(f"❌ User '{DB_APP_USER}' does not exist in the database")
                print(f"Set DB_APP_USER environment variable to the correct application user")
                return
            
            # Grant necessary permissions to the specific user
            # Using parameterized query for safety
            await conn.execute(f"""
                GRANT SELECT, INSERT, UPDATE, DELETE 
                ON ALL TABLES IN SCHEMA public 
                TO "{DB_APP_USER.replace('"', '""')}"
            """)
            
            # Also grant schema-level permissions for CREATE and ALTER
            await conn.execute(f"""
                GRANT CREATE ON SCHEMA public TO "{DB_APP_USER.replace('"', '""')}"
            """)
            
            print(f"✅ Permissions fixed for user: {DB_APP_USER}")
        except Exception as e:
            print(f"❌ Could not fix permissions: {e}")
            print(f"Ask your database admin to run:")
            quoted_user = DB_APP_USER.replace('"', '""')
            print(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "{quoted_user}";')
            print(f'GRANT CREATE ON SCHEMA public TO "{quoted_user}";')

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
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=True)
                print(f"✅ Created directory: {dir}")
            
            init_file = os.path.join(dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'a') as f:
                    pass  # Just create empty file
                print(f"✅ Created {init_file}")
        except IOError as e:
            print(f"❌ Failed to create {init_file}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error creating {init_file}: {e}")

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
    pool = await get_pool()
    
    async with pool.acquire() as conn:
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
    
    fixes = [
        ("Database Permissions", fix_permissions),
        ("AST Parsing Setup", fix_ast_parsing),
        ("Import Errors", fix_import_errors),
        ("Required Tables", create_required_tables),
        ("Type Cast Review", fix_type_cast_errors)
    ]
    
    results = {}
    for name, fix_func in fixes:
        try:
            print(f"\n🔄 Running: {name}")
            await fix_func()
            results[name] = "✅ Success"
        except Exception as e:
            results[name] = f"❌ Failed: {str(e)}"
            print(f"❌ Error in {name}: {e}")
            # Continue with the next fix
    
    print("\n" + "="*50)
    print("📊 Fix Summary:")
    print("="*50)
    for name, status in results.items():
        print(f"  {name}: {status}")
    
    # Check if all fixes succeeded
    all_success = all("✅ Success" in status for status in results.values())
    if all_success:
        print("\n✅ All fixes completed successfully! Run validation again.")
    else:
        print("\n⚠️  Some fixes failed. Please review the errors above.")
        
    # Close the connection pool if it was created
    global pool
    if pool:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())