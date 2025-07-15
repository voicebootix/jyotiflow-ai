import asyncpg
import asyncio
import os
import sys

async def create_credit_packages():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is required but not set")
        sys.exit(1)
    conn = await asyncpg.connect(database_url)
    
    try:
        # Create credit packages table if it doesn't exist
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS credit_packages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                credits INTEGER NOT NULL,
                price_usd DECIMAL(10, 2) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default credit packages
        packages = [
            (10, 9.99, "Starter Package", "Perfect for trying our services"),
            (25, 19.99, "Popular Package", "Great value for regular users"),
            (50, 34.99, "Value Package", "Best value for frequent users"),
            (100, 59.99, "Premium Package", "Maximum credits for power users")
        ]
        
        for credits, price, name, description in packages:
            await conn.execute("""
                INSERT INTO credit_packages (name, credits, price_usd, description)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (name) DO UPDATE SET
                    credits = $2,
                    price_usd = $3,
                    description = $4
            """, name, credits, price, description)
        
        print("✅ Credit packages created successfully")
        
    except Exception as e:
        print(f"❌ Error creating credit packages: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_credit_packages()) 