"""
Knowledge Seeding System for JyotiFlow RAG Database
Populates the knowledge base with authentic spiritual and astrological wisdom
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Try to import OpenAI, fallback gracefully
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Default embedding dimension for spiritual knowledge vectors
DEFAULT_EMBED_DIM = 1536

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_embedding_for_storage(embedding, vector_support: bool = True) -> any:
    """
    Convert embedding to appropriate format for database storage.
    
    SPIRITUAL CONTENT CRITICAL: Ensures authentic spiritual wisdom embeddings
    are stored correctly for RAG-based spiritual guidance responses.
    
    Args:
        embedding: The embedding data (str, list, or other)
        vector_support: True if pgvector is available, False for JSON storage
        
    Returns:
        Properly formatted embedding for the target storage type
    """
    if vector_support:
        # For pgvector/FLOAT[], we need list format for spiritual knowledge vectors
        if isinstance(embedding, str):
            try:
                # If it's a JSON string, parse it to get the list
                parsed_embedding = json.loads(embedding)
                if not isinstance(parsed_embedding, list):
                    logger.warning("🕉️ Spiritual knowledge embedding not in list format, creating default")
                    return [0.0] * DEFAULT_EMBED_DIM
                
                # Coerce each element to float and validate
                try:
                    float_embedding = [float(x) for x in parsed_embedding]
                    # Resize to DEFAULT_EMBED_DIM (truncate if longer, pad if shorter)
                    if len(float_embedding) > DEFAULT_EMBED_DIM:
                        float_embedding = float_embedding[:DEFAULT_EMBED_DIM]
                        logger.warning(f"🕉️ Spiritual knowledge embedding truncated from {len(parsed_embedding)} to {DEFAULT_EMBED_DIM}")
                    elif len(float_embedding) < DEFAULT_EMBED_DIM:
                        float_embedding.extend([0.0] * (DEFAULT_EMBED_DIM - len(float_embedding)))
                        logger.warning(f"🕉️ Spiritual knowledge embedding padded from {len(parsed_embedding)} to {DEFAULT_EMBED_DIM}")
                    
                    return float_embedding
                except (ValueError, TypeError) as e:
                    logger.warning(f"🕉️ Cannot convert spiritual knowledge embedding elements to float: {e}, using default")
                    return [0.0] * DEFAULT_EMBED_DIM
                    
            except json.JSONDecodeError:
                # If it's not valid JSON, create a default vector for spiritual content
                logger.warning("🕉️ Invalid spiritual knowledge embedding JSON, using default vector")
                return [0.0] * DEFAULT_EMBED_DIM
        elif isinstance(embedding, list):
            # If it's already a list (like from OpenAI), validate and coerce to float
            if len(embedding) > 0 and all(isinstance(x, (int, float)) for x in embedding):
                try:
                    float_embedding = [float(x) for x in embedding]
                    # Resize to DEFAULT_EMBED_DIM (truncate if longer, pad if shorter)
                    if len(float_embedding) > DEFAULT_EMBED_DIM:
                        float_embedding = float_embedding[:DEFAULT_EMBED_DIM]
                        logger.warning(f"🕉️ Spiritual knowledge embedding truncated from {len(embedding)} to {DEFAULT_EMBED_DIM}")
                    elif len(float_embedding) < DEFAULT_EMBED_DIM:
                        float_embedding.extend([0.0] * (DEFAULT_EMBED_DIM - len(float_embedding)))
                        logger.warning(f"🕉️ Spiritual knowledge embedding padded from {len(embedding)} to {DEFAULT_EMBED_DIM}")
                    
                    return float_embedding
                except (ValueError, TypeError) as e:
                    logger.warning(f"🕉️ Cannot convert spiritual knowledge embedding list elements to float: {e}, using default")
                    return [0.0] * DEFAULT_EMBED_DIM
            else:
                logger.warning("🕉️ Invalid spiritual knowledge embedding list, using default")
                return [0.0] * DEFAULT_EMBED_DIM
        else:
            # For other types, create default vector
            logger.warning("🕉️ Unknown spiritual knowledge embedding type, using default")
            return [0.0] * DEFAULT_EMBED_DIM
    else:
        # For non-pgvector, use JSON string format
        if isinstance(embedding, str):
            try:
                # If it's already a JSON string, parse and re-serialize to ensure consistency
                parsed_embedding = json.loads(embedding)
                return json.dumps(parsed_embedding)
            except json.JSONDecodeError:
                # If it's not valid JSON, keep as is but log for spiritual content
                logger.warning("🕉️ Spiritual knowledge embedding not valid JSON, storing as-is")
                return embedding
        else:
            # If it's a list, serialize to JSON string
            return json.dumps(embedding)


class KnowledgeSeeder:
    """
    Comprehensive knowledge seeding system
    """
    
    def __init__(self, database_pool, openai_api_key: str):
        self.db_pool = database_pool
        self.openai_client = AsyncOpenAI(api_key=openai_api_key) if OPENAI_AVAILABLE else None
        
        # Log initialization status
        logger.info(f"KnowledgeSeeder initialized with:")
        logger.info(f"  - Database pool: {'✅ Available' if database_pool else '❌ None'}")
        logger.info(f"  - OpenAI available: {'✅ Yes' if OPENAI_AVAILABLE else '❌ No'}")
        logger.info(f"  - OpenAI client: {'✅ Initialized' if self.openai_client else '❌ None'}")
        logger.info(f"  - API key: {'✅ Provided' if openai_api_key and openai_api_key != 'fallback_key' else '❌ Fallback'}")
        
    async def seed_complete_knowledge_base(self):
        """Main seeding process for complete knowledge base with robust connection handling"""
        try:
            logger.info("Starting comprehensive knowledge base seeding...")
            
            # Validate database connection first with timeout
            if self.db_pool:
                try:
                    # Use proper async context manager for connection acquisition
                    async with self.db_pool.acquire() as conn:
                            # Check if table exists with timeout
                            table_exists = await asyncio.wait_for(
                                conn.fetchval("""
                                    SELECT EXISTS (
                                        SELECT FROM information_schema.tables 
                                        WHERE table_name = 'rag_knowledge_base'
                                    )
                                """),
                                timeout=10.0
                            )
                            if not table_exists:
                                logger.error("❌ rag_knowledge_base table does not exist")
                                raise Exception("Database table 'rag_knowledge_base' not found")
                            
                            # Check if content_type column exists with timeout
                            content_type_exists = await asyncio.wait_for(
                                conn.fetchval("""
                                    SELECT EXISTS (
                                        SELECT FROM information_schema.columns 
                                        WHERE table_name = 'rag_knowledge_base' 
                                        AND column_name = 'content_type'
                                    )
                                """),
                                timeout=10.0
                            )
                            
                            if not content_type_exists:
                                logger.warning("⚠️ content_type column missing, adding it...")
                                await asyncio.wait_for(
                                    conn.execute("""
                                        ALTER TABLE rag_knowledge_base 
                                        ADD COLUMN content_type VARCHAR(50) NOT NULL DEFAULT 'knowledge'
                                    """),
                                    timeout=30.0
                                )
                                logger.info("✅ content_type column added to rag_knowledge_base")
                            
                            logger.info("✅ Database table validated successfully")
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Database connection timed out during validation, proceeding with fallback seeding")
                except Exception as e:
                    logger.error(f"❌ Database validation failed: {e}, proceeding with fallback seeding")
            
            # Test OpenAI API if available
            if self.openai_client and OPENAI_AVAILABLE:
                try:
                    logger.info("Testing OpenAI API connection...")
                    test_response = await self.openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input="test"
                    )
                    logger.info("✅ OpenAI API test successful")
                except Exception as api_error:
                    logger.warning(f"OpenAI API test failed: {api_error}")
                    logger.warning("Will use fallback embeddings for all knowledge pieces")
            
            # Seed classical astrology knowledge
            await self._seed_classical_astrology_knowledge()
            
            # Seed Tamil spiritual literature
            await self._seed_tamil_spiritual_knowledge()
            
            # Seed relationship astrology
            await self._seed_relationship_astrology()
            
            # Seed career astrology
            await self._seed_career_astrology()
            
            # Seed health astrology
            await self._seed_health_astrology()
            
            # Seed remedial measures
            await self._seed_remedial_measures()
            
            # Seed world knowledge integration
            await self._seed_world_knowledge()
            
            # Seed psychological integration
            await self._seed_psychological_integration()
            
            logger.info("Knowledge base seeding completed successfully!")
            
        except Exception as e:
            import traceback
            logger.error(f"Knowledge seeding error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def _seed_classical_astrology_knowledge(self):
        """Seed classical Vedic astrology knowledge"""
        classical_knowledge = [
            {
                "title": "Brihat Parasara Hora Shastra - Planetary Strength Analysis",
                "content": "The classical text Brihat Parasara Hora Shastra establishes that planetary strength (Shadbala) consists of six components: Sthanabala (positional strength), Digbala (directional strength), Kaalabala (temporal strength), Chestabala (motional strength), Naisargikabala (natural strength), and Drikbala (aspectual strength). A planet with high Shadbala indicates strong results in its significations. When analyzing birth charts, planets with Shadbala above 5 Rupas are considered strong enough to deliver positive results during their dashas and transits.",
                "knowledge_domain": "classical_astrology",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "vedic_tradition",
                "tags": ["shadbala", "planetary_strength", "brihat_parasara", "hora_shastra"],
                "source_reference": "Brihat Parasara Hora Shastra, Chapter 27-28"
            },
            {
                "title": "Nakshatra Analysis for Life Predictions",
                "content": "Each of the 27 Nakshatras represents specific life themes and karmic patterns. Ashwini nakshatra natives possess pioneering spirit and healing abilities. Bharani represents transformation and bearing responsibilities. Krittika indicates sharp intellect and purification. The ruling deity, symbol, and planetary lord of each nakshatra provide deep insights into personality traits, life purpose, and spiritual evolution. The Nakshatra of the Moon at birth (Janma Nakshatra) is particularly significant for personality analysis and compatibility assessment.",
                "knowledge_domain": "classical_astrology",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "vedic_tradition",
                "tags": ["nakshatra", "life_predictions", "personality", "moon_nakshatra"],
                "source_reference": "Classical Nakshatra Texts and Jyotish Commentaries"
            },
            {
                "title": "Dasha System - Timing of Life Events",
                "content": "The Vimshottari Dasha system divides a 120-year life cycle among nine planets based on the Moon's nakshatra at birth. Each planet's dasha period brings events related to its significations and house positions. Mahadasha (major period) sets the overall theme, while Antardasha (sub-period) provides specific timing. The interaction between Dasha lord and Antardasha lord determines the nature of events. Strong planets in favorable houses give positive results during their periods, while weak or afflicted planets may cause challenges that serve as learning experiences.",
                "knowledge_domain": "classical_astrology",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "vedic_tradition",
                "tags": ["dasha", "timing", "vimshottari", "life_events"],
                "source_reference": "Brihat Parasara Hora Shastra, Dasha Adhyaya"
            },
            {
                "title": "House Significance in Vedic Astrology",
                "content": "The twelve houses represent different life areas: 1st house (self, personality), 2nd house (wealth, family), 3rd house (courage, siblings), 4th house (home, mother), 5th house (children, creativity), 6th house (health, service), 7th house (partnerships, marriage), 8th house (transformation, longevity), 9th house (dharma, higher learning), 10th house (career, reputation), 11th house (gains, social circle), 12th house (spirituality, liberation). The strength of house lords and planets placed in houses determines the quality of experiences in each life area.",
                "knowledge_domain": "classical_astrology",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "vedic_tradition",
                "tags": ["houses", "life_areas", "house_lords", "chart_analysis"],
                "source_reference": "Phaladeepika and Jataka Parijata"
            },
            {
                "title": "Yogas in Vedic Astrology - Special Combinations",
                "content": "Planetary yogas are special combinations that create specific results. Raj Yogas (formed by lords of kendra and trikona houses) indicate power and status. Dhana Yogas (wealth combinations) show financial prosperity. Gaja Kesari Yoga (Moon-Jupiter combination) grants wisdom and respect. Panch Mahapurusha Yogas (formed by strong benefics in specific positions) create exceptional personalities. The presence and strength of yogas must be carefully analyzed considering the overall chart strength and planetary periods for accurate predictions.",
                "knowledge_domain": "classical_astrology",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "vedic_tradition",
                "tags": ["yogas", "combinations", "raj_yoga", "dhana_yoga"],
                "source_reference": "Saravali and Hora Ratna"
            }
        ]
        
        for knowledge in classical_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_tamil_spiritual_knowledge(self):
        """Seed Tamil spiritual literature and wisdom"""
        tamil_knowledge = [
            {
                "title": "Thirukkural on Dharmic Living",
                "content": "Thiruvalluvar's Thirukkural emphasizes that dharmic living is the foundation of all success. 'அறத்தினூஉங்கு ஆக்கமும் இல்லை அதனின் ஊங்கில்லை ஊக்கமும் இல்லை' - There is no greater wealth than dharma, and no greater strength than righteous action. This applies to astrological guidance where planetary influences work best when aligned with dharmic principles. Even challenging planetary periods become opportunities for growth when faced with righteous intent and actions.",
                "knowledge_domain": "tamil_spiritual_literature",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "tamil_tradition",
                "tags": ["thirukkural", "dharma", "righteous_living", "tamil_wisdom"],
                "source_reference": "Thirukkural, Arathupaal"
            },
            {
                "title": "Devotional Path in Tamil Tradition",
                "content": "The Tamil Saiva and Vaishnava traditions emphasize that devotion (bhakti) transcends astrological influences. The Nayanmars and Alvars demonstrated that pure devotion can overcome even the most challenging planetary periods. 'பத்தியில் செய்யும் நற்கர்மம் பார்க்க தரும் உத்தமம்' - Good deeds performed with devotion yield the highest results. This principle guides spiritual remedies in Tamil astrology, where mantra, temple worship, and service to others are prescribed based on planetary positions.",
                "knowledge_domain": "tamil_spiritual_literature",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "tamil_tradition",
                "tags": ["devotion", "bhakti", "nayanmars", "alvars", "spiritual_remedies"],
                "source_reference": "Thevaram and Nalayira Divya Prabandham"
            },
            {
                "title": "Tamil Concept of Cosmic Order",
                "content": "Ancient Tamil literature speaks of 'Aram, Porul, Inbam, Veedu' - the four life goals of Dharma, Wealth, Pleasure, and Liberation. This corresponds to the Vedic Purusharthas but with Tamil cultural nuances. Astrological analysis in Tamil tradition considers how planetary influences support or challenge progress in these four areas. The ultimate goal is 'Veedu' (liberation), which can be achieved through proper understanding and alignment with cosmic rhythms as revealed through Jyotish.",
                "knowledge_domain": "tamil_spiritual_literature",
                "content_type": "classical_text",
                "authority_level": 5,
                "cultural_context": "tamil_tradition",
                "tags": ["purushartha", "life_goals", "cosmic_order", "liberation"],
                "source_reference": "Tolkappiyam and Sangam Literature"
            }
        ]
        
        for knowledge in tamil_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_relationship_astrology(self):
        """Seed relationship and marriage astrology knowledge"""
        relationship_knowledge = [
            {
                "title": "Venus and 7th House Analysis for Love Relationships",
                "content": "Venus represents love, attraction, and partnership harmony. Its placement by sign, house, and aspects determines relationship patterns. Strong Venus in benefic houses (1, 4, 5, 7, 9, 10) indicates harmonious relationships. Venus in water signs (Cancer, Scorpio, Pisces) brings emotional depth. Venus-Mars aspects create passion and attraction. The 7th house lord's position shows partner characteristics and relationship timing. Benefic planets aspecting the 7th house bless the native with supportive partnerships.",
                "knowledge_domain": "relationship_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "universal",
                "tags": ["venus", "7th_house", "love", "relationships", "partnership"],
                "source_reference": "Hora Shastra Relationship Principles"
            },
            {
                "title": "Compatibility Analysis through Ashtakoot Matching",
                "content": "Ashtakoot (eight-fold) compatibility analysis examines Varna (spiritual compatibility), Vashya (mutual attraction), Tara (health and well-being), Yoni (sexual compatibility), Graha Maitri (planetary friendship), Gana (temperament), Rashi (emotional harmony), and Nadi (genetic compatibility). A minimum of 18 out of 36 points indicates basic compatibility. However, individual chart analysis is more important than just point-based matching. Strong Venus and 7th house in both charts, along with harmonious Moon positions, create lasting relationships.",
                "knowledge_domain": "relationship_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["ashtakoot", "compatibility", "marriage_matching", "relationship_harmony"],
                "source_reference": "Vivah Muhurta Texts"
            },
            {
                "title": "Timing of Marriage through Dasha Analysis",
                "content": "Marriage timing is determined by analyzing Venus dasha/antardasha, 7th house lord periods, and supportive transits. Jupiter's transit over the 7th house or its lord often coincides with marriage. The period of strongest benefic influencing the 7th house typically brings partnership opportunities. For women, Jupiter's influence is particularly important as it represents the husband. Rahu-Ketu axis affecting the 7th house can cause delays but ultimately leads to destined partnerships. The 2nd and 11th houses also influence marriage timing as they represent family expansion.",
                "knowledge_domain": "relationship_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["marriage_timing", "dasha", "jupiter_transit", "7th_house"],
                "source_reference": "Predictive Astrology Texts"
            },
            {
                "title": "Remedies for Relationship Challenges",
                "content": "Relationship challenges often arise from Venus affliction or 7th house malefic influences. Remedies include Venus mantras ('Om Shukraya Namaha'), Friday fasting, wearing white clothes, and offering white flowers to deities. For 7th house afflictions, worship of Shiva-Parvati or Lakshmi-Narayana is recommended. Charity to couples, feeding cows, and supporting marriages of deserving couples create positive karma. Gemstone remedies include wearing diamond or white sapphire for Venus strength, and pearl for Moon if emotional harmony is needed.",
                "knowledge_domain": "relationship_astrology",
                "content_type": "remedial_measures",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["relationship_remedies", "venus_remedies", "marriage_harmony", "gemstones"],
                "source_reference": "Lal Kitab and Remedial Astrology"
            }
        ]
        
        for knowledge in relationship_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_career_astrology(self):
        """Seed career and professional success knowledge"""
        career_knowledge = [
            {
                "title": "10th House and Career Success Analysis",
                "content": "The 10th house represents career, reputation, and public image. Its lord's placement indicates career direction and success potential. Strong 10th house lord in benefic houses (1, 4, 5, 7, 9, 11) grants career success. The 10th house lord in own sign or exaltation creates 'Swa-Graha' yoga, indicating authority and recognition. Planets in the 10th house show career nature: Sun (government, leadership), Moon (public service, hospitality), Mars (engineering, defense), Mercury (communication, commerce), Jupiter (teaching, consulting), Venus (arts, luxury), Saturn (service, persistence), Rahu (foreign connections, technology), Ketu (research, spirituality).",
                "knowledge_domain": "career_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "universal",
                "tags": ["10th_house", "career", "profession", "success", "reputation"],
                "source_reference": "Jataka Parijata Career Principles"
            },
            {
                "title": "Saturn's Role in Career Development",
                "content": "Saturn represents hard work, discipline, and long-term success. Well-placed Saturn creates 'Shasha Yoga' (one of Panch Mahapurusha Yogas), indicating sustained professional achievement. Saturn in the 10th house grants authority through perseverance. Saturn's aspects on the 10th house or its lord demand consistent effort but ultimately reward with lasting success. Saturn dasha/antardasha periods are crucial for career establishment, especially for service-oriented professions. The key is to embrace Saturn's lessons of discipline, patience, and systematic approach to work.",
                "knowledge_domain": "career_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["saturn", "career_development", "discipline", "long_term_success"],
                "source_reference": "Brihat Jataka Saturn Analysis"
            },
            {
                "title": "Entrepreneurship and Business Success Indicators",
                "content": "Entrepreneurial success requires strong Mars (initiative), Mercury (business acumen), and Jupiter (wisdom) in the chart. The 3rd house represents self-effort and courage, while the 11th house shows gains and network support. Mars-Mercury combination creates 'Buddhaditya Yoga' variation, indicating business intelligence. Rahu's positive influence brings innovation and unconventional success. The 2nd house (wealth) and 10th house (reputation) lords should be well-placed for business sustainability. Timing of business launch should consider Mercury and Jupiter dashas, along with favorable transits.",
                "knowledge_domain": "career_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "universal",
                "tags": ["entrepreneurship", "business", "mars_mercury", "innovation", "timing"],
                "source_reference": "Business Astrology Principles"
            },
            {
                "title": "Career Remedies and Success Rituals",
                "content": "Career growth remedies focus on strengthening the 10th house, its lord, and professional significators. Sun remedies (Surya mantras, offering water to Sun, wearing ruby) enhance leadership qualities. Saturn remedies (Shani mantras, Saturday fasting, helping the underprivileged) build long-term success foundation. Mercury remedies (Budh mantras, wearing emerald, knowledge donations) improve communication and business skills. Jupiter remedies (Guru mantras, Thursday worship, teaching others) bring wisdom and good opportunities. The most powerful remedy is excelling in one's current role while maintaining ethical standards.",
                "knowledge_domain": "career_astrology",
                "content_type": "remedial_measures",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["career_remedies", "success_rituals", "planetary_remedies", "professional_growth"],
                "source_reference": "Remedial Astrology for Career"
            }
        ]
        
        for knowledge in career_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_health_astrology(self):
        """Seed health and wellness astrology knowledge"""
        health_knowledge = [
            {
                "title": "6th House and Health Analysis",
                "content": "The 6th house represents health, disease, and healing capacity. A strong 6th house lord indicates good disease resistance and recovery ability. Malefic planets in the 6th house can create health challenges but also provide strength to overcome them. The 6th house lord's placement by sign and house shows health vulnerabilities and healing approaches. Fire signs in the 6th house indicate inflammatory conditions, earth signs show metabolic issues, air signs relate to nervous system, and water signs affect body fluids and emotional health. Aspect patterns to the 6th house reveal timing and nature of health events.",
                "knowledge_domain": "health_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "ayurvedic_tradition",
                "tags": ["6th_house", "health", "disease", "healing", "recovery"],
                "source_reference": "Ayurvedic Astrology Principles"
            },
            {
                "title": "Planetary Influence on Body Systems",
                "content": "Each planet governs specific body systems: Sun (heart, spine, vitality), Moon (mind, stomach, fluids), Mars (blood, muscles, energy), Mercury (nervous system, communication), Jupiter (liver, fat, wisdom), Venus (reproductive system, beauty), Saturn (bones, joints, chronic conditions), Rahu (sudden ailments, toxins), Ketu (spiritual practices, detoxification). Planetary strength and afflictions indicate corresponding body system health. Remedial measures should address both the afflicted planet and its associated body system through appropriate lifestyle, dietary, and spiritual practices.",
                "knowledge_domain": "health_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "ayurvedic_tradition",
                "tags": ["planetary_health", "body_systems", "ayurveda", "holistic_healing"],
                "source_reference": "Ayurvedic Astrology Texts"
            },
            {
                "title": "Healing Remedies and Preventive Measures",
                "content": "Health remedies combine astrological and Ayurvedic principles. Sun afflictions require Surya mantras, early morning sunlight exposure, and heart-strengthening yoga. Moon afflictions need mind-calming practices, proper hydration, and emotional balance. Mars afflictions require cooling foods, anger management, and physical exercise. Mercury afflictions need mental exercises, communication practices, and nervous system support. Jupiter afflictions require liver cleansing, wisdom cultivation, and optimistic thinking. Venus afflictions need reproductive health care, beauty practices, and harmonious relationships. Saturn afflictions require joint care, patience cultivation, and service to others.",
                "knowledge_domain": "health_astrology",
                "content_type": "remedial_measures",
                "authority_level": 4,
                "cultural_context": "ayurvedic_tradition",
                "tags": ["healing_remedies", "preventive_measures", "ayurvedic_remedies", "holistic_health"],
                "source_reference": "Remedial Astrology for Health"
            }
        ]
        
        for knowledge in health_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_remedial_measures(self):
        """Seed comprehensive remedial measures knowledge"""
        remedial_knowledge = [
            {
                "title": "Mantra Therapy for Planetary Healing",
                "content": "Mantra therapy uses sound vibrations to harmonize planetary energies. Each planet has specific mantras: Sun ('Om Hraam Hreem Hroum Sah Suryaya Namaha'), Moon ('Om Shraam Shreem Shroum Sah Chandraya Namaha'), Mars ('Om Angarakaya Namaha'), Mercury ('Om Budhaya Namaha'), Jupiter ('Om Brihaspataye Namaha'), Venus ('Om Shukraya Namaha'), Saturn ('Om Shanecharaya Namaha'), Rahu ('Om Rahave Namaha'), Ketu ('Om Ketave Namaha'). The number of recitations depends on the planet's affliction level and the devotee's capacity. Daily practice during the planet's hora (planetary hour) amplifies the effect.",
                "knowledge_domain": "remedial_measures",
                "content_type": "spiritual_practice",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["mantra_therapy", "planetary_healing", "sound_vibrations", "spiritual_practice"],
                "source_reference": "Mantra Shastra and Remedial Astrology"
            },
            {
                "title": "Gemstone Therapy in Vedic Astrology",
                "content": "Gemstones amplify positive planetary energies when worn correctly. Primary gemstones: Ruby (Sun), Pearl (Moon), Red Coral (Mars), Emerald (Mercury), Yellow Sapphire (Jupiter), Diamond (Venus), Blue Sapphire (Saturn). The gemstone should be natural, untreated, and of appropriate weight (generally 1-5 carats depending on the planet). It should be set in the metal associated with the planet and worn on the specific finger during the prescribed time. Proper purification and energization rituals are essential before wearing. The gemstone should be tested for a probationary period to ensure compatibility.",
                "knowledge_domain": "remedial_measures",
                "content_type": "gemstone_therapy",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["gemstone_therapy", "planetary_energies", "natural_gemstones", "energization"],
                "source_reference": "Ratna Shastra and Gemstone Astrology"
            },
            {
                "title": "Charity and Dana for Karmic Healing",
                "content": "Charitable giving (dana) neutralizes negative karma and strengthens planetary influences. Specific donations for each planet: Sun (wheat, jaggery, copper), Moon (rice, milk, silver), Mars (red lentils, red clothes, land), Mercury (green vegetables, books, education), Jupiter (yellow items, turmeric, gold), Venus (white items, sugar, silver), Saturn (black items, iron, service to the needy), Rahu (blue items, donations to outcasts), Ketu (multi-colored items, spiritual donations). The dana should be given with genuine devotion and without expectation of return. The best time for donation is during the planet's dasha/antardasha or on its specific day.",
                "knowledge_domain": "remedial_measures",
                "content_type": "karmic_healing",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["charity", "dana", "karmic_healing", "planetary_donations"],
                "source_reference": "Dana Shastra and Remedial Astrology"
            },
            {
                "title": "Temple Worship and Deity Connection",
                "content": "Temple worship creates divine connection and planetary harmony. Specific deities for planetary healing: Sun (Surya, Vishnu), Moon (Chandra, Parvati), Mars (Hanuman, Muruga), Mercury (Vishnu, Ganesha), Jupiter (Brihaspati, Vishnu), Venus (Lakshmi, Saraswati), Saturn (Shani, Shiva), Rahu (Durga, Ganesha), Ketu (Ganesha, Shiva). Regular temple visits, especially on the planet's specific day, create positive energy. Offering the planet's favorite items, performing abhisheka (sacred bathing), and participating in temple activities amplify the remedial effect. The devotee's sincere devotion and surrender are more important than elaborate rituals.",
                "knowledge_domain": "remedial_measures",
                "content_type": "temple_worship",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["temple_worship", "deity_connection", "planetary_deities", "divine_grace"],
                "source_reference": "Agama Shastra and Devotional Practices"
            }
        ]
        
        for knowledge in remedial_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_world_knowledge(self):
        """Seed current world knowledge with spiritual perspectives"""
        world_knowledge = [
            {
                "title": "Digital Age and Saturn's Influence",
                "content": "The digital revolution corresponds to Saturn's transit through different signs, bringing systematic transformation to human communication and work patterns. Saturn in Aquarius (2020-2023) accelerated digital adoption, remote work, and technological integration. From a spiritual perspective, technology should serve dharma and human connection rather than create isolation. The key is maintaining mindful awareness while using digital tools, ensuring they enhance rather than replace genuine human relationships and spiritual practice.",
                "knowledge_domain": "world_knowledge",
                "content_type": "modern_analysis",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["digital_age", "saturn", "technology", "mindful_living"],
                "source_reference": "Contemporary Astrological Analysis"
            },
            {
                "title": "Global Economic Cycles and Jupiter-Saturn Conjunctions",
                "content": "Major economic cycles correlate with Jupiter-Saturn conjunctions occurring every 20 years. The 2020 conjunction in Aquarius marked a shift toward technology-based economics and digital currencies. Historical analysis shows that these conjunctions coincide with significant economic restructuring. From a spiritual perspective, economic changes are opportunities to reassess values, practice detachment from material outcomes, and focus on dharmic wealth creation that serves society's greater good.",
                "knowledge_domain": "world_knowledge",
                "content_type": "economic_analysis",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["economic_cycles", "jupiter_saturn", "wealth_creation", "dharmic_economics"],
                "source_reference": "Financial Astrology and Economic Cycles"
            },
            {
                "title": "Environmental Consciousness and Planetary Healing",
                "content": "Environmental challenges reflect humanity's disconnection from natural planetary rhythms. Ancient Vedic texts emphasize living in harmony with Pancha Mahabhuta (five elements). Current environmental crises during Kali Yuga require both individual and collective conscious action. Astrological remedies now include environmental service: tree planting for Jupiter, water conservation for Moon, renewable energy for Sun, reducing waste for Saturn. This integration of ecological awareness with spiritual practice creates holistic healing for both individual and planetary karma.",
                "knowledge_domain": "world_knowledge",
                "content_type": "environmental_spirituality",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["environmental_healing", "five_elements", "ecological_consciousness", "planetary_health"],
                "source_reference": "Ecological Spirituality and Vedic Principles"
            }
        ]
        
        for knowledge in world_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _seed_psychological_integration(self):
        """Seed psychological integration with ancient wisdom"""
        psychological_knowledge = [
            {
                "title": "Jungian Psychology and Planetary Archetypes",
                "content": "Carl Jung's psychological archetypes correspond remarkably with planetary symbolism. The Sun represents the Self (individuation), Moon the Anima/emotional patterns, Mars the Warrior archetype, Mercury the Messenger/communicator, Jupiter the Wise King/teacher, Venus the Lover/creator, Saturn the Senex/disciplinarian. This integration helps modern seekers understand planetary influences as internal psychological patterns rather than external fate. Working with planetary energies becomes a process of conscious psychological integration and self-awareness.",
                "knowledge_domain": "psychological_integration",
                "content_type": "psychological_analysis",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["jungian_psychology", "planetary_archetypes", "self_awareness", "integration"],
                "source_reference": "Jungian Astrology and Psychological Integration"
            },
            {
                "title": "Mindfulness and Planetary Awareness",
                "content": "Mindfulness practices can be enhanced by planetary awareness. Each planet represents different aspects of consciousness: Sun (awareness itself), Moon (emotional awareness), Mercury (mental awareness), Venus (aesthetic awareness), Mars (energy awareness), Jupiter (wisdom awareness), Saturn (time awareness). Daily practice includes observing these different levels of awareness, noting which planetary energies are dominant, and consciously working with them. This creates a bridge between ancient astrological wisdom and contemporary mindfulness practice.",
                "knowledge_domain": "psychological_integration",
                "content_type": "mindfulness_practice",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["mindfulness", "planetary_awareness", "consciousness", "daily_practice"],
                "source_reference": "Mindful Astrology and Conscious Living"
            },
            {
                "title": "Trauma Healing and Karmic Understanding",
                "content": "Modern trauma therapy can be enriched by karmic understanding from Vedic astrology. Traumatic experiences often correlate with challenging planetary periods or aspects, representing karmic lessons rather than random suffering. The healing process involves both psychological work and spiritual understanding. Techniques include: recognizing planetary patterns in trauma timing, using appropriate planetary remedies alongside therapy, understanding the soul's growth through difficult experiences, and integrating spiritual practices with psychological healing. This approach honors both human psychology and soul evolution.",
                "knowledge_domain": "psychological_integration",
                "content_type": "trauma_healing",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["trauma_healing", "karmic_understanding", "soul_evolution", "integrated_healing"],
                "source_reference": "Integrative Healing and Karmic Psychology"
            }
        ]
        
        for knowledge in psychological_knowledge:
            await self._add_knowledge_with_embedding(knowledge)
    
    async def _add_knowledge_with_embedding(self, knowledge_data: Dict[str, Any]):
        """Add knowledge piece to database with OpenAI embedding"""
        try:
            # Generate embedding if OpenAI is available
            embedding = None
            if self.openai_client and OPENAI_AVAILABLE:
                try:
                    logger.info(f"Generating embedding for: {knowledge_data['title'][:50]}...")
                    response = await self.openai_client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=knowledge_data["content"]
                    )
                    embedding = response.data[0].embedding
                    logger.info("✅ OpenAI embedding generated successfully")
                except Exception as embed_error:
                    import traceback
                    logger.warning(f"OpenAI embedding failed: {embed_error}")
                    logger.warning(f"OpenAI error traceback: {traceback.format_exc()}")
                    logger.info("Using fallback zero vector")
                    embedding = [0.0] * DEFAULT_EMBED_DIM
            else:
                # Fallback to zero vector if OpenAI not available
                logger.info("Using fallback zero vector (no OpenAI client)")
                embedding = [0.0] * DEFAULT_EMBED_DIM
            
            # Check if pgvector is available by checking column type
            vector_support = True
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    column_type = await conn.fetchval("""
                        SELECT data_type FROM information_schema.columns 
                        WHERE table_name = 'rag_knowledge_base' 
                        AND column_name = 'embedding_vector'
                    """)
                    # Support both pgvector (USER-DEFINED) and FLOAT[] (ARRAY) types
                    vector_support = column_type in ('USER-DEFINED', 'ARRAY')
            
            # Convert embedding to appropriate format
            embedding_data = format_embedding_for_storage(embedding, vector_support)
            
            # Add to database - handle both pool and direct connection
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    logger.info(f"Inserting knowledge piece: {knowledge_data['title'][:50]}...")
                    
                    # Check if content_type column exists
                    content_type_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'rag_knowledge_base' 
                            AND column_name = 'content_type'
                        )
                    """)
                    
                    # Check if cultural_context column exists
                    cultural_context_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'rag_knowledge_base' 
                            AND column_name = 'cultural_context'
                        )
                    """)
                    
                    if content_type_exists and cultural_context_exists:
                        await conn.execute("""
                            INSERT INTO rag_knowledge_base (
                                knowledge_domain, content_type, title, content, metadata,
                                embedding_vector, tags, source_reference, authority_level,
                                cultural_context, created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                            ON CONFLICT (title) DO UPDATE SET
                                content = EXCLUDED.content,
                                metadata = EXCLUDED.metadata,
                                embedding_vector = EXCLUDED.embedding_vector,
                                updated_at = NOW()
                        """, 
                            knowledge_data["knowledge_domain"],
                            knowledge_data.get("content_type", "knowledge"),
                            knowledge_data["title"],
                            knowledge_data["content"],
                            json.dumps(knowledge_data.get("metadata", {})),
                            embedding_data,
                            knowledge_data.get("tags", []),
                            knowledge_data["source_reference"],
                            knowledge_data["authority_level"],
                            knowledge_data.get("cultural_context", "universal")
                        )
                    elif content_type_exists:
                        # Table has content_type but no cultural_context
                        await conn.execute("""
                            INSERT INTO rag_knowledge_base (
                                knowledge_domain, content_type, title, content, metadata,
                                embedding_vector, tags, source_reference, authority_level,
                                created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                            ON CONFLICT (title) DO UPDATE SET
                                content = EXCLUDED.content,
                                metadata = EXCLUDED.metadata,
                                embedding_vector = EXCLUDED.embedding_vector,
                                updated_at = NOW()
                        """, 
                            knowledge_data["knowledge_domain"],
                            knowledge_data.get("content_type", "knowledge"),
                            knowledge_data["title"],
                            knowledge_data["content"],
                            json.dumps(knowledge_data.get("metadata", {})),
                            embedding_data,
                            knowledge_data.get("tags", []),
                            knowledge_data["source_reference"],
                            knowledge_data["authority_level"]
                        )
                    else:
                        # Fallback for tables without content_type and cultural_context columns
                        await conn.execute("""
                            INSERT INTO rag_knowledge_base (
                                knowledge_domain, title, content, metadata,
                                embedding_vector, tags, source_reference, authority_level,
                                created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                            ON CONFLICT (title) DO UPDATE SET
                                content = EXCLUDED.content,
                                metadata = EXCLUDED.metadata,
                                embedding_vector = EXCLUDED.embedding_vector,
                                updated_at = NOW()
                        """, 
                            knowledge_data["knowledge_domain"],
                            knowledge_data["title"],
                            knowledge_data["content"],
                            json.dumps(knowledge_data.get("metadata", {})),
                            embedding_data,
                            knowledge_data.get("tags", []),
                            knowledge_data["source_reference"],
                            knowledge_data["authority_level"]
                        )
            else:
                    raise RuntimeError(
                    "Database pool is not available in KnowledgeSeeder. "
                    "This should be provided during initialization."
                )
            
            logger.info(f"Added knowledge: {knowledge_data['title'][:50]}...")
            
        except Exception as e:
            import traceback
            logger.error(f"Error adding knowledge piece: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Continue with next piece rather than failing completely
            pass

# Initialize and run seeding
async def run_knowledge_seeding(db_pool_override: Optional[Any] = None):
    """
    Run the complete knowledge seeding process.
    It can accept an external db_pool to avoid dependency on a global pool.
    """
    db_pool = None
    try:
        if db_pool_override:
            db_pool = db_pool_override
            logger.info("Using provided database pool override for seeding.")
        else:
            # Fallback to global pool if no override is provided
            try:
                from . import db
            except ImportError:
                import db
        
        db_pool = db.get_db_pool()
        if db_pool is None:
            raise Exception("Shared database pool not available - ensure main.py has initialized it")
        
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found, using fallback embeddings")
            openai_api_key = "fallback_key"
        
        # Initialize seeder
        seeder = KnowledgeSeeder(db_pool, openai_api_key)
        
        # Run seeding
        await seeder.seed_complete_knowledge_base()
        
        logger.info("Knowledge seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Knowledge seeding failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_knowledge_seeding())