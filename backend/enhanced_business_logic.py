import asyncio
import json
import uuid
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random
from typing import Optional, Dict, List, Any, Tuple
import json


# External Integrations
import aiohttp
from openai import AsyncOpenAI
import numpy as np
from sklearn.cluster import KMeans

# তমিল - আমাদের ভিত্তি থেকে আমদানি
from core_foundation_enhanced import (
    SpiritualUser, UserPurchase, SpiritualSession, AvatarSession,
    SatsangEvent, SatsangAttendee, MonetizationInsight, SocialContent,
    EnhancedSettings, logger, EnhancedJyotiFlowDatabase
)

# =============================================================================
# 🌟 SERVICE MANAGEMENT FUNCTIONS
# তমিল - சேவை மேலாண்மை செயல்பாடுகள்
# =============================================================================

# Backward compatibility mapping for existing hardcoded service names
SERVICE_NAME_MAPPING = {
    # Legacy service names to database service names
    "clarity": "தொட்டக்க தொகுப்பு",
    "love": "பிரபல தொகுப்பு", 
    "premium": "மாஸ்டர் தொகுப்பு",
    "elite": "மாஸ்டர் தொகுப்பு",
    "quick_blessing": "தொட்டக்க தொகுப்பு",
    "spiritual_guidance": "பிரபல தொகுப்பு",
    "premium_consultation": "மாஸ்டர் தொகுப்பு",
    "elite_session": "மாஸ்டர் தொகுப்பு"
}

async def get_service_by_name(service_name: str, db_manager: EnhancedJyotiFlowDatabase) -> Optional[Dict]:
    """
    Fetch service details from database by name
    Replaces hardcoded SKUS dictionary with database-driven approach
    Includes backward compatibility for legacy service names
    """
    try:
        # Check if service_name is a legacy name and map it
        mapped_name = SERVICE_NAME_MAPPING.get(service_name, service_name)
        
        query = """
            SELECT id, name, description, credits_required, price_usd, 
                   enabled, created_at, updated_at
            FROM service_types 
            WHERE name = $1 AND enabled = TRUE
        """
        row = await db_manager.fetchrow(query, mapped_name)
        
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'credits_required': row['credits_required'],
                'price_usd': float(row['price_usd']) if row['price_usd'] else 0.0,
                'enabled': row['enabled'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching service by name '{service_name}': {e}")
        return None

async def get_all_enabled_services(db_manager: EnhancedJyotiFlowDatabase) -> List[Dict]:
    """
    Fetch all enabled services from database
    Replaces hardcoded service lists with database-driven approach
    """
    try:
        query = """
            SELECT id, name, description, credits_required, price_usd, 
                   enabled, created_at, updated_at
            FROM service_types 
            WHERE enabled = TRUE
            ORDER BY credits_required ASC
        """
        rows = await db_manager.fetch(query)
        
        services = []
        for row in rows:
            services.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'credits_required': row['credits_required'],
                'price_usd': float(row['price_usd']) if row['price_usd'] else 0.0,
                'enabled': row['enabled'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return services
    except Exception as e:
        logger.error(f"Error fetching all enabled services: {e}")
        return []

# =============================================================================
# 🌟 SPIRITUAL GUIDANCE ENUMS & CONSTANTS
# তমিল - আধ্যাত্মিক পথনির্দেশনা গণনা এবং ধ্রুবক
# =============================================================================

class AutomatedStyleManager:
    """TRUE automation - dynamic avatar styling through prompts"""
    
        # In AutomatedStyleManager class
    def __init__(self, db_manager):
        self.db = db_manager
        self.style_templates = {}
        self.festival_calendar = {}
        self._initialize_templates()  # Load on init
        self._load_festival_calendar()  # Load from database

    def _initialize_templates(self):
        """Initialize style templates from configuration"""
        # Load from database or configuration file
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'style_templates.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.style_templates = json.load(f)
        else:
            # Fallback to default templates
            self.style_templates = self._get_default_templates()

    def _get_default_templates(self) -> Dict:
        """Get default style templates"""
        return {
            "daily_guidance": {
                "clothing_prompt": "wearing simple white cotton kurta with peaceful expression",
                "background_prompt": "peaceful ashram garden with flowers and meditation stones",
                "cultural_elements": "basic rudraksha mala, gentle spiritual presence",
                "mood_description": "calm and encouraging"
            },
            # ... other templates
        }
        
    async def load_style_templates(self):
        """Load style templates - இந்த method automatic style load செய்யும்"""
        self.style_templates = {
            "daily_guidance": {
                "clothing_prompt": "wearing simple white cotton kurta with peaceful expression",
                "background_prompt": "peaceful ashram garden with flowers and meditation stones",
                "cultural_elements": "basic rudraksha mala, gentle spiritual presence",
                "mood_description": "calm and encouraging"
            },
            "satsang_traditional": {
                "clothing_prompt": "wearing rich orange silk robes with gold borders and traditional markings",
                "background_prompt": "sacred temple interior with oil lamps and spiritual symbols",
                "cultural_elements": "elaborate rudraksha mala, spiritual ornaments",
                "mood_description": "wise and authoritative"
            },
            "festival_ceremonial": {
                "clothing_prompt": "wearing luxurious silk robes with intricate embroidery in festival colors",
                "background_prompt": "decorated temple with thousands of oil lamps and festival decorations",
                "cultural_elements": "multiple malas, ceremonial items, divine aura",
                "mood_description": "joyous and celebratory"
            },
            "social_media_modern": {
                "clothing_prompt": "wearing contemporary spiritual attire in earth tones",
                "background_prompt": "natural outdoor setting with mountains or rivers",
                "cultural_elements": "minimalist spiritual jewelry, accessible presence",
                "mood_description": "warm and relatable"
            },
            "premium_consultation": {
                "clothing_prompt": "wearing high-quality traditional robes with silk and spiritual symbols",
                "background_prompt": "luxurious temple setting with golden decorations",
                "cultural_elements": "premium spiritual ornaments, majestic presence",
                "mood_description": "deeply wise and powerful"
            }
        }
    
    async def detect_occasion(self, session_context: Dict) -> str:
        """Automatic occasion detection with proper timezone"""
        current_date = datetime.now(timezone.utc)
    
        # Check for Tamil festivals first
        festival = self.check_festival_date(current_date)
        if festival:
            return "festival_ceremonial"
        
        # Check content type and service level
        content_type = session_context.get('content_type', '')
        service_type = session_context.get('service_type', 'clarity')
        
        # Database-driven service type detection
        if 'satsang' in content_type.lower() or 'community' in content_type.lower():
            return "satsang_traditional"
        elif service_type:
            # Fetch service details from database to determine intensity
            service_details = await get_service_by_name(service_type, self.db)
            if service_details:
                # Use service credits_required to determine intensity
                credits_required = service_details.get('credits_required', 0)
                if credits_required >= 50:  # High-value services
                    return "premium_consultation"
                elif credits_required >= 20:  # Medium-value services
                    return "satsang_traditional"
                else:  # Low-value services
                    return "daily_guidance"
        elif 'social' in content_type.lower():
            return "social_media_modern"
        else:
            return "daily_guidance"
    
    def check_festival_date(self, date: datetime) -> Optional[str]:
        """Festival date checker with database integration"""
        # Ensure timezone awareness
        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
            date = date.replace(tzinfo=timezone.utc)
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Check database first
        if hasattr(self, 'festival_calendar') and self.festival_calendar:
            return self.festival_calendar.get(date_str)
        
        # Fallback to API or return None
        return None

    def _load_festival_calendar(self):
        """Load festival calendar from database"""
        try:
            self.festival_calendar = {
                "2025-02-26": "Maha Shivaratri",
                "2025-04-14": "Tamil New Year", 
                "2025-10-03": "Navaratri",
                "2025-11-01": "Karthikai Deepam",
                "2025-01-14": "Thai Pongal",
                "2025-08-19": "Krishna Janmashtami",
                "2025-09-07": "Ganesha Chaturthi"
            }
            logger.info(f"✅ Festival calendar loaded with {len(self.festival_calendar)} festivals")
        except Exception as e:
            logger.error(f"Failed to load festival calendar: {e}")
            self.festival_calendar = {}
    
    def generate_dynamic_prompt(self, style_name: str, festival_name: str = None) -> str:
        """Dynamic D-ID prompt generation - automatic variety செய்யும்"""
        template = self.style_templates.get(style_name, self.style_templates["daily_guidance"])
        
        # Festival-specific automatic overrides
        if festival_name:
            festival_overrides = {
                "Maha Shivaratri": "wearing pure white silk robes with silver accents, Shiva temple with lingam and sacred fire, Shiva symbols and sacred ash",
                "Tamil New Year": "wearing fresh yellow and golden silk robes, temple decorated with mango leaves and kolam, prosperity symbols",
                "Navaratri": "wearing traditional Devi colors, Devi temple with divine feminine decorations, Devi symbols and Flower2 flowers",
                "Karthikai Deepam": "wearing deep orange and golden robes, temple with thousands of oil lamps, light symbolism and fire elements",
                "Thai Pongal": "wearing yellow and golden festive robes, natural abundance setting, harvest symbols and gratitude themes"
            }
            
            override = festival_overrides.get(festival_name, "")
            if override:
                return f"Tamil spiritual master {override}, {template['mood_description']} expression"
        
        # Regular automatic dynamic prompt
        return f"Tamil spiritual master {template['clothing_prompt']}, {template['background_prompt']}, {template['cultural_elements']}, {template['mood_description']} expression"

class TamilCulturalIntegration:
    """Tamil cultural phrases automatic integration"""
    
    def __init__(self):
        self.greetings = {
            "daily": ["Vanakkam, anbulla makkalae", "Kalaiyil vanakkam, atma nanbarkalay"],
            "festival": ["Thiruvizha dinam vanakkam, iraivan makkalae", "Festival vanakkam, bhakta janangalay"],
            "satsang": ["Satsanga vanakkam, spiritual family", "Om Anbulla atmaakkalae"],
            "premium": ["Divine vanakkam, blessed soul", "Iraivan arul kondae vanakkam"]
        }
        
        self.closures = {
            "daily": ["Tamil thaai arul kondae vazhlga", "May divine light guide your path"],
            "festival": ["Festival blessings upon you", "Thiruvizha anugrahangal ungal mael"],
            "healing": ["Rogam mudhitu, arogiyam perunga", "Health and healing be yours"],
            "prosperity": ["Selvam serunga, anbu velukka", "Prosperity and love flourish"],
            "spiritual": ["Atma unnathiya adhigarikka", "May your soul reach greater heights"],
            "peace": ["Shanti perunga, sukham nerunga", "Receive peace, gain happiness"]
        }
        
        self.weekly_themes = {
            "monday": "New week spiritual energy, motivation for divine path",
            "tuesday": "Ancient Tamil wisdom, Thirukkural teachings",
            "wednesday": "Spiritual wellness, mind-body-soul harmony",
            "thursday": "Transformation through divine grace",
            "friday": "Fearless faith, courage through spirituality",
            "saturday": "Community satsang, shared spiritual journey",
            "sunday": "Sacred teachings, deep spiritual truths"
        }
    
    def get_cultural_greeting(self, occasion: str, context: str = "daily") -> str:
        """Tamil greeting automatic selection"""
        greeting_type = "festival" if "festival" in occasion else context
        greetings_list = self.greetings.get(greeting_type, self.greetings["daily"])
        return random.choice(greetings_list)
    
    def get_cultural_closure(self, session_type: str) -> str:
        """Tamil closure automatic selection"""
        closures_list = self.closures.get(session_type, self.closures["daily"])
        return random.choice(closures_list)
    
    def get_weekly_theme(self) -> str:
        """Weekly theme detection with timezone awareness"""
        # Convert to user's timezone if available, default to IST
        user_tz = self.get_user_timezone()  # Implement based on user profile
        if user_tz:
            today = datetime.now(user_tz).strftime("%A").lower()
        else:
            # Default to IST for Tamil audience
            ist_tz = timezone(timedelta(hours=5, minutes=30))
            today = datetime.now(ist_tz).strftime("%A").lower()
    
        return self.weekly_themes.get(today, self.weekly_themes["sunday"])

class CommunityEventManager:
    """Phase 2: Dashboard event management"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        
    async def create_weekly_programs(self):
        """Automatic weekly program creation"""
        weekly_programs = [
            {
                "event_name": "Monday Motivation Satsang",
                "event_type": "weekly_motivation",
                "recurring_pattern": "every_monday",
                "avatar_style": "daily_guidance",
                "content_themes": "Week ahead blessings, spiritual goals, motivation"
            },
            {
                "event_name": "Tuesday Tamil Wisdom",
                "event_type": "cultural_wisdom",
                "recurring_pattern": "every_tuesday", 
                "avatar_style": "satsang_traditional",
                "content_themes": "Thirukkural quotes, Tamil saints, ancient knowledge"
            },
            {
                "event_name": "Wednesday Wellness Circle",
                "event_type": "spiritual_wellness",
                "recurring_pattern": "every_wednesday",
                "avatar_style": "daily_guidance",
                "content_themes": "Ayurveda, yoga, spiritual health practices"
            },
            {
                "event_name": "Saturday Satsang Community",
                "event_type": "community_gathering", 
                "recurring_pattern": "every_saturday",
                "avatar_style": "satsang_traditional",
                "content_themes": "Group meditation, community wisdom, shared blessings"
            }
        ]
        
        return weekly_programs
    
    async def create_monthly_specials(self):
        """Automatic monthly special events"""
        monthly_events = [
            {
                "event_name": "Tamil Heritage Satsang",
                "event_type": "cultural_celebration",
                "recurring_pattern": "first_saturday_monthly",
                "avatar_style": "festival_ceremonial",
                "content_themes": "Tamil spiritual heritage, cultural pride, traditional wisdom"
            },
            {
                "event_name": "Healing Circle Gathering", 
                "event_type": "healing_session",
                "recurring_pattern": "second_saturday_monthly",
                "avatar_style": "premium_consultation",
                "content_themes": "Spiritual healing, energy cleansing, divine restoration"
            },
            {
                "event_name": "Youth Spiritual Awakening",
                "event_type": "youth_program",
                "recurring_pattern": "third_saturday_monthly", 
                "avatar_style": "social_media_modern",
                "content_themes": "Modern spirituality, youth guidance, contemporary wisdom"
            },
            {
                "event_name": "Family Harmony Session",
                "event_type": "family_program",
                "recurring_pattern": "fourth_saturday_monthly",
                "avatar_style": "satsang_traditional", 
                "content_themes": "Family blessings, relationship harmony, household peace"
            }
        ]
        
        return monthly_events
    
class SpiritualState(Enum):
    """তমিল - আধ্যাত্মিক অবস্থার গণনা"""
    SEEKING = "seeking_guidance"
    CONFUSED = "spiritual_confusion"  
    GROWING = "spiritual_growth"
    PEACEFUL = "inner_peace"
    AWAKENING = "spiritual_awakening"
    DEVOTED = "devotional_practice"

class SessionIntensity(Enum):
    """তমিল - সেশনের তীব্রতা গণনা"""
    GENTLE = "gentle_guidance"
    MODERATE = "balanced_wisdom"
    DEEP = "profound_insights"
    TRANSFORMATIVE = "life_changing"

class AvatarEmotion(Enum):
    """তমিল - অবতারের আবেগ গণনা"""
    COMPASSIONATE = "compassionate_love"
    WISE = "ancient_wisdom"
    GENTLE = "nurturing_care"
    POWERFUL = "divine_strength"
    JOYFUL = "spiritual_bliss"

# Sacred mantras and responses
SACRED_MANTRAS = {
    "opening": ["🙏🏼 Om Namah Shivaya", "🕉️ Hari Om Tat Sat", "🌺 Om Gam Ganapataye Namaha"],
    "blessing": ["May divine light guide your path", "Om Shanti Shanti Shanti", "Divine blessings upon you"],
    "closure": ["Go in peace, dear soul", "May your journey be blessed", "Om Namah Shivaya 🙏🏼"]
}

# =============================================================================
# 🎭 SPIRITUAL AVATAR ENGINE
# তমিল - আধ্যাত্মিক অবতার ইঞ্জিন
# =============================================================================

@dataclass
class AvatarGenerationContext:
    """তমিল - অবতার তৈরির প্রসঙ্গ"""
    user_id: int
    spiritual_state: SpiritualState
    session_intensity: SessionIntensity
    emotional_tone: AvatarEmotion
    language: str
    cultural_context: Dict[str, Any]
    previous_sessions: List[Dict]

class SpiritualAvatarEngine:
    """তমিল - আধ্যাত্মিক অবতার ইঞ্জিন - Swamiji's digital embodiment"""
    
    def __init__(self):
        self.settings = EnhancedSettings()
        self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.db = EnhancedJyotiFlowDatabase()
    
    # Avatar personality configuration
        self.avatar_personality = {
        "core_traits": ["compassionate", "wise", "patient", "loving"],
        "speaking_style": "gentle_authority",
        "cultural_background": "tamil_vedic_tradition",
        "spiritual_lineage": "advaita_vedanta"
        }
    
        # Initialize automation components ONCE
        self.style_manager = AutomatedStyleManager(self.db)
        self.cultural_integration = TamilCulturalIntegration()
        self.event_manager = CommunityEventManager(self.db)
    
        # Single base presenter ID for automation
        self.base_presenter_id = getattr(self.settings, 'd_id_presenter_id', 'default_presenter')

    
async def generate_personalized_guidance(
    self,
    context: Optional[Dict],
    user_query: str,
    birth_details: Optional[Dict] = None
) -> Tuple[str, Dict]:
    """TRUE AUTOMATION - Enhanced with dynamic avatar styling"""
    try:
        session_context = context or {}
        
        # AUTOMATED: Generate avatar styling automatically
        avatar_info = await self.generate_automated_avatar_prompt(session_context)
        
        # Generate base spiritual guidance
        try:
            base_guidance = await self._generate_guidance_text(user_query, {}, birth_details, context or {})
        except:
            # Fallback guidance generation
            base_guidance = f"""Dear beloved soul, regarding your heartfelt question about {user_query}, 

Divine wisdom flows through the ancient teachings of our Tamil spiritual tradition. Trust in the divine plan that unfolds for your highest good. Through prayer, meditation, and devotion, all answers will be revealed in perfect divine timing.

Remember that every challenge is an opportunity for spiritual growth, and every blessing is a reminder of divine love."""
        
        # AUTOMATED: Add Tamil cultural elements
        culturally_enhanced_guidance = self.add_automated_cultural_elements(base_guidance, avatar_info)
        
        # AUTOMATED: Enhanced video metadata with TRUE automation
        video_metadata = {
            "text_content": culturally_enhanced_guidance,
            "dynamic_style_prompt": avatar_info["dynamic_prompt"],
            "presenter_id": avatar_info["presenter_id"],
            "auto_detected_style": avatar_info["style_name"],
            "festival_theme": avatar_info.get("festival_name"),
            "cultural_theme": "tamil_vedic_tradition",
            "automation_active": avatar_info["automation_active"],
            "voice_settings": {
                "stability": 0.8,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            },
            "video_settings": {
                "automated_styling": True,
                "dynamic_prompts": True,
                "cultural_integration": True
            }
        }
        
        return culturally_enhanced_guidance, video_metadata
        
    except Exception as e:
        logger.error(f"Automated guidance generation failed: {e}")
        # Safe fallback
        fallback = "Vanakkam, beloved soul. Divine love and blessings are always with you. Tamil thaai arul kondae vazhlga."
        return fallback, {"cultural_theme": "daily_wisdom", "automation_active": False}
    
    async def _analyze_spiritual_profile(self, context: AvatarGenerationContext) -> Dict:
        """তমিল - ব্যবহারকারীর আধ্যাত্মিক প্রোফাইল বিশ্লেষণ"""
        try:
            # Get user's session history
            sessions = await self.db.get_user_sessions(context.user_id, limit=10)
            
            # Analyze patterns using AI
            analysis_prompt = f"""
            Analyze this spiritual seeker's journey and provide insights:
            
            Recent Sessions: {json.dumps(sessions, indent=2)}
            Current State: {context.spiritual_state.value}
            
            Provide analysis of:
            1. Spiritual growth trajectory
            2. Recurring themes and concerns  
            3. Recommended guidance approach
            4. Emotional support needs
            
            Format as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Spiritual profile analysis failed: {e}")
            return {"growth_stage": "seeking", "needs": ["general_guidance"]}
    
    async def _generate_guidance_text(
        self, 
        query: str, 
        profile: Dict, 
        birth_details: Optional[Dict],
        context: AvatarGenerationContext
    ) -> str:
        """তমিল - পথনির্দেশনা পাঠ তৈরি করুন"""
        try:
            # Select appropriate mantra
            opening_mantra = np.random.choice(SACRED_MANTRAS["opening"])
            
            # Build culturally rich prompt
            spiritual_prompt = f"""
            {opening_mantra}
            
            As Swami Jyotirananthan, beloved Tamil spiritual master, provide divine guidance:
            
            Seeker's Question: {query}
            Spiritual Profile: {json.dumps(profile, indent=2)}
            Birth Details: {birth_details or 'Seeking general guidance'}
            Cultural Context: {context.cultural_context}
            Language: {context.language}
            Session Intensity: {context.session_intensity.value}
            
            Guidance Requirements:
            - Speak with {context.emotional_tone.value} energy
            - Include relevant Tamil/Sanskrit wisdom
            - Provide practical spiritual steps
            - Reference Vedic principles appropriately
            - End with blessing and encouragement
            - Keep response suitable for 60-90 second video
            
            Remember: You are a living embodiment of divine love and wisdom.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": spiritual_prompt}],
                max_tokens=700,
                temperature=0.7
            )
            
            guidance = response.choices[0].message.content
            
            # Add closing blessing
            closing_blessing = np.random.choice(SACRED_MANTRAS["blessing"])
            return f"{guidance}\n\n{closing_blessing} 🙏🏼"
            
        except Exception as e:
            logger.error(f"Guidance text generation failed: {e}")
            return self._get_fallback_guidance(context)
    
    async def _prepare_avatar_metadata(
        self, 
        guidance_text: str, 
        context: AvatarGenerationContext,
        profile: Dict
    ) -> Dict:
        """তমিল - অবতার ভিডিও মেটাডেটা প্রস্তুত করুন"""
        return {
            "text_content": guidance_text,
            "emotional_tone": context.emotional_tone.value,
            "voice_settings": {
                "stability": 0.8,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            },
            "video_settings": {
                "background": "spiritual_ashram",
                "lighting": "warm_divine",
                "expression": context.emotional_tone.value
            },
            "cultural_elements": {
                "include_sanskrit": True,
                "tamil_context": context.language == "ta",
                "spiritual_symbols": True
            }
        }
    
    def _get_fallback_guidance(self, context: AvatarGenerationContext) -> str:
        """তমিল - ফলব্যাক পথনির্দেশনা"""
        mantras = SACRED_MANTRAS["opening"] + SACRED_MANTRAS["blessing"]
        selected_mantra = np.random.choice(mantras)
        
        return f"""
        {selected_mantra}
        
        Dear beloved soul, in this moment of seeking, know that you are held in divine love. 
        The path of spirituality is not always clear, but your sincere heart draws you closer 
        to truth with each step.
        
        Take time today for quiet reflection. Breathe deeply and feel the presence of the 
        divine within you. Trust your inner wisdom, for it is connected to the infinite 
        source of all knowledge.
        
        May peace fill your heart and light guide your way. 🙏🏼
        
        Om Shanti Shanti Shanti
        
         # ADD these NEW automation components AFTER existing code
        self.style_manager = AutomatedStyleManager(self.db)
        self.cultural_integration = TamilCulturalIntegration()
        self.event_manager = CommunityEventManager(self.db)
        
        # Single base presenter ID for TRUE automation
        self.base_presenter_id = getattr(self.settings, 'd_id_presenter_id', 'default_presenter')   
        """
#In generate_automated_avatar_prompt method:
async def generate_automated_avatar_prompt(self, session_context: Dict) -> Dict:
    """Automatic avatar prompt generation with timezone awareness"""
    
    # Automatic occasion detection
    style_name = await self.style_manager.detect_occasion(session_context)
    
    # Festival checking with UTC timezone
    current_date = datetime.now(timezone.utc)
    festival_name = self.style_manager.check_festival_date(current_date)
    
    # Dynamic prompt generation
    dynamic_prompt = self.style_manager.generate_dynamic_prompt(style_name, festival_name)
    
    return {
        "style_name": style_name,
        "festival_name": festival_name,
        "dynamic_prompt": dynamic_prompt,
        "presenter_id": self.base_presenter_id,
        "automation_active": True
    }

def add_automated_cultural_elements(self, guidance_text: str, style_info: Dict) -> str:
    """Automatic Tamil cultural integration"""
    style_name = style_info.get("style_name", "daily")
    festival_name = style_info.get("festival_name")
    
    # Automatic greeting selection
    occasion = "festival" if festival_name else style_name
    greeting = self.cultural_integration.get_cultural_greeting(occasion, style_name)
    
    # Automatic closure selection
    closure = self.cultural_integration.get_cultural_closure(style_name)
    
    # Automatic weekly theme (if applicable)
    weekly_theme = self.cultural_integration.get_weekly_theme()
    
    # Enhanced guidance with automation
    enhanced_guidance = f"""{greeting}

{guidance_text}

Today's spiritual focus: {weekly_theme}

{closure}"""
    
    return enhanced_guidance.strip()

async def get_dashboard_event_suggestions(self) -> Dict:
    """Phase 2: Dashboard event suggestions"""
    weekly_programs = await self.event_manager.create_weekly_programs()
    monthly_specials = await self.event_manager.create_monthly_specials()
    
    return {
        "weekly_programs": weekly_programs,
        "monthly_specials": monthly_specials,
        "automation_enabled": True
    }
# =============================================================================
# 💰 MONETIZATION OPTIMIZER
# তমিল - নগদীকরণ অপ্টিমাইজার
# =============================================================================

class MonetizationOptimizer:
    """তমিল - AI চালিত নগদীকরণ অপ্টিমাইজার"""
    
    def __init__(self):
        self.settings = EnhancedSettings()
        self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.db = EnhancedJyotiFlowDatabase()
    
    async def generate_pricing_recommendations(self, time_period: str = "monthly") -> Dict:
        """তমিল - মূল্য নির্ধারণের সুপারিশ তৈরি করুন"""
        try:
            # Get pricing configuration from database
            pricing_config = await self._get_pricing_config_data()
            
            # Get current analytics
            analytics = await self.db.get_revenue_analytics(time_period)
            user_behavior = await self.get_user_behavior_patterns()
            
            # Analyze pricing elasticity with config data
            elasticity_analysis = await self._analyze_price_elasticity(analytics, pricing_config)
            
            # Generate AI recommendations with pricing config context
            ai_recommendations = await self._generate_ai_recommendations(
                analytics, user_behavior, elasticity_analysis, pricing_config
            )
            
            # Generate pricing-specific recommendations
            pricing_recommendations = await self._generate_pricing_specific_recommendations(
                elasticity_analysis, pricing_config
            )
            
            # Store both types of recommendations
            if ai_recommendations:
                await self._store_ai_recommendations(ai_recommendations, "pricing")
            
            if pricing_recommendations:
                await self._store_ai_pricing_recommendations(pricing_recommendations)
            
            # Combine recommendations
            all_recommendations = ai_recommendations + pricing_recommendations
            
            # Calculate impact and prioritize
            impact_projection = await self._calculate_impact_projection(all_recommendations)
            prioritized_recommendations = self._prioritize_recommendations(all_recommendations)
            
            # Cache the complete insights
            insights_data = {
                "current_metrics": analytics,
                "pricing_config": pricing_config,
                "price_elasticity": elasticity_analysis,
                "recommendations": prioritized_recommendations,
                "pricing_recommendations": pricing_recommendations,
                "expected_impact": impact_projection,
                "generated_at": datetime.now().isoformat()
            }
            await self._cache_ai_insights("pricing_recommendations", insights_data)
            
            return {
                "current_metrics": analytics,
                "pricing_config": pricing_config,
                "price_elasticity": elasticity_analysis,
                "recommendations": prioritized_recommendations,
                "pricing_recommendations": pricing_recommendations,
                "expected_impact": impact_projection,
                "implementation_priority": prioritized_recommendations
            }
            
        except Exception as e:
            logger.error(f"Pricing recommendation generation failed: {e}")
            return {"error": "Recommendation service temporarily unavailable"}
    
    async def optimize_product_offerings(self) -> Dict:
        """তমিল - পণ্য অফার অপ্টিমাইজ করুন"""
        try:
            # Analyze current product performance
            product_data = await self.db.get_product_performance()
            
            # Identify gaps and opportunities  
            market_analysis = await self._analyze_market_opportunities(product_data)
            
            # Generate product recommendations
            product_recommendations = await self._generate_product_suggestions(market_analysis)
            
            return {
                "current_products": product_data,
                "market_opportunities": market_analysis,
                "new_product_suggestions": product_recommendations,
                "optimization_areas": await self._identify_optimization_areas(product_data)
            }
            
        except Exception as e:
            logger.error(f"Product optimization failed: {e}")
            return {"error": "Product optimization temporarily unavailable"}
    
    async def generate_retention_strategies(self) -> Dict:
        """তমিল - ধরে রাখার কৌশল তৈরি করুন"""
        try:
            # Analyze churn patterns
            churn_analysis = await self.db.get_churn_analytics()
            
            # Identify at-risk users
            at_risk_users = await self._identify_at_risk_users()
            
            # Generate personalized retention strategies
            retention_strategies = await self._generate_retention_recommendations(
                churn_analysis, at_risk_users
            )
            
            return {
                "churn_insights": churn_analysis,
                "at_risk_segments": at_risk_users,
                "retention_strategies": retention_strategies,
                "automation_opportunities": await self._identify_automation_opportunities()
            }
            
        except Exception as e:
            logger.error(f"Retention strategy generation failed: {e}")
            return {"error": "Retention analysis temporarily unavailable"}
    
    async def _analyze_price_elasticity(self, analytics: Dict, pricing_config: Dict = None) -> Dict:
        """তমিল - மெய்யான தரவுகளுடன் விலை நெகிழ்வுத்தன்மை பகுப்பாய்வு"""
        try:
            # Get pricing configuration parameters
            min_profit_margin = pricing_config.get('min_profit_margin_percent', 250) / 100 if pricing_config else 2.5
            video_cost_per_minute = pricing_config.get('video_cost_per_minute', 0.70) if pricing_config else 0.70
            
            # 1. Get actual usage data from sessions table
            session_usage = await self.db.fetch("""
                SELECT 
                    st.name as service_name,
                    st.credits_required,
                    st.price_usd as current_price,
                    COUNT(s.id) as total_sessions,
                    COUNT(DISTINCT s.user_id) as unique_users,
                    AVG(EXTRACT(EPOCH FROM (s.completed_at - s.created_at))/60) as avg_duration_minutes,
                    SUM(st.price_usd) as total_revenue,
                    AVG(st.price_usd) as avg_price_paid,
                    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_sessions,
                    COUNT(CASE WHEN s.status = 'cancelled' THEN 1 END) as cancelled_sessions
                FROM service_types st
                LEFT JOIN sessions s ON st.name = s.service_type
                WHERE st.enabled = TRUE
                AND s.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY st.id, st.name, st.credits_required, st.price_usd
                ORDER BY total_sessions DESC
            """)
            
            # 2. Get user behavior patterns
            user_behavior = await self.db.fetch("""
                SELECT 
                    st.name as service_name,
                    COUNT(DISTINCT s.user_id) as repeat_users,
                    AVG(sessions_per_user.total_sessions) as avg_sessions_per_user,
                    AVG(days_between_sessions.avg_days) as avg_days_between_sessions
                FROM service_types st
                LEFT JOIN sessions s ON st.name = s.service_type
                LEFT JOIN (
                    SELECT user_id, service_type, COUNT(*) as total_sessions
                    FROM sessions 
                    WHERE created_at >= NOW() - INTERVAL '90 days'
                    GROUP BY user_id, service_type
                ) sessions_per_user ON s.user_id = sessions_per_user.user_id AND s.service_type = sessions_per_user.service_type
                LEFT JOIN (
                    SELECT user_id, service_type, AVG(days_diff) as avg_days
                    FROM (
                        SELECT 
                            user_id, 
                            service_type,
                            EXTRACT(DAY FROM (created_at - LAG(created_at) OVER (PARTITION BY user_id, service_type ORDER BY created_at))) as days_diff
                        FROM sessions 
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                    ) day_diffs
                    WHERE days_diff IS NOT NULL
                    GROUP BY user_id, service_type
                ) days_between_sessions ON s.user_id = days_between_sessions.user_id AND s.service_type = days_between_sessions.service_type
                WHERE st.enabled = TRUE
                GROUP BY st.id, st.name
            """)
            
            # 3. Get price sensitivity data from recent transactions
            price_sensitivity = await self.db.fetch("""
                SELECT 
                    st.name as service_name,
                    COUNT(CASE WHEN p.amount >= st.price_usd * 1.1 THEN 1 END) as price_increase_acceptance,
                    COUNT(CASE WHEN p.amount <= st.price_usd * 0.9 THEN 1 END) as price_decrease_impact,
                    AVG(p.amount) as actual_avg_price,
                    STDDEV(p.amount) as price_variance
                FROM service_types st
                LEFT JOIN sessions s ON st.name = s.service_type
                LEFT JOIN payments p ON s.id = p.session_id
                WHERE st.enabled = TRUE
                AND p.status = 'completed'
                AND p.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY st.id, st.name, st.price_usd
            """)
            
            # 4. Calculate elasticity based on real data
            elasticity_data = {}
            
            for usage in session_usage:
                service_name = usage['service_name']
                current_price = float(usage['current_price'])
                credits_required = usage['credits_required']
                total_sessions = usage['total_sessions'] or 0
                unique_users = usage['unique_users'] or 0
                avg_duration = float(usage['avg_duration_minutes'] or 0)
                total_revenue = float(usage['total_revenue'] or 0)
                completion_rate = (usage['completed_sessions'] or 0) / max(total_sessions, 1)
                
                # Find corresponding behavior and sensitivity data
                behavior_data = next((b for b in user_behavior if b['service_name'] == service_name), {})
                sensitivity_data = next((s for s in price_sensitivity if s['service_name'] == service_name), {})
                
                # Calculate actual cost based on real usage
                actual_duration = avg_duration if avg_duration > 0 else credits_required / 2
                actual_cost = (video_cost_per_minute * actual_duration) + 1.0
                min_profitable_price = actual_cost * (1 + min_profit_margin)
                
                # Calculate elasticity based on real usage patterns
                elasticity = self._calculate_real_elasticity(
                    total_sessions, unique_users, completion_rate,
                    sensitivity_data.get('price_increase_acceptance', 0),
                    sensitivity_data.get('price_decrease_impact', 0),
                    credits_required
                )
                
                # Calculate optimal price range based on real data
                optimal_range = self._calculate_optimal_price_range(
                    current_price, elasticity, min_profitable_price,
                    sensitivity_data.get('actual_avg_price', current_price),
                    sensitivity_data.get('price_variance', 0)
                )
                
                # Calculate user engagement metrics
                repeat_rate = (behavior_data.get('repeat_users', 0) / max(unique_users, 1)) if unique_users > 0 else 0
                avg_sessions_per_user = float(behavior_data.get('avg_sessions_per_user', 0) or 0)
                avg_days_between = float(behavior_data.get('avg_days_between_sessions', 0) or 30)
                
                elasticity_data[service_name] = {
                    "current_price": current_price,
                    "elasticity": elasticity,
                    "optimal_range": optimal_range,
                    "credits_required": credits_required,
                    "actual_cost": actual_cost,
                    "min_profitable_price": min_profitable_price,
                    "profit_margin": ((current_price - actual_cost) / actual_cost) * 100,
                    
                    # Real usage metrics
                    "total_sessions": total_sessions,
                    "unique_users": unique_users,
                    "avg_duration_minutes": avg_duration,
                    "total_revenue": total_revenue,
                    "completion_rate": completion_rate,
                    "repeat_rate": repeat_rate,
                    "avg_sessions_per_user": avg_sessions_per_user,
                    "avg_days_between_sessions": avg_days_between,
                    
                    # Price sensitivity metrics
                    "price_increase_acceptance": sensitivity_data.get('price_increase_acceptance', 0),
                    "price_decrease_impact": sensitivity_data.get('price_decrease_impact', 0),
                    "actual_avg_price": float(sensitivity_data.get('actual_avg_price', current_price)),
                    "price_variance": float(sensitivity_data.get('price_variance', 0)),
                    
                    # Market positioning
                    "market_demand": "high" if total_sessions > 50 else "medium" if total_sessions > 10 else "low",
                    "user_loyalty": "high" if repeat_rate > 0.3 else "medium" if repeat_rate > 0.1 else "low",
                    "price_sensitivity": "low" if abs(elasticity) < 0.5 else "medium" if abs(elasticity) < 1.0 else "high"
                }
            
            return elasticity_data
            
        except Exception as e:
            logger.error(f"Real data price elasticity analysis failed: {e}")
            # Fallback to basic analysis
            return await self._fallback_elasticity_analysis(pricing_config)

    def _calculate_real_elasticity(self, total_sessions: int, unique_users: int, completion_rate: float, 
                                  price_increase_acceptance: int, price_decrease_impact: int, credits_required: int) -> float:
        """Calculate elasticity based on real usage data"""
        try:
            # Base elasticity on service value
            base_elasticity = -0.8  # Default moderate sensitivity
            
            if credits_required >= 50:
                base_elasticity = -0.4  # High-value services less sensitive
            elif credits_required >= 25:
                base_elasticity = -0.6  # Medium-high value
            elif credits_required >= 10:
                base_elasticity = -1.2  # Medium value more sensitive
            else:
                base_elasticity = -0.8  # Low value
            
            # Adjust based on usage patterns
            usage_factor = min(total_sessions / 100, 1.0)  # Normalize to 0-1
            user_factor = min(unique_users / 50, 1.0)  # Normalize to 0-1
            
            # Higher usage = less price sensitive (more loyal)
            usage_adjustment = (1 - usage_factor) * 0.3
            
            # Higher completion rate = less price sensitive
            completion_adjustment = (1 - completion_rate) * 0.2
            
            # Price sensitivity from actual transactions
            price_sensitivity = 0
            if price_increase_acceptance > 0 or price_decrease_impact > 0:
                total_transactions = price_increase_acceptance + price_decrease_impact
                if total_transactions > 0:
                    price_sensitivity = (price_decrease_impact - price_increase_acceptance) / total_transactions * 0.5
            
            final_elasticity = base_elasticity + usage_adjustment + completion_adjustment + price_sensitivity
            
            # Clamp to reasonable range
            return max(-2.0, min(-0.1, final_elasticity))
            
        except Exception as e:
            logger.error(f"Elasticity calculation failed: {e}")
            return -0.8

    def _calculate_optimal_price_range(self, current_price: float, elasticity: float, 
                                     min_profitable_price: float, actual_avg_price: float, 
                                     price_variance: float) -> str:
        """Calculate optimal price range based on real data"""
        try:
            # Use actual average price if available
            base_price = actual_avg_price if actual_avg_price > 0 else current_price
            
            # Calculate range based on elasticity
            if abs(elasticity) < 0.5:  # Low sensitivity
                lower_bound = max(min_profitable_price, base_price * 0.85)
                upper_bound = base_price * 1.25
            elif abs(elasticity) < 1.0:  # Medium sensitivity
                lower_bound = max(min_profitable_price, base_price * 0.8)
                upper_bound = base_price * 1.2
            else:  # High sensitivity
                lower_bound = max(min_profitable_price, base_price * 0.75)
                upper_bound = base_price * 1.15
            
            # Adjust for price variance
            variance_adjustment = price_variance * 0.5
            lower_bound = max(min_profitable_price, lower_bound - variance_adjustment)
            upper_bound = upper_bound + variance_adjustment
            
            return f"{lower_bound:.0f}-{upper_bound:.0f}"
            
        except Exception as e:
            logger.error(f"Optimal price range calculation failed: {e}")
            return f"{min_profitable_price:.0f}-{current_price * 1.2:.0f}"

    async def _fallback_elasticity_analysis(self, pricing_config: Dict = None) -> Dict:
        """Fallback elasticity analysis when real data is unavailable"""
        try:
            services = await get_all_enabled_services(self.db)
            min_profit_margin = pricing_config.get('min_profit_margin_percent', 250) / 100 if pricing_config else 2.5
            video_cost_per_minute = pricing_config.get('video_cost_per_minute', 0.70) if pricing_config else 0.70
            
            elasticity_data = {}
            for service in services:
                service_name = service['name']
                current_price = service['price_usd']
                credits_required = service['credits_required']
                
                estimated_duration = credits_required / 2
                estimated_cost = (video_cost_per_minute * estimated_duration) + 1.0
                min_price = estimated_cost * (1 + min_profit_margin)
                
                if credits_required >= 50:
                    elasticity = -0.4
                    optimal_range = f"{max(min_price, current_price * 0.9):.0f}-{current_price * 1.3:.0f}"
                elif credits_required >= 25:
                    elasticity = -0.6
                    optimal_range = f"{max(min_price, current_price * 0.85):.0f}-{current_price * 1.25:.0f}"
                elif credits_required >= 10:
                    elasticity = -1.2
                    optimal_range = f"{max(min_price, current_price * 0.8):.0f}-{current_price * 1.2:.0f}"
                else:
                    elasticity = -0.8
                    optimal_range = f"{max(min_price, current_price * 0.75):.0f}-{current_price * 1.15:.0f}"
                
                elasticity_data[service_name] = {
                    "current_price": current_price,
                    "elasticity": elasticity,
                    "optimal_range": optimal_range,
                    "credits_required": credits_required,
                    "actual_cost": estimated_cost,
                    "min_profitable_price": min_price,
                    "profit_margin": ((current_price - estimated_cost) / estimated_cost) * 100,
                    "total_sessions": 0,
                    "unique_users": 0,
                    "avg_duration_minutes": credits_required / 2,
                    "total_revenue": 0,
                    "completion_rate": 0,
                    "repeat_rate": 0,
                    "avg_sessions_per_user": 0,
                    "avg_days_between_sessions": 30,
                    "price_increase_acceptance": 0,
                    "price_decrease_impact": 0,
                    "actual_avg_price": current_price,
                    "price_variance": 0,
                    "market_demand": "unknown",
                    "user_loyalty": "unknown",
                    "price_sensitivity": "unknown"
                }
            
            return elasticity_data
            
        except Exception as e:
            logger.error(f"Fallback elasticity analysis failed: {e}")
            return {
                "quick_blessing": {"current_price": 5, "elasticity": -0.8, "optimal_range": "4-7"},
                "spiritual_guidance": {"current_price": 15, "elasticity": -1.2, "optimal_range": "12-18"},
                "premium_consultation": {"current_price": 50, "elasticity": -0.6, "optimal_range": "45-65"},
                "elite_session": {"current_price": 100, "elasticity": -0.4, "optimal_range": "90-120"}
            }
    
    async def _generate_ai_recommendations(
        self, 
        analytics: Dict, 
        user_behavior: Dict, 
        elasticity: Dict,
        pricing_config: Dict = None
    ) -> List[Dict]:
        """তমিল - AI সুপারিশ তৈরি করুন"""
        try:
            recommendation_prompt = f"""
            Analyze JyotiFlow.ai spiritual platform data and provide specific recommendations:
            
            Revenue Analytics: {json.dumps(analytics, indent=2)}
            User Behavior: {json.dumps(user_behavior, indent=2)}
            Price Elasticity: {json.dumps(elasticity, indent=2)}
            Pricing Configuration: {json.dumps(pricing_config, indent=2)}
            
            Current Pricing Parameters:
            - Minimum Profit Margin: {pricing_config.get('min_profit_margin_percent', 250)}%
            - Video Cost per Minute: ${pricing_config.get('video_cost_per_minute', 0.70)}
            - Cost Protection: {pricing_config.get('cost_protection_enabled', True)}
            
            Provide 5 specific, actionable recommendations with:
            1. Recommendation title
            2. Detailed description
            3. Expected revenue impact (USD amount)
            4. Implementation difficulty (1-5)
            5. Timeline for results (weeks)
            
            Focus on sustainable growth, user satisfaction, and maintaining minimum profit margins.
            Consider the current pricing configuration when making recommendations.
            Format as JSON array with keys: title, description, expected_revenue_impact, implementation_difficulty, timeline_weeks
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": recommendation_prompt}],
                max_tokens=1200,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {e}")
            return []

    async def _calculate_impact_projection(self, recommendations: List[Dict]) -> Dict:
        """তমিল - பரிந்துரைகளின் தாக்கத்தை கணிக்கவும்"""
        try:
            total_impact = 0
            impact_breakdown = {}
            
            for rec in recommendations:
                if isinstance(rec, dict) and 'expected_revenue_impact' in rec:
                    impact = rec.get('expected_revenue_impact', 0)
                    total_impact += impact
                    impact_breakdown[rec.get('title', 'Unknown')] = impact
            
            return {
                "total_projected_revenue_increase": total_impact,
                "impact_breakdown": impact_breakdown,
                "confidence_level": "medium",
                "timeframe_months": 6
            }
        except Exception as e:
            logger.error(f"Impact projection calculation failed: {e}")
            return {
                "total_projected_revenue_increase": 0,
                "impact_breakdown": {},
                "confidence_level": "low",
                "timeframe_months": 6
            }

    def _prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """তমিল - பரிந்துரைகளை முன்னுரிமைப்படுத்தவும்"""
        try:
            if not recommendations:
                return []
            
            # Score each recommendation based on impact and difficulty
            scored_recommendations = []
            for rec in recommendations:
                if isinstance(rec, dict):
                    impact_score = rec.get('expected_revenue_impact', 0) / 1000  # Normalize
                    difficulty = rec.get('implementation_difficulty', 3)
                    difficulty_score = (6 - difficulty) / 5  # Lower difficulty = higher score
                    
                    priority_score = (impact_score * 0.7) + (difficulty_score * 0.3)
                    
                    scored_recommendations.append({
                        **rec,
                        "priority_score": priority_score,
                        "priority_level": "high" if priority_score > 0.7 else "medium" if priority_score > 0.4 else "low"
                    })
            
            # Sort by priority score (highest first)
            scored_recommendations.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
            
            return scored_recommendations
            
        except Exception as e:
            logger.error(f"Recommendation prioritization failed: {e}")
            return recommendations

    async def _get_pricing_config_data(self) -> Dict:
        """তমিল - விலை கட்டமைப்பு தரவைப் பெறவும்"""
        try:
            # Read from pricing_config table
            config_rows = await self.db.fetch("""
                SELECT config_key, config_value, config_type, description 
                FROM pricing_config 
                WHERE is_active = true
                ORDER BY config_key
            """)
            
            config_data = {}
            for row in config_rows:
                key = row['config_key']
                value = row['config_value']
                config_type = row['config_type']
                
                # Parse value based on type
                if config_type == 'number':
                    try:
                        config_data[key] = float(value)
                    except:
                        config_data[key] = value
                elif config_type == 'boolean':
                    config_data[key] = value.lower() == 'true'
                elif config_type == 'json':
                    try:
                        config_data[key] = json.loads(value)
                    except:
                        config_data[key] = value
                else:
                    config_data[key] = value
            
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to read pricing config: {e}")
            return {}

    async def _store_ai_recommendations(self, recommendations: List[Dict], recommendation_type: str = "pricing") -> bool:
        """তমিল - AI பரிந்துரைகளை சேமிக்கவும்"""
        try:
            for rec in recommendations:
                if isinstance(rec, dict):
                    await self.db.execute("""
                        INSERT INTO ai_recommendations (
                            recommendation_type, title, description, 
                            expected_revenue_impact, implementation_difficulty, 
                            timeline_weeks, priority_score, priority_level,
                            ai_model_version, confidence_level, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """, 
                    recommendation_type,
                    rec.get('title', ''),
                    rec.get('description', ''),
                    rec.get('expected_revenue_impact', 0),
                    rec.get('implementation_difficulty', 3),
                    rec.get('timeline_weeks', 4),
                    rec.get('priority_score', 0),
                    rec.get('priority_level', 'medium'),
                    'gpt-4',
                    rec.get('confidence_level', 0.7),
                    json.dumps(rec.get('metadata', {}))
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store AI recommendations: {e}")
            return False

    async def _cache_ai_insights(self, insight_type: str, data: Dict, expires_hours: int = 24) -> bool:
        """তমিল - AI நுண்ணறிவை கேஷ் செய்யவும்"""
        try:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            await self.db.execute("""
                INSERT INTO ai_insights_cache (insight_type, data, expires_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (insight_type) 
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    expires_at = EXCLUDED.expires_at,
                    generated_at = NOW()
            """, insight_type, json.dumps(data), expires_at)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache AI insights: {e}")
            return False

    async def _store_ai_pricing_recommendations(self, recommendations: List[Dict]) -> bool:
        """Store AI pricing recommendations in the new ai_pricing_recommendations table"""
        try:
            for rec in recommendations:
                if isinstance(rec, dict):
                    # Extract pricing-specific data
                    recommendation_type = rec.get('type', 'service_price')
                    current_value = rec.get('current_value', 0)
                    suggested_value = rec.get('suggested_value', 0)
                    expected_impact = rec.get('expected_revenue_impact', 0)
                    confidence_level = rec.get('confidence_level', 0.7)
                    reasoning = rec.get('reasoning', rec.get('description', ''))
                    implementation_difficulty = rec.get('implementation_difficulty', 3)
                    priority_level = rec.get('priority_level', 'medium')
                    service_name = rec.get('service_name', '')
                    
                    # Store in ai_pricing_recommendations table
                    await self.db.execute("""
                        INSERT INTO ai_pricing_recommendations (
                            recommendation_type, current_value, suggested_value, expected_impact,
                            confidence_level, reasoning, implementation_difficulty, priority_level,
                            service_name, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """, 
                    recommendation_type,
                    current_value,
                    suggested_value,
                    expected_impact,
                    confidence_level,
                    reasoning,
                    implementation_difficulty,
                    priority_level,
                    service_name,
                    json.dumps(rec.get('metadata', {}))
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store AI pricing recommendations: {e}")
            return False

    async def _generate_pricing_specific_recommendations(self, elasticity_data: Dict, pricing_config: Dict) -> List[Dict]:
        """Generate specific pricing recommendations based on real usage data analysis"""
        try:
            recommendations = []
            
            # Get real usage data for more accurate recommendations
            usage_data = await self._get_real_usage_analytics()
            
            # Generate service price recommendations based on real data
            for service_name, data in elasticity_data.items():
                current_price = data.get('current_price', 0)
                elasticity = data.get('elasticity', -0.8)
                total_sessions = data.get('total_sessions', 0)
                market_demand = data.get('market_demand', 'low')
                
                # Get real usage metrics for this service
                service_usage = usage_data.get(service_name, {})
                completion_rate = service_usage.get('completion_rate', 0.7)
                avg_session_duration = service_usage.get('avg_duration', 15)
                user_satisfaction = service_usage.get('satisfaction_score', 0.8)
                revenue_per_session = service_usage.get('revenue_per_session', current_price)
                
                # Enhanced reasoning based on real data
                reasoning_parts = []
                
                # Calculate suggested price based on elasticity and real usage
                if abs(elasticity) < 0.5:  # Low sensitivity - can increase price
                    suggested_price = current_price * 1.1  # 10% increase
                    reasoning_parts.append(f"{service_name}க்கான விலையை 10% அதிகரிக்கலாம்.")
                    reasoning_parts.append(f"விலை நெகிழ்வுத்தன்மை குறைவாக உள்ளது ({elasticity:.2f}).")
                elif abs(elasticity) > 1.0:  # High sensitivity - should decrease price
                    suggested_price = current_price * 0.9  # 10% decrease
                    reasoning_parts.append(f"{service_name}க்கான விலையை 10% குறைக்கலாம்.")
                    reasoning_parts.append(f"விலை நெகிழ்வுத்தன்மை அதிகமாக உள்ளது ({elasticity:.2f}).")
                else:  # Medium sensitivity - small adjustment
                    if market_demand == 'high' and completion_rate > 0.8:
                        suggested_price = current_price * 1.05  # 5% increase
                        reasoning_parts.append(f"{service_name}க்கான விலையை 5% அதிகரிக்கலாம்.")
                        reasoning_parts.append(f"சந்தை தேவை அதிகமாக உள்ளது மற்றும் முடிவு விகிதம் {completion_rate:.1%}.")
                    else:
                        suggested_price = current_price * 0.95  # 5% decrease
                        reasoning_parts.append(f"{service_name}க்கான விலையை 5% குறைக்கலாம்.")
                        reasoning_parts.append(f"சந்தை தேவையை அதிகரிக்க வேண்டும்.")
                
                # Add real usage insights
                if completion_rate < 0.6:
                    reasoning_parts.append(f"முடிவு விகிதம் குறைவாக உள்ளது ({completion_rate:.1%}).")
                elif completion_rate > 0.9:
                    reasoning_parts.append(f"முடிவு விகிதம் சிறப்பாக உள்ளது ({completion_rate:.1%}).")
                
                if user_satisfaction < 0.7:
                    reasoning_parts.append(f"பயனர் திருப்தி குறைவாக உள்ளது ({user_satisfaction:.1%}).")
                elif user_satisfaction > 0.9:
                    reasoning_parts.append(f"பயனர் திருப்தி சிறப்பாக உள்ளது ({user_satisfaction:.1%}).")
                
                # Calculate expected impact based on real data
                price_change_percent = ((suggested_price - current_price) / current_price) * 100
                sessions_per_month = total_sessions / 12  # Assuming yearly data
                expected_impact = sessions_per_month * abs(price_change_percent) * revenue_per_session * 0.1
                
                # Adjust confidence based on data quality
                confidence_factors = []
                if total_sessions > 100:
                    confidence_factors.append(0.2)
                if completion_rate > 0.7:
                    confidence_factors.append(0.15)
                if user_satisfaction > 0.8:
                    confidence_factors.append(0.1)
                
                confidence_level = 0.6 + sum(confidence_factors)
                confidence_level = min(confidence_level, 0.95)  # Cap at 95%
                
                recommendations.append({
                    'type': 'service_price',
                    'current_value': current_price,
                    'suggested_value': suggested_price,
                    'expected_revenue_impact': expected_impact,
                    'confidence_level': confidence_level,
                    'reasoning': ' '.join(reasoning_parts),
                    'implementation_difficulty': 1,  # Easy to change service prices
                    'priority_level': 'high' if abs(price_change_percent) > 10 else 'medium',
                    'service_name': service_name,
                    'metadata': {
                        'elasticity': elasticity,
                        'total_sessions': total_sessions,
                        'market_demand': market_demand,
                        'price_change_percent': price_change_percent,
                        'completion_rate': completion_rate,
                        'user_satisfaction': user_satisfaction,
                        'avg_session_duration': avg_session_duration,
                        'revenue_per_session': revenue_per_session,
                        'data_quality': 'high' if total_sessions > 100 else 'medium'
                    }
                })
            
            # Generate credit package recommendations
            credit_packages = await self.db.fetch("""
                SELECT name, credits_amount, price_usd, bonus_credits
                FROM credit_packages 
                WHERE enabled = TRUE
                ORDER BY credits_amount ASC
            """)
            
            for package in credit_packages:
                current_price = float(package['price_usd'])
                credits = package['credits_amount']
                bonus = package['bonus_credits']
                total_credits = credits + bonus
                
                # Calculate value per credit
                value_per_credit = current_price / total_credits
                
                # Suggest optimization based on value
                if value_per_credit > 2.5:  # Expensive
                    suggested_price = current_price * 0.9  # 10% discount
                    reasoning = f"{package['name']} தொகுப்பின் விலையை 10% குறைப்பதன் மூலம் சிறந்த மதிப்பு வழங்கலாம்."
                elif value_per_credit < 1.5:  # Very cheap
                    suggested_price = current_price * 1.05  # 5% increase
                    reasoning = f"{package['name']} தொகுப்பின் விலையை 5% அதிகரிப்பதன் மூலம் வருவாயை அதிகரிக்கலாம்."
                else:
                    continue  # Good value, no change needed
                
                expected_impact = 5000  # Base impact for credit packages
                
                recommendations.append({
                    'type': 'credit_package',
                    'current_value': current_price,
                    'suggested_value': suggested_price,
                    'expected_revenue_impact': expected_impact,
                    'confidence_level': 0.75,
                    'reasoning': reasoning,
                    'implementation_difficulty': 2,
                    'priority_level': 'medium',
                    'service_name': package['name'],
                    'metadata': {
                        'credits_amount': credits,
                        'bonus_credits': bonus,
                        'value_per_credit': value_per_credit
                    }
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate pricing-specific recommendations: {e}")
            return []

    async def get_ai_pricing_recommendations(self, status: str = 'pending') -> List[Dict]:
        """Get AI pricing recommendations from the database"""
        try:
            recommendations = await self.db.fetch("""
                SELECT 
                    id, recommendation_type, current_value, suggested_value, 
                    expected_impact, confidence_level, reasoning, implementation_difficulty,
                    status, priority_level, service_name, metadata, created_at
                FROM ai_pricing_recommendations 
                WHERE status = $1
                ORDER BY priority_level DESC, expected_impact DESC, created_at DESC
            """, status)
            
            return [dict(rec) for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Failed to get AI pricing recommendations: {e}")
            return []

    async def _get_real_usage_analytics(self) -> Dict:
        """Get real usage analytics from database for AI recommendations"""
        try:
            # Get service usage data
            service_usage = await self.db.fetch("""
                SELECT 
                    st.name as service_name,
                    COUNT(s.id) as total_sessions,
                    AVG(EXTRACT(EPOCH FROM (s.end_time - s.start_time))/60) as avg_duration_minutes,
                    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) * 1.0 / COUNT(s.id) as completion_rate,
                    AVG(s.user_rating) as avg_rating,
                    AVG(s.credits_used * st.price_usd) as avg_revenue_per_session
                FROM service_types st
                LEFT JOIN sessions s ON st.name = s.service_type
                WHERE st.enabled = TRUE
                AND s.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY st.name, st.id
                HAVING COUNT(s.id) > 0
            """)
            
            # Get user satisfaction data
            satisfaction_data = await self.db.fetch("""
                SELECT 
                    service_type,
                    AVG(user_rating) as satisfaction_score,
                    COUNT(*) as rating_count
                FROM sessions 
                WHERE user_rating IS NOT NULL
                AND created_at >= NOW() - INTERVAL '90 days'
                GROUP BY service_type
            """)
            
            # Get credit usage patterns
            credit_usage = await self.db.fetch("""
                SELECT 
                    service_type,
                    AVG(credits_used) as avg_credits,
                    SUM(credits_used) as total_credits_used,
                    COUNT(*) as session_count
                FROM sessions 
                WHERE created_at >= NOW() - INTERVAL '90 days'
                GROUP BY service_type
            """)
            
            # Combine data into service-specific analytics
            usage_analytics = {}
            
            for service in service_usage:
                service_name = service['service_name']
                usage_analytics[service_name] = {
                    'total_sessions': service['total_sessions'],
                    'avg_duration': service['avg_duration_minutes'] or 15,
                    'completion_rate': service['completion_rate'] or 0.7,
                    'avg_rating': service['avg_rating'] or 4.0,
                    'revenue_per_session': service['avg_revenue_per_session'] or 0,
                    'satisfaction_score': 0.8,  # Default
                    'avg_credits': 0,
                    'total_credits_used': 0
                }
            
            # Add satisfaction scores
            for sat in satisfaction_data:
                service_name = sat['service_type']
                if service_name in usage_analytics:
                    usage_analytics[service_name]['satisfaction_score'] = (sat['satisfaction_score'] or 4.0) / 5.0
            
            # Add credit usage
            for credit in credit_usage:
                service_name = credit['service_type']
                if service_name in usage_analytics:
                    usage_analytics[service_name]['avg_credits'] = credit['avg_credits'] or 0
                    usage_analytics[service_name]['total_credits_used'] = credit['total_credits_used'] or 0
            
            # Add market demand indicators
            for service_name, data in usage_analytics.items():
                # Calculate market demand based on usage patterns
                sessions_per_day = data['total_sessions'] / 90  # 90 days
                if sessions_per_day > 5:
                    data['market_demand'] = 'high'
                elif sessions_per_day > 2:
                    data['market_demand'] = 'medium'
                else:
                    data['market_demand'] = 'low'
                
                # Calculate growth rate (if we have historical data)
                data['growth_rate'] = 0.1  # Default 10% growth
                
                # Calculate user engagement score
                engagement_score = (
                    data['completion_rate'] * 0.4 +
                    data['satisfaction_score'] * 0.3 +
                    (data['avg_duration'] / 30) * 0.3  # Normalize to 30 minutes
                )
                data['engagement_score'] = min(engagement_score, 1.0)
            
            return usage_analytics
            
        except Exception as e:
            logger.error(f"Failed to get real usage analytics: {e}")
            # Return default data structure
            return {
                'தொட்டக்க தொகுப்பு': {
                    'total_sessions': 150,
                    'avg_duration': 12,
                    'completion_rate': 0.85,
                    'satisfaction_score': 0.88,
                    'revenue_per_session': 29.0,
                    'market_demand': 'high',
                    'growth_rate': 0.15,
                    'engagement_score': 0.82
                },
                'பிரபல தொகுப்பு': {
                    'total_sessions': 89,
                    'avg_duration': 18,
                    'completion_rate': 0.92,
                    'satisfaction_score': 0.91,
                    'revenue_per_session': 79.0,
                    'market_demand': 'medium',
                    'growth_rate': 0.08,
                    'engagement_score': 0.89
                },
                'மாஸ்டர் தொகுப்பு': {
                    'total_sessions': 45,
                    'avg_duration': 25,
                    'completion_rate': 0.78,
                    'satisfaction_score': 0.85,
                    'revenue_per_session': 149.0,
                    'market_demand': 'low',
                    'growth_rate': 0.05,
                    'engagement_score': 0.76
                }
            }

# Export all classes
__all__ = [
    "SERVICE_NAME_MAPPING",
    "get_service_by_name",
    "get_all_enabled_services", 
    "SpiritualAvatarEngine", 
    "MonetizationOptimizer", 
    "SatsangManager",
    "SocialContentEngine",
    "EnhancedSessionProcessor",
    "SpiritualState",
    "SessionIntensity", 
    "AvatarEmotion"
]