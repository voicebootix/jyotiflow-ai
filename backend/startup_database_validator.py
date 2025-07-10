"""
Startup Database Validator for JyotiFlow
Validates and fixes database issues during application startup
"""

import os
import logging
import asyncpg
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class StartupDatabaseValidator:
    """Validates and fixes database issues during startup"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    async def validate_and_fix(self) -> Dict[str, Any]:
        """Validate database and fix critical issues"""
        results = {
            "validation_passed": False,
            "fixes_applied": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # 1. Validate table structures
            await self._validate_table_structures(conn, results)
            
            # 2. Fix missing columns
            await self._fix_missing_columns(conn, results)
            
            # 3. Validate constraints
            await self._validate_constraints(conn, results)
            
            # 4. Ensure required data exists
            await self._ensure_required_data(conn, results)
            
            await conn.close()
            
            # Mark validation as passed if no critical errors
            results["validation_passed"] = len(results["errors"]) == 0
            
            return results
            
        except Exception as e:
            results["errors"].append(f"Database validation failed: {e}")
            return results
    
    async def _validate_table_structures(self, conn, results):
        """Validate that required tables exist"""
        required_tables = [
            'users', 'sessions', 'service_types', 'user_purchases',
            'avatar_sessions', 'satsang_events', 'live_chat_sessions'
        ]
        
        for table in required_tables:
            try:
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if not exists:
                    results["warnings"].append(f"Table '{table}' does not exist")
                else:
                    logger.debug(f"✅ Table '{table}' exists")
            except Exception as e:
                results["errors"].append(f"Could not validate table '{table}': {e}")
    
    async def _fix_missing_columns(self, conn, results):
        """Fix missing columns in critical tables"""
        fixes = []
        
        try:
            # Fix sessions table
            missing_cols = await self._get_missing_columns(conn, 'sessions', 
                ['duration_minutes', 'session_data', 'user_id'])
            
            for col in missing_cols:
                if col == 'duration_minutes':
                    await conn.execute("ALTER TABLE sessions ADD COLUMN duration_minutes INTEGER DEFAULT 0")
                    fixes.append("Added duration_minutes to sessions table")
                elif col == 'session_data':
                    await conn.execute("ALTER TABLE sessions ADD COLUMN session_data TEXT")
                    fixes.append("Added session_data to sessions table")
                elif col == 'user_id':
                    await conn.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT")
                    fixes.append("Added user_id to sessions table")
            
            # Fix service_types table
            missing_cols = await self._get_missing_columns(conn, 'service_types',
                ['base_credits', 'duration_minutes', 'video_enabled'])
            
            for col in missing_cols:
                if col == 'base_credits':
                    await conn.execute("ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 5")
                    fixes.append("Added base_credits to service_types table")
                elif col == 'duration_minutes':
                    await conn.execute("ALTER TABLE service_types ADD COLUMN duration_minutes INTEGER DEFAULT 15")
                    fixes.append("Added duration_minutes to service_types table")
                elif col == 'video_enabled':
                    await conn.execute("ALTER TABLE service_types ADD COLUMN video_enabled BOOLEAN DEFAULT true")
                    fixes.append("Added video_enabled to service_types table")
            
            results["fixes_applied"].extend(fixes)
            
        except Exception as e:
            results["warnings"].append(f"Could not fix missing columns: {e}")
    
    async def _get_missing_columns(self, conn, table_name: str, required_columns: List[str]) -> List[str]:
        """Get list of missing columns for a table"""
        missing = []
        
        for column in required_columns:
            try:
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = $1 AND column_name = $2
                    )
                """, table_name, column)
                
                if not exists:
                    missing.append(column)
            except Exception:
                # If we can't check, assume it's missing
                missing.append(column)
        
        return missing
    
    async def _validate_constraints(self, conn, results):
        """Validate database constraints"""
        try:
            # Check for foreign key constraint issues
            constraint_check = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.table_constraints 
                WHERE constraint_type = 'FOREIGN KEY' 
                AND table_name = 'service_usage_logs'
            """)
            
            if constraint_check == 0:
                results["warnings"].append("Foreign key constraints may need attention")
            
        except Exception as e:
            results["warnings"].append(f"Constraint validation warning: {e}")
    
    async def _ensure_required_data(self, conn, results):
        """Ensure required default data exists"""
        try:
            # Check if service_types has data
            service_count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
            
            if service_count == 0:
                # Insert essential service types
                essential_services = [
                    ('comprehensive_life_reading_30min', 'Comprehensive 30-minute life reading', 15, 30, True),
                    ('horoscope_reading_quick', 'Quick horoscope reading', 8, 10, True),
                    ('satsang_community', 'Community satsang session', 5, 60, True)
                ]
                
                for service in essential_services:
                    try:
                        await conn.execute("""
                            INSERT INTO service_types (name, description, base_credits, duration_minutes, video_enabled)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (name) DO NOTHING
                        """, *service)
                        
                        results["fixes_applied"].append(f"Added service type: {service[0]}")
                    except Exception as e:
                        results["warnings"].append(f"Could not add service {service[0]}: {e}")
            
        except Exception as e:
            results["warnings"].append(f"Required data validation warning: {e}")

async def validate_startup_database(database_url: str) -> Dict[str, Any]:
    """Main function to validate database during startup"""
    validator = StartupDatabaseValidator(database_url)
    return await validator.validate_and_fix()

# Integration function for main application
async def run_startup_database_validation():
    """Run database validation as part of application startup"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set, skipping database validation")
        return {"validation_passed": False, "errors": ["DATABASE_URL not configured"]}
    
    try:
        results = await validate_startup_database(database_url)
        
        if results["validation_passed"]:
            logger.info("✅ Database validation passed")
            if results["fixes_applied"]:
                logger.info(f"🔧 Applied {len(results['fixes_applied'])} fixes")
            if results["warnings"]:
                logger.warning(f"⚠️ {len(results['warnings'])} warnings detected")
        else:
            logger.error("❌ Database validation failed")
            for error in results["errors"]:
                logger.error(f"  - {error}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Database validation exception: {e}")
        return {"validation_passed": False, "errors": [str(e)]}

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_startup_database_validation())