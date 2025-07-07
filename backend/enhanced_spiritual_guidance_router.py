"""
Enhanced Spiritual Guidance Router with RAG Integration
Seamlessly integrates with existing JyotiFlow spiritual guidance system
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime

# Try to import enhanced RAG system
try:
    from enhanced_rag_knowledge_engine import (
        initialize_rag_system, 
        get_rag_enhanced_guidance, 
        rag_engine, 
        persona_engine,
        knowledge_expansion
    )
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logging.warning("RAG system not available, using fallback mode")

# Import existing spiritual guidance logic
try:
    from routers.spiritual import get_spiritual_guidance_response
    EXISTING_SPIRITUAL_AVAILABLE = True
except ImportError:
    EXISTING_SPIRITUAL_AVAILABLE = False
    logging.warning("Existing spiritual guidance not available")

# Database imports
try:
    import db
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced request/response models
class EnhancedSpiritualGuidanceRequest(BaseModel):
    """Enhanced request model for spiritual guidance"""
    question: str = Field(..., description="User's spiritual question")
    birth_details: Optional[Dict[str, Any]] = Field(None, description="Birth chart details")
    service_type: str = Field("general", description="Type of spiritual service")
    preferred_depth: str = Field("standard", description="Depth of analysis: basic, standard, comprehensive, comprehensive_30_minute")
    cultural_context: str = Field("tamil_vedic", description="Cultural context preference")
    analysis_sections: Optional[List[str]] = Field(None, description="Specific analysis sections requested")
    session_id: Optional[str] = Field(None, description="Session identifier for tracking")

class EnhancedSpiritualGuidanceResponse(BaseModel):
    """Enhanced response model with RAG integration"""
    enhanced_guidance: str = Field(..., description="AI-generated spiritual guidance")
    traditional_guidance: Optional[str] = Field(None, description="Traditional guidance for comparison")
    knowledge_sources: List[Dict[str, Any]] = Field(default_factory=list, description="Sources of knowledge used")
    persona_mode: str = Field("general", description="Swami persona mode used")
    service_configuration: Dict[str, Any] = Field(default_factory=dict, description="Service configuration applied")
    analysis_sections: List[str] = Field(default_factory=list, description="Analysis sections included")
    confidence_score: float = Field(0.0, description="Confidence score of the response")
    response_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")

class ServiceConfigurationRequest(BaseModel):
    """Model for dynamic service configuration"""
    service_name: str = Field(..., description="Name of the service")
    knowledge_domains: List[str] = Field(..., description="Knowledge domains to focus on")
    persona_mode: str = Field("general", description="Swami persona mode")
    analysis_depth: str = Field("standard", description="Analysis depth level")
    specialized_prompts: Dict[str, Any] = Field(default_factory=dict, description="Specialized prompts configuration")
    response_behavior: Dict[str, Any] = Field(default_factory=dict, description="Response behavior configuration")

# Initialize enhanced router
enhanced_router = APIRouter(prefix="/api/spiritual/enhanced", tags=["Enhanced Spiritual Guidance"])

class EnhancedSpiritualGuidanceEngine:
    """
    Enhanced spiritual guidance engine with RAG integration
    """
    
    def __init__(self):
        self.rag_initialized = False
        self.fallback_mode = False
        
    async def initialize(self):
        """Initialize the enhanced guidance engine"""
        try:
            if RAG_AVAILABLE and DATABASE_AVAILABLE and db.db_pool:
                openai_api_key = os.getenv("OPENAI_API_KEY", "fallback_key")
                
                # Initialize RAG system
                await initialize_rag_system(db.db_pool, openai_api_key)
                self.rag_initialized = True
                logger.info("Enhanced RAG system initialized successfully")
            else:
                logger.warning("RAG system not available, using fallback mode")
                self.fallback_mode = True
                
        except Exception as e:
            logger.error(f"RAG initialization failed: {e}")
            self.fallback_mode = True
    
    async def get_enhanced_guidance(self, request: EnhancedSpiritualGuidanceRequest) -> EnhancedSpiritualGuidanceResponse:
        """Get enhanced spiritual guidance with RAG integration"""
        try:
            # Initialize if not already done
            if not self.rag_initialized and not self.fallback_mode:
                await self.initialize()
            
            # Get enhanced guidance if RAG is available
            enhanced_result = None
            traditional_result = None
            
            if self.rag_initialized and not self.fallback_mode:
                enhanced_result = await get_rag_enhanced_guidance(
                    request.question,
                    request.birth_details,
                    request.service_type
                )
            
            # Get traditional guidance for comparison/fallback
            if EXISTING_SPIRITUAL_AVAILABLE:
                traditional_result = await self._get_traditional_guidance(request)
            
            # Combine results
            return await self._combine_guidance_results(
                request, enhanced_result, traditional_result
            )
            
        except Exception as e:
            logger.error(f"Enhanced guidance error: {e}")
            # Fallback to traditional guidance
            return await self._get_fallback_guidance(request)
    
    async def _get_traditional_guidance(self, request: EnhancedSpiritualGuidanceRequest) -> Optional[str]:
        """Get traditional spiritual guidance for comparison"""
        try:
            # This would call the existing spiritual guidance system
            # For now, return a placeholder that maintains existing functionality
            traditional_guidance = f"Traditional guidance for: {request.question}"
            return traditional_guidance
            
        except Exception as e:
            logger.error(f"Traditional guidance error: {e}")
            return None
    
    async def _combine_guidance_results(self, 
                                      request: EnhancedSpiritualGuidanceRequest,
                                      enhanced_result: Optional[Dict[str, Any]],
                                      traditional_result: Optional[str]) -> EnhancedSpiritualGuidanceResponse:
        """Combine enhanced and traditional guidance results"""
        
        if enhanced_result and not enhanced_result.get("error"):
            # Use enhanced guidance as primary
            return EnhancedSpiritualGuidanceResponse(
                enhanced_guidance=enhanced_result["enhanced_guidance"],
                traditional_guidance=traditional_result,
                knowledge_sources=enhanced_result.get("knowledge_sources", []),
                persona_mode=enhanced_result.get("persona_mode", "general"),
                service_configuration=enhanced_result.get("service_configuration", {}),
                analysis_sections=enhanced_result.get("analysis_sections", []),
                confidence_score=0.95,
                response_metadata={
                    "enhancement_type": "rag_enhanced",
                    "timestamp": datetime.now().isoformat(),
                    "service_type": request.service_type,
                    "analysis_depth": request.preferred_depth
                }
            )
        else:
            # Fallback to traditional guidance
            return EnhancedSpiritualGuidanceResponse(
                enhanced_guidance=traditional_result or "I apologize, but I'm experiencing technical difficulties. Please try again.",
                traditional_guidance=traditional_result,
                knowledge_sources=[],
                persona_mode="general",
                service_configuration={},
                analysis_sections=[],
                confidence_score=0.7,
                response_metadata={
                    "enhancement_type": "fallback_mode",
                    "timestamp": datetime.now().isoformat(),
                    "service_type": request.service_type,
                    "analysis_depth": request.preferred_depth
                }
            )
    
    async def _get_fallback_guidance(self, request: EnhancedSpiritualGuidanceRequest) -> EnhancedSpiritualGuidanceResponse:
        """Provide fallback guidance when systems are unavailable"""
        fallback_guidance = f"""
Vanakkam! I am Swami Jyotirananthan, and I welcome your spiritual inquiry.

Your question: {request.question}

Based on classical Vedic principles, every spiritual question contains its own answer when approached with the right understanding. The ancient Tamil wisdom teaches us that 'அறிந்தாரிடம் கேட்பது அறிவு' - asking the wise is wisdom itself.

Your birth chart, if provided, would reveal the deeper karmic patterns influencing your current situation. However, even without detailed analysis, I can offer this guidance:

1. **Spiritual Foundation**: Begin each day with sincere prayer and gratitude
2. **Dharmic Action**: Act in alignment with your highest values
3. **Patience & Faith**: Trust in divine timing and cosmic order
4. **Service**: Find opportunities to serve others selflessly

The stars guide us, but our choices shape our destiny. May divine grace illuminate your path.

Om Namah Shivaya
Tamil thaai arul kondae vazhlga

With blessings,
Swami Jyotirananthan
"""
        
        return EnhancedSpiritualGuidanceResponse(
            enhanced_guidance=fallback_guidance,
            traditional_guidance=None,
            knowledge_sources=[{
                "domain": "general_spiritual_wisdom",
                "source": "Classical Tamil Vedic Principles",
                "authority_level": 4,
                "relevance": 0.8
            }],
            persona_mode="general",
            service_configuration={},
            analysis_sections=["spiritual_foundation", "dharmic_guidance"],
            confidence_score=0.6,
            response_metadata={
                "enhancement_type": "fallback_guidance",
                "timestamp": datetime.now().isoformat(),
                "service_type": request.service_type,
                "analysis_depth": request.preferred_depth
            }
        )
    
    async def configure_service(self, config_request: ServiceConfigurationRequest) -> Dict[str, Any]:
        """Configure service dynamically through admin interface"""
        try:
            if not DATABASE_AVAILABLE or not db.db_pool:
                raise HTTPException(status_code=500, detail="Database not available")
            
            # Update service configuration
            async with db.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE service_types 
                    SET 
                        knowledge_configuration = $1,
                        specialized_prompts = $2,
                        response_behavior = $3,
                        swami_persona_mode = $4,
                        analysis_depth = $5
                    WHERE name = $6
                """, 
                    json.dumps({
                        "knowledge_domains": config_request.knowledge_domains,
                        "analysis_depth": config_request.analysis_depth
                    }),
                    json.dumps(config_request.specialized_prompts),
                    json.dumps(config_request.response_behavior),
                    config_request.persona_mode,
                    config_request.analysis_depth,
                    config_request.service_name
                )
            
            return {
                "success": True,
                "message": f"Service '{config_request.service_name}' configured successfully",
                "configuration": {
                    "knowledge_domains": config_request.knowledge_domains,
                    "persona_mode": config_request.persona_mode,
                    "analysis_depth": config_request.analysis_depth
                }
            }
            
        except Exception as e:
            logger.error(f"Service configuration error: {e}")
            raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")
    
    async def get_service_insights(self, service_name: str) -> Dict[str, Any]:
        """Get insights about service performance and knowledge effectiveness"""
        try:
            if not DATABASE_AVAILABLE or not db.db_pool:
                return {"error": "Database not available"}
            
            async with db.db_pool.acquire() as conn:
                # Get service configuration
                service_config = await conn.fetchrow(
                    "SELECT * FROM service_types WHERE name = $1", service_name
                )
                
                # Get effectiveness metrics
                effectiveness_metrics = await conn.fetchrow("""
                    SELECT 
                        AVG(user_satisfaction) as avg_satisfaction,
                        COUNT(*) as total_sessions,
                        AVG(CASE WHEN prediction_accuracy THEN 1.0 ELSE 0.0 END) as accuracy_rate
                    FROM knowledge_effectiveness_tracking
                    WHERE session_id LIKE $1
                """, f"%{service_name}%")
                
                # Get recent knowledge updates
                recent_updates = await conn.fetch("""
                    SELECT update_type, content_added, effectiveness_improvement, processed_at
                    FROM automated_knowledge_updates
                    ORDER BY processed_at DESC
                    LIMIT 5
                """)
                
                return {
                    "service_name": service_name,
                    "configuration": dict(service_config) if service_config else {},
                    "effectiveness_metrics": dict(effectiveness_metrics) if effectiveness_metrics else {},
                    "recent_updates": [dict(update) for update in recent_updates],
                    "knowledge_domains_available": [
                        "classical_astrology", "tamil_spiritual_literature", 
                        "relationship_astrology", "career_astrology",
                        "health_astrology", "remedial_measures", 
                        "world_knowledge", "psychological_integration"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Service insights error: {e}")
            return {"error": f"Insights retrieval failed: {str(e)}"}

# Initialize the engine
guidance_engine = EnhancedSpiritualGuidanceEngine()

# API Endpoints
@enhanced_router.post("/guidance", response_model=EnhancedSpiritualGuidanceResponse)
async def get_enhanced_spiritual_guidance(request: EnhancedSpiritualGuidanceRequest):
    """
    Get enhanced spiritual guidance with RAG integration
    
    This endpoint provides the full enhanced experience:
    - RAG-powered knowledge retrieval
    - Dynamic persona configuration
    - Authentic spiritual guidance
    - Comprehensive analysis options
    """
    try:
        return await guidance_engine.get_enhanced_guidance(request)
    except Exception as e:
        logger.error(f"Enhanced guidance endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Guidance generation failed: {str(e)}")

@enhanced_router.post("/configure-service")
async def configure_service_dynamically(config_request: ServiceConfigurationRequest):
    """
    Configure service dynamically through admin interface
    
    This endpoint allows admins to:
    - Set knowledge domains for specific services
    - Configure persona modes
    - Adjust analysis depth
    - Customize response behavior
    """
    try:
        return await guidance_engine.configure_service(config_request)
    except Exception as e:
        logger.error(f"Service configuration endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Service configuration failed: {str(e)}")

@enhanced_router.get("/service-insights/{service_name}")
async def get_service_insights(service_name: str):
    """
    Get insights about service performance and knowledge effectiveness
    
    This endpoint provides:
    - Service configuration status
    - Effectiveness metrics
    - Recent knowledge updates
    - Performance analytics
    """
    try:
        return await guidance_engine.get_service_insights(service_name)
    except Exception as e:
        logger.error(f"Service insights endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

@enhanced_router.get("/knowledge-domains")
async def get_available_knowledge_domains():
    """
    Get list of available knowledge domains for service configuration
    """
    return {
        "knowledge_domains": [
            {
                "domain": "classical_astrology",
                "description": "Classical Vedic astrology texts and principles",
                "authority_level": 5,
                "cultural_context": "vedic_tradition"
            },
            {
                "domain": "tamil_spiritual_literature",
                "description": "Tamil spiritual texts and wisdom tradition",
                "authority_level": 5,
                "cultural_context": "tamil_tradition"
            },
            {
                "domain": "relationship_astrology",
                "description": "Love, marriage, and relationship guidance",
                "authority_level": 4,
                "cultural_context": "universal"
            },
            {
                "domain": "career_astrology",
                "description": "Career and professional success guidance",
                "authority_level": 4,
                "cultural_context": "universal"
            },
            {
                "domain": "health_astrology",
                "description": "Health and wellness astrological guidance",
                "authority_level": 4,
                "cultural_context": "ayurvedic_tradition"
            },
            {
                "domain": "remedial_measures",
                "description": "Spiritual remedies and practices",
                "authority_level": 4,
                "cultural_context": "vedic_tradition"
            },
            {
                "domain": "world_knowledge",
                "description": "Current world events and modern applications",
                "authority_level": 3,
                "cultural_context": "universal"
            },
            {
                "domain": "psychological_integration",
                "description": "Modern psychology integrated with ancient wisdom",
                "authority_level": 3,
                "cultural_context": "universal"
            }
        ]
    }

@enhanced_router.get("/persona-modes")
async def get_available_persona_modes():
    """
    Get list of available Swami persona modes
    """
    return {
        "persona_modes": [
            {
                "mode": "general",
                "description": "General spiritual guidance with Tamil Vedic wisdom",
                "expertise_level": "experienced_spiritual_guide"
            },
            {
                "mode": "relationship_counselor_authority",
                "description": "Specialized relationship and marriage guidance",
                "expertise_level": "master_relationship_guide"
            },
            {
                "mode": "business_mentor_authority",
                "description": "Career and business success guidance",
                "expertise_level": "career_success_master"
            },
            {
                "mode": "comprehensive_life_master",
                "description": "Complete life analysis and transformation guidance",
                "expertise_level": "complete_life_analysis_authority"
            }
        ]
    }

# Health check endpoint
@enhanced_router.get("/health")
async def health_check():
    """
    Health check for enhanced spiritual guidance system
    """
    return {
        "status": "healthy",
        "rag_available": RAG_AVAILABLE,
        "database_available": DATABASE_AVAILABLE,
        "existing_spiritual_available": EXISTING_SPIRITUAL_AVAILABLE,
        "fallback_mode": guidance_engine.fallback_mode,
        "initialized": guidance_engine.rag_initialized,
        "timestamp": datetime.now().isoformat()
    }

# Integration endpoint for existing spiritual router
@enhanced_router.post("/integrate-with-existing")
async def integrate_with_existing_spiritual_guidance(request: EnhancedSpiritualGuidanceRequest):
    """
    Integration endpoint that can be called from existing spiritual guidance router
    This provides enhanced functionality without breaking existing endpoints
    """
    try:
        # Get enhanced guidance
        enhanced_response = await guidance_engine.get_enhanced_guidance(request)
        
        # Return in format compatible with existing system
        return {
            "spiritual_guidance": enhanced_response.enhanced_guidance,
            "confidence_score": enhanced_response.confidence_score,
            "enhancement_metadata": enhanced_response.response_metadata,
            "knowledge_sources": enhanced_response.knowledge_sources,
            "persona_mode": enhanced_response.persona_mode
        }
        
    except Exception as e:
        logger.error(f"Integration endpoint error: {e}")
        # Return fallback compatible with existing system
        return {
            "spiritual_guidance": "I apologize, but I'm experiencing technical difficulties. Please try again.",
            "confidence_score": 0.5,
            "enhancement_metadata": {"error": str(e)},
            "knowledge_sources": [],
            "persona_mode": "general"
        }

# Export router for inclusion in main app
router = enhanced_router