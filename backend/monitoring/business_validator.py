"""
💼 BUSINESS LOGIC VALIDATOR - Validates spiritual guidance business logic
Ensures the integration chain produces high-quality, authentic spiritual guidance.
"""

import json
import logging
import time
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import re

# Try to import numpy, but handle gracefully if not installed
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Log warning after logger is properly imported
    pass

from db import db_manager
import logging
import os
import openai

logger = logging.getLogger(__name__)

# Log numpy availability warning if needed
if not NUMPY_AVAILABLE:
    logger.warning("numpy not installed - semantic similarity will use fallback calculation")

class BusinessLogicValidator:
    """
    Validates that the entire integration chain follows correct
    business logic and produces high-quality spiritual guidance.
    """
    
    def __init__(self):
        # Validate OpenAI API key is present
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError(
                "OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable."
            )
        
        try:
            self.openai_client = openai.AsyncClient(api_key=openai_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
            
        self.spiritual_keywords = self._load_spiritual_keywords()
        self.tamil_vedic_terms = self._load_tamil_vedic_terms()
        
        # Rate limiting and caching for OpenAI API
        self._embedding_cache = {}
        self._api_call_times = []
        self._max_calls_per_minute = 30  # Conservative rate limit
        
    async def validate_session(self, session_context: Dict) -> Dict:
        """Run comprehensive business logic validation for the entire session"""
        validation_result = {
            "overall_valid": True,
            "validations": {},
            "critical_issues": [],
            "warnings": [],
            "quality_scores": {},
            "recommendations": []
        }
        
        try:
            # 1. Validate integration chain completeness
            chain_validation = await self._validate_integration_chain(session_context)
            validation_result["validations"]["integration_chain"] = chain_validation
            
            # 2. Validate Prokerala data quality
            if "prokerala_data" in session_context["integration_results"]:
                prokerala_validation = await self._validate_prokerala_business_logic(
                    session_context["birth_details"],
                    session_context["integration_results"]["prokerala_data"]
                )
                validation_result["validations"]["prokerala"] = prokerala_validation
            
            # 3. Validate RAG knowledge relevance (USER SPECIFICALLY ASKED FOR THIS)
            if "rag_knowledge" in session_context["integration_results"]:
                rag_validation = await self._validate_rag_relevance(
                    session_context["spiritual_question"],
                    session_context["integration_results"]["rag_knowledge"],
                    session_context.get("birth_details", {})
                )
                validation_result["validations"]["rag_relevance"] = rag_validation
                validation_result["quality_scores"]["rag_relevance_score"] = rag_validation["overall_relevance"]
            
            # 4. Validate OpenAI response quality
            if "openai_guidance" in session_context["integration_results"]:
                openai_validation = await self._validate_openai_response_quality(
                    session_context["integration_results"]["openai_guidance"],
                    session_context
                )
                validation_result["validations"]["openai_quality"] = openai_validation
            
            # 5. Validate spiritual authenticity
            authenticity_validation = await self._validate_spiritual_authenticity(session_context)
            validation_result["validations"]["spiritual_authenticity"] = authenticity_validation
            
            # 6. Validate context preservation
            context_validation = await self._validate_context_preservation(session_context)
            validation_result["validations"]["context_preservation"] = context_validation
            
            # 7. Validate user experience quality
            ux_validation = await self._validate_user_experience_quality(session_context)
            validation_result["validations"]["user_experience"] = ux_validation
            
            # Compile critical issues
            for key, validation in validation_result["validations"].items():
                if not validation.get("valid", True):
                    if validation.get("severity", "error") == "critical":
                        validation_result["critical_issues"].append({
                            "type": key,
                            "description": validation.get("error", "Validation failed"),
                            "user_impact": validation.get("user_impact", "May affect guidance quality")
                        })
                        validation_result["overall_valid"] = False
                    else:
                        validation_result["warnings"].append({
                            "type": key,
                            "description": validation.get("warning", "Minor issue detected")
                        })
            
            # Generate recommendations
            validation_result["recommendations"] = await self._generate_recommendations(
                validation_result["validations"]
            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Business logic validation error: {e}")
            return {
                "overall_valid": False,
                "error": str(e),
                "critical_issues": [{
                    "type": "validation_error",
                    "description": f"Validation system error: {str(e)}",
                    "user_impact": "Cannot validate guidance quality"
                }]
            }
    
    async def _validate_integration_chain(self, session_context: Dict) -> Dict:
        """Validate that all required integrations were completed"""
        required_integrations = ["prokerala", "rag_knowledge", "openai_guidance"]
        optional_integrations = ["elevenlabs_voice", "did_avatar"]
        
        validation = {
            "valid": True,
            "missing_required": [],
            "missing_optional": [],
            "integration_sequence_correct": True
        }
        
        integration_results = session_context.get("integration_results", {})
        
        # Check required integrations
        for integration in required_integrations:
            if integration not in integration_results:
                validation["missing_required"].append(integration)
                validation["valid"] = False
            elif not integration_results[integration].get("passed", False):
                validation["missing_required"].append(f"{integration} (failed)")
                validation["valid"] = False
        
        # Check optional integrations
        for integration in optional_integrations:
            if integration not in integration_results:
                validation["missing_optional"].append(integration)
        
        # Validate sequence order
        if len(integration_results) > 1:
            integration_order = list(integration_results.keys())
            expected_order = ["prokerala", "rag_knowledge", "openai_guidance", "elevenlabs_voice", "did_avatar"]
            
            # Check if actual order follows expected order
            actual_positions = {int_name: i for i, int_name in enumerate(integration_order)}
            for i, int_name in enumerate(expected_order[:-1]):
                next_int = expected_order[i + 1]
                if int_name in actual_positions and next_int in actual_positions:
                    if actual_positions[int_name] > actual_positions[next_int]:
                        validation["integration_sequence_correct"] = False
                        validation["sequence_error"] = f"{int_name} executed after {next_int}"
        
        if validation["missing_required"]:
            validation["severity"] = "critical"
            validation["error"] = f"Missing required integrations: {', '.join(validation['missing_required'])}"
            validation["user_impact"] = "User will not receive complete spiritual guidance"
        
        return validation
    
    async def _validate_prokerala_business_logic(self, birth_details: Dict, prokerala_result: Dict) -> Dict:
        """Validate Prokerala API response business logic"""
        validation = {
            "valid": True,
            "birth_data_complete": True,
            "planetary_data_valid": True,
            "nakshatra_valid": True,
            "issues": []
        }
        
        try:
            # Check birth details completeness
            required_birth_fields = ["date", "time", "location"]
            for field in required_birth_fields:
                if field not in birth_details or not birth_details[field]:
                    validation["birth_data_complete"] = False
                    validation["issues"].append(f"Missing birth {field}")
            
            # Validate Prokerala response
            if prokerala_result.get("passed", False):
                output_data = prokerala_result.get("actual", {})
                
                # Check planetary data
                if "planets" not in output_data or not output_data["planets"]:
                    validation["planetary_data_valid"] = False
                    validation["issues"].append("No planetary data in response")
                
                # Check nakshatra
                if "nakshatra" not in output_data or not output_data["nakshatra"]:
                    validation["nakshatra_valid"] = False
                    validation["issues"].append("No nakshatra data in response")
                
                # Validate data sanity
                if "planets" in output_data and isinstance(output_data["planets"], list):
                    # Check if all major planets are present
                    planet_names = [p.get("name", "").lower() for p in output_data["planets"]]
                    major_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
                    missing_planets = [p for p in major_planets if p not in planet_names]
                    
                    if missing_planets:
                        validation["issues"].append(f"Missing planets: {', '.join(missing_planets)}")
                        validation["planetary_data_valid"] = False
            else:
                validation["valid"] = False
                validation["error"] = "Prokerala API call failed"
                validation["severity"] = "critical"
                validation["user_impact"] = "Cannot provide accurate astrological guidance"
            
            if validation["issues"]:
                validation["valid"] = False
                validation["warning"] = f"Prokerala data issues: {'; '.join(validation['issues'])}"
            
            return validation
            
        except Exception as e:
            logger.error(f"Prokerala validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    async def _validate_rag_relevance(self, user_question: str, rag_result: Dict, birth_context: Dict) -> Dict:
        """
        Comprehensive RAG relevance validation - USER SPECIFICALLY NEEDS THIS
        """
        validation = {
            "valid": True,
            "overall_relevance": 0.0,
            "keyword_match": 0.0,
            "domain_match": 0.0,
            "astro_relevance": 0.0,
            "semantic_similarity": 0.0,
            "cultural_authenticity": 0.0,
            "is_relevant": False,
            "improvement_suggestions": []
        }
        
        try:
            if not rag_result.get("passed", False):
                validation["valid"] = False
                validation["error"] = "RAG retrieval failed"
                return validation
            
            retrieved_knowledge = rag_result.get("actual", {}).get("knowledge", "")
            if not retrieved_knowledge:
                validation["valid"] = False
                validation["error"] = "No knowledge retrieved"
                return validation
            
            # Method 1: Keyword Analysis
            question_keywords = self._extract_spiritual_keywords(user_question)
            knowledge_keywords = self._extract_spiritual_keywords(retrieved_knowledge)
            validation["keyword_match"] = self._calculate_weighted_overlap(
                question_keywords, knowledge_keywords
            )
            
            # Method 2: Spiritual Domain Matching
            question_domain = self._classify_spiritual_domain(user_question)
            knowledge_domains = self._extract_knowledge_domains(retrieved_knowledge)
            validation["domain_match"] = self._calculate_domain_relevance(
                question_domain, knowledge_domains
            )
            
            # Method 3: Birth Chart Context Relevance
            astrological_elements = self._extract_astrological_elements(birth_context)
            knowledge_astro_refs = self._extract_astrological_references(retrieved_knowledge)
            validation["astro_relevance"] = self._calculate_astro_context_match(
                astrological_elements, knowledge_astro_refs
            )
            
            # Method 4: Semantic Similarity (Using OpenAI Embeddings)
            validation["semantic_similarity"] = await self._calculate_semantic_similarity(
                user_question, retrieved_knowledge
            )
            
            # Method 5: Tamil/Vedic Cultural Context
            validation["cultural_authenticity"] = self._validate_cultural_authenticity(
                retrieved_knowledge, birth_context
            )
            
            # Combined Relevance Score
            validation["overall_relevance"] = (
                validation["keyword_match"] * 0.25 +
                validation["domain_match"] * 0.30 +
                validation["astro_relevance"] * 0.20 +
                validation["semantic_similarity"] * 0.15 +
                validation["cultural_authenticity"] * 0.10
            )
            
            validation["is_relevant"] = validation["overall_relevance"] > 0.65
            
            if not validation["is_relevant"]:
                validation["valid"] = False
                validation["severity"] = "error"
                validation["error"] = f"RAG knowledge not relevant (score: {validation['overall_relevance']:.2f})"
                validation["user_impact"] = "User may receive generic instead of personalized guidance"
                
                # Generate improvement suggestions
                validation["improvement_suggestions"] = self._generate_rag_improvement_suggestions(
                    user_question, retrieved_knowledge, validation
                )
            
            return validation
            
        except Exception as e:
            logger.error(f"RAG relevance validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    async def _validate_openai_response_quality(self, openai_result: Dict, session_context: Dict) -> Dict:
        """Validate OpenAI response quality and context usage"""
        validation = {
            "valid": True,
            "uses_swami_persona": False,
            "includes_birth_context": False,
            "incorporates_rag_knowledge": False,
            "appropriate_length": False,
            "spiritual_tone": False,
            "cultural_authenticity": False,
            "quality_score": 0.0
        }
        
        try:
            if not openai_result.get("passed", False):
                validation["valid"] = False
                validation["error"] = "OpenAI generation failed"
                return validation
            
            response = openai_result.get("actual", {}).get("response", "")
            if not response:
                validation["valid"] = False
                validation["error"] = "Empty OpenAI response"
                return validation
            
            # Check Swami persona language patterns
            swami_patterns = [
                r"my child", r"dear one", r"blessed one", r"divine", 
                r"cosmic", r"spiritual", r"soul", r"karma", r"dharma"
            ]
            validation["uses_swami_persona"] = any(
                re.search(pattern, response.lower()) for pattern in swami_patterns
            )
            
            # Check birth chart references
            birth_context = session_context.get("birth_details", {})
            if birth_context:
                birth_references = ["nakshatra", "rasi", "planet", "house", "dasha"]
                validation["includes_birth_context"] = any(
                    ref in response.lower() for ref in birth_references
                )
            
            # Check RAG knowledge incorporation
            rag_knowledge = session_context.get("integration_results", {}).get(
                "rag_knowledge", {}
            ).get("actual", {}).get("knowledge", "")
            
            if rag_knowledge:
                # Check if key phrases from RAG appear in response
                rag_keywords = self._extract_key_phrases(rag_knowledge)[:5]
                matches = sum(1 for keyword in rag_keywords if keyword.lower() in response.lower())
                validation["incorporates_rag_knowledge"] = matches >= 2
            
            # Check response length
            word_count = len(response.split())
            validation["appropriate_length"] = 100 <= word_count <= 300
            
            # Check spiritual tone
            validation["spiritual_tone"] = self._check_spiritual_tone(response)
            
            # Check cultural authenticity
            validation["cultural_authenticity"] = self._check_tamil_vedic_references(response)
            
            # Calculate quality score
            quality_checks = [
                validation["uses_swami_persona"],
                validation["includes_birth_context"],
                validation["incorporates_rag_knowledge"],
                validation["appropriate_length"],
                validation["spiritual_tone"],
                validation["cultural_authenticity"]
            ]
            validation["quality_score"] = sum(quality_checks) / len(quality_checks)
            
            if validation["quality_score"] < 0.6:
                validation["valid"] = False
                validation["severity"] = "error"
                validation["error"] = f"Low quality response (score: {validation['quality_score']:.2f})"
                
                # Add detailed feedback on specific quality issues
                quality_feedback = []
                if not validation["uses_swami_persona"]:
                    quality_feedback.append("Missing authentic Swami persona and speech patterns")
                if not validation["includes_birth_context"]:
                    quality_feedback.append("Birth chart context not properly incorporated")
                if not validation["incorporates_rag_knowledge"]:
                    quality_feedback.append("RAG knowledge not effectively utilized")
                if not validation["appropriate_length"]:
                    quality_feedback.append("Response length inappropriate for spiritual guidance")
                if not validation["spiritual_tone"]:
                    quality_feedback.append("Lacks proper spiritual tone and reverence")
                if not validation["cultural_authenticity"]:
                    quality_feedback.append("Missing Tamil/Vedic cultural authenticity")
                
                validation["quality_feedback"] = quality_feedback
                validation["improvement_suggestions"] = self._generate_quality_improvement_suggestions(quality_feedback)
                validation["user_impact"] = "User receives low quality spiritual guidance"
            
            return validation
            
        except Exception as e:
            logger.error(f"OpenAI validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    def _generate_quality_improvement_suggestions(self, quality_feedback: List[str]) -> List[str]:
        """Generate specific improvement suggestions based on quality feedback"""
        suggestions = []
        
        if "Missing authentic Swami persona and speech patterns" in quality_feedback:
            suggestions.append("Include phrases like 'my child', 'divine wisdom shows', 'let me guide you'")
        
        if "Birth chart context not properly incorporated" in quality_feedback:
            suggestions.append("Reference specific planetary positions, houses, or nakshatra from birth chart")
        
        if "RAG knowledge not effectively utilized" in quality_feedback:
            suggestions.append("Integrate relevant Vedic principles and classical astrology concepts")
        
        if "Response length inappropriate for spiritual guidance" in quality_feedback:
            suggestions.append("Provide more comprehensive guidance (aim for 150-300 words)")
        
        if "Lacks proper spiritual tone and reverence" in quality_feedback:
            suggestions.append("Use respectful, compassionate language befitting spiritual guidance")
        
        if "Missing Tamil/Vedic cultural authenticity" in quality_feedback:
            suggestions.append("Include Sanskrit terms, Tamil cultural references, or Vedic concepts")
        
        return suggestions
    
    def _get_embedding_cache_key(self, text: str) -> str:
        """Generate cache key for embedding"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def _rate_limited_api_call(self):
        """Implement rate limiting for OpenAI API calls"""
        current_time = time.time()
        
        # Remove calls older than 1 minute
        self._api_call_times = [t for t in self._api_call_times if current_time - t < 60]
        
        # Check if we're at the rate limit
        if len(self._api_call_times) >= self._max_calls_per_minute:
            sleep_time = 60 - (current_time - self._api_call_times[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        # Record this API call
        self._api_call_times.append(current_time)
     
    async def _validate_spiritual_authenticity(self, session_context: Dict) -> Dict:
        """Validate overall spiritual authenticity of the guidance"""
        validation = {
            "valid": True,
            "authenticity_score": 0.0,
            "respectful_language": True,
            "cultural_accuracy": True,
            "appropriate_tone": True,
            "factual_accuracy": True,
            "persona_consistency": True
        }
        
        try:
            # Get the final response
            openai_result = session_context.get("integration_results", {}).get("openai_guidance", {})
            response = openai_result.get("actual", {}).get("response", "")
            
            if not response:
                validation["valid"] = False
                validation["error"] = "No response to validate"
                return validation
            
            # Check respectful spiritual language
            disrespectful_terms = ["fake", "stupid", "nonsense", "scam", "fool"]
            validation["respectful_language"] = not any(
                term in response.lower() for term in disrespectful_terms
            )
            
            # Check cultural accuracy
            validation["cultural_accuracy"] = self._validate_tamil_vedic_references(response)
            
            # Check appropriate tone
            validation["appropriate_tone"] = self._check_spiritual_guidance_tone(response)
            
            # Check factual accuracy (basic astrology facts)
            validation["factual_accuracy"] = self._validate_astrological_facts(response)
            
            # Check Swami persona consistency
            validation["persona_consistency"] = self._check_swami_persona_consistency(response)
            
            # Calculate authenticity score
            authenticity_checks = [
                validation["respectful_language"],
                validation["cultural_accuracy"],
                validation["appropriate_tone"],
                validation["factual_accuracy"],
                validation["persona_consistency"]
            ]
            validation["authenticity_score"] = sum(authenticity_checks) / len(authenticity_checks)
            
            if validation["authenticity_score"] < 0.8:
                validation["valid"] = False
                validation["warning"] = f"Low spiritual authenticity (score: {validation['authenticity_score']:.2f})"
                validation["improvements"] = self._generate_authenticity_improvements(validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Spiritual authenticity validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    async def _validate_context_preservation(self, session_context: Dict) -> Dict:
        """Validate that context is preserved through the chain"""
        validation = {
            "valid": True,
            "context_preserved": True,
            "critical_data_intact": True,
            "missing_fields": []
        }
        
        try:
            # Check if birth details are preserved
            if "birth_details" in session_context:
                birth_details = session_context["birth_details"]
                
                # Check if birth details appear in OpenAI context
                openai_result = session_context.get("integration_results", {}).get("openai_guidance", {})
                if openai_result.get("passed", False):
                    # This would be enhanced with actual context checking
                    validation["context_preserved"] = True
            
            # Check for data loss events
            if session_context.get("data_loss_detected", False):
                validation["context_preserved"] = False
                validation["valid"] = False
                validation["error"] = "Critical context lost during integration"
                validation["severity"] = "critical"
                validation["user_impact"] = "Personalized guidance may be compromised"
            
            return validation
            
        except Exception as e:
            logger.error(f"Context preservation validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    async def _validate_user_experience_quality(self, session_context: Dict) -> Dict:
        """Validate overall user experience quality"""
        validation = {
            "valid": True,
            "response_time_acceptable": True,
            "guidance_complete": True,
            "personalization_level": 0.0,
            "overall_quality": 0.0
        }
        
        try:
            # Check response time
            total_duration = sum(
                result.get("duration_ms", 0) 
                for result in session_context.get("integration_results", {}).values()
            )
            validation["response_time_acceptable"] = total_duration < 15000  # 15 seconds
            
            # Check guidance completeness
            required_elements = ["greeting", "analysis", "guidance", "conclusion"]
            response = session_context.get("integration_results", {}).get(
                "openai_guidance", {}
            ).get("actual", {}).get("response", "")
            
            if response:
                validation["guidance_complete"] = len(response) > 200  # Basic check
            
            # Calculate personalization level
            birth_mentioned = "birth" in response.lower() or "nakshatra" in response.lower()
            question_addressed = any(
                word in response.lower() 
                for word in session_context.get("spiritual_question", "").lower().split()
            )
            validation["personalization_level"] = (
                (1.0 if birth_mentioned else 0.0) + 
                (1.0 if question_addressed else 0.0)
            ) / 2
            
            # Calculate overall quality
            quality_factors = [
                validation["response_time_acceptable"],
                validation["guidance_complete"],
                validation["personalization_level"] > 0.5
            ]
            validation["overall_quality"] = sum(quality_factors) / len(quality_factors)
            
            if validation["overall_quality"] < 0.7:
                validation["warning"] = "User experience quality below threshold"
            
            return validation
            
        except Exception as e:
            logger.error(f"User experience validation error: {e}")
            validation["valid"] = False
            validation["error"] = str(e)
            return validation
    
    async def _generate_recommendations(self, validations: Dict) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check each validation area
        if not validations.get("integration_chain", {}).get("valid", True):
            recommendations.append("Fix missing integrations in the spiritual guidance flow")
        
        if validations.get("rag_relevance", {}).get("overall_relevance", 1.0) < 0.65:
            recommendations.append("Enhance RAG query generation for better knowledge retrieval")
            suggestions = validations.get("rag_relevance", {}).get("improvement_suggestions", [])
            recommendations.extend(suggestions[:3])  # Top 3 suggestions
        
        if validations.get("openai_quality", {}).get("quality_score", 1.0) < 0.6:
            recommendations.append("Improve OpenAI prompt to ensure context usage")
            if not validations.get("openai_quality", {}).get("includes_birth_context", True):
                recommendations.append("Ensure birth chart data is included in OpenAI prompt")
            if not validations.get("openai_quality", {}).get("incorporates_rag_knowledge", True):
                recommendations.append("Ensure RAG knowledge is incorporated in the response")
        
        if validations.get("spiritual_authenticity", {}).get("authenticity_score", 1.0) < 0.8:
            recommendations.append("Enhance spiritual authenticity with more Tamil/Vedic references")
        
        if validations.get("user_experience", {}).get("overall_quality", 1.0) < 0.7:
            recommendations.append("Optimize integration performance for faster response times")
        
        return recommendations
    
    # Helper methods for spiritual keyword and domain analysis
    def _load_spiritual_keywords(self) -> Dict[str, List[str]]:
        """Load spiritual keywords for analysis"""
        return {
            "career": ["job", "work", "career", "profession", "business", "success", "money", "wealth", "promotion", "employment"],
            "relationships": ["love", "marriage", "partner", "relationship", "family", "spouse", "compatibility", "divorce", "separation"],
            "health": ["health", "illness", "healing", "medicine", "body", "wellness", "disease", "treatment", "recovery"],
            "spiritual": ["dharma", "karma", "moksha", "meditation", "prayer", "temple", "spiritual", "soul", "enlightenment"],
            "astrology": ["planet", "star", "nakshatra", "rasi", "dasha", "graha", "house", "horoscope", "chart"]
        }
    
    def _load_tamil_vedic_terms(self) -> List[str]:
        """Load Tamil and Vedic spiritual terms"""
        return [
            "dharma", "karma", "moksha", "satsang", "guru", "swami", "mantra", 
            "yantra", "tantra", "veda", "upanishad", "nakshatra", "rasi", "dasha", 
            "graha", "bhava", "puja", "homam", "abhishekam", "pradosham", "thiruvadhirai"
        ]
    
    def _extract_spiritual_keywords(self, text: str) -> List[Tuple[str, str]]:
        """Extract spiritually relevant keywords from text"""
        found_keywords = []
        text_lower = text.lower()
        
        for category, keywords in self.spiritual_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append((keyword, category))
        
        return found_keywords
    
    def _classify_spiritual_domain(self, question: str) -> str:
        """Classify user question into spiritual domain"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["career", "job", "work", "business", "money", "profession"]):
            return "career_astrology"
        elif any(word in question_lower for word in ["love", "marriage", "relationship", "partner", "spouse"]):
            return "relationship_astrology"
        elif any(word in question_lower for word in ["health", "illness", "body", "wellness", "healing"]):
            return "health_astrology"
        elif any(word in question_lower for word in ["remedy", "solution", "problem", "trouble"]):
            return "remedial_measures"
        else:
            return "classical_astrology"
    
    def _extract_knowledge_domains(self, knowledge_text: str) -> List[str]:
        """Extract knowledge domains from retrieved text"""
        domains = []
        domain_keywords = {
            "career_astrology": ["career", "profession", "job", "work"],
            "relationship_astrology": ["love", "marriage", "relationship"],
            "health_astrology": ["health", "wellness", "healing"],
            "remedial_measures": ["remedy", "solution", "puja", "mantra"],
            "classical_astrology": ["nakshatra", "graha", "dasha", "rasi"]
        }
        
        text_lower = knowledge_text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains
    
    def _calculate_weighted_overlap(self, keywords1: List[Tuple[str, str]], 
                                  keywords2: List[Tuple[str, str]]) -> float:
        """Calculate weighted overlap between keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
        
        # Extract just the keywords
        words1 = set(k[0] for k in keywords1)
        words2 = set(k[0] for k in keywords2)
        
        # Calculate overlap
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        return overlap / total if total > 0 else 0.0
    
    def _calculate_domain_relevance(self, question_domain: str, knowledge_domains: List[str]) -> float:
        """Calculate domain relevance score"""
        if not knowledge_domains:
            return 0.0
        
        if question_domain in knowledge_domains:
            return 1.0
        
        # Partial credit for related domains
        related_domains = {
            "career_astrology": ["classical_astrology", "remedial_measures"],
            "relationship_astrology": ["classical_astrology", "remedial_measures"],
            "health_astrology": ["classical_astrology", "remedial_measures"],
            "remedial_measures": ["career_astrology", "relationship_astrology", "health_astrology"],
            "classical_astrology": ["career_astrology", "relationship_astrology", "health_astrology"]
        }
        
        related = related_domains.get(question_domain, [])
        overlap = len(set(related) & set(knowledge_domains))
        
        return 0.5 * (overlap / len(related)) if related else 0.0
    
    def _extract_astrological_elements(self, birth_context: Dict) -> List[str]:
        """Extract astrological elements from birth context"""
        elements = []
        
        # This would be enhanced with actual birth chart parsing
        if birth_context:
            elements.extend(["birth_chart", "natal_positions"])
        
        return elements
    
    def _extract_astrological_references(self, text: str) -> List[str]:
        """Extract astrological references from text"""
        astro_terms = [
            "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
            "rahu", "ketu", "nakshatra", "rasi", "dasha", "bhava", "house",
            "ascendant", "lagna", "navamsa", "aspect", "conjunction"
        ]
        
        found_refs = []
        text_lower = text.lower()
        
        for term in astro_terms:
            if term in text_lower:
                found_refs.append(term)
        
        return found_refs
    
    def _calculate_astro_context_match(self, birth_elements: List[str], 
                                     knowledge_refs: List[str]) -> float:
        """Calculate astrological context match score"""
        if not knowledge_refs:
            return 0.0
        
        # Basic scoring based on presence of astrological terms
        score = min(len(knowledge_refs) / 5, 1.0)  # Cap at 1.0
        
        return score
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using OpenAI embeddings with caching and rate limiting"""
        try:
            # Check cache first
            cache_key1 = self._get_embedding_cache_key(text1)
            cache_key2 = self._get_embedding_cache_key(text2)
            
            # Get embeddings (with caching)
            if cache_key1 in self._embedding_cache:
                embedding1 = self._embedding_cache[cache_key1]
            else:
                await self._rate_limited_api_call()
                embedding1_response = await self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text1[:8000]  # Limit input length
                )
                embedding1 = embedding1_response.data[0].embedding
                self._embedding_cache[cache_key1] = embedding1
            
            if cache_key2 in self._embedding_cache:
                embedding2 = self._embedding_cache[cache_key2]
            else:
                await self._rate_limited_api_call()
                embedding2_response = await self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text2[:8000]  # Limit input length
                )
                embedding2 = embedding2_response.data[0].embedding
                self._embedding_cache[cache_key2] = embedding2
            
            # Calculate cosine similarity
            if NUMPY_AVAILABLE:
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                
                similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
            else:
                # Fallback: manual cosine similarity calculation without numpy
                dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
                norm1 = sum(a * a for a in embedding1) ** 0.5
                norm2 = sum(b * b for b in embedding2) ** 0.5
                
                similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation error: {e}")
            return 0.5  # Default middle score on error
    
    def _validate_cultural_authenticity(self, text: str, birth_context: Dict) -> float:
        """Validate Tamil/Vedic cultural authenticity"""
        tamil_score = sum(1 for term in self.tamil_vedic_terms if term.lower() in text.lower())
        tamil_score = tamil_score / len(self.tamil_vedic_terms) if self.tamil_vedic_terms else 0
        
        # Check for cultural context based on birth location
        if birth_context.get("location", "").lower() in ["chennai", "tamil nadu", "india"]:
            tamil_score *= 1.2  # Boost score for Tamil context
        
        return min(tamil_score, 1.0)
    
    def _generate_rag_improvement_suggestions(self, question: str, 
                                            retrieved_knowledge: str,
                                            validation: Dict) -> List[str]:
        """Generate specific suggestions to improve RAG retrieval"""
        suggestions = []
        
        if validation["keyword_match"] < 0.5:
            suggestions.append("Enhance keyword extraction to better match user questions")
        
        if validation["domain_match"] < 0.5:
            suggestions.append(f"Query '{self._classify_spiritual_domain(question)}' domain more specifically")
        
        if validation["astro_relevance"] < 0.5:
            suggestions.append("Include more astrological context in RAG queries")
        
        if validation["semantic_similarity"] < 0.6:
            suggestions.append("Use semantic search enhancements for better relevance")
        
        if validation["cultural_authenticity"] < 0.5:
            suggestions.append("Prioritize Tamil/Vedic cultural knowledge sources")
        
        return suggestions
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text for matching"""
        # Simple extraction - would be enhanced with NLP
        words = text.lower().split()
        phrases = []
        
        # Extract 2-3 word phrases
        for i in range(len(words) - 1):
            phrase = " ".join(words[i:i+2])
            if len(phrase) > 5:  # Skip very short phrases
                phrases.append(phrase)
        
        return phrases[:10]  # Top 10 phrases
    
    def _check_spiritual_tone(self, text: str) -> bool:
        """Check if text has appropriate spiritual tone"""
        spiritual_indicators = [
            "blessed", "divine", "spiritual", "cosmic", "soul", "sacred",
            "wisdom", "guidance", "enlightenment", "journey", "path"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in spiritual_indicators if indicator in text_lower)
        
        return matches >= 3
    
    def _check_tamil_vedic_references(self, text: str) -> bool:
        """Check for Tamil/Vedic references"""
        text_lower = text.lower()
        matches = sum(1 for term in self.tamil_vedic_terms if term in text_lower)
        
        return matches >= 2
    
    def _validate_tamil_vedic_references(self, text: str) -> bool:
        """Validate accuracy of Tamil/Vedic references"""
        # Basic validation - would be enhanced with knowledge base
        return self._check_tamil_vedic_references(text)
    
    def _check_spiritual_guidance_tone(self, text: str) -> bool:
        """Check if guidance has appropriate tone"""
        positive_indicators = ["hope", "guidance", "blessed", "divine", "wisdom"]
        negative_indicators = ["doom", "curse", "bad luck", "hopeless", "terrible fate"]
        
        text_lower = text.lower()
        positive_count = sum(1 for ind in positive_indicators if ind in text_lower)
        negative_count = sum(1 for ind in negative_indicators if ind in text_lower)
        
        return positive_count > negative_count
    
    def _validate_astrological_facts(self, text: str) -> bool:
        """Validate basic astrological facts"""
        # Check for obvious errors
        errors = [
            "13 zodiac signs",  # Should be 12
            "28 nakshatras",    # Should be 27
            "8 planets",        # Should be 9 in Vedic
        ]
        
        text_lower = text.lower()
        return not any(error in text_lower for error in errors)
    
    def _check_swami_persona_consistency(self, text: str) -> bool:
        """Check Swami persona consistency"""
        persona_indicators = [
            "my child", "dear one", "blessed one", "i see", "the cosmos reveals"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in persona_indicators if indicator in text_lower)
        
        return matches >= 1
    
    def _generate_authenticity_improvements(self, validation: Dict) -> List[str]:
        """Generate improvements for spiritual authenticity"""
        improvements = []
        
        if not validation["respectful_language"]:
            improvements.append("Ensure all language is respectful and spiritual")
        
        if not validation["cultural_accuracy"]:
            improvements.append("Add more authentic Tamil/Vedic references")
        
        if not validation["appropriate_tone"]:
            improvements.append("Adjust tone to be more compassionate and guiding")
        
        if not validation["persona_consistency"]:
            improvements.append("Strengthen Swami persona voice and mannerisms")
        
        return improvements