"""
Enhanced Spiritual Guidance Router with Dynamic Pricing Integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import asyncpg

# Try to import dynamic pricing system
try:
    from dynamic_comprehensive_pricing import (
        DynamicComprehensivePricing, 
        generate_pricing_recommendations,
        apply_admin_approved_pricing
    )
    DYNAMIC_PRICING_AVAILABLE = True
except ImportError:
    DYNAMIC_PRICING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Dynamic pricing system not available - using fixed pricing")

# RAG system availability flag (will be checked at runtime)
RAG_AVAILABLE = None  # Unknown until first runtime check

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

class ComprehensiveReadingRequest(BaseModel):
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format")
    birth_location: str = Field(..., description="Birth location")
    focus_areas: List[str] = Field(default=["general"], description="Areas of focus")
    
class ComprehensiveReadingResponse(BaseModel):
    session_id: str
    current_price: float
    estimated_duration: int
    service_configuration: Dict[str, Any]
    pricing_rationale: str
    reading_preview: Dict[str, Any]
    success: bool
    message: str

# Initialize enhanced router
enhanced_router = APIRouter(prefix="/api/spiritual/enhanced", tags=["Enhanced Spiritual Guidance"])

# Database dependency
async def get_db():
    """Get database connection dependency"""
    database_url = os.getenv("DATABASE_URL")
    
    # Validate DATABASE_URL is set
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is missing or empty. "
            "Please set the DATABASE_URL environment variable in your environment. "
            "Example: export DATABASE_URL='postgresql://user:password@localhost/dbname'"
        )
    
    conn = await asyncpg.connect(database_url)
    try:
        yield conn
    finally:
        await conn.close()

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
            # Runtime import of RAG system
            try:
                from .enhanced_rag_knowledge_engine import initialize_rag_system
                global RAG_AVAILABLE
                RAG_AVAILABLE = True
            except ImportError as import_error:
                logger.warning(f"RAG system not available: {import_error}")
                global RAG_AVAILABLE
                RAG_AVAILABLE = False
                self.fallback_mode = True
                return
            
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
                # Runtime import for RAG guidance function
                try:
                    from .enhanced_rag_knowledge_engine import get_rag_enhanced_guidance
                    enhanced_result = await get_rag_enhanced_guidance(
                        request.question,
                        request.birth_details,
                        request.service_type
                    )
                except ImportError as import_error:
                    logger.warning(f"RAG guidance function not available: {import_error}")
                    enhanced_result = None
            
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

@enhanced_router.post("/comprehensive-reading", response_model=ComprehensiveReadingResponse)
async def get_comprehensive_reading(
    request: ComprehensiveReadingRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Get comprehensive 30-minute life reading with DYNAMIC PRICING
    """
    try:
        # Initialize dynamic pricing engine or use fallback
        if DYNAMIC_PRICING_AVAILABLE:
            pricing_engine = DynamicComprehensivePricing()
            pricing_info = await pricing_engine.calculate_comprehensive_reading_price()
            current_price = pricing_info["current_price"]
        else:
            # Fallback to fixed pricing
            current_price = 12
            pricing_info = {
                "current_price": 12,
                "pricing_rationale": "Fixed pricing - dynamic system not available",
                "demand_factor": 1.0,
                "cost_breakdown": {"total_operational_cost": 8.5},
                "ai_recommendation": {"recommended_price": 12, "confidence": 0.5}
            }
        
        # Check if user has sufficient credits (this would be implemented with user auth)
        # For now, we'll proceed with the pricing calculation
        
        # Get service configuration with dynamic pricing
        service_config = await get_comprehensive_service_config(current_price)
        
        # Generate preview of the reading
        reading_preview = await generate_reading_preview(
            request.birth_date, 
            request.birth_time, 
            request.birth_location
        )
        
        # Create session with dynamic pricing
        session_id = await create_comprehensive_session(
            request, 
            current_price, 
            service_config, 
            db
        )
        
        # Schedule pricing recommendation generation in background
        background_tasks.add_task(generate_pricing_recommendations)
        
        return ComprehensiveReadingResponse(
            session_id=session_id,
            current_price=current_price,
            estimated_duration=service_config["duration_minutes"],
            service_configuration=service_config,
            pricing_rationale=pricing_info["pricing_rationale"],
            reading_preview=reading_preview,
            success=True,
            message=f"Comprehensive reading session created. Current price: {current_price} credits"
        )
        
    except Exception as e:
        logger.error(f"Comprehensive reading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_comprehensive_service_config(current_price: float) -> Dict[str, Any]:
    """Get service configuration with dynamic pricing"""
    return {
        "service_type": "comprehensive_life_reading_30min",
        "duration_minutes": 30,
        "credits_required": current_price,  # DYNAMIC PRICING!
        "knowledge_domains": [
            "classical_astrology",
            "tamil_spiritual_literature", 
            "relationship_astrology",
            "career_astrology",
            "health_astrology",
            "remedial_measures"
        ],
        "persona_mode": "comprehensive_life_master",
        "analysis_sections": [
            "birth_chart_analysis",
            "planetary_positions",
            "house_analysis", 
            "dasha_predictions",
            "life_path_guidance",
            "relationship_insights",
            "career_guidance",
            "health_indicators",
            "remedial_measures"
        ],
        "includes_birth_chart": True,
        "includes_remedies": True,
        "includes_predictions": True,
        "pricing_model": "dynamic_market_based"
    }

async def create_comprehensive_session(
    request: ComprehensiveReadingRequest,
    current_price: float,
    service_config: Dict[str, Any],
    db: asyncpg.Connection
) -> str:
    """Create session with dynamic pricing"""
    session_id = f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store session with dynamic pricing
    await db.execute("""
        INSERT INTO sessions 
        (session_id, service_type, credits_required, birth_date, birth_time, birth_location, 
         focus_areas, service_configuration, pricing_rationale, created_at, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CURRENT_TIMESTAMP, 'active')
    """, (
        session_id,
        service_config["service_type"],
        current_price,  # Dynamic price
        request.birth_date,
        request.birth_time,
        request.birth_location,
        ",".join(request.focus_areas),
        json.dumps(service_config),
        f"Dynamic pricing: {current_price} credits"
    ))
    
    return session_id

async def generate_reading_preview(birth_date: str, birth_time: str, birth_location: str) -> Dict[str, Any]:
    """Generate a preview of the comprehensive reading"""
    try:
        # Simple preview generation - in a real implementation this would use actual astrology calculations
        return {
            "chart_summary": f"Birth chart for {birth_date} at {birth_time} in {birth_location}",
            "key_highlights": [
                "Planetary positions indicate strong spiritual inclination",
                "Favorable period for major life decisions approaching",
                "Relationships sector shows positive developments"
            ],
            "analysis_sections": [
                "Complete birth chart analysis",
                "Planetary strength assessment", 
                "Dasha periods and predictions",
                "Relationship compatibility insights",
                "Career and financial prospects",
                "Health and wellness guidance",
                "Spiritual development path",
                "Personalized remedies and mantras"
            ],
            "estimated_reading_time": "30 minutes",
            "included_features": [
                "Detailed birth chart visualization",
                "Personalized gemstone recommendations",
                "Custom mantra prescriptions",
                "Favorable timing suggestions"
            ]
        }
    except Exception as e:
        logger.error(f"Preview generation error: {e}")
        return {
            "chart_summary": "Preview generation in progress...",
            "key_highlights": ["Comprehensive analysis being prepared"],
            "analysis_sections": ["Full reading available after booking"],
            "estimated_reading_time": "30 minutes",
            "included_features": ["Complete spiritual guidance package"]
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

@enhanced_router.get("/pricing/comprehensive")
async def get_comprehensive_pricing():
    """Get current comprehensive reading pricing information"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "current_price": 12,
                "recommended_price": 12,
                "price_change_needed": False,
                "demand_factor": 1.0,
                "cost_breakdown": {"total_operational_cost": 8.5},
                "ai_recommendation": {"recommended_price": 12, "confidence": 0.5},
                "pricing_rationale": "Fixed pricing - dynamic system not available",
                "last_updated": datetime.now().isoformat(),
                "next_review": datetime.now().isoformat()
            }
        
        pricing_engine = DynamicComprehensivePricing()
        pricing_info = await pricing_engine.get_current_price_info()
        new_calculation = await pricing_engine.calculate_comprehensive_reading_price()
        
        return {
            "current_price": pricing_info.get("current_price", 12),
            "recommended_price": new_calculation["current_price"],
            "price_change_needed": abs(pricing_info.get("current_price", 12) - new_calculation["current_price"]) > 1,
            "demand_factor": new_calculation["demand_factor"],
            "cost_breakdown": new_calculation["cost_breakdown"],
            "ai_recommendation": new_calculation["ai_recommendation"],
            "pricing_rationale": new_calculation["pricing_rationale"],
            "last_updated": pricing_info.get("last_updated", datetime.now().isoformat()),
            "next_review": new_calculation["next_review"]
        }
    except Exception as e:
        logger.error(f"Pricing info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/pricing/comprehensive/recommend")
async def generate_comprehensive_pricing_recommendation():
    """Generate pricing recommendation for comprehensive reading"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available",
                "recommendation": {
                    "current_price": 12,
                    "recommended_price": 12,
                    "requires_admin_approval": True
                }
            }
        
        pricing_recommendation = await generate_pricing_recommendations()
        
        return {
            "success": True,
            "message": "Pricing recommendation generated successfully",
            "recommendation": pricing_recommendation,
            "requires_admin_approval": True,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Pricing recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.post("/pricing/comprehensive/apply")
async def apply_comprehensive_pricing(
    approved_price: float,
    admin_notes: str = ""
):
    """Apply admin-approved comprehensive reading price"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available"
            }
        
        result = await apply_admin_approved_pricing(approved_price, admin_notes)
        
        return result
    except Exception as e:
        logger.error(f"Pricing application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@enhanced_router.get("/pricing/dashboard")
async def get_pricing_dashboard():
    """Get comprehensive pricing dashboard data for admin"""
    try:
        if not DYNAMIC_PRICING_AVAILABLE:
            return {
                "success": False,
                "message": "Dynamic pricing system not available",
                "data": {
                    "current_pricing": {"current_price": 12},
                    "recommended_pricing": {"current_price": 12},
                    "price_change_needed": False,
                    "market_conditions": {"demand_factor": 1.0}
                },
                "timestamp": datetime.now().isoformat()
            }
        
        from dynamic_comprehensive_pricing import get_pricing_dashboard_data
        
        dashboard_data = await get_pricing_dashboard_data()
        
        return {
            "success": True,
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Personalized Remedies Models
class PersonalizedRemediesRequest(BaseModel):
    birth_details: Dict[str, Any]
    current_issues: List[str] = Field(default_factory=lambda: ["general_wellbeing"])
    preferences: Dict[str, Any] = Field(default_factory=dict)

class RemedyItem(BaseModel):
    name: str
    description: str
    benefits: str
    instructions: str

class PersonalizedRemediesResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""

@enhanced_router.post("/personalized-remedies", response_model=PersonalizedRemediesResponse)
async def get_personalized_remedies(
    request: PersonalizedRemediesRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate personalized spiritual remedies based on birth details and current issues
    """
    try:
        # Extract preferences for filtering
        preferences = request.preferences
        
        # TODO: Implement personalization logic using birth_details and current_issues
        # For now, this returns static remedies but can be enhanced to use:
        # - request.birth_details for astrological calculations
        # - request.current_issues for targeted remedy selection
        
        # Determine the most relevant remedies based on birth details
        # This is a simplified implementation - in a full system, this would
        # involve complex astrological calculations
        
        remedies_data = {
            "mantras": [
                {
                    "name": "Ganesha Mantra for Obstacle Removal",
                    "sanskrit": "ॐ गं गणपतये नमः",
                    "transliteration": "Om Gam Ganapataye Namaha",
                    "meaning": "I bow to Lord Ganesha, the remover of obstacles",
                    "benefits": "Removes obstacles, brings clarity and new beginnings",
                    "repetitions": "108 times daily",
                    "best_time": "Early morning (6-8 AM)",
                    "duration": "21 days minimum",
                    "special_instructions": "Face east while chanting, use a rosary for counting"
                },
                {
                    "name": "Surya Mantra for Vitality",
                    "sanskrit": "ॐ सूर्याय नमः",
                    "transliteration": "Om Suryaya Namaha",
                    "meaning": "I bow to the Sun God",
                    "benefits": "Increases energy, confidence, and leadership qualities",
                    "repetitions": "108 times daily",
                    "best_time": "Sunrise",
                    "duration": "40 days",
                    "special_instructions": "Face the rising sun, offer water to the sun while chanting"
                }
            ],
            "gemstones": [
                {
                    "name": "Yellow Sapphire (Pukhraj)",
                    "planet": "Jupiter",
                    "benefits": "Enhances wisdom, prosperity, and spiritual growth",
                    "weight_range": "3-5 carats",
                    "metal": "Gold",
                    "wearing_position": "Index finger of right hand",
                    "best_day": "Thursday morning",
                    "quality_guidelines": [
                        "Should be natural and untreated",
                        "Clear and transparent with good luster",
                        "Free from cracks and inclusions",
                        "Certified by a reputable gemological institute"
                    ],
                    "energization_process": [
                        "Soak in raw milk overnight",
                        "Wash with Ganga water or clean water",
                        "Chant Jupiter mantra 108 times",
                        "Wear during Jupiter hora on Thursday"
                    ]
                }
            ],
            "charity": [
                {
                    "name": "Education Support",
                    "purpose": "Strengthen Jupiter and enhance knowledge",
                    "suggested_amount": "As per your capacity, minimum 1% of monthly income",
                    "best_day": "Thursday",
                    "planet": "Jupiter",
                    "items": [
                        "Books and educational materials",
                        "School supplies for underprivileged children",
                        "Sponsoring a child's education",
                        "Donations to libraries or educational institutions"
                    ],
                    "spiritual_significance": "Supporting education creates positive karma and enhances the Jupiter principle of wisdom and knowledge in your life"
                }
            ],
            "temple_worship": [
                {
                    "deity": "Lord Ganesha",
                    "purpose": "Remove obstacles and ensure success in new endeavors",
                    "best_days": "Wednesday and Chaturthi (4th lunar day)",
                    "best_time": "Morning hours (6-10 AM)",
                    "offerings": [
                        "Modak (sweet dumplings)",
                        "Red flowers (especially hibiscus)",
                        "Durva grass",
                        "Coconut and banana"
                    ],
                    "special_prayers": [
                        {
                            "name": "Ganesha Ashtakam",
                            "description": "Eight verses praising Lord Ganesha"
                        },
                        {
                            "name": "Vakratunda Mahakaya",
                            "description": "Powerful Ganesha prayer for obstacle removal"
                        }
                    ],
                    "recommended_temples": [
                        "Local Ganesha temple in your area",
                        "Any Vinayaka temple on Chaturthi days"
                    ]
                }
            ],
            "general_guidance": "These remedies are designed to harmonize your planetary energies and address the current challenges in your life. Practice them with faith and consistency. Remember that the most powerful remedy is living a righteous life with compassion and service to others. Regular meditation, prayer, and acts of kindness amplify the effects of all remedial measures."
        }
        
        # Filter based on preferences
        if not preferences.get("include_mantras", True):
            remedies_data.pop("mantras", None)
        if not preferences.get("include_gemstones", True):
            remedies_data.pop("gemstones", None)
        if not preferences.get("include_charity", True):
            remedies_data.pop("charity", None)
        if not preferences.get("include_temple_worship", True):
            remedies_data.pop("temple_worship", None)
        
        return PersonalizedRemediesResponse(
            success=True,
            data=remedies_data,
            message="Personalized remedies generated successfully"
        )
        
    except Exception as e:
        logging.error(f"Error generating personalized remedies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate personalized remedies: {str(e)}"
        ) from e

# Alternative path removed since frontend now uses correct enhanced path

# Export router for inclusion in main app
router = enhanced_router