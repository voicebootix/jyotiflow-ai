"""
🤖 SOCIAL MEDIA MARKETING AUTOMATION ENGINE

This engine is the core of JyotiFlow.ai's autonomous social media presence.
It plans, generates, and prepares content for posting across multiple platforms.
"""
import asyncio
import random
import logging
from datetime import datetime, time
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from fastapi import Depends

# Local dependencies
# REFRESH.MD: Use direct imports from the root of the 'backend' package for Render compatibility.
from core_foundation_enhanced import EnhancedSpiritualEngine, get_spiritual_engine
from spiritual_avatar_generation_engine import SpiritualAvatarGenerationEngine, get_avatar_engine
from schemas.social_media import SocialPlatform, ContentType, ContentPlan
from config.social_media_config import PLATFORM_CONFIGS, CONTENT_PROMPTS
from services.spiritual_calendar_service import SpiritualCalendarService # IMPORT PUTHU SERVICE
import db

# Initialize logger
logger = logging.getLogger(__name__)

class SocialMediaMarketingEngine:
    """
    The main engine for planning and generating social media content.
    """

    def __init__(
        self,
        spiritual_engine: EnhancedSpiritualEngine,
        avatar_engine: SpiritualAvatarGenerationEngine,
        calendar_service: SpiritualCalendarService  # PUTHU SERVICE-A SERKKA POREN
    ):
        self.spiritual_engine = spiritual_engine
        self.avatar_engine = avatar_engine
        self.calendar_service = calendar_service  # SERTHAAYIRUCHU
        self.platform_configs = PLATFORM_CONFIGS
        logger.info("🤖 Social Media Marketing Engine initialized with Spiritual Calendar.")

    async def _generate_ai_content(self, platform: SocialPlatform, content_type: ContentType, daily_theme: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates AI-powered content for a specific platform and content type
        using the spiritual engine and RAG system, based on the daily spiritual theme.
        """
        try:
            # Use the daily theme to create a specific prompt
            theme_name = daily_theme.get("theme", "general spiritual guidance")
            theme_description = daily_theme.get("description", "")
            
            guidance_prompt = f"Create a social media post about '{theme_name}'. The theme is about: {theme_description}. Provide wisdom, context, and maybe a short mantra or practice related to it."
            
            # Context for the RAG system
            guidance_context = {
                "service_type": "daily_social_media_post",
                "cultural_context": {"language": "en", "tradition": "vedic_philosophy"},
                "platform": platform.value,
                "daily_theme": theme_name # Pass the theme to RAG
            }
            
            # Generate the core spiritual text using RAG
            guidance_text, metadata = await self.spiritual_engine.generate_personalized_guidance(
                context=guidance_context,
                user_query=guidance_prompt
            )
            
            # Adapt the core text into a full social media post
            platform_adaptation_prompt = f"""
            Adapt the following spiritual guidance into a compelling social media post for {platform.name}.
            The post should be in the voice of a wise, modern spiritual master (Swamiji).
            It must include:
            1. A catchy title/hook (max 15 words).
            2. The main body content, adapted from the guidance below.
            3. A call-to-action (e.g., 'Comment your thoughts below', 'Share with a friend').
            4. 3-5 relevant, trending hashtags.

            Here is the spiritual guidance to adapt:
            ---
            {guidance_text}
            ---

            Return the response as a JSON object with keys: "title", "body", "cta", "hashtags".
            """
            
            # This call now goes to a generic LLM for adaptation, not the RAG-based one
            post_structure = await self.spiritual_engine.llm_interface.get_structured_response(platform_adaptation_prompt)
            
            logger.info(f"✅ Generated content for {platform.name} on {content_type.name}")
            return {
                "title": post_structure.get("title", "A Moment of Wisdom"),
                "description": post_structure.get("body", guidance_text),
                "hashtags": post_structure.get("hashtags", ["#spiritual", "#wisdom"]),
                "cta": post_structure.get("cta", "Share your light."),
                "base_content": guidance_text # Keep original for video generation
            }

        except Exception as e:
            logger.error(f"AI content generation failed for {platform.name}/{content_type.name}: {e}", exc_info=True)
            return self._get_fallback_content(platform, content_type)

    def _get_fallback_content(self, platform: SocialPlatform, content_type: ContentType) -> Dict[str, Any]:
        """Provides a safe, generic piece of content if AI generation fails."""
        logger.warning(f"Using fallback content for {platform.name}/{content_type.name}")
        return {
            "title": "Divine Wisdom for You",
            "description": "Embrace the peace within and let your spirit soar. The universe is always guiding you towards your true path. Have faith in your journey.",
            "hashtags": ["#jyotiflow", "#spiritualawakening", "#peace", "#wisdom"],
            "cta": "Share this message with someone who needs it.",
            "base_content": "Embrace the peace within and let your spirit soar."
        }
        
    async def _generate_platform_content_plan(self, platform: SocialPlatform, daily_theme: Dict[str, Any]) -> List[ContentPlan]:
        """Generates a content plan for a single platform for the day based on the spiritual theme."""
        config = self.platform_configs.get(platform)
        if not config:
            return []
            
        plans = []
        # Generate a variable number of posts based on platform config
        num_posts = random.randint(config["posts_per_day"][0], config["posts_per_day"][1])
        
        for _ in range(num_posts):
            content_type = random.choice(config["content_types"])
            
            ai_content = await self._generate_ai_content(platform, content_type, daily_theme)
            
            plan = ContentPlan(
                platform=platform.value,
                content_type=content_type.value,
                title=ai_content["title"],
                description=ai_content["description"],
                hashtags=ai_content["hashtags"],
                cta=ai_content["cta"],
                base_content_for_video=ai_content["base_content"],
                media_type="video" if content_type == ContentType.DAILY_WISDOM else "text",
                status="pending_generation",
                scheduled_time=None, # Will be set during execution phase
                media_url=None,
            )
            plans.append(plan)
        
        return plans

    async def generate_daily_content_plan(self) -> Dict[str, List[ContentPlan]]:
        """
        Generates a comprehensive content plan for all active platforms for one day.
        This is the main entry point for daily content planning.
        """
        daily_plan = {}
        platforms_to_generate = [p for p in SocialPlatform]

        # Get the daily spiritual theme first
        daily_theme = await self.calendar_service.get_daily_spiritual_theme()
        logger.info(f"📅 Today's spiritual theme is: {daily_theme['theme']}")

        # Use asyncio.gather for concurrent plan generation
        tasks = [self._generate_platform_content_plan(platform, daily_theme) for platform in platforms_to_generate]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for platform, result in zip(platforms_to_generate, results):
            if isinstance(result, Exception):
                logger.error(f"Content plan generation failed for {platform.name}: {result}", exc_info=True)
                daily_plan[platform.value] = []
            else:
                daily_plan[platform.value] = result
        
        logger.info(f"📅 Daily content plan generated for {len(daily_plan)} platforms.")
        
        # This will be called from the router which will provide the DB connection
        # await self._store_content_plan_in_db(daily_plan) 
        
        return daily_plan

    async def _store_content_plan_in_db(self, plan: Dict[str, List[ContentPlan]], conn):
        """Stores the generated content plan into the database for persistence."""
        try:
            # The database connection is now passed in as an argument
            # In a real app, you would insert these plans into a `content_schedule` table.
            logger.info("Simulating storage of content plan into database.")
            # Example:
            # async with conn.transaction():
            #     for platform, posts in plan.items():
            #         for post in posts:
            #             await conn.execute("INSERT INTO content_schedule (..) VALUES (..)", post.dict())
        except Exception as e:
            logger.error(f"Failed to store content plan in database: {e}", exc_info=True)
            # The calling function should handle this error.

# --- FastAPI Dependency Injection ---
# REFRESH.MD: Correctly use FastAPI's dependency injection system.
# The factory now accepts dependencies as arguments, which will be provided by FastAPI.
def get_social_media_engine(
    spiritual_engine: EnhancedSpiritualEngine = Depends(get_spiritual_engine),
    avatar_engine: SpiritualAvatarGenerationEngine = Depends(get_avatar_engine),
    calendar_service: SpiritualCalendarService = Depends() # PUTHU DEPENDENCY
) -> SocialMediaMarketingEngine:
    """
    Provides a singleton-like instance of the SocialMediaMarketingEngine
    by leveraging FastAPI's dependency caching.
    """
    # FastAPI caches the result of this for a single request, effectively making it a singleton per-request.
    return SocialMediaMarketingEngine(spiritual_engine, avatar_engine, calendar_service)

