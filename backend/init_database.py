from core_foundation_enhanced import EnhancedJyotiFlowDatabase
import asyncio

async def main():
    db = EnhancedJyotiFlowDatabase()
    await db.initialize_tables()
    print("All tables initialized successfully.")

    # Create credit_packages table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS credit_packages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL,
            description TEXT,
            price_usd DECIMAL(10,2) NOT NULL,
            credits_amount INTEGER NOT NULL,
            bonus_credits INTEGER DEFAULT 0,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Insert sample credit packages
    await db.execute("""
        INSERT INTO credit_packages (name, description, price_usd, credits_amount, bonus_credits, enabled) VALUES
        ('தொடக்க தொகுப்பு', 'சிறிய தொடக்கத்திற்கு', 9.99, 50, 5, true),
        ('நடுத்தர தொகுப்பு', 'சராசரி பயனர்களுக்கு', 19.99, 120, 20, true),
        ('பிரீமியம் தொகுப்பு', 'தீவிர பயனர்களுக்கு', 49.99, 350, 50, true),
        ('எலைட் தொகுப்பு', 'முழுமையான அனுபவத்திற்கு', 99.99, 800, 200, true)
        ON CONFLICT DO NOTHING
    """)

if __name__ == "__main__":
    asyncio.run(main())