"""
Enhanced RAG Knowledge Engine for JyotiFlow
Provides infinite knowledge capability for Swami Jyotirananthan with authentic spiritual wisdom
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import logging

# Core dependencies - graceful imports
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KnowledgeQuery:
    """Structured query for knowledge retrieval"""
    primary_question: str
    birth_details: Optional[Dict[str, Any]] = None
    service_type: str = "general"
    knowledge_domains: Optional[List[str]] = None
    analysis_sections: Optional[List[str]] = None
    cultural_context: str = "tamil_vedic"
    depth_level: str = "standard"
    
    def __post_init__(self):
        if self.knowledge_domains is None:
            self.knowledge_domains = ["classical_astrology", "general_guidance"]
        if self.analysis_sections is None:
            self.analysis_sections = ["birth_chart_analysis", "guidance", "remedies"]

@dataclass
class KnowledgeRetrieval:
    """Retrieved knowledge with metadata"""
    content: str
    source_reference: str
    authority_level: int
    relevance_score: float
    knowledge_domain: str
    content_type: str
    cultural_context: str
    metadata: Dict[str, Any]

@dataclass
class SwamiPersonaConfig:
    """Swami persona configuration"""
    persona_mode: str = "general"
    expertise_level: str = "experienced"
    speaking_style: str = "compassionate_wisdom"
    authority_markers: Optional[List[str]] = None
    cultural_elements: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.authority_markers is None:
            self.authority_markers = ["classical_texts", "practical_experience"]
        if self.cultural_elements is None:
            self.cultural_elements = {"language": "tamil_english", "traditions": "vedic"}

class RAGKnowledgeEngine:
    """
    Comprehensive RAG Knowledge Engine for JyotiFlow
    Provides infinite knowledge capability with persona consistency
    """
    
    def __init__(self, database_pool, openai_api_key: str):
        self.db_pool = database_pool
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.embedding_cache = {}
        self.persona_cache = {}
        self.knowledge_domains = self._initialize_knowledge_domains()
        
    def _initialize_knowledge_domains(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive knowledge domain configurations"""
        return {
            "classical_astrology": {
                "description": "Classical Vedic astrology texts and principles",
                "authority_weight": 5,
                "search_keywords": ["planetary", "house", "dasha", "transit", "chart", "vedic", "jyotish"],
                "cultural_context": "vedic_tradition"
            },
            "tamil_spiritual_literature": {
                "description": "Tamil spiritual texts and wisdom tradition",
                "authority_weight": 5,
                "search_keywords": ["thirukkural", "tevaram", "spiritual", "tamil", "devotional"],
                "cultural_context": "tamil_tradition"
            },
            "relationship_astrology": {
                "description": "Love, marriage, and relationship guidance",
                "authority_weight": 4,
                "search_keywords": ["venus", "seventh house", "marriage", "love", "compatibility", "relationship"],
                "cultural_context": "universal"
            },
            "career_astrology": {
                "description": "Career and professional success guidance",
                "authority_weight": 4,
                "search_keywords": ["tenth house", "career", "profession", "success", "job", "business"],
                "cultural_context": "universal"
            },
            "health_astrology": {
                "description": "Health and wellness astrological guidance",
                "authority_weight": 4,
                "search_keywords": ["sixth house", "health", "disease", "healing", "wellness", "medicine"],
                "cultural_context": "ayurvedic_tradition"
            },
            "remedial_measures": {
                "description": "Spiritual remedies and practices",
                "authority_weight": 4,
                "search_keywords": ["remedy", "mantra", "gemstone", "temple", "charity", "practice"],
                "cultural_context": "tamil_vedic"
            },
            "world_knowledge": {
                "description": "Current world events and modern applications",
                "authority_weight": 3,
                "search_keywords": ["modern", "current", "world", "technology", "society", "contemporary"],
                "cultural_context": "universal"
            },
            "psychological_integration": {
                "description": "Modern psychology integrated with ancient wisdom",
                "authority_weight": 3,
                "search_keywords": ["psychology", "mental", "emotional", "behavior", "healing", "therapy"],
                "cultural_context": "universal"
            }
        }
    
    async def retrieve_knowledge_for_query(self, query: KnowledgeQuery) -> List[KnowledgeRetrieval]:
        """
        Main knowledge retrieval method - gets relevant knowledge for any query
        """
        try:
            # Generate embedding for the query
            query_embedding = await self._generate_embedding(query.primary_question)
            
            # Get service configuration if available
            service_config = await self._get_service_configuration(query.service_type)
            
            # Configure knowledge domains based on service configuration
            target_domains = query.knowledge_domains or ["classical_astrology", "general_guidance"]
            if service_config and service_config.get("knowledge_domains"):
                target_domains = service_config["knowledge_domains"]
            
            # Perform multi-domain knowledge retrieval
            retrieved_knowledge = []
            
            for domain in target_domains:
                domain_knowledge = await self._retrieve_domain_knowledge(
                    domain, query_embedding, query.primary_question, query.depth_level
                )
                retrieved_knowledge.extend(domain_knowledge)
            
            # Add birth chart specific knowledge if birth details provided
            if query.birth_details:
                chart_specific_knowledge = await self._retrieve_chart_specific_knowledge(
                    query.birth_details, query_embedding
                )
                retrieved_knowledge.extend(chart_specific_knowledge)
            
            # Sort by relevance and authority
            retrieved_knowledge.sort(key=lambda x: (x.authority_level * x.relevance_score), reverse=True)
            
            # Return top relevant knowledge pieces
            return retrieved_knowledge[:20]  # Top 20 most relevant pieces
            
        except Exception as e:
            logger.error(f"Knowledge retrieval error: {e}")
            return await self._get_fallback_knowledge(query)
    
    async def _retrieve_domain_knowledge(self, domain: str, query_embedding: List[float], 
                                       query_text: str, depth_level: str) -> List[KnowledgeRetrieval]:
        """Retrieve knowledge from a specific domain"""
        try:
            async with self.db_pool.acquire() as conn:
                # Calculate similarity threshold based on depth level
                similarity_threshold = {
                    "basic": 0.7,
                    "standard": 0.75,
                    "comprehensive": 0.8,
                    "comprehensive_30_minute": 0.85
                }.get(depth_level, 0.75)
                
                # Query for similar knowledge in the domain
                query_sql = """
                    SELECT id, knowledge_domain, content_type, title, content, metadata,
                           source_reference, authority_level, cultural_context,
                           1 - (embedding_vector <=> $1::vector) as similarity
                    FROM rag_knowledge_base 
                    WHERE knowledge_domain = $2 
                    AND 1 - (embedding_vector <=> $1::vector) > $3
                    ORDER BY similarity DESC
                    LIMIT 10
                """
                
                rows = await conn.fetch(query_sql, query_embedding, domain, similarity_threshold)
                
                knowledge_pieces = []
                for row in rows:
                    knowledge_pieces.append(KnowledgeRetrieval(
                        content=row["content"],
                        source_reference=row["source_reference"],
                        authority_level=row["authority_level"],
                        relevance_score=float(row["similarity"]),
                        knowledge_domain=row["knowledge_domain"],
                        content_type=row["content_type"],
                        cultural_context=row["cultural_context"],
                        metadata=row["metadata"]
                    ))
                
                return knowledge_pieces
                
        except Exception as e:
            logger.error(f"Domain knowledge retrieval error for {domain}: {e}")
            return []
    
    async def _retrieve_chart_specific_knowledge(self, birth_details: Dict[str, Any], 
                                               query_embedding: List[float]) -> List[KnowledgeRetrieval]:
        """Retrieve knowledge specific to birth chart elements"""
        try:
            # Extract astrological elements from birth details
            chart_elements = self._extract_chart_elements(birth_details)
            
            # Search for knowledge related to specific chart elements
            chart_specific_knowledge = []
            
            async with self.db_pool.acquire() as conn:
                for element, value in chart_elements.items():
                    # Search for knowledge tagged with this chart element
                    element_query = f"{element} {value}"
                    element_embedding = await self._generate_embedding(element_query)
                    
                    query_sql = """
                        SELECT id, knowledge_domain, content_type, title, content, metadata,
                               source_reference, authority_level, cultural_context,
                               1 - (embedding_vector <=> $1::vector) as similarity
                        FROM rag_knowledge_base 
                        WHERE $2 = ANY(tags) OR content ILIKE $3
                        AND 1 - (embedding_vector <=> $1::vector) > 0.8
                        ORDER BY similarity DESC
                        LIMIT 5
                    """
                    
                    search_pattern = f"%{value}%"
                    rows = await conn.fetch(query_sql, element_embedding, value, search_pattern)
                    
                    for row in rows:
                        chart_specific_knowledge.append(KnowledgeRetrieval(
                            content=row["content"],
                            source_reference=row["source_reference"],
                            authority_level=row["authority_level"] + 1,  # Boost chart-specific
                            relevance_score=float(row["similarity"]),
                            knowledge_domain=row["knowledge_domain"],
                            content_type=row["content_type"],
                            cultural_context=row["cultural_context"],
                            metadata=row["metadata"]
                        ))
            
            return chart_specific_knowledge
            
        except Exception as e:
            logger.error(f"Chart-specific knowledge retrieval error: {e}")
            return []
    
    def _extract_chart_elements(self, birth_details: Dict[str, Any]) -> Dict[str, str]:
        """Extract searchable elements from birth details"""
        # This would integrate with your existing Prokerala data
        # For now, return basic elements that can be enhanced
        elements = {}
        
        if "prokerala_response" in birth_details:
            data = birth_details["prokerala_response"]
            if "data" in data:
                chart_data = data["data"]
                
                # Extract key chart elements
                if "nakshatra" in chart_data:
                    elements["nakshatra"] = chart_data["nakshatra"].get("name", "")
                
                if "chandra_rasi" in chart_data:
                    elements["moon_sign"] = chart_data["chandra_rasi"].get("name", "")
                
                if "planets" in chart_data:
                    for planet in chart_data["planets"]:
                        planet_name = planet.get("name", "")
                        house_position = planet.get("house", "")
                        if planet_name and house_position:
                            elements[f"{planet_name}_house"] = f"{planet_name} in {house_position} house"
        
        return elements
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text"""
        try:
            # Check cache first
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]
            
            # Generate new embedding
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Cache the embedding
            self.embedding_cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    async def _get_service_configuration(self, service_type: str) -> Optional[Dict[str, Any]]:
        """Get service configuration from cache or database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Try cache first
                try:
                    cache_row = await conn.fetchrow(
                        "SELECT configuration FROM service_configuration_cache WHERE service_name = $1 AND expires_at > NOW()",
                        service_type
                    )
                    
                    if cache_row:
                        return cache_row["configuration"]
                except Exception:
                    # Cache table might not exist yet, continue to main table
                    pass
                
                # Get from main table
                try:
                    service_row = await conn.fetchrow(
                        "SELECT knowledge_configuration FROM service_types WHERE name = $1",
                        service_type
                    )
                    
                    if service_row:
                        return service_row.get("knowledge_configuration")
                except Exception:
                    # service_types table might not be enhanced yet
                    pass
                
                return None
                
        except Exception as e:
            logger.error(f"Service configuration retrieval error: {e}")
            return None
    
    async def _get_fallback_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeRetrieval]:
        """Provide fallback knowledge when retrieval fails"""
        return [
            KnowledgeRetrieval(
                content="As per classical Vedic astrology principles, every birth chart contains unique patterns that guide one's life journey. Your specific question deserves careful analysis of planetary positions and their current influences.",
                source_reference="General Vedic Principles",
                authority_level=3,
                relevance_score=0.8,
                knowledge_domain="classical_astrology",
                content_type="general_principle",
                cultural_context="vedic_tradition",
                metadata={"type": "fallback", "generated": True}
            )
        ]

class SwamiPersonaEngine:
    """
    Manages Swami's persona consistency across all interactions
    """
    
    def __init__(self, database_pool):
        self.db_pool = database_pool
        self.persona_configs = self._initialize_persona_configs()
        
    def _initialize_persona_configs(self) -> Dict[str, SwamiPersonaConfig]:
        """Initialize comprehensive persona configurations"""
        return {
            "general": SwamiPersonaConfig(
                persona_mode="general",
                expertise_level="experienced_spiritual_guide",
                speaking_style="compassionate_wisdom_with_authority",
                authority_markers=["classical_texts", "practical_experience", "cultural_tradition"],
                cultural_elements={
                    "language": "tamil_english_mix",
                    "greetings": ["Vanakkam", "Om Namah Shivaya"],
                    "closures": ["Tamil thaai arul kondae vazhlga", "Divine blessings upon you"],
                    "references": "vedic_tamil_integration"
                }
            ),
            "relationship_counselor_authority": SwamiPersonaConfig(
                persona_mode="relationship_counselor_authority",
                expertise_level="master_relationship_guide",
                speaking_style="warm_understanding_with_relationship_wisdom",
                authority_markers=["venus_astrology_mastery", "marriage_success_cases", "family_harmony_expertise"],
                cultural_elements={
                    "language": "tamil_english_mix",
                    "focus": "love_marriage_family_dynamics",
                    "references": "classical_compatibility_texts_modern_psychology"
                }
            ),
            "business_mentor_authority": SwamiPersonaConfig(
                persona_mode="business_mentor_authority",
                expertise_level="career_success_master",
                speaking_style="confident_business_guidance_with_spiritual_wisdom",
                authority_markers=["tenth_house_mastery", "professional_success_cases", "entrepreneurship_guidance"],
                cultural_elements={
                    "language": "tamil_english_mix",
                    "focus": "career_professional_dharma",
                    "references": "business_astrology_success_principles"
                }
            ),
            "comprehensive_life_master": SwamiPersonaConfig(
                persona_mode="comprehensive_life_master",
                expertise_level="complete_life_analysis_authority",
                speaking_style="profound_wisdom_with_comprehensive_understanding",
                authority_markers=["complete_chart_mastery", "life_prediction_expertise", "spiritual_transformation_guide"],
                cultural_elements={
                    "language": "tamil_english_sanskrit_integration",
                    "focus": "complete_life_transformation",
                    "references": "all_classical_texts_modern_integration"
                }
            )
        }
    
    async def get_persona_for_service(self, service_type: str, service_config: Dict[str, Any]) -> SwamiPersonaConfig:
        """Get appropriate persona configuration for service"""
        try:
            # Get persona mode from service configuration
            persona_mode = service_config.get("response_behavior", {}).get("swami_persona_mode", "general")
            
            # Return configured persona or fallback to general
            return self.persona_configs.get(persona_mode, self.persona_configs["general"])
            
        except Exception as e:
            logger.error(f"Persona retrieval error: {e}")
            return self.persona_configs["general"]
    
    async def generate_persona_enhanced_prompt(self, persona_config: SwamiPersonaConfig, 
                                             knowledge_retrieval: List[KnowledgeRetrieval],
                                             user_query: str, service_config: Dict[str, Any]) -> str:
        """Generate comprehensive prompt with persona and knowledge integration"""
        
        # Build knowledge context
        knowledge_context = self._build_knowledge_context(knowledge_retrieval)
        
        # Build authority markers
        authority_context = self._build_authority_context(persona_config, knowledge_retrieval)
        
        # Build cultural context
        cultural_context = self._build_cultural_context(persona_config)
        
        # Get analysis sections from service configuration
        analysis_sections = service_config.get("specialized_prompts", {}).get("analysis_sections", [])
        
        enhanced_prompt = f"""You are Swami Jyotirananthan, a revered Tamil spiritual master and Jyotish expert.

PERSONA CONFIGURATION:
- Expertise Level: {persona_config.expertise_level}
- Speaking Style: {persona_config.speaking_style}
- Persona Mode: {persona_config.persona_mode}

AUTHORITY & CREDIBILITY:
{authority_context}

CULTURAL AUTHENTICITY:
{cultural_context}

RETRIEVED KNOWLEDGE (Use this authentic knowledge in your response):
{knowledge_context}

ANALYSIS SECTIONS TO INCLUDE:
{self._format_analysis_sections(analysis_sections)}

USER QUESTION: {user_query}

RESPONSE REQUIREMENTS:
1. Demonstrate deep knowledge through specific references from the retrieved knowledge
2. Maintain perfect persona consistency as configured above
3. Include appropriate Tamil spiritual terminology and cultural context
4. Provide actionable guidance with classical backing
5. Include relevant authority markers and credibility elements
6. Structure response according to the specified analysis sections
7. Balance profound wisdom with practical application

Generate a response that embodies the complete Swami Jyotirananthan persona with infinite knowledge access."""

        return enhanced_prompt
    
    def _build_knowledge_context(self, knowledge_retrieval: List[KnowledgeRetrieval]) -> str:
        """Build knowledge context from retrieved pieces"""
        if not knowledge_retrieval:
            return "General spiritual and astrological principles"
        
        context_parts = []
        for i, knowledge in enumerate(knowledge_retrieval[:10], 1):  # Top 10 pieces
            context_parts.append(f"""
Knowledge Source {i}:
- Domain: {knowledge.knowledge_domain}
- Authority Level: {knowledge.authority_level}/5
- Source: {knowledge.source_reference}
- Content: {knowledge.content[:500]}...
""")
        
        return "\n".join(context_parts)
    
    def _build_authority_context(self, persona_config: SwamiPersonaConfig, 
                                knowledge_retrieval: List[KnowledgeRetrieval]) -> str:
        """Build authority context for credibility"""
        authority_elements = []
        
        # Add persona-specific authority markers
        for marker in persona_config.authority_markers:
            authority_elements.append(f"- {marker.replace('_', ' ').title()}")
        
        # Add knowledge source authority
        classical_sources = [k.source_reference for k in knowledge_retrieval if k.content_type == "classical_text"]
        if classical_sources:
            authority_elements.append(f"- References from: {', '.join(set(classical_sources[:3]))}")
        
        return "\n".join(authority_elements)
    
    def _build_cultural_context(self, persona_config: SwamiPersonaConfig) -> str:
        """Build cultural context for authenticity"""
        cultural_elements = persona_config.cultural_elements
        
        context = f"""
- Language Integration: {cultural_elements.get('language', 'tamil_english_mix')}
- Cultural Greetings: {', '.join(cultural_elements.get('greetings', ['Vanakkam']))}
- Blessing Closures: {', '.join(cultural_elements.get('closures', ['Divine blessings']))}
- Reference Style: {cultural_elements.get('references', 'vedic_tamil_integration')}
"""
        
        if 'focus' in cultural_elements:
            context += f"- Specialized Focus: {cultural_elements['focus']}\n"
        
        return context
    
    def _format_analysis_sections(self, analysis_sections: List[str]) -> str:
        """Format analysis sections for prompt"""
        if not analysis_sections:
            return "General analysis covering birth chart, current guidance, and remedial suggestions"
        
        formatted_sections = []
        for section in analysis_sections:
            formatted_sections.append(f"- {section.replace('_', ' ').title()}")
        
        return "\n".join(formatted_sections)

class AutomatedKnowledgeExpansion:
    """
    Handles automated daily knowledge expansion and learning
    """
    
    def __init__(self, database_pool, openai_client: AsyncOpenAI):
        self.db_pool = database_pool
        self.openai_client = openai_client
        
    async def daily_knowledge_update(self):
        """Main daily knowledge expansion process"""
        try:
            logger.info("Starting daily knowledge expansion...")
            
            # Update world knowledge with spiritual perspectives
            world_updates = await self._process_world_events()
            
            # Learn from user feedback and interactions
            user_learning = await self._process_user_feedback()
            
            # Update effectiveness tracking
            effectiveness_improvements = await self._analyze_knowledge_effectiveness()
            
            # Log the update
            await self._log_knowledge_update("daily_automated", "system", 
                                            world_updates + user_learning, 
                                            effectiveness_improvements)
            
            logger.info(f"Daily knowledge update completed: {world_updates + user_learning} new pieces added")
            
        except Exception as e:
            logger.error(f"Daily knowledge update error: {e}")
    
    async def _process_world_events(self) -> int:
        """Process current world events with spiritual perspective"""
        try:
            # This would integrate with news APIs in production
            # For now, add some sample current world wisdom
            current_wisdom = [
                {
                    "title": "Spiritual Perspective on Modern Technology",
                    "content": "As we navigate the digital age, ancient Vedic principles remind us that technology should serve dharma. The key is maintaining spiritual consciousness while embracing beneficial innovations. Saturn's influence in technology sectors suggests the need for responsible development.",
                    "domain": "world_knowledge",
                    "tags": ["technology", "modern_life", "dharma", "saturn"]
                },
                {
                    "title": "Economic Uncertainty and Spiritual Stability",
                    "content": "During times of economic volatility, Jupiter's wisdom teaches us that true wealth lies in spiritual knowledge and dharmic action. The classical text Chanakya Neeti emphasizes building both material and spiritual resources.",
                    "domain": "world_knowledge", 
                    "tags": ["economics", "jupiter", "stability", "chanakya"]
                }
            ]
            
            pieces_added = 0
            for wisdom in current_wisdom:
                if await self._add_knowledge_piece(wisdom):
                    pieces_added += 1
            
            return pieces_added
            
        except Exception as e:
            logger.error(f"World events processing error: {e}")
            return 0
    
    async def _process_user_feedback(self) -> int:
        """Learn from user interactions and feedback"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get recent high-rated interactions
                recent_feedback = await conn.fetch("""
                    SELECT session_id, knowledge_used, user_satisfaction, user_feedback
                    FROM knowledge_effectiveness_tracking
                    WHERE tracked_at > NOW() - INTERVAL '7 days'
                    AND user_satisfaction >= 4
                    ORDER BY user_satisfaction DESC
                    LIMIT 10
                """)
                
                learning_pieces = 0
                for feedback in recent_feedback:
                    # Extract successful patterns
                    if feedback["knowledge_used"] and feedback["user_satisfaction"] >= 4:
                        success_pattern = await self._extract_success_pattern(feedback)
                        if success_pattern and await self._add_knowledge_piece(success_pattern):
                            learning_pieces += 1
                
                return learning_pieces
                
        except Exception as e:
            logger.error(f"User feedback processing error: {e}")
            return 0
    
    async def _extract_success_pattern(self, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract successful guidance patterns from user feedback"""
        try:
            knowledge_used = feedback["knowledge_used"]
            satisfaction = feedback["user_satisfaction"]
            
            # Create a learning piece from successful interaction
            return {
                "title": f"Successful Guidance Pattern - Rating {satisfaction}/5",
                "content": f"This guidance approach achieved high user satisfaction ({satisfaction}/5). Knowledge domains used: {', '.join(knowledge_used.get('domains', []))}. User feedback indicates this combination of classical references with practical application resonates well.",
                "domain": "effectiveness_patterns",
                "tags": ["success_pattern", "user_satisfaction", f"rating_{satisfaction}"]
            }
            
        except Exception as e:
            logger.error(f"Success pattern extraction error: {e}")
            return None
    
    async def _analyze_knowledge_effectiveness(self) -> float:
        """Analyze overall knowledge effectiveness improvements"""
        try:
            async with self.db_pool.acquire() as conn:
                # Calculate average effectiveness metrics
                metrics = await conn.fetchrow("""
                    SELECT 
                        AVG(user_satisfaction) as avg_satisfaction,
                        COUNT(CASE WHEN prediction_accuracy = true THEN 1 END)::float / COUNT(*) as accuracy_rate,
                        COUNT(CASE WHEN remedy_effectiveness = true THEN 1 END)::float / COUNT(*) as remedy_success_rate
                    FROM knowledge_effectiveness_tracking
                    WHERE tracked_at > NOW() - INTERVAL '30 days'
                """)
                
                if metrics:
                    # Calculate composite effectiveness score
                    satisfaction = float(metrics["avg_satisfaction"] or 0) / 5.0
                    accuracy = float(metrics["accuracy_rate"] or 0)
                    remedy_success = float(metrics["remedy_success_rate"] or 0)
                    
                    composite_score = (satisfaction + accuracy + remedy_success) / 3.0
                    return composite_score
                
                return 0.0
                
        except Exception as e:
            logger.error(f"Effectiveness analysis error: {e}")
            return 0.0
    
    async def _add_knowledge_piece(self, knowledge_data: Dict[str, Any]) -> bool:
        """Add a new knowledge piece to the database"""
        try:
            # Generate embedding for the content
            rag_engine = RAGKnowledgeEngine(self.db_pool, os.getenv("OPENAI_API_KEY"))
            embedding = await rag_engine._generate_embedding(knowledge_data["content"])
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO rag_knowledge_base (
                        knowledge_domain, content_type, title, content, metadata,
                        embedding_vector, tags, source_reference, authority_level,
                        cultural_context, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
                """, 
                    knowledge_data["domain"],
                    knowledge_data.get("content_type", "generated_wisdom"),
                    knowledge_data["title"],
                    knowledge_data["content"],
                    json.dumps(knowledge_data.get("metadata", {})),
                    embedding,
                    knowledge_data.get("tags", []),
                    knowledge_data.get("source", "Automated Learning"),
                    knowledge_data.get("authority_level", 3),
                    knowledge_data.get("cultural_context", "universal")
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Knowledge piece addition error: {e}")
            return False
    
    async def _log_knowledge_update(self, update_type: str, source: str, 
                                  content_added: int, effectiveness_improvement: float):
        """Log knowledge update for tracking"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO automated_knowledge_updates (
                        update_type, source, content_added, effectiveness_improvement,
                        update_summary, processed_at
                    ) VALUES ($1, $2, $3, $4, $5, NOW())
                """,
                    update_type, source, content_added, effectiveness_improvement,
                    f"Added {content_added} knowledge pieces with {effectiveness_improvement:.4f} effectiveness improvement"
                )
                
        except Exception as e:
            logger.error(f"Knowledge update logging error: {e}")

# Initialize global instances
rag_engine = None
persona_engine = None
knowledge_expansion = None

async def initialize_rag_system(database_pool, openai_api_key: str):
    """Initialize the complete RAG system"""
    global rag_engine, persona_engine, knowledge_expansion
    
    rag_engine = RAGKnowledgeEngine(database_pool, openai_api_key)
    persona_engine = SwamiPersonaEngine(database_pool)
    knowledge_expansion = AutomatedKnowledgeExpansion(database_pool, AsyncOpenAI(api_key=openai_api_key))
    
    logger.info("RAG Knowledge Engine initialized successfully")
    
    return rag_engine, persona_engine, knowledge_expansion

async def get_rag_enhanced_guidance(user_query: str, birth_details: Optional[Dict[str, Any]], 
                                  service_type: str = "general") -> Dict[str, Any]:
    """
    Main interface for getting RAG-enhanced spiritual guidance with REAL PROKERALA INTEGRATION
    """
    try:
        if not rag_engine or not persona_engine:
            raise Exception("RAG system not initialized")
        
        # ENHANCED: Get real birth chart data from Prokerala if birth details provided
        enhanced_birth_details = birth_details
        if birth_details and all(birth_details.get(key) for key in ["date", "time", "location"]):
            try:
                from routers.sessions import get_prokerala_chart_data
                prokerala_data = await get_prokerala_chart_data(birth_details)
                
                # Enhance birth_details with real Prokerala calculations
                enhanced_birth_details = {
                    **birth_details,
                    "prokerala_response": prokerala_data,
                    "real_astrology": True
                }
                
                logger.info(f"Enhanced RAG with Prokerala data: {len(str(prokerala_data))} chars")
                
            except Exception as e:
                logger.warning(f"Prokerala integration failed in RAG: {e}")
                enhanced_birth_details = {
                    **birth_details,
                    "prokerala_error": str(e),
                    "real_astrology": False
                }
        
        # Create knowledge query with enhanced birth details
        query = KnowledgeQuery(
            primary_question=user_query,
            birth_details=enhanced_birth_details,
            service_type=service_type
        )
        
        # Retrieve relevant knowledge
        knowledge_retrieval = await rag_engine.retrieve_knowledge_for_query(query)
        
        # Get service configuration
        service_config = await rag_engine._get_service_configuration(service_type) or {}
        
        # Get appropriate persona
        persona_config = await persona_engine.get_persona_for_service(service_type, service_config)
        
        # Generate enhanced prompt
        enhanced_prompt = await persona_engine.generate_persona_enhanced_prompt(
            persona_config, knowledge_retrieval, user_query, service_config
        )
        
        # Generate response with OpenAI
        response = await rag_engine.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": user_query}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        
        enhanced_guidance = response.choices[0].message.content
        
        # Prepare response with transparency
        return {
            "enhanced_guidance": enhanced_guidance,
            "enhanced_birth_details": enhanced_birth_details,  # Include enhanced birth details
            "knowledge_sources": [
                {
                    "domain": k.knowledge_domain,
                    "source": k.source_reference,
                    "authority_level": k.authority_level,
                    "relevance": round(k.relevance_score, 3)
                }
                for k in knowledge_retrieval[:5]  # Top 5 sources
            ],
            "persona_mode": persona_config.persona_mode,
            "service_configuration": service_config.get("knowledge_configuration", {}),
            "analysis_sections": service_config.get("specialized_prompts", {}).get("analysis_sections", [])
        }
        
    except Exception as e:
        logger.error(f"RAG enhanced guidance error: {e}")
        return {
            "enhanced_guidance": "I apologize, but I'm experiencing some difficulty accessing my knowledge base right now. Please try again in a moment.",
            "knowledge_sources": [],
            "persona_mode": "general",
            "service_configuration": {},
            "analysis_sections": [],
            "error": str(e)
        }