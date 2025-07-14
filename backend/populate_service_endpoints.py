#!/usr/bin/env python3
"""
Populate Service Types with Prokerala Endpoint Configurations
This script adds endpoint configurations to existing services
"""

import os
import asyncio
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service endpoint configurations
SERVICE_ENDPOINT_CONFIGS = {
    'horoscope_reading_quick': {
        'prokerala_endpoints': ['/astrology/birth-details', '/horoscope/daily'],
        'estimated_api_calls': 2,
        'cache_effectiveness': 85.0
    },
    'comprehensive_life_reading_30min': {
        'prokerala_endpoints': [
            '/astrology/birth-details', 
            '/astrology/kundli/advanced', 
            '/astrology/planet-position',
            '/astrology/dasha-periods',
            '/astrology/yoga',
            '/numerology/life-path-number'
        ],
        'estimated_api_calls': 6,
        'cache_effectiveness': 70.0
    },
    'love_compatibility_reading': {
        'prokerala_endpoints': [
            '/astrology/birth-details', 
            '/astrology/nakshatra-porutham', 
            '/astrology/kundli-matching',
            '/numerology/life-path-number'
        ],
        'estimated_api_calls': 4,
        'cache_effectiveness': 80.0
    },
    'career_guidance_session': {
        'prokerala_endpoints': [
            '/astrology/birth-details', 
            '/astrology/planet-position', 
            '/astrology/dasha-periods',
            '/astrology/auspicious-period'
        ],
        'estimated_api_calls': 4,
        'cache_effectiveness': 75.0
    },
    'spiritual_guidance_session': {
        'prokerala_endpoints': ['/astrology/birth-details', '/horoscope/daily'],
        'estimated_api_calls': 2,
        'cache_effectiveness': 90.0
    },
    'birth_chart_analysis': {
        'prokerala_endpoints': [
            '/astrology/birth-details',
            '/astrology/birth-chart',
            '/astrology/planet-position',
            '/astrology/chart'
        ],
        'estimated_api_calls': 4,
        'cache_effectiveness': 60.0
    }
}

async def populate_service_endpoints():
    """Populate existing services with Prokerala endpoint configurations"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("🚀 Starting service endpoint configuration...")
        
        # First, check if migration fields exist
        try:
            columns = await conn.fetch("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'service_types' 
                AND column_name IN ('prokerala_endpoints', 'estimated_api_calls', 'cache_effectiveness')
            """)
            
            if len(columns) < 3:
                logger.warning("⚠️ Migration fields not found. Run migration first!")
                logger.info("Missing fields - please run: python3 backend/run_prokerala_migration.py")
                return False
            
        except Exception as e:
            logger.error(f"❌ Could not check migration fields: {e}")
            return False
        
        # Get existing services
        services = await conn.fetch("SELECT id, name FROM service_types")
        logger.info(f"📋 Found {len(services)} existing services")
        
        updated_count = 0
        
        for service in services:
            service_name = service['name']
            service_id = service['id']
            
            # Check if we have configuration for this service
            config = None
            for config_name, config_data in SERVICE_ENDPOINT_CONFIGS.items():
                if config_name in service_name or service_name in config_name:
                    config = config_data
                    break
            
            # If no specific config, use a default based on service name
            if not config:
                if 'quick' in service_name.lower() or 'basic' in service_name.lower():
                    config = {
                        'prokerala_endpoints': ['/astrology/birth-details', '/horoscope/daily'],
                        'estimated_api_calls': 2,
                        'cache_effectiveness': 85.0
                    }
                elif 'comprehensive' in service_name.lower() or 'complete' in service_name.lower():
                    config = {
                        'prokerala_endpoints': [
                            '/astrology/birth-details', 
                            '/astrology/planet-position',
                            '/astrology/dasha-periods'
                        ],
                        'estimated_api_calls': 3,
                        'cache_effectiveness': 70.0
                    }
                else:
                    config = {
                        'prokerala_endpoints': ['/astrology/birth-details'],
                        'estimated_api_calls': 1,
                        'cache_effectiveness': 80.0
                    }
            
            try:
                # Update service with endpoint configuration
                await conn.execute("""
                    UPDATE service_types 
                    SET prokerala_endpoints = $1,
                        estimated_api_calls = $2,
                        cache_effectiveness = $3
                    WHERE id = $4
                """, 
                config['prokerala_endpoints'],
                config['estimated_api_calls'], 
                config['cache_effectiveness'],
                service_id)
                
                logger.info(f"✅ Updated {service_name}: {len(config['prokerala_endpoints'])} endpoints, {config['estimated_api_calls']} calls, {config['cache_effectiveness']}% cache")
                updated_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to update {service_name}: {e}")
        
        await conn.close()
        
        logger.info(f"🎉 Service endpoint configuration completed!")
        logger.info(f"📊 Updated {updated_count}/{len(services)} services")
        
        return updated_count > 0
        
    except Exception as e:
        logger.error(f"❌ Service configuration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(populate_service_endpoints())
    exit(0 if success else 1)