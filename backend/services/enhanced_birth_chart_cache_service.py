"""
Enhanced Birth Chart Caching Service
Handles caching of birth chart data + PDF reports + AI-generated Swamiji readings
"""

import hashlib
import json
import asyncpg
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import os
from pathlib import Path

# Try to import OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import existing RAG engine
try:
    from enhanced_rag_knowledge_engine import RAGKnowledgeEngine, KnowledgeQuery
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProkeralaPDFProcessor:
    """Process PDF reports from Prokerala API"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expiry = 0
    
    async def get_token(self) -> str:
        """Get valid Prokerala API token"""
        if not self.token or datetime.now().timestamp() > self.token_expiry:
            await self._refresh_token()
        return self.token or ""
    
    async def _refresh_token(self):
        """Refresh Prokerala API token"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                response = await client.post("https://api.prokerala.com/token", data=data)
                response.raise_for_status()
                token_data = response.json()
                self.token = token_data["access_token"]
                self.token_expiry = datetime.now().timestamp() + token_data.get("expires_in", 3600) - 60
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    async def fetch_pdf_reports(self, birth_details: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch available PDF reports from Prokerala API"""
        reports = {}
        
        # Prokerala PDF report endpoints (these are the actual available endpoints)
        pdf_endpoints = {
            'basic_prediction': '/v2/astrology/basic-prediction',
            'detailed_horoscope': '/v2/astrology/birth-details',  # This gives detailed text
            'planetary_positions': '/v2/astrology/planet-position',
            'house_cusps': '/v2/astrology/house-cusps',
            'dasha_periods': '/v2/astrology/current-dasha'
        }
        
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Prepare parameters
        datetime_str = f"{birth_details['date']}T{birth_details['time']}:00+05:30"
        coordinates = "9.66845,80.00742"  # Default coordinates
        
        params = {
            "datetime": datetime_str,
            "coordinates": coordinates,
            "ayanamsa": "1"
        }
        
        async with httpx.AsyncClient() as client:
            for report_type, endpoint in pdf_endpoints.items():
                try:
                    response = await client.get(
                        f"https://api.prokerala.com{endpoint}",
                        headers=headers,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        report_data = response.json()
                        if report_data.get('data'):
                            reports[report_type] = {
                                'data': report_data['data'],
                                'text_content': self._extract_text_from_data(report_data['data']),
                                'structured_data': report_data['data'],
                                'generated_at': datetime.now().isoformat(),
                                'endpoint': endpoint
                            }
                    else:
                        logger.warning(f"Failed to fetch {report_type}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error fetching {report_type}: {e}")
        
        return reports
    
    def _extract_text_from_data(self, data: Dict[str, Any]) -> str:
        """Extract meaningful text from structured data for RAG processing"""
        text_parts = []
        
        def extract_text_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and len(value) > 3:
                        text_parts.append(f"{prefix}{key}: {value}")
                    elif isinstance(value, (dict, list)):
                        extract_text_recursive(value, f"{prefix}{key}_")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_text_recursive(item, f"{prefix}{i}_")
            elif isinstance(obj, str) and len(obj) > 3:
                text_parts.append(f"{prefix}: {obj}")
        
        extract_text_recursive(data)
        return "\n".join(text_parts)

class EnhancedBirthChartCacheService:
    """Enhanced service for managing birth chart data + PDF reports + AI readings"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.cache_duration_days = 365
        
        # Initialize Prokerala API
        self.prokerala_client_id = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
        self.prokerala_client_secret = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
        self.pdf_processor = ProkeralaPDFProcessor(self.prokerala_client_id, self.prokerala_client_secret)
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.openai_client = None
            logger.warning("OpenAI not available for AI readings")
    
    def generate_birth_details_hash(self, birth_details: Dict[str, Any]) -> str:
        """Generate unique hash for birth details"""
        normalized_data = {
            'date': birth_details.get('date', ''),
            'time': birth_details.get('time', ''),
            'location': birth_details.get('location', '').lower().strip(),
            'timezone': birth_details.get('timezone', 'Asia/Colombo')
        }
        
        normalized_string = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(normalized_string.encode()).hexdigest()
    
    async def get_cached_complete_profile(self, user_email: str, birth_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get complete cached profile including birth chart + PDF reports + AI reading"""
        try:
            birth_hash = self.generate_birth_details_hash(birth_details)
            
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetchrow("""
                SELECT birth_chart_data, birth_chart_cached_at, birth_chart_expires_at
                FROM users 
                WHERE email = $1 
                AND birth_chart_hash = $2 
                AND birth_chart_expires_at > NOW()
                AND birth_chart_data IS NOT NULL
            """, user_email, birth_hash)
            
            await conn.close()
            
            if result:
                logger.info(f"✅ Complete profile cache HIT for user {user_email}")
                cached_data = json.loads(result['birth_chart_data'])
                
                return {
                    'birth_chart': cached_data.get('birth_chart', {}),
                    'pdf_reports': cached_data.get('pdf_reports', {}),
                    'swamiji_reading': cached_data.get('swamiji_reading', {}),
                    'cached_at': result['birth_chart_cached_at'],
                    'expires_at': result['birth_chart_expires_at'],
                    'cache_hit': True
                }
            else:
                logger.info(f"❌ Complete profile cache MISS for user {user_email}")
                return None
                    
        except Exception as e:
            logger.error(f"Error getting cached profile: {e}")
            return None
    
    async def generate_and_cache_complete_profile(self, user_email: str, birth_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete profile: birth chart + PDF reports + AI reading and cache it"""
        try:
            logger.info(f"🚀 Generating complete profile for {user_email}")
            
            # Step 1: Get birth chart data from Prokerala
            birth_chart_data = await self._fetch_birth_chart_data(birth_details)
            
            # Step 2: Get PDF reports from Prokerala  
            pdf_reports = await self.pdf_processor.fetch_pdf_reports(birth_details)
            
            # Step 3: Generate AI reading with Swamiji's persona
            swamiji_reading = await self._generate_swamiji_reading(birth_chart_data, pdf_reports, birth_details)
            
            # Step 4: Cache the complete profile
            complete_profile = {
                'birth_chart': birth_chart_data,
                'pdf_reports': pdf_reports,
                'swamiji_reading': swamiji_reading,
                'generated_at': datetime.now().isoformat(),
                'data_sources': {
                    'birth_chart': 'Prokerala API v2/astrology/birth-details + chart',
                    'pdf_reports': list(pdf_reports.keys()),
                    'ai_reading': 'OpenAI + Swamiji RAG Knowledge',
                    'total_api_calls': len(pdf_reports) + 2  # birth chart + chart + PDF reports
                }
            }
            
            success = await self._cache_complete_profile(user_email, birth_details, complete_profile)
            
            if success:
                logger.info(f"✅ Complete profile cached for {user_email}")
                complete_profile['cached'] = True
            else:
                logger.error(f"❌ Failed to cache profile for {user_email}")
                complete_profile['cached'] = False
            
            return complete_profile
            
        except Exception as e:
            logger.error(f"Error generating complete profile: {e}")
            raise
    
    async def _fetch_birth_chart_data(self, birth_details: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch birth chart data from Prokerala API (existing logic)"""
        try:
            token = await self.pdf_processor.get_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            datetime_str = f"{birth_details['date']}T{birth_details['time']}:00+05:30"
            coordinates = "9.66845,80.00742"
            
            params = {
                "datetime": datetime_str,
                "coordinates": coordinates,
                "ayanamsa": "1"
            }
            
            chart_data = {}
            
            async with httpx.AsyncClient() as client:
                # Get basic birth details
                basic_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/birth-details",
                    headers=headers,
                    params=params
                )
                
                if basic_resp.status_code == 200:
                    basic_data = basic_resp.json()
                    if "data" in basic_data:
                        chart_data.update(basic_data["data"])
                
                # Get chart visualization
                chart_params = {**params, "chart_type": "rasi", "chart_style": "north-indian", "format": "json"}
                chart_resp = await client.get(
                    "https://api.prokerala.com/v2/astrology/chart",
                    headers=headers,
                    params=chart_params
                )
                
                if chart_resp.status_code == 200:
                    chart_visual_data = chart_resp.json()
                    if "data" in chart_visual_data:
                        chart_data["chart_visualization"] = chart_visual_data["data"]
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Birth chart data fetch failed: {e}")
            raise
    
    async def _generate_swamiji_reading(self, birth_chart_data: Dict[str, Any], 
                                       pdf_reports: Dict[str, Any], 
                                       birth_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI reading with Swamiji's persona using RAG + PDF insights"""
        try:
            if not self.openai_client:
                return {
                    'reading': 'AI reading service not available. Please configure OpenAI API key.',
                    'generated_with': 'fallback',
                    'error': 'OpenAI not available'
                }
            
            # Build comprehensive prompt with all data
            prompt = await self._build_swamiji_prompt(birth_chart_data, pdf_reports, birth_details)
            
            # Generate AI response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are Swami Jyotirananthan, a revered Tamil Vedic astrology master. 
                        You speak with wisdom, compassion, and authority. Mix Tamil phrases naturally with English.
                        Always start with "Vanakkam" and end with "Tamil thaai arul kondae vazhlga".
                        Base your reading on the provided astrological data and give practical spiritual guidance."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_reading = response.choices[0].message.content
            
            # Structure the reading
            return {
                'complete_reading': ai_reading,
                'birth_chart_summary': self._extract_chart_summary(birth_chart_data),
                'personality_insights': self._extract_personality_insights(ai_reading),
                'spiritual_guidance': self._extract_spiritual_guidance(ai_reading),
                'practical_advice': self._extract_practical_advice(ai_reading),
                'generated_with': 'OpenAI GPT-4 + Swamiji Persona',
                'data_sources_used': {
                    'birth_chart': bool(birth_chart_data),
                    'pdf_reports': list(pdf_reports.keys()),
                    'ai_model': 'gpt-4'
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Swamiji reading generation failed: {e}")
            return {
                'reading': f'Vanakkam! I apologize, but I am experiencing technical difficulties in generating your reading. Please try again later. Tamil thaai arul kondae vazhlga.',
                'generated_with': 'fallback',
                'error': str(e)
            }
    
    async def _build_swamiji_prompt(self, birth_chart_data: Dict[str, Any], 
                                   pdf_reports: Dict[str, Any], 
                                   birth_details: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Swamiji's reading"""
        
        # Extract key astrological data
        nakshatra = birth_chart_data.get('nakshatra', {}).get('name', 'Unknown')
        moon_sign = birth_chart_data.get('chandra_rasi', {}).get('name', 'Unknown')
        sun_sign = birth_chart_data.get('soorya_rasi', {}).get('name', 'Unknown')
        ascendant = birth_chart_data.get('lagna', {}).get('name', 'Unknown')
        
        # Build PDF insights
        pdf_insights = ""
        for report_type, report_data in pdf_reports.items():
            if report_data.get('text_content'):
                pdf_insights += f"\n\n{report_type.upper()} INSIGHTS:\n{report_data['text_content'][:500]}..."
        
        prompt = f"""
Vanakkam! I am providing a comprehensive spiritual reading for someone born on {birth_details.get('date')} at {birth_details.get('time')} in {birth_details.get('location')}.

ASTROLOGICAL FOUNDATION:
- Birth Nakshatra: {nakshatra}
- Moon Sign (Chandra Rasi): {moon_sign}
- Sun Sign (Soorya Rasi): {sun_sign}
- Ascendant (Lagna): {ascendant}

DETAILED ASTROLOGICAL INSIGHTS:{pdf_insights}

CHART VISUALIZATION DATA:
{json.dumps(birth_chart_data.get('chart_visualization', {}), indent=2)[:1000]}...

Please provide a comprehensive reading that includes:
1. Personality analysis based on nakshatra and planetary positions
2. Life path guidance and spiritual development
3. Relationship and marriage prospects
4. Career and financial guidance
5. Health and wellness advice
6. Specific spiritual remedies and practices
7. Auspicious timings and recommendations

Write in your authentic Tamil-English style with compassion and wisdom.
Make it personal and practical for daily life.
"""
        
        return prompt
    
    def _extract_chart_summary(self, birth_chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key chart summary for quick display"""
        return {
            'nakshatra': birth_chart_data.get('nakshatra', {}).get('name', 'Unknown'),
            'moon_sign': birth_chart_data.get('chandra_rasi', {}).get('name', 'Unknown'),
            'sun_sign': birth_chart_data.get('soorya_rasi', {}).get('name', 'Unknown'),
            'ascendant': birth_chart_data.get('lagna', {}).get('name', 'Unknown'),
            'has_chart_visualization': bool(birth_chart_data.get('chart_visualization'))
        }
    
    def _extract_personality_insights(self, reading: str) -> List[str]:
        """Extract personality insights from AI reading"""
        insights = []
        lines = reading.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['personality', 'nature', 'character', 'trait']):
                insights.append(line.strip())
        
        return insights[:3]  # Top 3 personality insights
    
    def _extract_spiritual_guidance(self, reading: str) -> List[str]:
        """Extract spiritual guidance from AI reading"""
        guidance = []
        lines = reading.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['spiritual', 'remedy', 'practice', 'mantra', 'meditation']):
                guidance.append(line.strip())
        
        return guidance[:3]  # Top 3 spiritual guidance points
    
    def _extract_practical_advice(self, reading: str) -> List[str]:
        """Extract practical advice from AI reading"""
        advice = []
        lines = reading.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['should', 'avoid', 'recommend', 'suggest', 'advice']):
                advice.append(line.strip())
        
        return advice[:3]  # Top 3 practical advice points
    
    async def _cache_complete_profile(self, user_email: str, birth_details: Dict[str, Any], 
                                     complete_profile: Dict[str, Any]) -> bool:
        """Cache complete profile to database"""
        try:
            birth_hash = self.generate_birth_details_hash(birth_details)
            cached_at = datetime.now()
            expires_at = cached_at + timedelta(days=self.cache_duration_days)
            
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute("""
                UPDATE users SET 
                    birth_chart_data = $1,
                    birth_chart_hash = $2,
                    birth_chart_cached_at = $3,
                    birth_chart_expires_at = $4,
                    has_free_birth_chart = $5,
                    birth_date = $6,
                    birth_time = $7,
                    birth_location = $8
                WHERE email = $9
            """, 
            json.dumps(complete_profile),
            birth_hash,
            cached_at,
            expires_at,
            True,
            birth_details.get('date'),
            birth_details.get('time'),
            birth_details.get('location'),
            user_email)
            
            await conn.close()
            
            logger.info(f"✅ Complete profile cached for {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching complete profile: {e}")
            return False
    
    async def get_user_profile_status(self, user_email: str) -> Dict[str, Any]:
        """Get user's complete profile status"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            result = await conn.fetchrow("""
                SELECT 
                    birth_date, birth_time, birth_location, birth_chart_cached_at, 
                    birth_chart_expires_at, has_free_birth_chart,
                    (birth_chart_data IS NOT NULL) as has_cached_data,
                    (birth_chart_expires_at > NOW()) as cache_valid
                FROM users 
                WHERE email = $1
            """, user_email)
            
            await conn.close()
            
            if result:
                return {
                    'has_birth_details': bool(result['birth_date'] and result['birth_time'] and result['birth_location']),
                    'has_cached_data': bool(result['has_cached_data']),
                    'cache_valid': bool(result['cache_valid']),
                    'cached_at': result['birth_chart_cached_at'],
                    'expires_at': result['birth_chart_expires_at'],
                    'has_free_birth_chart': bool(result['has_free_birth_chart'])
                }
            else:
                return {
                    'has_birth_details': False,
                    'has_cached_data': False,
                    'cache_valid': False,
                    'cached_at': None,
                    'expires_at': None,
                    'has_free_birth_chart': False
                }
                    
        except Exception as e:
            logger.error(f"Error getting user profile status: {e}")
            return {'error': str(e)}