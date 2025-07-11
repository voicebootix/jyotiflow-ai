"""
Authentication System Fix for JyotiFlow.ai
Addresses JWT token validation issues and session management problems
identified in deployment log analysis.
"""

import asyncio
import asyncpg
import os
import logging
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationFixer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/jyotiflow')
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', '1cdc8d78417b8fc61716ccc3d5e169cc')
        self.connection = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("✅ Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("✅ Database connection closed")
    
    async def create_session_tables(self):
        """Create enhanced session management tables"""
        logger.info("🔧 Creating session management tables...")
        
        # User sessions table
        create_sessions_sql = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            jwt_token TEXT,
            session_type VARCHAR(50) DEFAULT 'web',
            ip_address INET,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT true,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self.connection.execute(create_sessions_sql)
        
        # Live chat sessions table
        create_chat_sessions_sql = """
        CREATE TABLE IF NOT EXISTS live_chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            session_type VARCHAR(50) DEFAULT 'text',
            status VARCHAR(50) DEFAULT 'pending',
            credits_used INTEGER DEFAULT 0,
            duration_seconds INTEGER DEFAULT 0,
            agora_channel_name VARCHAR(255),
            agora_token TEXT,
            started_at TIMESTAMP WITH TIME ZONE,
            ended_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self.connection.execute(create_chat_sessions_sql)
        
        # Authentication logs table
        create_auth_logs_sql = """
        CREATE TABLE IF NOT EXISTS authentication_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            ip_address INET,
            user_agent TEXT,
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self.connection.execute(create_auth_logs_sql)
        
        logger.info("✅ Session management tables created")
    
    async def fix_user_table_structure(self):
        """Ensure user table has all required fields for authentication"""
        logger.info("🔧 Fixing user table structure...")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("password_hash", "VARCHAR(255)"),
            ("email_verified", "BOOLEAN DEFAULT false"),
            ("is_active", "BOOLEAN DEFAULT true"),
            ("role", "VARCHAR(50) DEFAULT 'user'"),
            ("credits", "INTEGER DEFAULT 0"),
            ("last_login", "TIMESTAMP WITH TIME ZONE"),
            ("last_login_at", "TIMESTAMP WITH TIME ZONE"),
            ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT NOW()"),
            ("updated_at", "TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
        ]
        
        for column_name, column_definition in columns_to_add:
            try:
                alter_sql = f"""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS {column_name} {column_definition};
                """
                await self.connection.execute(alter_sql)
                logger.info(f"📝 Added column {column_name} to users table")
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {column_name}: {e}")
        
        # Ensure admin user has proper setup
        await self.ensure_admin_user()
        
        logger.info("✅ User table structure fixed")
    
    async def ensure_admin_user(self):
        """Ensure admin user exists and has proper credentials"""
        logger.info("🔧 Ensuring admin user setup...")
        
        # Check if admin user exists
        admin_user = await self.connection.fetchrow(
            "SELECT * FROM users WHERE email = $1", 
            "admin@jyotiflow.ai"
        )
        
        if admin_user:
            # Update admin user with proper fields
            update_sql = """
            UPDATE users 
            SET 
                role = 'admin',
                credits = 1000,
                is_active = true,
                email_verified = true,
                updated_at = NOW()
            WHERE email = 'admin@jyotiflow.ai';
            """
            await self.connection.execute(update_sql)
            logger.info("✅ Admin user updated")
        else:
            # Create admin user
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            insert_sql = """
            INSERT INTO users (
                email, name, password_hash, role, credits, 
                is_active, email_verified, created_at, updated_at
            ) VALUES (
                'admin@jyotiflow.ai', 'Admin User', $1, 'admin', 1000,
                true, true, NOW(), NOW()
            );
            """
            await self.connection.execute(insert_sql, password_hash)
            logger.info("✅ Admin user created")
    
    def generate_jwt_token(self, user_id, email, role="user", expires_hours=24):
        """Generate a properly formatted JWT token"""
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    def validate_jwt_token(self, token):
        """Validate a JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return None, f"Invalid token: {str(e)}"
    
    async def create_test_tokens(self):
        """Create test tokens for debugging"""
        logger.info("🔧 Creating test tokens...")
        
        # Get admin user
        admin_user = await self.connection.fetchrow(
            "SELECT id, email, role FROM users WHERE email = $1", 
            "admin@jyotiflow.ai"
        )
        
        if admin_user:
            # Generate test token
            token = self.generate_jwt_token(
                admin_user['id'], 
                admin_user['email'], 
                admin_user['role']
            )
            
            # Validate the token
            payload, error = self.validate_jwt_token(token)
            
            if payload:
                logger.info("✅ Test token generated and validated successfully")
                logger.info(f"📝 Token payload: {payload}")
                
                # Save token to file for testing
                with open('/tmp/test_jwt_token.txt', 'w') as f:
                    f.write(token)
                logger.info("📁 Test token saved to /tmp/test_jwt_token.txt")
                
                return token
            else:
                logger.error(f"❌ Token validation failed: {error}")
                return None
        else:
            logger.error("❌ Admin user not found")
            return None
    
    async def fix_authentication_middleware_data(self):
        """Fix data issues that might affect authentication middleware"""
        logger.info("🔧 Fixing authentication middleware data...")
        
        # Clean up invalid sessions
        cleanup_sql = """
        UPDATE user_sessions 
        SET is_active = false 
        WHERE expires_at < NOW() OR expires_at IS NULL;
        """
        await self.connection.execute(cleanup_sql)
        
        # Ensure all users have proper role assignments
        role_fix_sql = """
        UPDATE users 
        SET role = COALESCE(role, 'user')
        WHERE role IS NULL OR role = '';
        """
        await self.connection.execute(role_fix_sql)
        
        # Fix any null email issues
        email_fix_sql = """
        UPDATE users 
        SET email = CONCAT('user_', id, '@jyotiflow.ai')
        WHERE email IS NULL OR email = '';
        """
        await self.connection.execute(email_fix_sql)
        
        logger.info("✅ Authentication middleware data fixed")
    
    async def create_session_management_functions(self):
        """Create database functions for session management"""
        logger.info("🔧 Creating session management functions...")
        
        # Function to create a new session
        create_session_function = """
        CREATE OR REPLACE FUNCTION create_user_session(
            p_user_id INTEGER,
            p_session_token VARCHAR(255),
            p_jwt_token TEXT,
            p_session_type VARCHAR(50) DEFAULT 'web',
            p_ip_address INET DEFAULT NULL,
            p_user_agent TEXT DEFAULT NULL,
            p_expires_hours INTEGER DEFAULT 24
        ) RETURNS INTEGER AS $$
        DECLARE
            session_id INTEGER;
        BEGIN
            INSERT INTO user_sessions (
                user_id, session_token, jwt_token, session_type,
                ip_address, user_agent, expires_at, created_at, updated_at
            ) VALUES (
                p_user_id, p_session_token, p_jwt_token, p_session_type,
                p_ip_address, p_user_agent, 
                NOW() + INTERVAL '1 hour' * p_expires_hours,
                NOW(), NOW()
            ) RETURNING id INTO session_id;
            
            RETURN session_id;
        END;
        $$ LANGUAGE plpgsql;
        """
        await self.connection.execute(create_session_function)
        
        # Function to validate a session
        validate_session_function = """
        CREATE OR REPLACE FUNCTION validate_user_session(
            p_session_token VARCHAR(255)
        ) RETURNS TABLE(
            user_id INTEGER,
            email VARCHAR(255),
            role VARCHAR(50),
            is_valid BOOLEAN
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                u.id as user_id,
                u.email,
                u.role,
                (s.is_active AND s.expires_at > NOW()) as is_valid
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = p_session_token;
        END;
        $$ LANGUAGE plpgsql;
        """
        await self.connection.execute(validate_session_function)
        
        logger.info("✅ Session management functions created")
    
    async def run_comprehensive_auth_fix(self):
        """Run all authentication fixes in sequence"""
        logger.info("🚀 Starting comprehensive authentication fix...")
        
        if not await self.connect():
            return False
        
        try:
            # Create session tables
            await self.create_session_tables()
            
            # Fix user table structure
            await self.fix_user_table_structure()
            
            # Fix authentication data
            await self.fix_authentication_middleware_data()
            
            # Create session management functions
            await self.create_session_management_functions()
            
            # Create test tokens
            test_token = await self.create_test_tokens()
            
            logger.info("🎉 Comprehensive authentication fix completed successfully!")
            
            if test_token:
                logger.info("🔑 Test JWT token created and validated")
                return True
            else:
                logger.warning("⚠️ Authentication fix completed but token validation failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Authentication fix failed: {e}")
            return False
        
        finally:
            await self.close()

async def main():
    """Main execution function"""
    fixer = AuthenticationFixer()
    success = await fixer.run_comprehensive_auth_fix()
    
    if success:
        print("✅ Authentication fixes applied successfully!")
        print("🔄 Please restart the application to apply changes.")
        print("🔑 Test JWT token available at /tmp/test_jwt_token.txt")
    else:
        print("❌ Authentication fixes failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())

