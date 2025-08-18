
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SpiritualCalendarService:
    """
    Provides daily spiritual themes based on a simulated calendar.
    In a real application, this would connect to a database or an external API.
    """
    def __init__(self):
        self._themes = [
            {"theme": "Inner Peace", "description": "Finding tranquility within amidst the chaos of the world."},
            {"theme": "Cosmic Connection", "description": "Understanding our place in the universe and connection to all things."},
            {"theme": "Gratitude", "description": "Cultivating thankfulness for the blessings in our lives, big and small."},
            {"theme": "Self-Reflection", "description": "Taking time to look inward, understand our motivations, and grow."},
            {"theme": "Compassion", "description": "Extending kindness and empathy to ourselves and all other beings."},
            {"theme": "Letting Go", "description": "Releasing attachments to past events and future expectations to live in the present."},
            {"theme": "Mindfulness", "description": "Paying full attention to the present moment without judgment."}
        ]
        logger.info("Spiritual Calendar Service initialized.")

    async def get_daily_spiritual_theme(self) -> Dict[str, Any]:
        """
        Retrieves the spiritual theme for the current day.
        This implementation uses the day of the week to pick a theme deterministically.
        """
        try:
            day_of_year = datetime.now().timetuple().tm_yday
            # Simple deterministic way to get a theme for the day
            theme_index = day_of_year % len(self._themes)
            theme = self._themes[theme_index]
            logger.info(f"Today's spiritual theme is: {theme['theme']}")
            return theme
        except Exception as e:
            logger.error(f"Failed to retrieve daily spiritual theme: {e}", exc_info=True)
            return self._get_fallback_theme()

    def _get_fallback_theme(self) -> Dict[str, Any]:
        """Returns a default theme if the main logic fails."""
        logger.warning("Using fallback spiritual theme.")
        return {"theme": "Universal Love", "description": "Connecting with the boundless love that permeates the universe."}

    async def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieves a list of spiritual events for the upcoming number of days.
        """
        events = []
        today = datetime.now()
        for i in range(days):
            current_day = today + timedelta(days=i)
            day_of_year = current_day.timetuple().tm_yday
            theme_index = day_of_year % len(self._themes)
            theme = self._themes[theme_index]
            
            events.append({
                "date": current_day.strftime("%Y-%m-%d"),
                "theme": theme["theme"],
                "description": theme["description"]
            })
        logger.info(f"Retrieved {len(events)} upcoming spiritual events.")
        return events

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
