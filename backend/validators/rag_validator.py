"""
📚 RAG VALIDATOR - Validates RAG knowledge retrieval relevance
USER SPECIFICALLY REQUESTED THIS - Comprehensive relevance validation.
"""

from typing import Dict, List, Tuple
import re

# Try to import numpy, but handle gracefully if not installed
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Log warning after logger is properly imported
    pass

import logging
logger = logging.getLogger(__name__)
import openai

class RAGValidator:
    """
    Validates RAG knowledge retrieval for relevance and quality.
    Implements comprehensive validation methods as requested by user.
    """
    
    def __init__(self):
        # Log numpy availability warning if needed
        if not NUMPY_AVAILABLE:
            logger.warning("numpy not installed - semantic similarity will use fallback calculation")
            
        self.openai_client = openai.AsyncClient(api_key=settings.openai_api_key)
        self.spiritual_keywords = self._load_spiritual_keywords()
        self.domain_keywords = self._load_domain_keywords()
        
    async def validate(self, input_data: Dict, output_data: Dict, session_context: Dict) -> Dict:
        """Validate RAG knowledge retrieval relevance"""
        validation_result = {
            "passed": True,
            "validation_type": "rag_knowledge_relevance",
            "errors": [],
            "warnings": [],
            "auto_fixable": False,
            "expected": {},
            "actual": output_data,
            "relevance_scores": {}
        }
        
        try:
            # Extract user question and retrieved knowledge
            user_question = input_data.get("question", "") or session_context.get("spiritual_question", "")
            retrieved_knowledge = output_data.get("knowledge", "") or output_data.get("retrieved_text", "")
            
            if not user_question:
                validation_result["passed"] = False
                validation_result["errors"].append("No user question found")
                return validation_result
            
            if not retrieved_knowledge:
                validation_result["passed"] = False
                validation_result["errors"].append("No knowledge retrieved from RAG")
                validation_result["severity"] = "critical"
                validation_result["user_impact"] = "Generic guidance instead of personalized knowledge"
                validation_result["auto_fixable"] = True
                validation_result["auto_fix_type"] = "retry_with_enhanced_query"
                return validation_result
            
            # Run comprehensive relevance validation
            relevance_analysis = await self._comprehensive_relevance_check(
                user_question, 
                retrieved_knowledge,
                session_context.get("birth_details", {})
            )
            
            validation_result["relevance_scores"] = relevance_analysis
            validation_result["overall_relevance"] = relevance_analysis["overall_relevance"]
            
            # Check if relevance meets threshold
            if relevance_analysis["overall_relevance"] < 0.65:
                validation_result["passed"] = False
                validation_result["severity"] = "error"
                validation_result["errors"].append(
                    f"Low relevance score: {relevance_analysis['overall_relevance']:.2f} (threshold: 0.65)"
                )
                validation_result["user_impact"] = "User may receive irrelevant or generic guidance"
                validation_result["auto_fixable"] = True
                validation_result["auto_fix_type"] = "enhance_query"
                
                # Add specific improvement suggestions
                validation_result["improvement_suggestions"] = self._generate_improvement_suggestions(
                    relevance_analysis, user_question, retrieved_knowledge
                )
            
            # Check for specific issues
            if relevance_analysis["keyword_match"] < 0.3:
                validation_result["warnings"].append("Poor keyword match between question and knowledge")
            
            if relevance_analysis["domain_match"] < 0.5:
                validation_result["warnings"].append("Knowledge domain doesn't match question domain")
            
            if relevance_analysis["cultural_authenticity"] < 0.3:
                validation_result["warnings"].append("Low Tamil/Vedic cultural relevance")
            
            # Set expected values
            validation_result["expected"] = {
                "minimum_relevance": 0.65,
                "minimum_keyword_match": 0.3,
                "minimum_domain_match": 0.5,
                "user_question": user_question
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"RAG validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def auto_fix(self, validation_result: Dict, session_context: Dict) -> Dict:
        """Attempt to auto-fix RAG retrieval issues"""
        fix_result = {
            "fixed": False,
            "fix_type": None,
            "retry_needed": False,
            "enhanced_query": None
        }
        
        try:
            if validation_result.get("auto_fix_type") == "enhance_query":
                # Generate enhanced query
                user_question = session_context.get("spiritual_question", "")
                birth_details = session_context.get("birth_details", {})
                
                enhanced_query = await self._generate_enhanced_query(
                    user_question, 
                    birth_details,
                    validation_result.get("relevance_scores", {})
                )
                
                fix_result["fixed"] = True
                fix_result["fix_type"] = "enhanced_query"
                fix_result["enhanced_query"] = enhanced_query
                fix_result["retry_needed"] = True
                fix_result["message"] = "Generated enhanced query for better relevance"
                
            elif validation_result.get("auto_fix_type") == "retry_with_enhanced_query":
                # Retry with different knowledge domains
                fix_result["fixed"] = True
                fix_result["fix_type"] = "expand_domains"
                fix_result["expanded_domains"] = self._get_expanded_domains(
                    session_context.get("spiritual_question", "")
                )
                fix_result["retry_needed"] = True
                
            return fix_result
            
        except Exception as e:
            logger.error(f"RAG auto-fix error: {e}")
            return fix_result
    
    async def _comprehensive_relevance_check(self, user_question: str, 
                                           retrieved_knowledge: str, 
                                           birth_context: Dict) -> Dict:
        """
        Comprehensive RAG relevance validation as requested by user.
        Implements multiple methods to ensure knowledge relevance.
        """
        
        # Method 1: Keyword Analysis
        question_keywords = self._extract_spiritual_keywords(user_question)
        knowledge_keywords = self._extract_spiritual_keywords(retrieved_knowledge)
        keyword_match = self._calculate_weighted_overlap(question_keywords, knowledge_keywords)
        
        # Method 2: Spiritual Domain Matching
        question_domain = self._classify_spiritual_domain(user_question)
        knowledge_domains = self._extract_knowledge_domains(retrieved_knowledge)
        domain_match = self._calculate_domain_relevance(question_domain, knowledge_domains)
        
        # Method 3: Birth Chart Context Relevance
        astrological_elements = self._extract_astrological_elements(birth_context)
        knowledge_astro_refs = self._extract_astrological_references(retrieved_knowledge)
        astro_relevance = self._calculate_astro_context_match(astrological_elements, knowledge_astro_refs)
        
        # Method 4: Semantic Similarity
        semantic_similarity = await self._calculate_semantic_similarity(user_question, retrieved_knowledge)
        
        # Method 5: Tamil/Vedic Cultural Context
        cultural_authenticity = self._validate_cultural_authenticity(retrieved_knowledge, birth_context)
        
        # Method 6: Question-Answer Alignment
        qa_alignment = self._check_question_answer_alignment(user_question, retrieved_knowledge)
        
        # Combined Relevance Score (weighted)
        overall_relevance = (
            keyword_match * 0.20 +
            domain_match * 0.25 +
            astro_relevance * 0.15 +
            semantic_similarity * 0.20 +
            cultural_authenticity * 0.10 +
            qa_alignment * 0.10
        )
        
        return {
            "overall_relevance": overall_relevance,
            "keyword_match": keyword_match,
            "domain_match": domain_match,
            "astro_relevance": astro_relevance,
            "semantic_similarity": semantic_similarity,
            "cultural_authenticity": cultural_authenticity,
            "qa_alignment": qa_alignment,
            "question_domain": question_domain,
            "knowledge_domains": knowledge_domains
        }
    
    def _extract_spiritual_keywords(self, text: str) -> List[Tuple[str, str, float]]:
        """Extract spiritually relevant keywords with categories and weights"""
        found_keywords = []
        text_lower = text.lower()
        
        # Extract keywords with importance weights
        for category, keywords in self.spiritual_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Calculate importance based on frequency and position
                    count = text_lower.count(keyword)
                    first_pos = text_lower.find(keyword) / len(text_lower) if len(text_lower) > 0 else 1
                    importance = count * (1 - first_pos * 0.5)  # Earlier mentions are more important
                    
                    found_keywords.append((keyword, category, importance))
        
        # Sort by importance
        found_keywords.sort(key=lambda x: x[2], reverse=True)
        return found_keywords
    
    def _classify_spiritual_domain(self, question: str) -> str:
        """Classify user question into spiritual domain"""
        question_lower = question.lower()
        
        domain_scores = {
            "career_astrology": 0,
            "relationship_astrology": 0,
            "health_astrology": 0,
            "remedial_measures": 0,
            "classical_astrology": 0,
            "spiritual_growth": 0
        }
        
        # Score each domain based on keyword presence
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    domain_scores[domain] += 1
        
        # Return domain with highest score
        max_domain = max(domain_scores, key=domain_scores.get)
        return max_domain if domain_scores[max_domain] > 0 else "classical_astrology"
    
    def _extract_knowledge_domains(self, knowledge_text: str) -> List[str]:
        """Extract knowledge domains from retrieved text"""
        domains = []
        text_lower = knowledge_text.lower()
        
        for domain, keywords in self.domain_keywords.items():
            domain_score = sum(1 for keyword in keywords if keyword in text_lower)
            if domain_score >= 2:  # At least 2 keywords from domain
                domains.append(domain)
        
        return domains if domains else ["classical_astrology"]
    
    def _calculate_weighted_overlap(self, keywords1: List[Tuple[str, str, float]], 
                                  keywords2: List[Tuple[str, str, float]]) -> float:
        """Calculate weighted overlap between keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
        
        # Extract keywords and their categories
        words1 = {(k[0], k[1]) for k in keywords1}
        words2 = {(k[0], k[1]) for k in keywords2}
        
        # Calculate overlap with category matching
        exact_matches = len(words1 & words2)
        
        # Partial credit for same category
        category_matches = 0
        cats1 = {k[1] for k in keywords1}
        cats2 = {k[1] for k in keywords2}
        category_matches = len(cats1 & cats2)
        
        total_unique = len(words1 | words2)
        
        if total_unique == 0:
            return 0.0
        
        # Weighted score
        overlap_score = (exact_matches + category_matches * 0.5) / total_unique
        
        return min(overlap_score, 1.0)
    
    def _calculate_domain_relevance(self, question_domain: str, knowledge_domains: List[str]) -> float:
        """Calculate domain relevance score"""
        if not knowledge_domains:
            return 0.0
        
        if question_domain in knowledge_domains:
            return 1.0
        
        # Related domains mapping
        related_domains = {
            "career_astrology": ["classical_astrology", "remedial_measures", "spiritual_growth"],
            "relationship_astrology": ["classical_astrology", "remedial_measures", "spiritual_growth"],
            "health_astrology": ["classical_astrology", "remedial_measures", "spiritual_growth"],
            "remedial_measures": ["career_astrology", "relationship_astrology", "health_astrology"],
            "classical_astrology": ["career_astrology", "relationship_astrology", "health_astrology"],
            "spiritual_growth": ["classical_astrology", "remedial_measures"]
        }
        
        related = related_domains.get(question_domain, [])
        overlap = len(set(related) & set(knowledge_domains))
        
        return 0.7 * (overlap / len(related)) if related else 0.3
    
    def _extract_astrological_elements(self, birth_context: Dict) -> List[str]:
        """Extract astrological elements from birth context"""
        elements = []
        
        if birth_context:
            # Extract from birth date
            if "date" in birth_context:
                elements.append("birth_date")
                # Could calculate moon sign, etc.
            
            if "time" in birth_context:
                elements.append("birth_time")
                elements.append("ascendant")
            
            if "location" in birth_context:
                elements.append("birth_place")
            
            # Add general elements
            elements.extend(["natal_chart", "planetary_positions"])
        
        return elements
    
    def _extract_astrological_references(self, text: str) -> List[str]:
        """Extract astrological references from text"""
        astro_terms = [
            "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
            "rahu", "ketu", "nakshatra", "rasi", "dasha", "bhava", "house",
            "ascendant", "lagna", "navamsa", "aspect", "conjunction",
            "retrograde", "exalted", "debilitated", "yoga", "dosha",
            "manglik", "sade sati", "graha", "tithi", "karana"
        ]
        
        found_refs = []
        text_lower = text.lower()
        
        for term in astro_terms:
            if term in text_lower:
                count = text_lower.count(term)
                found_refs.extend([term] * min(count, 3))  # Cap at 3 per term
        
        return found_refs
    
    def _calculate_astro_context_match(self, birth_elements: List[str], 
                                     knowledge_refs: List[str]) -> float:
        """Calculate astrological context match score"""
        if not knowledge_refs:
            return 0.0
        
        # Base score on number of astrological references
        ref_score = min(len(knowledge_refs) / 10, 1.0)
        
        # Bonus for birth-specific elements
        birth_bonus = 0.2 if birth_elements else 0.0
        
        # Check for specific important terms
        important_terms = ["nakshatra", "dasha", "rasi", "lagna", "navamsa"]
        important_score = sum(0.1 for term in important_terms if term in knowledge_refs)
        
        return min(ref_score + birth_bonus + important_score, 1.0)
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using OpenAI embeddings"""
        try:
            # Get embeddings
            embedding1_response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text1[:8000]  # Limit length
            )
            embedding2_response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text2[:8000]
            )
            
            embedding1 = embedding1_response.data[0].embedding
            embedding2 = embedding2_response.data[0].embedding
            
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
            return 0.5  # Default middle score
    
    def _validate_cultural_authenticity(self, text: str, birth_context: Dict) -> float:
        """Validate Tamil/Vedic cultural authenticity"""
        tamil_vedic_terms = [
            "dharma", "karma", "moksha", "artha", "kama", "satsang", "guru", "swami", 
            "mantra", "yantra", "tantra", "veda", "upanishad", "purana", "shastra",
            "puja", "homam", "abhishekam", "pradosham", "ekadashi", "pournami",
            "amavasya", "tamil", "sanskrit", "sloka", "stotra", "namaskaram"
        ]
        
        text_lower = text.lower()
        term_count = sum(1 for term in tamil_vedic_terms if term in text_lower)
        base_score = term_count / len(tamil_vedic_terms) if tamil_vedic_terms else 0
        
        # Boost score for Tamil context
        location = birth_context.get("location", "").lower() if birth_context else ""
        tamil_boost = 0.2 if any(place in location for place in ["tamil", "chennai", "madurai", "trichy"]) else 0
        
        # Check for authentic phrases
        authentic_phrases = [
            "vedic astrology", "nadi astrology", "tamil calendar",
            "panchangam", "muhurtham", "rahu kalam", "yamagandam"
        ]
        phrase_score = sum(0.1 for phrase in authentic_phrases if phrase in text_lower)
        
        return min(base_score * 3 + tamil_boost + phrase_score, 1.0)
    
    def _check_question_answer_alignment(self, question: str, knowledge: str) -> float:
        """Check if knowledge addresses the question type"""
        question_lower = question.lower()
        knowledge_lower = knowledge.lower()
        
        # Question type patterns
        question_patterns = {
            "when": ["time", "period", "date", "year", "month", "soon", "duration"],
            "what": ["is", "are", "means", "signifies", "indicates"],
            "how": ["method", "way", "approach", "technique", "process"],
            "why": ["reason", "because", "due to", "caused by"],
            "will": ["future", "prediction", "forecast", "likely", "possibility"],
            "should": ["advice", "recommendation", "suggest", "better", "beneficial"]
        }
        
        alignment_score = 0.5  # Base score
        
        # Check which question type
        for q_type, answer_keywords in question_patterns.items():
            if q_type in question_lower:
                # Check if answer contains appropriate keywords
                matches = sum(1 for keyword in answer_keywords if keyword in knowledge_lower)
                if matches > 0:
                    alignment_score = min(0.5 + matches * 0.2, 1.0)
                break
        
        return alignment_score
    
    def _generate_improvement_suggestions(self, relevance_analysis: Dict, 
                                        question: str, knowledge: str) -> List[str]:
        """Generate specific suggestions to improve RAG retrieval"""
        suggestions = []
        
        if relevance_analysis["keyword_match"] < 0.3:
            suggestions.append("Enhance keyword extraction algorithm to better capture question intent")
            suggestions.append(f"Add query expansion for domain: {relevance_analysis.get('question_domain', 'unknown')}")
        
        if relevance_analysis["domain_match"] < 0.5:
            domain = relevance_analysis.get("question_domain", "unknown")
            suggestions.append(f"Prioritize '{domain}' knowledge sources in retrieval")
            suggestions.append("Implement domain-specific query templates")
        
        if relevance_analysis["astro_relevance"] < 0.3:
            suggestions.append("Include birth chart context in RAG query formulation")
            suggestions.append("Add astrological term synonyms to query")
        
        if relevance_analysis["semantic_similarity"] < 0.5:
            suggestions.append("Use semantic search with embedding similarity threshold")
            suggestions.append("Implement query reformulation for better semantic matching")
        
        if relevance_analysis["cultural_authenticity"] < 0.3:
            suggestions.append("Prioritize Tamil/Vedic knowledge sources")
            suggestions.append("Add cultural context filters to retrieval pipeline")
        
        return suggestions[:5]  # Top 5 suggestions
    
    async def _generate_enhanced_query(self, original_query: str, 
                                     birth_details: Dict, 
                                     relevance_scores: Dict) -> str:
        """Generate an enhanced query for better retrieval"""
        enhanced_parts = [original_query]
        
        # Add domain context
        domain = self._classify_spiritual_domain(original_query)
        if domain != "classical_astrology":
            enhanced_parts.append(f"[{domain.replace('_', ' ')}]")
        
        # Add birth context if available
        if birth_details:
            if "date" in birth_details:
                enhanced_parts.append("birth chart analysis")
        
        # Add specific enhancements based on low scores
        if relevance_scores.get("keyword_match", 1) < 0.3:
            # Extract key terms and add synonyms
            key_terms = re.findall(r'\b\w{4,}\b', original_query.lower())
            enhanced_parts.append(f"related to {' '.join(key_terms[:3])}")
        
        if relevance_scores.get("astro_relevance", 1) < 0.3:
            enhanced_parts.append("vedic astrology perspective")
        
        return " ".join(enhanced_parts)
    
    def _get_expanded_domains(self, question: str) -> List[str]:
        """Get expanded list of domains to search"""
        primary_domain = self._classify_spiritual_domain(question)
        
        # Always include these core domains
        domains = [primary_domain, "classical_astrology", "tamil_spiritual_literature"]
        
        # Add related domains
        if "career" in question.lower() or "job" in question.lower():
            domains.extend(["career_astrology", "remedial_measures"])
        elif "love" in question.lower() or "marriage" in question.lower():
            domains.extend(["relationship_astrology", "compatibility_analysis"])
        elif "health" in question.lower():
            domains.extend(["health_astrology", "ayurvedic_astrology"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_domains = []
        for domain in domains:
            if domain not in seen:
                seen.add(domain)
                unique_domains.append(domain)
        
        return unique_domains
    
    def _load_spiritual_keywords(self) -> Dict[str, List[str]]:
        """Load spiritual keywords for analysis"""
        return {
            "career": ["job", "work", "career", "profession", "business", "success", 
                      "money", "wealth", "promotion", "employment", "salary", "growth"],
            "relationships": ["love", "marriage", "partner", "relationship", "family", 
                            "spouse", "compatibility", "divorce", "separation", "romance"],
            "health": ["health", "illness", "healing", "medicine", "body", "wellness", 
                      "disease", "treatment", "recovery", "ailment", "cure"],
            "spiritual": ["dharma", "karma", "moksha", "meditation", "prayer", "temple", 
                         "spiritual", "soul", "enlightenment", "consciousness", "divine"],
            "astrology": ["planet", "star", "nakshatra", "rasi", "dasha", "graha", 
                         "house", "horoscope", "chart", "kundli", "jathakam"],
            "remedies": ["remedy", "solution", "puja", "mantra", "yantra", "gemstone",
                        "ritual", "worship", "offering", "parihara"]
        }
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Load domain-specific keywords"""
        return {
            "career_astrology": ["career", "job", "profession", "work", "business", 
                               "10th house", "saturn", "sun", "success", "promotion"],
            "relationship_astrology": ["love", "marriage", "7th house", "venus", 
                                     "compatibility", "spouse", "partner", "relationship"],
            "health_astrology": ["health", "6th house", "illness", "recovery", 
                               "wellness", "healing", "medical", "body"],
            "remedial_measures": ["remedy", "solution", "puja", "mantra", "ritual",
                                "gemstone", "donation", "worship", "parihara"],
            "classical_astrology": ["nakshatra", "graha", "dasha", "rasi", "bhava",
                                   "yoga", "dosha", "transit", "aspect"],
            "spiritual_growth": ["spiritual", "meditation", "dharma", "karma", "moksha",
                               "enlightenment", "consciousness", "soul", "divine"]
        }