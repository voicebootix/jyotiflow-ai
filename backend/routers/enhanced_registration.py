"""
Enhanced Registration System
Automatically generates complete birth chart profiles on registration:
- Birth chart data from Prokerala API
- PDF reports and insights
- AI-generated Swamiji readings
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr, validator
import bcrypt
import asyncpg
import json
import logging
import os

from services.enhanced_birth_chart_cache_service import EnhancedBirthChartCacheService
import db

logger = logging.getLogger(__name__)

router = APIRouter()

# Enhanced registration models
class BirthDetails(BaseModel):
    """Birth details for chart generation"""
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    location: str
    timezone: str = "Asia/Colombo"
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format')

class EnhancedUserRegistration(BaseModel):
    """Enhanced user registration with birth details"""
    name: str
    email: EmailStr
    password: str
    birth_details: BirthDetails
    phone: Optional[str] = None
    spiritual_level: str = "beginner"
    preferred_language: str = "en"
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class RegistrationResponse(BaseModel):
    """Registration response with birth chart status"""
    message: str
    user_id: int
    email: str
    birth_chart_generated: bool
    free_reading_available: bool
    registration_welcome: Dict[str, Any]

# Enhanced registration service
class EnhancedRegistrationService:
    """Service for handling enhanced user registration"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/yourdb")
        self.birth_chart_service = EnhancedBirthChartCacheService(self.database_url)
    
    async def register_user_with_birth_chart(self, user_data: EnhancedUserRegistration) -> RegistrationResponse:
        """Register user and automatically generate complete birth chart profile"""
        try:
            # Step 1: Validate and create user account
            user_id = await self._create_user_account(user_data)
            
            # Step 2: Generate complete birth chart profile in background
            welcome_data = await self._generate_welcome_profile(user_data.email, user_data.birth_details)
            
            logger.info(f"✅ Enhanced registration completed for {user_data.email}")
            
            return RegistrationResponse(
                message="வணக்கம்! Welcome to JyotiFlow! Your personalized birth chart and spiritual reading are ready.",
                user_id=user_id,
                email=user_data.email,
                birth_chart_generated=welcome_data.get('birth_chart_generated', False),
                free_reading_available=welcome_data.get('free_reading_available', False),
                registration_welcome=welcome_data
            )
            
        except Exception as e:
            logger.error(f"Registration failed for {user_data.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def _create_user_account(self, user_data: EnhancedUserRegistration) -> int:
        """Create user account in database"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = await asyncpg.connect(self.database_url)
            try:
                # Check if user already exists
                existing_user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user_data.email)
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists"
                    )
                
                # Insert new user
                user_id = await conn.fetchval("""
                    INSERT INTO users (
                        name, email, password_hash, phone, birth_date, birth_time, 
                        birth_location, spiritual_level, preferred_language, 
                        role, credits, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                    RETURNING id
                """, 
                    user_data.name,
                    user_data.email,
                    password_hash,
                    user_data.phone,
                    user_data.birth_details.date,
                    user_data.birth_details.time,
                    user_data.birth_details.location,
                    user_data.spiritual_level,
                    user_data.preferred_language,
                    'user',
                    50  # Welcome credits
                )
                
                if user_id is None:
                    raise ValueError("Failed to get user ID after insertion")
                
                return user_id
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"User account creation failed: {e}")
            raise
    
    async def _generate_welcome_profile(self, email: str, birth_details: BirthDetails) -> Dict[str, Any]:
        """Generate welcome profile with birth chart + PDF + AI reading"""
        try:
            # Convert birth details to format expected by service
            birth_dict = {
                'date': birth_details.date,
                'time': birth_details.time,
                'location': birth_details.location,
                'timezone': birth_details.timezone
            }
            
            # Check if profile already cached
            cached_profile = await self.birth_chart_service.get_cached_complete_profile(email, birth_dict)
            
            if cached_profile:
                logger.info(f"Using cached profile for {email}")
                return self._format_welcome_data(cached_profile, from_cache=True)
            
            # Generate new complete profile
            complete_profile = await self.birth_chart_service.generate_and_cache_complete_profile(email, birth_dict)
            
            return self._format_welcome_data(complete_profile, from_cache=False)
            
        except Exception as e:
            logger.error(f"Welcome profile generation failed for {email}: {e}")
            # Return fallback welcome data
            return {
                'birth_chart_generated': False,
                'free_reading_available': False,
                'error': str(e),
                'fallback_message': 'Welcome to JyotiFlow! Your birth chart will be generated shortly.'
            }
    
    def _format_welcome_data(self, profile_data: Dict[str, Any], from_cache: bool = False) -> Dict[str, Any]:
        """Format profile data for welcome response"""
        birth_chart = profile_data.get('birth_chart', {})
        swamiji_reading = profile_data.get('swamiji_reading', {})
        pdf_reports = profile_data.get('pdf_reports', {})
        
        return {
            'birth_chart_generated': bool(birth_chart),
            'free_reading_available': bool(swamiji_reading),
            'from_cache': from_cache,
            'data_summary': {
                'birth_chart_available': bool(birth_chart),
                'ai_reading_available': bool(swamiji_reading.get('complete_reading')),
                'pdf_reports_count': len(pdf_reports),
                'chart_visualization': bool(birth_chart.get('chart_visualization')),
                'nakshatra': birth_chart.get('nakshatra', {}).get('name', 'Unknown'),
                'moon_sign': birth_chart.get('chandra_rasi', {}).get('name', 'Unknown'),
                'sun_sign': birth_chart.get('soorya_rasi', {}).get('name', 'Unknown'),
                'ascendant': birth_chart.get('lagna', {}).get('name', 'Unknown')
            },
            'reading_preview': {
                'introduction': swamiji_reading.get('complete_reading', '')[:200] + '...' if swamiji_reading.get('complete_reading') else '',
                'personality_insights': swamiji_reading.get('personality_insights', [])[:2],
                'spiritual_guidance': swamiji_reading.get('spiritual_guidance', [])[:2],
                'practical_advice': swamiji_reading.get('practical_advice', [])[:2]
            },
            'value_proposition': {
                'estimated_value': '$60-105 USD',
                'includes': [
                    'Complete Vedic Birth Chart',
                    'Personalized AI Reading by Swamiji',
                    'Multiple Astrological Reports',
                    'Spiritual Guidance & Remedies',
                    'Lifetime Access to Your Profile'
                ],
                'upgrade_benefits': [
                    'Live Spiritual Guidance Sessions',
                    'Direct Chat with Swamiji',
                    'Personalized Remedies & Practices',
                    'Ongoing Life Path Updates'
                ]
            }
        }

# Initialize service
registration_service = EnhancedRegistrationService()

@router.post("/register", response_model=RegistrationResponse)
async def enhanced_register(
    user_data: EnhancedUserRegistration,
    background_tasks: BackgroundTasks
):
    """
    Enhanced user registration with automatic birth chart generation
    
    Features:
    - Creates user account with birth details
    - Automatically generates complete birth chart
    - Fetches PDF reports from Prokerala API
    - Generates AI reading with Swamiji's persona
    - Caches everything for lifetime access
    - Provides immediate value ($60-105 worth)
    """
    try:
        logger.info(f"🚀 Enhanced registration started for {user_data.email}")
        
        # Register user and generate complete profile
        response = await registration_service.register_user_with_birth_chart(user_data)
        
        return response
        
    except Exception as e:
        logger.error(f"Registration endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/profile/{email}/birth-chart")
async def get_user_birth_chart_profile(email: str, conn: asyncpg.Connection = Depends(db.get_db)):
    """Get user's complete birth chart profile"""
    try:
        # Get user's birth details from database
        result = await conn.fetchrow("""
            SELECT birth_date, birth_time, birth_location, 
                   birth_chart_data, has_free_birth_chart
            FROM users 
            WHERE email = $1
        """, email)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        birth_date, birth_time, birth_location, cached_data, has_free_chart = result
        
        if not (birth_date and birth_time and birth_location):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User birth details incomplete"
            )
        
        # Check if cached data exists
        if cached_data and has_free_chart:
            profile_data = cached_data if isinstance(cached_data, dict) else json.loads(cached_data)
            return {
                "status": "success",
                "cached": True,
                "profile": profile_data,
                "message": "Your complete birth chart profile is ready!"
            }
        
        # Generate new profile if not cached
        birth_details = {
            'date': birth_date,
            'time': birth_time,
            'location': birth_location,
            'timezone': 'Asia/Colombo'
        }
        
        service = EnhancedBirthChartCacheService()
        profile_data = await service.generate_and_cache_complete_profile(email, birth_details)
        
        return {
            "status": "success",
            "cached": False,
            "profile": profile_data,
            "message": "Your birth chart profile has been generated!"
        }
        
    except Exception as e:
        logger.error(f"Profile retrieval failed for {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile retrieval failed: {str(e)}"
        )

@router.get("/user/{email}/status")
async def get_user_registration_status(email: str):
    """Get user registration and birth chart status"""
    try:
        service = EnhancedBirthChartCacheService()
        status_data = await service.get_user_profile_status(email)
        
        return {
            "status": "success",
            "user_email": email,
            "profile_status": status_data
        }
        
    except Exception as e:
        logger.error(f"Status check failed for {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )