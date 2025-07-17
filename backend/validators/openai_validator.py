"""
🤖 OPENAI VALIDATOR - Validates OpenAI spiritual guidance responses
Ensures responses use Swami persona and incorporate all context.
"""

from typing import Dict, List
import re

from core_foundation_enhanced import logger

class OpenAIValidator:
    """
    Validates OpenAI responses for quality, context usage, and persona consistency
    """
    
    def __init__(self):
        self.swami_patterns = self._load_swami_patterns()
        self.spiritual_indicators = self._load_spiritual_indicators()
        self.tamil_vedic_terms = self._load_tamil_vedic_terms()
        
    async def validate(self, input_data: Dict, output_data: Dict, session_context: Dict) -> Dict:
        """Validate OpenAI response quality and context usage"""
        validation_result = {
            "passed": True,
            "validation_type": "openai_response_quality",
            "errors": [],
            "warnings": [],
            "auto_fixable": False,
            "expected": {},
            "actual": output_data,
            "quality_metrics": {}
        }
        
        try:
            # Extract response
            response = output_data.get("response", "") or output_data.get("guidance", "")
            
            if not response:
                validation_result["passed"] = False
                validation_result["errors"].append("No response generated")
                validation_result["severity"] = "critical"
                validation_result["user_impact"] = "User receives no guidance"
                return validation_result
            
            # Extract context data
            birth_details = session_context.get("birth_details", {})
            rag_knowledge = session_context.get("rag_knowledge", "")
            prokerala_data = session_context.get("prokerala_data", {})
            
            # Run quality checks
            quality_metrics = {
                "uses_swami_persona": self._check_swami_persona(response),
                "includes_birth_context": self._check_birth_context_usage(response, birth_details, prokerala_data),
                "incorporates_rag_knowledge": self._check_rag_incorporation(response, rag_knowledge),
                "appropriate_length": self._check_response_length(response),
                "spiritual_tone": self._check_spiritual_tone(response),
                "cultural_authenticity": self._check_cultural_authenticity(response),
                "addresses_question": self._check_question_addressing(response, session_context.get("spiritual_question", ""))
            }
            
            validation_result["quality_metrics"] = quality_metrics
            
            # Calculate overall quality score
            quality_score = sum(1 for v in quality_metrics.values() if v) / len(quality_metrics)
            validation_result["quality_score"] = quality_score
            
            # Check for failures
            if quality_score < 0.6:
                validation_result["passed"] = False
                validation_result["severity"] = "error"
                validation_result["errors"].append(f"Low quality response (score: {quality_score:.2f})")
                validation_result["user_impact"] = "User receives poor quality spiritual guidance"
                validation_result["auto_fixable"] = True
                validation_result["auto_fix_type"] = "regenerate_with_enhanced_prompt"
            
            # Specific warnings
            if not quality_metrics["uses_swami_persona"]:
                validation_result["warnings"].append("Response lacks Swami persona characteristics")
            
            if not quality_metrics["includes_birth_context"]:
                validation_result["warnings"].append("Birth chart context not incorporated")
                if birth_details:  # If birth details were provided
                    validation_result["passed"] = False
                    validation_result["errors"].append("Failed to use provided birth chart data")
            
            if not quality_metrics["incorporates_rag_knowledge"]:
                validation_result["warnings"].append("RAG knowledge not incorporated")
                if rag_knowledge:  # If RAG knowledge was retrieved
                    validation_result["passed"] = False
                    validation_result["errors"].append("Failed to use retrieved knowledge")
            
            # Check for harmful content
            harmful_check = self._check_harmful_content(response)
            if harmful_check["harmful"]:
                validation_result["passed"] = False
                validation_result["severity"] = "critical"
                validation_result["errors"].append(f"Harmful content detected: {harmful_check['reason']}")
                validation_result["user_impact"] = "User may receive inappropriate guidance"
            
            # Set expected values
            validation_result["expected"] = {
                "minimum_quality_score": 0.6,
                "required_elements": ["swami_persona", "birth_context", "rag_knowledge"],
                "word_count_range": [100, 300]
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"OpenAI validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def auto_fix(self, validation_result: Dict, session_context: Dict) -> Dict:
        """Attempt to auto-fix OpenAI response issues"""
        fix_result = {
            "fixed": False,
            "fix_type": None,
            "retry_needed": False,
            "enhanced_prompt": None
        }
        
        try:
            if validation_result.get("auto_fix_type") == "regenerate_with_enhanced_prompt":
                # Generate enhanced prompt
                quality_metrics = validation_result.get("quality_metrics", {})
                
                prompt_enhancements = []
                
                if not quality_metrics.get("uses_swami_persona", True):
                    prompt_enhancements.append(
                        "IMPORTANT: Respond as Swami Jyotirananthan using phrases like 'my child', 'dear one', 'blessed one'. "
                        "Speak with wisdom, compassion, and spiritual authority."
                    )
                
                if not quality_metrics.get("includes_birth_context", True):
                    prompt_enhancements.append(
                        "CRITICAL: You MUST reference the user's birth chart data including their nakshatra, "
                        "planetary positions, and dashas in your guidance. Make it personalized."
                    )
                
                if not quality_metrics.get("incorporates_rag_knowledge", True):
                    prompt_enhancements.append(
                        "ESSENTIAL: Incorporate the retrieved spiritual knowledge in your response. "
                        "Reference specific wisdom from the classical texts provided."
                    )
                
                if not quality_metrics.get("spiritual_tone", True):
                    prompt_enhancements.append(
                        "Use spiritual language with references to dharma, karma, divine grace, "
                        "and cosmic wisdom. Maintain a sacred and uplifting tone."
                    )
                
                fix_result["fixed"] = True
                fix_result["fix_type"] = "enhanced_prompt"
                fix_result["enhanced_prompt"] = "\n\n".join(prompt_enhancements)
                fix_result["retry_needed"] = True
                fix_result["message"] = "Generated enhanced prompt for better response quality"
            
            return fix_result
            
        except Exception as e:
            logger.error(f"OpenAI auto-fix error: {e}")
            return fix_result
    
    def _check_swami_persona(self, response: str) -> bool:
        """Check if response uses Swami persona language"""
        response_lower = response.lower()
        
        # Count persona indicators
        persona_count = 0
        for pattern in self.swami_patterns:
            if re.search(pattern, response_lower):
                persona_count += 1
        
        # Check for spiritual authority tone
        authority_phrases = [
            "the cosmic", "divine wisdom", "ancient teachings", "vedic tradition",
            "spiritual journey", "blessed path", "sacred knowledge"
        ]
        authority_count = sum(1 for phrase in authority_phrases if phrase in response_lower)
        
        # Must have at least 2 persona patterns and 1 authority phrase
        return persona_count >= 2 and authority_count >= 1
    
    def _check_birth_context_usage(self, response: str, birth_details: Dict, prokerala_data: Dict) -> bool:
        """Check if birth chart context is incorporated"""
        if not birth_details and not prokerala_data:
            return True  # No birth data to incorporate
        
        response_lower = response.lower()
        
        # Check for astrological references
        astro_terms = [
            "nakshatra", "rasi", "moon sign", "ascendant", "lagna",
            "planetary position", "birth chart", "natal chart", "dasha",
            "house", "aspect", "conjunction", "transit"
        ]
        
        astro_references = sum(1 for term in astro_terms if term in response_lower)
        
        # Check for specific planet references
        planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        planet_references = sum(1 for planet in planets if planet in response_lower)
        
        # Check for birth-specific references
        birth_specific = False
        if birth_details:
            if "date" in birth_details and any(word in response_lower for word in ["birth", "born"]):
                birth_specific = True
        
        # Must have at least 2 astrological terms and 1 planet reference
        return (astro_references >= 2 and planet_references >= 1) or birth_specific
    
    def _check_rag_incorporation(self, response: str, rag_knowledge: str) -> bool:
        """Check if RAG knowledge is incorporated in response"""
        if not rag_knowledge:
            return True  # No RAG knowledge to incorporate
        
        # Extract key phrases from RAG knowledge
        rag_words = rag_knowledge.lower().split()
        rag_phrases = []
        
        # Extract 2-3 word phrases
        for i in range(len(rag_words) - 1):
            phrase = " ".join(rag_words[i:i+2])
            if len(phrase) > 10:  # Meaningful phrases
                rag_phrases.append(phrase)
        
        # Also extract unique spiritual terms
        spiritual_terms = [
            word for word in rag_words 
            if len(word) > 5 and word not in ["the", "and", "for", "with", "that", "this"]
        ]
        
        response_lower = response.lower()
        
        # Check phrase matches
        phrase_matches = sum(1 for phrase in rag_phrases[:10] if phrase in response_lower)
        
        # Check term matches
        term_matches = sum(1 for term in spiritual_terms[:10] if term in response_lower)
        
        # Must have at least 2 phrase matches or 3 term matches
        return phrase_matches >= 2 or term_matches >= 3
    
    def _check_response_length(self, response: str) -> bool:
        """Check if response length is appropriate"""
        word_count = len(response.split())
        return 100 <= word_count <= 300
    
    def _check_spiritual_tone(self, response: str) -> bool:
        """Check if response has appropriate spiritual tone"""
        response_lower = response.lower()
        
        # Count spiritual indicators
        spiritual_count = sum(1 for indicator in self.spiritual_indicators if indicator in response_lower)
        
        # Check for uplifting language
        positive_words = [
            "blessed", "divine", "grace", "wisdom", "peace", "harmony",
            "enlightenment", "spiritual", "sacred", "holy", "auspicious"
        ]
        positive_count = sum(1 for word in positive_words if word in response_lower)
        
        # Avoid negative/fearful language
        negative_words = [
            "doom", "curse", "bad luck", "terrible fate", "hopeless",
            "disaster", "punishment", "suffering", "misfortune"
        ]
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        # Must have spiritual indicators and positive tone, minimal negative
        return spiritual_count >= 3 and positive_count >= 2 and negative_count <= 1
    
    def _check_cultural_authenticity(self, response: str) -> bool:
        """Check Tamil/Vedic cultural authenticity"""
        response_lower = response.lower()
        
        # Count Tamil/Vedic terms
        cultural_count = sum(1 for term in self.tamil_vedic_terms if term in response_lower)
        
        # Check for authentic phrases
        authentic_phrases = [
            "vedic wisdom", "ancient tradition", "tamil heritage",
            "sacred texts", "divine grace", "cosmic law"
        ]
        phrase_count = sum(1 for phrase in authentic_phrases if phrase in response_lower)
        
        # Must have at least 2 cultural terms or 1 authentic phrase
        return cultural_count >= 2 or phrase_count >= 1
    
    def _check_question_addressing(self, response: str, question: str) -> bool:
        """Check if response addresses the user's question"""
        if not question:
            return True
        
        response_lower = response.lower()
        question_lower = question.lower()
        
        # Extract key terms from question
        question_words = [
            word for word in question_lower.split() 
            if len(word) > 3 and word not in ["what", "when", "where", "how", "why", "will", "should"]
        ]
        
        # Check how many question terms appear in response
        term_matches = sum(1 for word in question_words if word in response_lower)
        
        # Check for question type addressing
        question_addressed = True
        if "when" in question_lower:
            time_words = ["time", "period", "year", "month", "soon", "future"]
            question_addressed = any(word in response_lower for word in time_words)
        elif "how" in question_lower:
            method_words = ["way", "method", "approach", "practice", "remedy"]
            question_addressed = any(word in response_lower for word in method_words)
        elif "why" in question_lower:
            reason_words = ["because", "reason", "due to", "influence", "impact"]
            question_addressed = any(word in response_lower for word in reason_words)
        
        # Must address question type and have term matches
        return question_addressed and term_matches >= len(question_words) * 0.3
    
    def _check_harmful_content(self, response: str) -> Dict[str, Any]:
        """Check for harmful or inappropriate content"""
        response_lower = response.lower()
        
        harmful_patterns = {
            "medical_advice": [
                "stop taking medication", "ignore doctor", "cure disease",
                "treat illness", "medical diagnosis"
            ],
            "financial_scam": [
                "send money", "investment guarantee", "get rich quick",
                "financial miracle", "donate everything"
            ],
            "harmful_predictions": [
                "you will die", "death is near", "accident will happen",
                "tragedy awaits", "doomed to fail"
            ],
            "discrimination": [
                "caste superiority", "gender discrimination", "racial bias"
            ]
        }
        
        for category, patterns in harmful_patterns.items():
            for pattern in patterns:
                if pattern in response_lower:
                    logger.warning(
                        f"Harmful content detected - Category: {category}, Pattern: '{pattern}', "
                        f"Response snippet: '{response_lower[max(0, response_lower.find(pattern)-20):response_lower.find(pattern)+len(pattern)+20]}'"
                    )
                    return {
                        "harmful": True,
                        "category": category,
                        "reason": f"Contains '{pattern}'"
                    }
        
        return {"harmful": False}
    
    def _load_swami_patterns(self) -> List[str]:
        """Load Swami persona speech patterns"""
        return [
            r"my child", r"dear one", r"blessed one", r"my dear",
            r"i see", r"i perceive", r"the cosmos reveals", r"divine wisdom shows",
            r"let me guide", r"allow me to", r"i shall reveal",
            r"ancient wisdom", r"vedic tradition", r"cosmic truth"
        ]
    
    def _load_spiritual_indicators(self) -> List[str]:
        """Load spiritual tone indicators"""
        return [
            "blessed", "divine", "spiritual", "cosmic", "soul", "sacred",
            "wisdom", "guidance", "enlightenment", "journey", "path",
            "dharma", "karma", "grace", "consciousness", "energy"
        ]
    
    def _load_tamil_vedic_terms(self) -> List[str]:
        """Load Tamil and Vedic terms"""
        return [
            "dharma", "karma", "moksha", "artha", "kama", "guru", "swami",
            "mantra", "yantra", "veda", "upanishad", "nakshatra", "rasi",
            "dasha", "graha", "puja", "homam", "tamil", "sanskrit", "sloka"
        ]