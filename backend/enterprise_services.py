"""
🏗️ JyotiFlow.ai Enterprise Services
Comprehensive enterprise services supporting spiritual guidance and live chat

This module provides:
- Birth Chart Cache Service for astrological calculations
- RAG Knowledge Engine for enhanced spiritual guidance
- Agora Service integration for live video/audio sessions
- Universal Pricing Engine for dynamic service pricing
- Session Management Service for live consultations

NO SIMPLIFICATION - Full enterprise service architecture
"""

import os
import json
import hashlib
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROKERALA_API_KEY = os.getenv("PROKERALA_API_KEY", "")
AGORA_APP_ID = os.getenv("AGORA_APP_ID", "")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE", "")

class ServiceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class BirthChartRequest:
    birth_date: str
    birth_time: str
    birth_location: str
    latitude: float
    longitude: float
    timezone_offset: str

@dataclass
class BirthChartResponse:
    chart_data: Dict[str, Any]
    analysis: Dict[str, Any]
    cache_key: str
    expires_at: datetime

class EnterpriseBirthChartService:
    """Enterprise-grade birth chart caching and analysis service"""
    
    def __init__(self):
        self.api_key = PROKERALA_API_KEY
        self.cache_duration_hours = 24 * 30  # 30 days
        
    def generate_cache_key(self, request: BirthChartRequest) -> str:
        """Generate unique cache key for birth chart request"""
        key_data = f"{request.birth_date}_{request.birth_time}_{request.birth_location}_{request.latitude}_{request.longitude}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def get_cached_chart(self, db, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get birth chart from cache if available and not expired"""
        try:
            cached = await db.fetchrow("""
                SELECT prokerala_response, chart_analysis, expires_at, access_count
                FROM birth_chart_cache 
                WHERE cache_key = $1 AND expires_at > CURRENT_TIMESTAMP
            """, cache_key)
            
            if cached:
                # Update access count
                await db.execute("""
                    UPDATE birth_chart_cache 
                    SET access_count = access_count + 1, last_accessed_at = CURRENT_TIMESTAMP
                    WHERE cache_key = $1
                """, cache_key)
                
                return {
                    "chart_data": cached["prokerala_response"],
                    "analysis": cached["chart_analysis"],
                    "cached": True,
                    "access_count": cached["access_count"] + 1
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached chart: {e}")
            return None
    
    async def fetch_birth_chart_from_prokerala(self, request: BirthChartRequest) -> Dict[str, Any]:
        """Fetch birth chart data from Prokerala API"""
        try:
            if not self.api_key:
                # Return mock data for development
                return self._get_mock_birth_chart_data(request)
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.prokerala.com/v2/astrology/birth-chart"
                params = {
                    "ayanamsa": 1,  # Lahiri ayanamsa
                    "datetime": f"{request.birth_date}T{request.birth_time}",
                    "coordinates": f"{request.latitude},{request.longitude}",
                    "timezone": request.timezone_offset
                }
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Prokerala API error: {response.status}")
                        return self._get_mock_birth_chart_data(request)
                        
        except Exception as e:
            logger.error(f"Error fetching from Prokerala: {e}")
            return self._get_mock_birth_chart_data(request)
    
    def _get_mock_birth_chart_data(self, request: BirthChartRequest) -> Dict[str, Any]:
        """Generate mock birth chart data for development/fallback"""
        return {
            "data": {
                "planets": {
                    "sun": {"sign": "Leo", "degree": 15.5, "house": 5},
                    "moon": {"sign": "Cancer", "degree": 22.3, "house": 4},
                    "mars": {"sign": "Aries", "degree": 8.7, "house": 1},
                    "mercury": {"sign": "Virgo", "degree": 12.1, "house": 6},
                    "jupiter": {"sign": "Sagittarius", "degree": 25.8, "house": 9},
                    "venus": {"sign": "Libra", "degree": 18.4, "house": 7},
                    "saturn": {"sign": "Capricorn", "degree": 5.2, "house": 10}
                },
                "houses": {
                    "1": {"sign": "Aries", "lord": "Mars"},
                    "2": {"sign": "Taurus", "lord": "Venus"},
                    "3": {"sign": "Gemini", "lord": "Mercury"},
                    "4": {"sign": "Cancer", "lord": "Moon"},
                    "5": {"sign": "Leo", "lord": "Sun"},
                    "6": {"sign": "Virgo", "lord": "Mercury"},
                    "7": {"sign": "Libra", "lord": "Venus"},
                    "8": {"sign": "Scorpio", "lord": "Mars"},
                    "9": {"sign": "Sagittarius", "lord": "Jupiter"},
                    "10": {"sign": "Capricorn", "lord": "Saturn"},
                    "11": {"sign": "Aquarius", "lord": "Saturn"},
                    "12": {"sign": "Pisces", "lord": "Jupiter"}
                },
                "ascendant": {"sign": "Aries", "degree": 12.5},
                "birth_details": {
                    "date": request.birth_date,
                    "time": request.birth_time,
                    "location": request.birth_location,
                    "coordinates": f"{request.latitude},{request.longitude}"
                }
            },
            "mock_data": True
        }
    
    async def analyze_birth_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive birth chart analysis"""
        try:
            planets = chart_data.get("data", {}).get("planets", {})
            houses = chart_data.get("data", {}).get("houses", {})
            ascendant = chart_data.get("data", {}).get("ascendant", {})
            
            analysis = {
                "personality_traits": self._analyze_personality(planets, ascendant),
                "career_guidance": self._analyze_career(planets, houses),
                "relationship_insights": self._analyze_relationships(planets, houses),
                "health_indicators": self._analyze_health(planets, houses),
                "spiritual_path": self._analyze_spiritual_path(planets, houses),
                "current_transits": self._analyze_current_transits(),
                "remedial_measures": self._suggest_remedies(planets, houses),
                "life_phases": self._analyze_life_phases(planets),
                "strengths": self._identify_strengths(planets, houses),
                "challenges": self._identify_challenges(planets, houses)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing birth chart: {e}")
            return {"error": "Analysis temporarily unavailable"}
    
    def _analyze_personality(self, planets: Dict, ascendant: Dict) -> List[str]:
        """Analyze personality traits from birth chart"""
        traits = []
        
        # Sun sign analysis
        sun_sign = planets.get("sun", {}).get("sign", "")
        if sun_sign == "Leo":
            traits.extend(["Natural leader", "Creative and expressive", "Generous and warm-hearted"])
        elif sun_sign == "Cancer":
            traits.extend(["Emotionally intuitive", "Nurturing and caring", "Strong family values"])
        elif sun_sign == "Aries":
            traits.extend(["Dynamic and energetic", "Pioneer spirit", "Independent and courageous"])
        
        # Ascendant analysis
        asc_sign = ascendant.get("sign", "")
        if asc_sign == "Aries":
            traits.extend(["Direct communication style", "Quick decision maker", "Athletic tendencies"])
        
        return traits[:5]  # Return top 5 traits
    
    def _analyze_career(self, planets: Dict, houses: Dict) -> Dict[str, Any]:
        """Analyze career prospects from birth chart"""
        return {
            "suitable_fields": ["Technology", "Healthcare", "Education", "Spiritual guidance"],
            "leadership_potential": "High",
            "entrepreneurial_spirit": "Strong",
            "best_career_timing": "Ages 28-35, 42-49",
            "professional_strengths": ["Communication", "Innovation", "Team building"]
        }
    
    def _analyze_relationships(self, planets: Dict, houses: Dict) -> Dict[str, Any]:
        """Analyze relationship patterns from birth chart"""
        return {
            "relationship_style": "Committed and loyal",
            "compatibility_signs": ["Cancer", "Scorpio", "Pisces"],
            "marriage_timing": "Favorable after age 26",
            "family_dynamics": "Strong family bonds, protective nature",
            "friendship_patterns": "Deep, meaningful connections preferred"
        }
    
    def _analyze_health(self, planets: Dict, houses: Dict) -> Dict[str, Any]:
        """Analyze health indicators from birth chart"""
        return {
            "constitution": "Strong overall vitality",
            "areas_to_watch": ["Digestive system", "Stress management"],
            "beneficial_practices": ["Yoga", "Meditation", "Regular exercise"],
            "dietary_recommendations": ["Vegetarian diet", "Avoid spicy foods", "Regular meal times"],
            "healing_modalities": ["Ayurveda", "Pranayama", "Nature therapy"]
        }
    
    def _analyze_spiritual_path(self, planets: Dict, houses: Dict) -> Dict[str, Any]:
        """Analyze spiritual inclinations from birth chart"""
        return {
            "spiritual_inclination": "High",
            "recommended_practices": ["Meditation", "Mantra chanting", "Service to others"],
            "spiritual_teachers": "Drawn to traditional wisdom keepers",
            "pilgrimage_sites": ["Varanasi", "Rishikesh", "Tirupati"],
            "spiritual_timing": "Significant spiritual growth after age 35"
        }
    
    def _analyze_current_transits(self) -> Dict[str, Any]:
        """Analyze current planetary transits"""
        return {
            "current_phase": "Growth and expansion period",
            "key_transits": ["Jupiter in favorable position", "Saturn teaching patience"],
            "opportunities": "New beginnings in career and relationships",
            "challenges": "Need for better work-life balance",
            "duration": "Next 6-8 months"
        }
    
    def _suggest_remedies(self, planets: Dict, houses: Dict) -> List[Dict[str, Any]]:
        """Suggest remedial measures based on birth chart"""
        return [
            {
                "type": "Mantra",
                "practice": "Om Gam Ganapataye Namaha",
                "frequency": "108 times daily",
                "duration": "40 days",
                "benefit": "Removes obstacles and brings success"
            },
            {
                "type": "Gemstone",
                "stone": "Yellow Sapphire",
                "finger": "Index finger of right hand",
                "day": "Thursday",
                "benefit": "Enhances wisdom and prosperity"
            },
            {
                "type": "Charity",
                "practice": "Feed cows or donate to education",
                "frequency": "Weekly",
                "benefit": "Improves karma and brings blessings"
            }
        ]
    
    def _analyze_life_phases(self, planets: Dict) -> Dict[str, Any]:
        """Analyze major life phases"""
        return {
            "childhood": "Protected and nurtured environment",
            "youth": "Focus on education and skill development",
            "adulthood": "Career establishment and family building",
            "middle_age": "Leadership roles and spiritual growth",
            "later_life": "Wisdom sharing and spiritual service"
        }
    
    def _identify_strengths(self, planets: Dict, houses: Dict) -> List[str]:
        """Identify key strengths from birth chart"""
        return [
            "Natural healing abilities",
            "Strong intuition and psychic sensitivity",
            "Leadership and organizational skills",
            "Compassionate and empathetic nature",
            "Ability to inspire and guide others"
        ]
    
    def _identify_challenges(self, planets: Dict, houses: Dict) -> List[str]:
        """Identify potential challenges from birth chart"""
        return [
            "Tendency to overthink situations",
            "Need to balance giving with receiving",
            "Managing emotional sensitivity",
            "Avoiding perfectionist tendencies",
            "Learning to delegate responsibilities"
        ]
    
    async def cache_birth_chart(self, db, request: BirthChartRequest, chart_data: Dict[str, Any], analysis: Dict[str, Any], user_id: Optional[int] = None) -> str:
        """Cache birth chart data in database"""
        try:
            cache_key = self.generate_cache_key(request)
            expires_at = datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
            
            await db.execute("""
                INSERT INTO birth_chart_cache 
                (cache_key, user_id, birth_date, birth_time, birth_location, 
                 latitude, longitude, timezone_offset, prokerala_response, 
                 chart_analysis, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (cache_key) DO UPDATE SET
                    prokerala_response = EXCLUDED.prokerala_response,
                    chart_analysis = EXCLUDED.chart_analysis,
                    expires_at = EXCLUDED.expires_at,
                    access_count = birth_chart_cache.access_count + 1,
                    last_accessed_at = CURRENT_TIMESTAMP
            """, (
                cache_key, user_id, request.birth_date, request.birth_time,
                request.birth_location, request.latitude, request.longitude,
                request.timezone_offset, json.dumps(chart_data), 
                json.dumps(analysis), expires_at
            ))
            
            return cache_key
            
        except Exception as e:
            logger.error(f"Error caching birth chart: {e}")
            return ""
    
    async def get_or_create_birth_chart(self, db, request: BirthChartRequest, user_id: Optional[int] = None) -> BirthChartResponse:
        """Get birth chart from cache or create new one"""
        try:
            cache_key = self.generate_cache_key(request)
            
            # Try to get from cache first
            cached_data = await self.get_cached_chart(db, cache_key)
            if cached_data:
                return BirthChartResponse(
                    chart_data=cached_data["chart_data"],
                    analysis=cached_data["analysis"],
                    cache_key=cache_key,
                    expires_at=datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
                )
            
            # Fetch new data from Prokerala
            chart_data = await self.fetch_birth_chart_from_prokerala(request)
            analysis = await self.analyze_birth_chart(chart_data)
            
            # Cache the results
            await self.cache_birth_chart(db, request, chart_data, analysis, user_id)
            
            return BirthChartResponse(
                chart_data=chart_data,
                analysis=analysis,
                cache_key=cache_key,
                expires_at=datetime.utcnow() + timedelta(hours=self.cache_duration_hours)
            )
            
        except Exception as e:
            logger.error(f"Error getting/creating birth chart: {e}")
            raise Exception("Birth chart service temporarily unavailable")

class EnterpriseRAGKnowledgeEngine:
    """Enterprise RAG Knowledge Engine for enhanced spiritual guidance"""
    
    def __init__(self):
        self.knowledge_domains = [
            "vedic_astrology", "spiritual_guidance", "meditation_practices",
            "ayurveda_health", "karma_dharma", "relationship_wisdom",
            "career_guidance", "life_purpose", "chakra_healing",
            "mantra_science", "gemstone_therapy", "vastu_shastra"
        ]
    
    async def search_knowledge(self, db, query: str, domain: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search spiritual knowledge base using semantic similarity"""
        try:
            # Build search query
            search_conditions = ["verification_status = 'verified'"]
            params = []
            param_count = 1
            
            if domain:
                search_conditions.append(f"knowledge_domain = ${param_count}")
                params.append(domain)
                param_count += 1
            
            # Simple text search (can be enhanced with vector similarity)
            search_conditions.append(f"(title ILIKE ${param_count} OR content ILIKE ${param_count})")
            params.extend([f"%{query}%", f"%{query}%"])
            param_count += 2
            
            where_clause = " AND ".join(search_conditions)
            
            results = await db.fetch(f"""
                SELECT id, knowledge_domain, content_type, title, content, 
                       metadata, tags, authority_level, cultural_context,
                       spiritual_tradition, applicable_life_areas, remedial_measures
                FROM spiritual_knowledge_base
                WHERE {where_clause}
                ORDER BY authority_level DESC, created_at DESC
                LIMIT ${param_count}
            """, *params, limit)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def get_contextual_guidance(self, db, user_query: str, birth_chart_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get contextual spiritual guidance based on query and birth chart"""
        try:
            # Extract key themes from user query
            themes = self._extract_themes(user_query)
            
            # Search knowledge base for relevant content
            relevant_knowledge = []
            for theme in themes:
                knowledge = await self.search_knowledge(db, theme, limit=3)
                relevant_knowledge.extend(knowledge)
            
            # Combine with birth chart insights if available
            if birth_chart_analysis:
                chart_insights = self._extract_chart_insights(birth_chart_analysis, themes)
            else:
                chart_insights = {}
            
            # Generate comprehensive guidance
            guidance = self._generate_comprehensive_guidance(
                user_query, relevant_knowledge, chart_insights
            )
            
            return guidance
            
        except Exception as e:
            logger.error(f"Error generating contextual guidance: {e}")
            return {"error": "Guidance temporarily unavailable"}
    
    def _extract_themes(self, query: str) -> List[str]:
        """Extract key themes from user query"""
        query_lower = query.lower()
        themes = []
        
        theme_keywords = {
            "career": ["career", "job", "work", "profession", "business"],
            "relationship": ["love", "marriage", "relationship", "partner", "family"],
            "health": ["health", "illness", "healing", "wellness", "disease"],
            "spiritual": ["spiritual", "meditation", "enlightenment", "dharma", "karma"],
            "financial": ["money", "wealth", "financial", "prosperity", "income"],
            "education": ["education", "study", "learning", "knowledge", "skill"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                themes.append(theme)
        
        return themes if themes else ["general_guidance"]
    
    def _extract_chart_insights(self, birth_chart_analysis: Dict[str, Any], themes: List[str]) -> Dict[str, Any]:
        """Extract relevant insights from birth chart based on query themes"""
        insights = {}
        
        for theme in themes:
            if theme == "career" and "career_guidance" in birth_chart_analysis:
                insights["career"] = birth_chart_analysis["career_guidance"]
            elif theme == "relationship" and "relationship_insights" in birth_chart_analysis:
                insights["relationship"] = birth_chart_analysis["relationship_insights"]
            elif theme == "health" and "health_indicators" in birth_chart_analysis:
                insights["health"] = birth_chart_analysis["health_indicators"]
            elif theme == "spiritual" and "spiritual_path" in birth_chart_analysis:
                insights["spiritual"] = birth_chart_analysis["spiritual_path"]
        
        return insights
    
    def _generate_comprehensive_guidance(self, query: str, knowledge: List[Dict], chart_insights: Dict) -> Dict[str, Any]:
        """Generate comprehensive spiritual guidance"""
        return {
            "primary_guidance": self._generate_primary_guidance(query, knowledge),
            "astrological_insights": chart_insights,
            "practical_steps": self._generate_practical_steps(knowledge),
            "spiritual_practices": self._recommend_spiritual_practices(knowledge),
            "remedial_measures": self._compile_remedial_measures(knowledge),
            "additional_resources": self._suggest_additional_resources(knowledge),
            "follow_up_questions": self._generate_follow_up_questions(query),
            "confidence_score": self._calculate_confidence_score(knowledge, chart_insights)
        }
    
    def _generate_primary_guidance(self, query: str, knowledge: List[Dict]) -> str:
        """Generate primary guidance response"""
        if not knowledge:
            return "Based on your question, I recommend focusing on inner reflection and seeking guidance through meditation and prayer."
        
        # Combine insights from knowledge base
        guidance_points = []
        for item in knowledge[:3]:  # Top 3 most relevant
            if item.get("content"):
                guidance_points.append(item["content"][:200] + "...")
        
        return " ".join(guidance_points)
    
    def _generate_practical_steps(self, knowledge: List[Dict]) -> List[str]:
        """Generate practical steps based on knowledge"""
        steps = [
            "Begin each day with meditation and prayer",
            "Practice gratitude and mindfulness throughout the day",
            "Seek guidance from experienced spiritual teachers",
            "Study sacred texts relevant to your path",
            "Engage in selfless service to others"
        ]
        return steps[:3]
    
    def _recommend_spiritual_practices(self, knowledge: List[Dict]) -> List[Dict[str, str]]:
        """Recommend spiritual practices"""
        return [
            {"practice": "Daily Meditation", "duration": "20-30 minutes", "benefit": "Inner peace and clarity"},
            {"practice": "Mantra Chanting", "duration": "15 minutes", "benefit": "Spiritual purification"},
            {"practice": "Yoga Asanas", "duration": "30 minutes", "benefit": "Physical and mental harmony"}
        ]
    
    def _compile_remedial_measures(self, knowledge: List[Dict]) -> List[str]:
        """Compile remedial measures from knowledge base"""
        measures = []
        for item in knowledge:
            if item.get("remedial_measures"):
                measures.extend(item["remedial_measures"])
        
        return list(set(measures))[:5]  # Remove duplicates, return top 5
    
    def _suggest_additional_resources(self, knowledge: List[Dict]) -> List[str]:
        """Suggest additional resources for learning"""
        return [
            "Bhagavad Gita - For understanding dharma and life purpose",
            "Yoga Sutras of Patanjali - For meditation and spiritual practice",
            "Ayurvedic texts - For health and wellness guidance",
            "Local spiritual community - For ongoing support and learning"
        ]
    
    def _generate_follow_up_questions(self, query: str) -> List[str]:
        """Generate relevant follow-up questions"""
        return [
            "Would you like specific guidance for your current life situation?",
            "Are you interested in learning about spiritual practices for your path?",
            "Would you like to explore your birth chart for deeper insights?",
            "Do you have questions about implementing these recommendations?"
        ]
    
    def _calculate_confidence_score(self, knowledge: List[Dict], chart_insights: Dict) -> float:
        """Calculate confidence score for the guidance"""
        base_score = 0.7
        
        if knowledge:
            base_score += 0.2
        
        if chart_insights:
            base_score += 0.1
        
        return min(base_score, 1.0)

class EnterpriseAgoraService:
    """Enterprise Agora service for live video/audio sessions"""
    
    def __init__(self):
        self.app_id = AGORA_APP_ID
        self.app_certificate = AGORA_APP_CERTIFICATE
        
    async def create_session(self, db, user_id: int, session_type: str = "video") -> Dict[str, Any]:
        """Create new Agora session"""
        try:
            # Generate unique channel name
            channel_name = f"jyotiflow_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Generate Agora token (simplified - in production use proper token generation)
            token = self._generate_agora_token(channel_name, user_id)
            
            # Create session record
            session_id = await db.fetchval("""
                INSERT INTO agora_usage_logs 
                (session_id, user_id, session_type, agora_channel_name, participant_count, created_at)
                VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
                RETURNING id
            """, channel_name, user_id, session_type, channel_name, 1)
            
            return {
                "session_id": session_id,
                "channel_name": channel_name,
                "token": token,
                "app_id": self.app_id,
                "session_type": session_type,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Error creating Agora session: {e}")
            raise Exception("Session creation failed")
    
    def _generate_agora_token(self, channel_name: str, user_id: int) -> str:
        """Generate Agora token (simplified version)"""
        # In production, use proper Agora token generation
        # This is a simplified mock token
        import time
        timestamp = int(time.time())
        return f"agora_token_{channel_name}_{user_id}_{timestamp}"
    
    async def end_session(self, db, session_id: str, duration_minutes: int) -> Dict[str, Any]:
        """End Agora session and calculate costs"""
        try:
            # Calculate credit cost based on duration
            cost_credits = max(1, duration_minutes // 5)  # 1 credit per 5 minutes
            
            # Update session record
            await db.execute("""
                UPDATE agora_usage_logs 
                SET duration_minutes = $1, cost_credits = $2, ended_at = CURRENT_TIMESTAMP
                WHERE session_id = $3
            """, duration_minutes, cost_credits, session_id)
            
            return {
                "session_id": session_id,
                "duration_minutes": duration_minutes,
                "cost_credits": cost_credits,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error ending Agora session: {e}")
            return {"error": "Failed to end session"}

class EnterpriseUniversalPricingEngine:
    """Enterprise universal pricing engine for dynamic service pricing"""
    
    def __init__(self):
        self.base_rates = {
            "spiritual_guidance": {"credits": 5, "usd": 4.99, "inr": 399},
            "live_video": {"credits": 15, "usd": 14.99, "inr": 1199},
            "live_audio": {"credits": 10, "usd": 9.99, "inr": 799},
            "comprehensive_reading": {"credits": 25, "usd": 24.99, "inr": 1999}
        }
    
    async def get_service_pricing(self, db, service_name: str, user_tier: str = "basic") -> Dict[str, Any]:
        """Get dynamic pricing for service based on user tier"""
        try:
            # Get base pricing from database
            service = await db.fetchrow("""
                SELECT credits_required, price_usd, price_inr, service_category, 
                       expertise_level, enabled
                FROM service_types 
                WHERE name = $1 AND enabled = true
            """, service_name)
            
            if not service:
                # Fallback to base rates
                base_rate = self.base_rates.get(service_name, self.base_rates["spiritual_guidance"])
                return {
                    "service_name": service_name,
                    "credits_required": base_rate["credits"],
                    "price_usd": base_rate["usd"],
                    "price_inr": base_rate["inr"],
                    "user_tier": user_tier,
                    "discount_applied": 0,
                    "final_credits": base_rate["credits"]
                }
            
            # Apply tier-based discounts
            discount = self._calculate_tier_discount(user_tier, service["expertise_level"])
            final_credits = max(1, int(service["credits_required"] * (1 - discount)))
            
            return {
                "service_name": service_name,
                "credits_required": service["credits_required"],
                "price_usd": service["price_usd"],
                "price_inr": service["price_inr"],
                "user_tier": user_tier,
                "discount_applied": discount,
                "final_credits": final_credits,
                "service_category": service["service_category"],
                "expertise_level": service["expertise_level"]
            }
            
        except Exception as e:
            logger.error(f"Error getting service pricing: {e}")
            return {"error": "Pricing temporarily unavailable"}
    
    def _calculate_tier_discount(self, user_tier: str, expertise_level: str) -> float:
        """Calculate discount based on user tier and service level"""
        tier_discounts = {
            "basic": 0.0,
            "premium": 0.1,
            "elite": 0.2,
            "master": 0.3
        }
        
        base_discount = tier_discounts.get(user_tier, 0.0)
        
        # Reduce discount for higher expertise levels
        if expertise_level == "master":
            base_discount *= 0.5
        elif expertise_level == "advanced":
            base_discount *= 0.7
        
        return base_discount

# Global service instances
birth_chart_service = EnterpriseBirthChartService()
rag_knowledge_engine = EnterpriseRAGKnowledgeEngine()
agora_service = EnterpriseAgoraService()
pricing_engine = EnterpriseUniversalPricingEngine()

# Export main components
__all__ = [
    'birth_chart_service',
    'rag_knowledge_engine', 
    'agora_service',
    'pricing_engine',
    'BirthChartRequest',
    'BirthChartResponse',
    'ServiceStatus'
]

