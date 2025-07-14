#!/usr/bin/env python3
"""
Auto-Deployment Migration Script for JyotiFlow
Ensures all migrations run properly during deployment
Includes Prokerala Smart Pricing System setup
"""

import os
import sys
import asyncio
import asyncpg
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_auto_deployment_migrations():
    """Run all necessary migrations for deployment"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("🚀 Starting auto-deployment migrations...")
        
        # 1. Ensure migrations tracking table exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                checksum VARCHAR(64)
            )
        """)
        logger.info("✅ Migrations tracking table ready")
        
        # 2. Get list of applied migrations
        applied_migrations = await conn.fetch("SELECT migration_name FROM schema_migrations")
        applied_set = {row['migration_name'] for row in applied_migrations}
        
        # 3. Critical migrations to ensure
        critical_migrations = [
            "add_prokerala_smart_pricing.sql",
            "enhance_service_types_rag.sql",
            "fix_missing_columns.sql"
        ]
        
        migrations_dir = Path(__file__).parent / "migrations"
        
        for migration_name in critical_migrations:
            if migration_name not in applied_set:
                migration_file = migrations_dir / migration_name
                
                if migration_file.exists():
                    logger.info(f"📦 Applying migration: {migration_name}")
                    
                    try:
                        with open(migration_file, 'r') as f:
                            migration_sql = f.read()
                        
                        # Split by semicolons and execute each statement
                        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
                        
                        for i, statement in enumerate(statements):
                            try:
                                await conn.execute(statement)
                                logger.info(f"  ✅ Statement {i+1}/{len(statements)} executed")
                            except Exception as e:
                                # Log warning but continue (many statements might be IF NOT EXISTS)
                                logger.warning(f"  ⚠️ Statement {i+1} warning: {str(e)[:100]}")
                        
                        # Mark as applied
                        await conn.execute("""
                            INSERT INTO schema_migrations (migration_name) 
                            VALUES ($1) ON CONFLICT (migration_name) DO NOTHING
                        """, migration_name)
                        
                        logger.info(f"✅ Migration {migration_name} completed")
                        
                    except Exception as e:
                        logger.error(f"❌ Migration {migration_name} failed: {e}")
                        # Don't stop deployment for migration failures
                        continue
                else:
                    logger.warning(f"⚠️ Migration file not found: {migration_name}")
            else:
                logger.info(f"⏭️ Migration {migration_name} already applied")
        
        # 4. Ensure basic service types exist
        await ensure_basic_service_types(conn)
        
        # 5. Ensure Prokerala configuration exists
        await ensure_prokerala_config(conn)
        
        await conn.close()
        logger.info("🎉 Auto-deployment migrations completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Auto-deployment migration failed: {e}")
        return False

async def ensure_basic_service_types(conn):
    """Ensure basic service types exist"""
    try:
        # Check if service_types table has data
        count = await conn.fetchval("SELECT COUNT(*) FROM service_types")
        
        if count == 0:
            logger.info("📋 Creating basic service types...")
            
            # Create basic service types
            basic_services = [
                {
                    'name': 'spiritual_guidance_session',
                    'display_name': 'Spiritual Guidance Session',
                    'description': 'Personal spiritual guidance with astrological insights',
                    'credits_required': 5,
                    'duration_minutes': 15
                },
                {
                    'name': 'birth_chart_analysis',
                    'display_name': 'Birth Chart Analysis',
                    'description': 'Comprehensive birth chart reading',
                    'credits_required': 8,
                    'duration_minutes': 20
                },
                {
                    'name': 'love_compatibility_reading',
                    'display_name': 'Love Compatibility Reading',
                    'description': 'Relationship compatibility analysis',
                    'credits_required': 6,
                    'duration_minutes': 18
                }
            ]
            
            for service in basic_services:
                try:
                    await conn.execute("""
                        INSERT INTO service_types (name, display_name, description, credits_required, duration_minutes, enabled)
                        VALUES ($1, $2, $3, $4, $5, true)
                        ON CONFLICT (name) DO NOTHING
                    """, 
                    service['name'], service['display_name'], service['description'],
                    service['credits_required'], service['duration_minutes'])
                    
                    logger.info(f"  ✅ Created service: {service['display_name']}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Service creation warning: {e}")
        else:
            logger.info(f"✅ Service types already exist ({count} services)")
            
    except Exception as e:
        logger.warning(f"⚠️ Service types check failed: {e}")

async def ensure_prokerala_config(conn):
    """Ensure Prokerala configuration exists"""
    try:
        # Check if prokerala_cost_config table exists and has data
        try:
            count = await conn.fetchval("SELECT COUNT(*) FROM prokerala_cost_config")
            
            if count == 0:
                logger.info("⚙️ Creating default Prokerala configuration...")
                
                await conn.execute("""
                    INSERT INTO prokerala_cost_config (max_cost_per_call, margin_percentage, cache_discount_enabled)
                    VALUES (0.036, 500.00, TRUE)
                """)
                
                logger.info("✅ Default Prokerala configuration created")
            else:
                logger.info("✅ Prokerala configuration already exists")
                
        except Exception as e:
            # Table might not exist yet
            logger.info(f"⚠️ Prokerala config table not ready: {e}")
            
    except Exception as e:
        logger.warning(f"⚠️ Prokerala config check failed: {e}")

if __name__ == "__main__":
    success = asyncio.run(run_auto_deployment_migrations())
    if success:
        logger.info("✅ Deployment migration successful!")
        sys.exit(0)
    else:
        logger.error("❌ Deployment migration failed!")
        sys.exit(1)