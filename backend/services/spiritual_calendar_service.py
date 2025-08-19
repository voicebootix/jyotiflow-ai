
import logging
import asyncio
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List
import calendar

logger = logging.getLogger(__name__)

class SpiritualCalendarService:
    """
    Enhanced Spiritual Calendar Service with RAG knowledge integration.
    Generates dynamic spiritual themes using AI and knowledge base.
    """
    def __init__(self):
        # Fallback themes for when RAG is unavailable
        self._fallback_themes = [
            {"theme": "Inner Peace", "description": "Finding tranquility within amidst the chaos of the world."},
            {"theme": "Cosmic Connection", "description": "Understanding our place in the universe and connection to all things."},
            {"theme": "Gratitude", "description": "Cultivating thankfulness for the blessings in our lives, big and small."},
            {"theme": "Self-Reflection", "description": "Taking time to look inward, understand our motivations, and grow."},
            {"theme": "Compassion", "description": "Extending kindness and empathy to ourselves and all other beings."},
            {"theme": "Letting Go", "description": "Releasing attachments to past events and future expectations to live in the present."},
            {"theme": "Mindfulness", "description": "Paying full attention to the present moment without judgment."}
        ]
        logger.info("Enhanced Spiritual Calendar Service initialized with RAG integration.")

    async def get_daily_spiritual_theme(self) -> Dict[str, Any]:
        """
        Generates daily spiritual theme using RAG knowledge engine.
        Falls back to hardcoded themes if RAG is unavailable.
        """
        try:
            # Try RAG-powered dynamic generation first
            return await self._generate_rag_powered_theme()
        except Exception as e:
            logger.warning(f"RAG theme generation failed: {e}, using fallback")
            return await self._get_fallback_theme()

    async def _generate_rag_powered_theme(self) -> Dict[str, Any]:
        """Generate spiritual theme using RAG knowledge engine"""
        try:
            # Check if RAG system is available first
            try:
                from ..enhanced_rag_knowledge_engine import get_rag_enhanced_guidance, rag_engine
                if rag_engine is None:
                    raise Exception("RAG engine not initialized")
            except ImportError as ie:
                raise Exception("RAG system import failed") from ie
            
            # Get current date context
            today = datetime.now()
            day_name = calendar.day_name[today.weekday()]
            month_name = calendar.month_name[today.month]
            season = self._get_season(today.month)
            
            # Create contextual query for RAG
            spiritual_query = f"""
            Today is {day_name}, {today.day} {month_name} {today.year}, during {season} season.
            Please provide a daily spiritual theme for today that includes:
            1. A meaningful spiritual theme name (2-3 words)
            2. A beautiful description (1-2 sentences) that explains the essence of this theme
            
            The theme should be:
            - Appropriate for the current day and season
            - Inspiring and uplifting for spiritual seekers
            - Rooted in timeless wisdom traditions
            - Practical for daily contemplation
            
            Please provide the response in this format:
            Theme: [Theme Name]
            Description: [Beautiful description]
            """
            
            # Query RAG system with timeout
            try:
                rag_response = await asyncio.wait_for(
                    get_rag_enhanced_guidance(
                        user_query=spiritual_query,
                        birth_details=None,
                        service_type="daily_spiritual_guidance"
                    ),
                    timeout=10.0  # 10 second timeout
                )
            except asyncio.TimeoutError:
                raise Exception("RAG system timeout")
            
            if rag_response and rag_response.get("enhanced_guidance"):
                parsed_theme = self._parse_rag_theme_response(rag_response["enhanced_guidance"])
                logger.info(f"RAG generated spiritual theme: {parsed_theme['theme']}")
                return parsed_theme
            else:
                raise Exception("RAG response was empty or invalid")
                
        except Exception as e:
            logger.error(f"RAG theme generation error: {e}")
            raise e

    def _parse_rag_theme_response(self, rag_text: str) -> Dict[str, Any]:
        """Parse RAG response to extract theme and description"""
        try:
            lines = rag_text.strip().split('\n')
            theme = "Divine Guidance"
            description = "Following the path of wisdom and inner light."
            
            for line in lines:
                line = line.strip()
                if line.startswith("Theme:"):
                    theme = line.replace("Theme:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif ":" in line and len(line.split(":")[0]) < 20:  # Handle variations
                    parts = line.split(":", 1)
                    if "theme" in parts[0].lower():
                        theme = parts[1].strip()
                    elif "description" in parts[0].lower():
                        description = parts[1].strip()
            
            # Clean up the theme and description
            theme = theme.replace('"', '').replace("'", "").strip()
            description = description.replace('"', '').replace("'", "").strip()
            
            return {"theme": theme, "description": description}
            
        except Exception as e:
            logger.error(f"Failed to parse RAG theme response: {e}")
            # Extract first meaningful sentence as theme if parsing fails
            sentences = rag_text.split('.')
            if len(sentences) > 0:
                theme_text = sentences[0].strip()[:50]  # First 50 chars as theme
                desc_text = rag_text[:200] + "..." if len(rag_text) > 200 else rag_text
                return {"theme": theme_text, "description": desc_text}
            else:
                return {"theme": "Spiritual Wisdom", "description": rag_text[:200]}

    def _get_season(self, month: int) -> str:
        """Get season based on month"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    async def _get_fallback_theme(self) -> Dict[str, Any]:
        """Returns a deterministic fallback theme if RAG fails"""
        try:
            day_of_year = datetime.now().timetuple().tm_yday
            theme_index = day_of_year % len(self._fallback_themes)
            theme = self._fallback_themes[theme_index]
            logger.info(f"Using fallback spiritual theme: {theme['theme']}")
            return theme
        except Exception as e:
            logger.error(f"Even fallback theme failed: {e}")
            return {"theme": "Universal Love", "description": "Connecting with the boundless love that permeates the universe."}

    async def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieves a list of spiritual events for the upcoming number of days using RAG.
        Falls back to deterministic themes if RAG is unavailable.
        """
        events = []
        today = datetime.now()
        
        for i in range(days):
            current_day = today + timedelta(days=i)
            try:
                # Try to generate RAG theme for each day
                theme = await self._generate_rag_theme_for_date(current_day)
            except Exception as e:
                logger.warning(f"RAG failed for {current_day.strftime('%Y-%m-%d')}: {e}")
                # Fallback to deterministic theme
                day_of_year = current_day.timetuple().tm_yday
                theme_index = day_of_year % len(self._fallback_themes)
                theme = self._fallback_themes[theme_index]
            
            events.append({
                "date": current_day.strftime("%Y-%m-%d"),
                "theme": theme["theme"],
                "description": theme["description"]
            })
            
        logger.info(f"Retrieved {len(events)} upcoming spiritual events (RAG + fallback).")
        return events

    async def _generate_rag_theme_for_date(self, target_date: datetime) -> Dict[str, Any]:
        """Generate RAG theme for a specific date"""
        try:
            # Check if RAG system is available first
            try:
                from ..enhanced_rag_knowledge_engine import get_rag_enhanced_guidance, rag_engine
                if rag_engine is None:
                    raise Exception("RAG engine not initialized")
            except ImportError as ie:
                raise Exception("RAG system import failed") from ie
            
            day_name = calendar.day_name[target_date.weekday()]
            month_name = calendar.month_name[target_date.month]
            season = self._get_season(target_date.month)
            
            # Create date-specific query
            spiritual_query = f"""
            For {day_name}, {target_date.day} {month_name} {target_date.year}, during {season} season:
            Please provide a unique daily spiritual theme that includes:
            1. A meaningful spiritual theme name (2-3 words)
            2. An inspiring description (1-2 sentences)
            
            Make it specific to this day and season, rooted in wisdom traditions.
            Format: Theme: [Name] | Description: [Description]
            """
            
            # Query RAG system with timeout
            try:
                rag_response = await asyncio.wait_for(
                    get_rag_enhanced_guidance(
                        user_query=spiritual_query,
                        birth_details=None,
                        service_type="daily_spiritual_guidance"
                    ),
                    timeout=8.0  # 8 second timeout for individual dates
                )
            except asyncio.TimeoutError:
                raise Exception(f"RAG system timeout for {target_date}")
            
            if rag_response and rag_response.get("enhanced_guidance"):
                return self._parse_rag_theme_response(rag_response["enhanced_guidance"])
            else:
                raise Exception("No RAG response")
                
        except Exception as e:
            logger.error(f"RAG theme generation error for {target_date}: {e}")
            raise e

# --- FastAPI Dependency Injection ---
_calendar_service_instance = None

def get_spiritual_calendar_service() -> SpiritualCalendarService:
    """
    Provides a singleton instance of the SpiritualCalendarService.
    """
    global _calendar_service_instance
    if _calendar_service_instance is None:
        _calendar_service_instance = SpiritualCalendarService()
    return _calendar_service_instance
