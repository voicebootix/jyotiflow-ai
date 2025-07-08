#!/usr/bin/env python3
"""
Initialize default credit packages for JyotiFlow
This script creates sample credit packages that can be managed from the admin dashboard
"""

import asyncio
import asyncpg
import os
from datetime import datetime

async def init_credit_packages():
    """Initialize default credit packages in the database"""
    
    # Database connection
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/jyotiflow')
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("🔗 Connected to database")
        
        # Create credit_packages table if it doesn't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS credit_packages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                credits_amount INTEGER NOT NULL,
                price_usd DECIMAL(10,2) NOT NULL,
                bonus_credits INTEGER DEFAULT 0,
                description TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                stripe_product_id VARCHAR(255),
                stripe_price_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Credit packages table ready")
        
        # Default credit packages
        default_packages = [
            {
                'name': 'Starter Pack',
                'credits_amount': 10,
                'price_usd': 9.99,
                'bonus_credits': 2,
                'description': 'Perfect for beginners - try our spiritual guidance services'
            },
            {
                'name': 'Spiritual Seeker',
                'credits_amount': 25,
                'price_usd': 19.99,
                'bonus_credits': 5,
                'description': 'Great value for regular users - most popular choice'
            },
            {
                'name': 'Divine Wisdom',
                'credits_amount': 50,
                'price_usd': 34.99,
                'bonus_credits': 15,
                'description': 'Best value with maximum bonus credits for serious seekers'
            },
            {
                'name': 'Enlightened Master',
                'credits_amount': 100,
                'price_usd': 59.99,
                'bonus_credits': 30,
                'description': 'Ultimate spiritual journey package for dedicated practitioners'
            }
        ]
        
        # Insert default packages
        for package in default_packages:
            # Check if package already exists
            existing = await conn.fetchval(
                "SELECT 1 FROM credit_packages WHERE name = $1",
                package['name']
            )
            
            if not existing:
                await conn.execute("""
                    INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, description, enabled, created_at)
                    VALUES ($1, $2, $3, $4, $5, TRUE, NOW())
                """, 
                package['name'], 
                package['credits_amount'], 
                package['price_usd'], 
                package['bonus_credits'],
                package['description']
                )
                print(f"✅ Created credit package: {package['name']}")
            else:
                print(f"⏭️  Credit package already exists: {package['name']}")
        
        # Show current packages
        packages = await conn.fetch("SELECT name, credits_amount, price_usd, bonus_credits, enabled FROM credit_packages ORDER BY credits_amount")
        
        print(f"\n🎉 Credit packages initialized successfully!")
        print(f"\n📦 Current packages ({len(packages)}):")
        for pkg in packages:
            status = "✅ Active" if pkg['enabled'] else "❌ Inactive"
            bonus = f" (+{pkg['bonus_credits']} bonus)" if pkg['bonus_credits'] > 0 else ""
            print(f"   • {pkg['name']}: {pkg['credits_amount']} credits{bonus} - ${pkg['price_usd']} - {status}")
        
        await conn.close()
        print(f"\n✨ Credit packages are now ready for admin dashboard management!")
        
    except Exception as e:
        print(f"❌ Error initializing credit packages: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_credit_packages()) 