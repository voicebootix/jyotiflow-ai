#!/usr/bin/env python3
"""
JyotiFlow Dynamic Pricing Initialization Script
Initializes the database with sample service types and pricing configuration
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

async def init_dynamic_pricing():
    """Initialize dynamic pricing system with sample data"""
    
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("🕉️ Initializing JyotiFlow Dynamic Pricing System...")
        
        # Initialize Service Types
        print("📋 Creating service types...")
        
        service_types = [
            {
                'name': 'text_guidance',
                'display_name': 'Text Guidance',
                'description': 'Instant spiritual guidance through text responses',
                'credits_required': 1,
                'duration_minutes': 1,
                'price_usd': 9.00,
                'service_category': 'guidance',
                'avatar_video_enabled': False,
                'live_chat_enabled': False,
                'icon': '📝',
                'color_gradient': 'from-blue-500 to-cyan-600'
            },
            {
                'name': 'audio_guidance',
                'display_name': 'Audio Guidance',
                'description': '3-minute audio spiritual guidance with voice synthesis',
                'credits_required': 2,
                'duration_minutes': 3,
                'price_usd': 19.00,
                'service_category': 'guidance',
                'avatar_video_enabled': False,
                'live_chat_enabled': False,
                'icon': '🎵',
                'color_gradient': 'from-green-500 to-emerald-600'
            },
            {
                'name': 'interactive_video',
                'display_name': 'Interactive Video',
                'description': '5-minute interactive video session with AI Swami Jyotirananthan',
                'credits_required': 6,
                'duration_minutes': 5,
                'price_usd': 39.00,
                'service_category': 'guidance',
                'avatar_video_enabled': True,
                'live_chat_enabled': False,
                'icon': '🎥',
                'color_gradient': 'from-purple-500 to-indigo-600'
            },
            {
                'name': 'full_horoscope',
                'display_name': 'Full Horoscope',
                'description': '30-minute comprehensive Vedic astrology reading with detailed analysis',
                'credits_required': 18,
                'duration_minutes': 30,
                'price_usd': 149.00,
                'service_category': 'astrology',
                'avatar_video_enabled': True,
                'live_chat_enabled': True,
                'icon': '⭐',
                'color_gradient': 'from-yellow-500 to-orange-600'
            }
        ]
        
        for service in service_types:
            # Check if service already exists
            existing = await conn.fetchval(
                "SELECT 1 FROM service_types WHERE name = $1",
                service['name']
            )
            
            if not existing:
                await conn.execute("""
                    INSERT INTO service_types (name, display_name, description, credits_required, 
                                             duration_minutes, price_usd, service_category, 
                                             avatar_video_enabled, live_chat_enabled, icon, 
                                             color_gradient, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                """, service['name'], service['display_name'], service['description'],
                     service['credits_required'], service['duration_minutes'], service['price_usd'],
                     service['service_category'], service['avatar_video_enabled'],
                     service['live_chat_enabled'], service['icon'], service['color_gradient'])
                print(f"✅ Created service: {service['display_name']}")
            else:
                print(f"⏭️  Service already exists: {service['display_name']}")
        
        # Initialize Pricing Configuration
        print("💰 Creating pricing configuration...")
        
        pricing_config = [
            {
                'config_key': 'min_profit_margin_percent',
                'config_value': '250',
                'config_type': 'number',
                'description': 'Minimum profit margin percentage (250% = 2.5x markup)'
            },
            {
                'config_key': 'video_cost_per_minute',
                'config_value': '0.70',
                'config_type': 'number',
                'description': 'Our cost per minute for video generation (Agora + AI + Avatar)'
            },
            {
                'config_key': 'max_session_duration_minutes',
                'config_value': '30',
                'config_type': 'number',
                'description': 'Maximum allowed session duration in minutes'
            },
            {
                'config_key': 'min_session_duration_minutes',
                'config_value': '1',
                'config_type': 'number',
                'description': 'Minimum allowed session duration in minutes'
            },
            {
                'config_key': 'donation_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable donation and offering system during sessions'
            },
            {
                'config_key': 'live_chat_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable live chat features for premium services'
            },
            {
                'config_key': 'avatar_video_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable AI avatar video generation'
            },
            {
                'config_key': 'revenue_streams',
                'config_value': '{"credits": 80, "donations": 15, "subscriptions": 5}',
                'config_type': 'json',
                'description': 'Revenue stream percentages (credits, donations, subscriptions)'
            },
            {
                'config_key': 'cost_protection_enabled',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable cost protection to ensure minimum profit margins'
            },
            {
                'config_key': 'tamil_cultural_integration',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'Enable Tamil/Vedic cultural elements in services'
            }
        ]
        
        for config in pricing_config:
            # Check if config already exists
            existing = await conn.fetchval(
                "SELECT 1 FROM pricing_config WHERE config_key = $1",
                config['config_key']
            )
            
            if not existing:
                await conn.execute("""
                    INSERT INTO pricing_config (config_key, config_value, config_type, description, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                """, config['config_key'], config['config_value'], config['config_type'], config['description'])
                print(f"✅ Created config: {config['config_key']}")
            else:
                print(f"⏭️  Config already exists: {config['config_key']}")
        
        # Initialize Donation Options
        print("🪔 Creating donation options...")
        
        donation_options = [
            {
                'name': 'Digital Flowers',
                'tamil_name': 'மலர் அர்ப்பணிப்பு',
                'description': 'Offer digital flowers to the divine',
                'price_usd': 1.00,
                'icon': '🌸',
                'category': 'offering'
            },
            {
                'name': 'Lamp Offering',
                'tamil_name': 'தீப ஆராதனை',
                'description': 'Light a virtual lamp for spiritual blessings',
                'price_usd': 3.00,
                'icon': '🪔',
                'category': 'offering'
            },
            {
                'name': 'Prasadam Blessing',
                'tamil_name': 'பிரசாதம்',
                'description': 'Receive divine prasadam blessing',
                'price_usd': 5.00,
                'icon': '🍎',
                'category': 'offering'
            },
            {
                'name': 'Temple Donation',
                'tamil_name': 'கோவில் நன்கொடை',
                'description': 'Support temple maintenance and spiritual activities',
                'price_usd': 10.00,
                'icon': '🕉️',
                'category': 'donation'
            },
            {
                'name': 'Super Chat - Priority',
                'tamil_name': 'முன்னுரிமை செய்தி',
                'description': 'Priority message during live satsang',
                'price_usd': 2.00,
                'icon': '💬',
                'category': 'super_chat'
            },
            {
                'name': 'Super Chat - Featured',
                'tamil_name': 'முன்னிலை செய்தி',
                'description': 'Featured message with special highlighting',
                'price_usd': 5.00,
                'icon': '⭐',
                'category': 'super_chat'
            },
            {
                'name': 'Super Chat - VIP',
                'tamil_name': 'விஐபி செய்தி',
                'description': 'VIP message with maximum visibility',
                'price_usd': 25.00,
                'icon': '👑',
                'category': 'super_chat'
            }
        ]
        
        for donation in donation_options:
            # Check if donation already exists
            existing = await conn.fetchval(
                "SELECT 1 FROM donations WHERE name = $1",
                donation['name']
            )
            
            if not existing:
                await conn.execute("""
                    INSERT INTO donations (name, tamil_name, description, price_usd, icon, category, enabled, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE, NOW())
                """, donation['name'], donation['tamil_name'], donation['description'],
                     donation['price_usd'], donation['icon'], donation['category'])
                print(f"✅ Created donation: {donation['name']}")
            else:
                print(f"⏭️  Donation already exists: {donation['name']}")
        
        # Initialize Credit Packages
        print("💳 Creating credit packages...")
        
        credit_packages = [
            {
                'name': 'Starter Pack',
                'credits_amount': 5,
                'price_usd': 29.00,
                'bonus_credits': 0
            },
            {
                'name': 'Popular Pack',
                'credits_amount': 15,
                'price_usd': 79.00,
                'bonus_credits': 2
            },
            {
                'name': 'Premium Pack',
                'credits_amount': 30,
                'price_usd': 149.00,
                'bonus_credits': 5
            },
            {
                'name': 'Elite Pack',
                'credits_amount': 60,
                'price_usd': 279.00,
                'bonus_credits': 12
            }
        ]
        
        for package in credit_packages:
            # Check if package already exists
            existing = await conn.fetchval(
                "SELECT 1 FROM credit_packages WHERE name = $1",
                package['name']
            )
            
            if not existing:
                await conn.execute("""
                    INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled, created_at)
                    VALUES ($1, $2, $3, $4, TRUE, NOW())
                """, package['name'], package['credits_amount'], package['price_usd'], package['bonus_credits'])
                print(f"✅ Created credit package: {package['name']}")
            else:
                print(f"⏭️  Credit package already exists: {package['name']}")
        
        print("\n🎉 JyotiFlow Dynamic Pricing System initialized successfully!")
        print("\n📊 Summary:")
        print(f"   • {len(service_types)} service types configured")
        print(f"   • {len(pricing_config)} pricing variables set")
        print(f"   • {len(donation_options)} donation options available")
        print(f"   • {len(credit_packages)} credit packages created")
        print("\n🕉️ The platform is now ready for dynamic pricing management!")
        
    except Exception as e:
        print(f"❌ Error initializing dynamic pricing: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_dynamic_pricing()) 