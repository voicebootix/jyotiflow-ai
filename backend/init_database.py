from core_foundation_enhanced import EnhancedJyotiFlowDatabase
import asyncio

async def main():
    db = EnhancedJyotiFlowDatabase()
    await db.initialize_tables()
    print("All tables initialized successfully.")

if __name__ == "__main__":
    asyncio.run(main())