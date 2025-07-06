#!/usr/bin/env python3
"""
AI Scheduler for Daily Analysis and Recommendations
தமிழ் - தினசரி பகுப்பாய்வு மற்றும் பரிந்துரைகளுக்கான AI அட்டவணைப்படுத்தி
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from enhanced_business_logic import MonetizationOptimizer
from db import EnhancedJyotiFlowDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIScheduler:
    """AI Scheduler for automated daily analysis and recommendations"""
    
    def __init__(self):
        self.db = None
        self.optimizer = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize database and optimizer connections"""
        try:
            self.db = EnhancedJyotiFlowDatabase()
            await self.db.connect()
            
            self.optimizer = MonetizationOptimizer()
            self.optimizer.db = self.db
            
            logger.info("✅ AI Scheduler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Scheduler: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup database connections"""
        if self.db:
            await self.db.close()
            logger.info("🔌 Database connections closed")
    
    async def run_daily_analysis(self):
        """Run daily AI analysis and store top 3 recommendations"""
        try:
            logger.info("🕉️ Starting daily AI analysis...")
            logger.info("தமிழ் - தினசரி AI பகுப்பாய்வு தொடங்குகிறது...")
            
            # Generate comprehensive recommendations
            recommendations = await self.optimizer.generate_pricing_recommendations("daily")
            
            if not recommendations:
                logger.warning("⚠️ No recommendations generated")
                return False
            
            # Get pricing-specific recommendations
            pricing_recommendations = recommendations.get('pricing_recommendations', [])
            
            if not pricing_recommendations:
                logger.warning("⚠️ No pricing recommendations found")
                return False
            
            # Sort by expected impact and get top 3
            top_recommendations = sorted(
                pricing_recommendations,
                key=lambda x: x.get('expected_revenue_impact', 0),
                reverse=True
            )[:3]
            
            logger.info(f"📊 Generated {len(pricing_recommendations)} recommendations, selecting top 3")
            
            # Store top 3 recommendations with daily analysis flag
            for i, rec in enumerate(top_recommendations, 1):
                try:
                    # Add daily analysis metadata
                    rec['metadata'] = rec.get('metadata', {})
                    rec['metadata']['daily_analysis'] = True
                    rec['metadata']['analysis_date'] = datetime.now().isoformat()
                    rec['metadata']['rank'] = i
                    rec['metadata']['total_recommendations'] = len(pricing_recommendations)
                    
                    # Store in database
                    await self.optimizer._store_ai_pricing_recommendations([rec])
                    
                    logger.info(f"✅ Stored top recommendation {i}: {rec.get('service_name', 'Unknown')} "
                              f"(Impact: ${rec.get('expected_revenue_impact', 0):,.2f})")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to store recommendation {i}: {e}")
            
            # Store analysis summary
            await self._store_daily_analysis_summary(recommendations, top_recommendations)
            
            logger.info("🎉 Daily AI analysis completed successfully!")
            logger.info("🎉 தினசரி AI பகுப்பாய்வு வெற்றிகரமாக முடிந்தது!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Daily analysis failed: {e}")
            return False
    
    async def _store_daily_analysis_summary(self, full_recommendations, top_recommendations):
        """Store daily analysis summary in database"""
        try:
            summary = {
                "analysis_date": datetime.now().isoformat(),
                "total_recommendations": len(full_recommendations.get('pricing_recommendations', [])),
                "top_recommendations_count": len(top_recommendations),
                "total_expected_impact": sum(rec.get('expected_revenue_impact', 0) for rec in top_recommendations),
                "analysis_type": "daily_automated",
                "recommendation_types": list(set(rec.get('type', 'unknown') for rec in top_recommendations)),
                "priority_distribution": self._get_priority_distribution(top_recommendations),
                "confidence_average": sum(rec.get('confidence_level', 0) for rec in top_recommendations) / max(len(top_recommendations), 1)
            }
            
            # Store in ai_insights_cache
            await self.optimizer._cache_ai_insights(
                "daily_analysis_summary", 
                summary, 
                expires_hours=168  # 7 days
            )
            
            logger.info(f"📋 Stored daily analysis summary: {summary['total_recommendations']} total, "
                       f"{summary['top_recommendations_count']} top, "
                       f"${summary['total_expected_impact']:,.2f} impact")
            
        except Exception as e:
            logger.error(f"❌ Failed to store daily analysis summary: {e}")
    
    def _get_priority_distribution(self, recommendations):
        """Get priority distribution of recommendations"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for rec in recommendations:
            priority = rec.get('priority_level', 'medium')
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution
    
    async def run_scheduler(self):
        """Main scheduler loop - runs daily at 2 AM IST"""
        if not await self.initialize():
            return
        
        self.is_running = True
        logger.info("🕐 AI Scheduler started - will run daily at 2 AM IST")
        logger.info("தமிழ் - AI அட்டவணைப்படுத்தி தொடங்கியது - தினசரி காலை 2 மணிக்கு இயங்கும்")
        
        try:
            while self.is_running:
                now = datetime.now()
                
                # Check if it's 2 AM IST (or 8:30 PM UTC)
                target_hour = 2  # 2 AM IST
                
                if now.hour == target_hour and now.minute < 5:  # Run within first 5 minutes of 2 AM
                    logger.info("🕐 2 AM IST reached - running daily analysis...")
                    await self.run_daily_analysis()
                    
                    # Sleep for 6 minutes to avoid running multiple times
                    await asyncio.sleep(360)  # 6 minutes
                else:
                    # Sleep for 1 minute and check again
                    await asyncio.sleep(60)
                    
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
        finally:
            self.is_running = False
            await self.cleanup()

async def run_manual_analysis():
    """Run manual analysis for testing"""
    scheduler = AIScheduler()
    if await scheduler.initialize():
        try:
            await scheduler.run_daily_analysis()
        finally:
            await scheduler.cleanup()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Scheduler for Daily Analysis')
    parser.add_argument('--manual', action='store_true', help='Run manual analysis')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon scheduler')
    
    args = parser.parse_args()
    
    if args.manual:
        asyncio.run(run_manual_analysis())
    elif args.daemon:
        asyncio.run(AIScheduler().run_scheduler())
    else:
        print("Usage: python ai_scheduler.py --manual (for testing) or --daemon (for production)")
        print("பயன்பாடு: python ai_scheduler.py --manual (சோதனைக்கு) அல்லது --daemon (உற்பத்திக்கு)") 