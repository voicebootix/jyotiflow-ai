import asyncio
import aiosqlite
import os

async def create_credit_packages():
    # Use SQLite database
    db_path = "jyotiflow.db"
    conn = await aiosqlite.connect(db_path)
    
    try:
        # Create credit_packages table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS credit_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                credits INTEGER,
                price_usd REAL,
                bonus_credits INTEGER DEFAULT 0,
                description TEXT,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create credit_transactions table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                package_id INTEGER,
                credits_purchased INTEGER,
                bonus_credits INTEGER,
                total_credits INTEGER,
                amount_usd REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample credit packages with bonus credits
        packages = [
            ('Starter Pack', 10, 9.99, 2, 'Perfect for beginners'),
            ('Spiritual Seeker', 25, 19.99, 5, 'Great value for regular users'),
            ('Divine Wisdom', 50, 34.99, 15, 'Best value with maximum bonus'),
            ('Enlightened Master', 100, 59.99, 30, 'Ultimate spiritual journey package')
        ]
        
        for name, credits, price, bonus, description in packages:
            await conn.execute('''
                INSERT OR IGNORE INTO credit_packages (name, credits, price_usd, bonus_credits, description) 
                VALUES (?, ?, ?, ?, ?)
            ''', (name, credits, price, bonus, description))
        
        await conn.commit()
        
        print('✅ Credit packages created successfully with bonus credits!')
        print('📦 Available packages:')
        for name, credits, price, bonus, description in packages:
            total = credits + bonus
            print(f'   • {name}: {credits} credits + {bonus} bonus = {total} total (${price})')
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_credit_packages()) 