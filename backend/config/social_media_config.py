"""
⚙️ SOCIAL MEDIA CONFIGURATION

This file contains the core configuration for the Social Media Marketing Engine.
It defines platform-specific settings, content types, and prompts.
"""

from backend.schemas.social_media import SocialPlatform, ContentType

# --- Platform-Specific Configurations ---
# Defines how the engine should behave for each platform.
PLATFORM_CONFIGS = {
    SocialPlatform.FACEBOOK: {
        "posts_per_day": (1, 2),  # Min/max posts per day
        "optimal_times": ["09:00", "18:00"], # In UTC
        "content_types": [
            ContentType.DAILY_WISDOM,
            ContentType.SPIRITUAL_QUOTE,
            ContentType.SATSANG_PROMO,
            ContentType.USER_TESTIMONIAL
        ],
        "max_char_length": 2000,
    },
    SocialPlatform.INSTAGRAM: {
        "posts_per_day": (2, 3),
        "optimal_times": ["11:00", "19:00", "21:00"],
        "content_types": [
            ContentType.DAILY_WISDOM,
            ContentType.SPIRITUAL_QUOTE,
            ContentType.FESTIVAL_GREETING
        ],
        "max_char_length": 1500,
    },
    SocialPlatform.YOUTUBE: {
        "posts_per_day": (1, 1),
        "optimal_times": ["16:00"],
        "content_types": [
            ContentType.DAILY_WISDOM, # Typically as a YouTube Short
            ContentType.SATSANG_PROMO
        ],
        "max_char_length": 5000, # For video description
    },
    SocialPlatform.TIKTOK: {
        "posts_per_day": (2, 4),
        "optimal_times": ["12:00", "15:00", "19:00", "22:00"],
        "content_types": [
            ContentType.DAILY_WISDOM,
            ContentType.SPIRITUAL_QUOTE
        ],
        "max_char_length": 300,
    },
    SocialPlatform.TWITTER: {
        "posts_per_day": (3, 5),
        "optimal_times": ["08:00", "12:00", "15:00", "18:00", "21:00"],
        "content_types": [
            ContentType.SPIRITUAL_QUOTE,
            ContentType.SATSANG_PROMO
        ],
        "max_char_length": 280,
    },
}

# --- Content Generation Prompts ---
# Provides the initial prompts for the RAG system based on content type.
CONTENT_PROMPTS = {
    ContentType.DAILY_WISDOM: "Generate a short, profound piece of daily wisdom from Vedic philosophy about inner peace and self-realization. It should be inspiring and easy to understand for a modern audience.",
    ContentType.SPIRITUAL_QUOTE: "Find a powerful and concise spiritual quote from a respected guru or ancient text (like the Upanishads or Gita) and briefly explain its meaning in today's context.",
    ContentType.SATSANG_PROMO: "Create an exciting and welcoming promotional message for an upcoming online Satsang with Swamiji. Mention the topic, date, and the spiritual benefits of attending.",
    ContentType.FESTIVAL_GREETING: "Generate a warm and spiritual greeting for an upcoming major Indian festival (e.g., Diwali, Holi, Navaratri). The message should explain the spiritual significance of the festival.",
    ContentType.USER_TESTIMONIAL: "Adapt a user's positive experience with JyotiFlow.ai into a heartfelt and authentic testimonial. Focus on the transformation and positive impact.",
}

# --- Daily Thematic Prompts for Swamiji's Avatar ---
# Provides a theme for each day of the week for image generation.
# Monday=0, Sunday=6
THEMES = {
    0: "representing new beginnings and clarity, with serene white and silver tones, perhaps near a calm water body.",
    1: "embodying courage and energy, with dynamic red and orange hues, maybe in a vibrant temple setting.",
    2: "symbolizing intellect and communication, with lively green colors, in a lush, natural environment like a forest or garden.",
    3: "reflecting expansion and wisdom, with rich yellow and gold tones, possibly in a library of ancient scriptures.",
    4: "conveying love and abundance, with bright, luxurious colors, surrounded by offerings of flowers and fruits.",
    5: "representing introspection and discipline, with deep blue and black colors, in a meditative, peaceful, and quiet space.",
    6: "for spiritual connection and radiance, with brilliant golden and sun-like colors, in a scene depicting a sunrise or sunset."
} 