"""
SQLite-compatible Knowledge Seeding System for JyotiFlow
"""

import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteKnowledgeSeeder:
    """SQLite-compatible knowledge seeding system"""
    
    def __init__(self, db_path: str = "backend/jyotiflow.db"):
        self.db_path = db_path
        
    def seed_knowledge_base(self):
        """Seed the knowledge base with authentic spiritual content"""
        logger.info("Starting SQLite knowledge base seeding...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing knowledge (for fresh seeding)
        cursor.execute("DELETE FROM rag_knowledge_base")
        
        # Seed all knowledge domains
        knowledge_pieces = []
        
        # Classical Astrology Knowledge
        knowledge_pieces.extend(self._get_classical_astrology_knowledge())
        
        # Tamil Spiritual Literature
        knowledge_pieces.extend(self._get_tamil_spiritual_knowledge())
        
        # Relationship Astrology
        knowledge_pieces.extend(self._get_relationship_knowledge())
        
        # Career Astrology
        knowledge_pieces.extend(self._get_career_knowledge())
        
        # Health Astrology
        knowledge_pieces.extend(self._get_health_knowledge())
        
        # Remedial Measures
        knowledge_pieces.extend(self._get_remedial_knowledge())
        
        # World Knowledge
        knowledge_pieces.extend(self._get_world_knowledge())
        
        # Psychological Integration
        knowledge_pieces.extend(self._get_psychological_knowledge())
        
        # Insert all knowledge pieces
        for knowledge in knowledge_pieces:
            try:
                # Generate a simple embedding placeholder (in production, use OpenAI)
                embedding_text = f"[{','.join(['0.1'] * 10)}]"  # Simplified embedding
                
                cursor.execute("""
                    INSERT INTO rag_knowledge_base (
                        id, knowledge_domain, content_type, title, content, metadata,
                        embedding_vector, tags, source_reference, authority_level,
                        cultural_context, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self._generate_id(),
                    knowledge["knowledge_domain"],
                    knowledge["content_type"],
                    knowledge["title"],
                    knowledge["content"],
                    json.dumps(knowledge.get("metadata", {})),
                    embedding_text,
                    ",".join(knowledge.get("tags", [])),
                    knowledge["source_reference"],
                    knowledge["authority_level"],
                    knowledge["cultural_context"],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
            except Exception as e:
                logger.error(f"Failed to insert knowledge: {knowledge['title'][:50]}... - {e}")
        
        conn.commit()
        
        # Check result
        cursor.execute("SELECT COUNT(*) FROM rag_knowledge_base")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"✅ Knowledge seeding completed! Added {count} knowledge pieces")
        return count
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{hash(datetime.now())}".encode()).hexdigest()
    
    def _get_classical_astrology_knowledge(self) -> List[Dict[str, Any]]:
        """Classical Vedic astrology knowledge"""
        return [
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
            }
        ]
    
    def _get_tamil_spiritual_knowledge(self) -> List[Dict[str, Any]]:
        """Tamil spiritual literature and wisdom"""
        return [
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
            }
        ]
    
    def _get_relationship_knowledge(self) -> List[Dict[str, Any]]:
        """Relationship and marriage astrology knowledge"""
        return [
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
                "title": "Marriage Timing through Dasha Analysis",
                "content": "Marriage timing is determined by analyzing Venus dasha/antardasha, 7th house lord periods, and supportive transits. Jupiter's transit over the 7th house or its lord often coincides with marriage. The period of strongest benefic influencing the 7th house typically brings partnership opportunities. For women, Jupiter's influence is particularly important as it represents the husband. Rahu-Ketu axis affecting the 7th house can cause delays but ultimately leads to destined partnerships.",
                "knowledge_domain": "relationship_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["marriage_timing", "dasha", "jupiter_transit", "7th_house"],
                "source_reference": "Predictive Astrology Texts"
            }
        ]
    
    def _get_career_knowledge(self) -> List[Dict[str, Any]]:
        """Career and professional success knowledge"""
        return [
            {
                "title": "10th House and Career Success Analysis",
                "content": "The 10th house represents career, reputation, and public image. Its lord's placement indicates career direction and success potential. Strong 10th house lord in benefic houses (1, 4, 5, 7, 9, 11) grants career success. Planets in the 10th house show career nature: Sun (government, leadership), Moon (public service, hospitality), Mars (engineering, defense), Mercury (communication, commerce), Jupiter (teaching, consulting), Venus (arts, luxury), Saturn (service, persistence), Rahu (foreign connections, technology), Ketu (research, spirituality).",
                "knowledge_domain": "career_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "universal",
                "tags": ["10th_house", "career", "profession", "success", "reputation"],
                "source_reference": "Jataka Parijata Career Principles"
            },
            {
                "title": "Saturn's Role in Career Development",
                "content": "Saturn represents hard work, discipline, and long-term success. Well-placed Saturn creates 'Shasha Yoga' (one of Panch Mahapurusha Yogas), indicating sustained professional achievement. Saturn in the 10th house grants authority through perseverance. Saturn's aspects on the 10th house or its lord demand consistent effort but ultimately reward with lasting success. The key is to embrace Saturn's lessons of discipline, patience, and systematic approach to work.",
                "knowledge_domain": "career_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["saturn", "career_development", "discipline", "long_term_success"],
                "source_reference": "Brihat Jataka Saturn Analysis"
            }
        ]
    
    def _get_health_knowledge(self) -> List[Dict[str, Any]]:
        """Health and wellness astrology knowledge"""
        return [
            {
                "title": "6th House and Health Analysis",
                "content": "The 6th house represents health, disease, and healing capacity. A strong 6th house lord indicates good disease resistance and recovery ability. Malefic planets in the 6th house can create health challenges but also provide strength to overcome them. The 6th house lord's placement by sign and house shows health vulnerabilities and healing approaches. Fire signs in the 6th house indicate inflammatory conditions, earth signs show metabolic issues, air signs relate to nervous system, and water signs affect body fluids and emotional health.",
                "knowledge_domain": "health_astrology",
                "content_type": "astrological_analysis",
                "authority_level": 4,
                "cultural_context": "ayurvedic_tradition",
                "tags": ["6th_house", "health", "disease", "healing", "recovery"],
                "source_reference": "Ayurvedic Astrology Principles"
            }
        ]
    
    def _get_remedial_knowledge(self) -> List[Dict[str, Any]]:
        """Comprehensive remedial measures knowledge"""
        return [
            {
                "title": "Mantra Therapy for Planetary Healing",
                "content": "Mantra therapy uses sound vibrations to harmonize planetary energies. Each planet has specific mantras: Sun ('Om Hraam Hreem Hroum Sah Suryaya Namaha'), Moon ('Om Shraam Shreem Shroum Sah Chandraya Namaha'), Mars ('Om Angarakaya Namaha'), Mercury ('Om Budhaya Namaha'), Jupiter ('Om Brihaspataye Namaha'), Venus ('Om Shukraya Namaha'), Saturn ('Om Shanecharaya Namaha'), Rahu ('Om Rahave Namaha'), Ketu ('Om Ketave Namaha'). Daily practice during the planet's hora (planetary hour) amplifies the effect.",
                "knowledge_domain": "remedial_measures",
                "content_type": "spiritual_practice",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["mantra_therapy", "planetary_healing", "sound_vibrations", "spiritual_practice"],
                "source_reference": "Mantra Shastra and Remedial Astrology"
            },
            {
                "title": "Gemstone Therapy in Vedic Astrology",
                "content": "Gemstones amplify positive planetary energies when worn correctly. Primary gemstones: Ruby (Sun), Pearl (Moon), Red Coral (Mars), Emerald (Mercury), Yellow Sapphire (Jupiter), Diamond (Venus), Blue Sapphire (Saturn). The gemstone should be natural, untreated, and of appropriate weight (generally 1-5 carats depending on the planet). Proper purification and energization rituals are essential before wearing.",
                "knowledge_domain": "remedial_measures",
                "content_type": "gemstone_therapy",
                "authority_level": 4,
                "cultural_context": "vedic_tradition",
                "tags": ["gemstone_therapy", "planetary_energies", "natural_gemstones", "energization"],
                "source_reference": "Ratna Shastra and Gemstone Astrology"
            }
        ]
    
    def _get_world_knowledge(self) -> List[Dict[str, Any]]:
        """Current world knowledge with spiritual perspectives"""
        return [
            {
                "title": "Digital Age and Saturn's Influence",
                "content": "The digital revolution corresponds to Saturn's transit through different signs, bringing systematic transformation to human communication and work patterns. Saturn in Aquarius (2020-2023) accelerated digital adoption, remote work, and technological integration. From a spiritual perspective, technology should serve dharma and human connection rather than create isolation. The key is maintaining mindful awareness while using digital tools.",
                "knowledge_domain": "world_knowledge",
                "content_type": "modern_analysis",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["digital_age", "saturn", "technology", "mindful_living"],
                "source_reference": "Contemporary Astrological Analysis"
            }
        ]
    
    def _get_psychological_knowledge(self) -> List[Dict[str, Any]]:
        """Psychological integration with ancient wisdom"""
        return [
            {
                "title": "Jungian Psychology and Planetary Archetypes",
                "content": "Carl Jung's psychological archetypes correspond remarkably with planetary symbolism. The Sun represents the Self (individuation), Moon the Anima/emotional patterns, Mars the Warrior archetype, Mercury the Messenger/communicator, Jupiter the Wise King/teacher, Venus the Lover/creator, Saturn the Senex/disciplinarian. This integration helps modern seekers understand planetary influences as internal psychological patterns rather than external fate.",
                "knowledge_domain": "psychological_integration",
                "content_type": "psychological_analysis",
                "authority_level": 3,
                "cultural_context": "universal",
                "tags": ["jungian_psychology", "planetary_archetypes", "self_awareness", "integration"],
                "source_reference": "Jungian Astrology and Psychological Integration"
            }
        ]

def run_sqlite_knowledge_seeding():
    """Run the SQLite knowledge seeding"""
    seeder = SQLiteKnowledgeSeeder()
    return seeder.seed_knowledge_base()

if __name__ == "__main__":
    count = run_sqlite_knowledge_seeding()
    print(f"🎉 Seeded {count} knowledge pieces successfully!")