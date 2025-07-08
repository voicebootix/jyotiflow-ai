import os
import time
import httpx
import openai
from typing import Dict, Any, Optional
from datetime import datetime

class ProkeralaService:
    def __init__(self):
        self.client_id = os.getenv("PROKERALA_CLIENT_ID", "your-client-id")
        self.client_secret = os.getenv("PROKERALA_CLIENT_SECRET", "your-client-secret")
        self.token_url = "https://api.prokerala.com/token"
        self.api_base = "https://api.prokerala.com/v2/astrology"
        self.openai_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        
        # Token cache
        self.token = None
        self.token_expiry = 0
    
    async def get_token(self) -> str:
        """Get valid token, refresh if expired"""
        if not self.token or time.time() > self.token_expiry:
            return await self.fetch_new_token()
        return self.token
    
    async def fetch_new_token(self) -> str:
        """Fetch new access token from Prokerala"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            resp = await client.post(self.token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()
            self.token = token_data["access_token"]
            self.token_expiry = int(time.time()) + int(token_data.get("expires_in", 3600)) - 60
            return self.token
    
    def format_birth_details(self, birth_details: Dict[str, Any]) -> Dict[str, str]:
        """Format birth details for Prokerala API"""
        date = birth_details.get("date")
        time_str = birth_details.get("time")
        location = birth_details.get("location", "Jaffna, Sri Lanka")
        
        # Format datetime with timezone
        datetime_str = f"{date}T{time_str}:00+05:30"
        
        # Default coordinates for Jaffna (enhance with geocoding later)
        latitude = "9.66845"
        longitude = "80.00742"
        coordinates = f"{latitude},{longitude}"
        
        return {
            "datetime": datetime_str,
            "coordinates": coordinates,
            "ayanamsa": "1"
        }
    
    async def get_complete_birth_chart(self, birth_details: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete birth chart data from Prokerala"""
        params = self.format_birth_details(birth_details)
        chart_data = {}
        
        for attempt in range(2):  # Retry once with token refresh
            try:
                token = await self.get_token()
                headers = {"Authorization": f"Bearer {token}"}
                
                async with httpx.AsyncClient() as client:
                    # Get birth details
                    birth_resp = await client.get(
                        f"{self.api_base}/birth-details",
                        headers=headers,
                        params=params
                    )
                    if birth_resp.status_code == 200:
                        chart_data.update(birth_resp.json())
                    
                    # Get planets data
                    planets_resp = await client.get(
                        f"{self.api_base}/planets",
                        headers=headers,
                        params=params
                    )
                    if planets_resp.status_code == 200:
                        planets_data = planets_resp.json()
                        if "data" in planets_data:
                            chart_data["planets"] = planets_data["data"]
                    
                    # Get houses data
                    houses_resp = await client.get(
                        f"{self.api_base}/houses",
                        headers=headers,
                        params=params
                    )
                    if houses_resp.status_code == 200:
                        houses_data = houses_resp.json()
                        if "data" in houses_data:
                            chart_data["houses"] = houses_data["data"]
                
                # Ensure required keys exist
                chart_data.setdefault("planets", {})
                chart_data.setdefault("houses", {})
                chart_data.setdefault("data", {})
                
                return chart_data
                
            except Exception as e:
                if attempt == 0 and "401" in str(e):
                    # Token expired, refresh and retry
                    await self.fetch_new_token()
                    continue
                raise e
        
        # Return minimal data if all attempts fail
        return {
            "data": {
                "nakshatra": {"name": "Unable to calculate"},
                "chandra_rasi": {"name": "Unable to calculate"}
            },
            "error": "Prokerala API unavailable"
        }
    
    async def generate_spiritual_guidance(self, question: str, astrology_data: Dict[str, Any]) -> str:
        """Generate spiritual guidance using OpenAI based on real astrology data"""
        try:
            openai.api_key = self.openai_key
            
            # Extract key astrological information
            nakshatra = "Unknown"
            rasi = "Unknown"
            
            if "data" in astrology_data:
                if "nakshatra" in astrology_data["data"]:
                    nakshatra = astrology_data["data"]["nakshatra"].get("name", "Unknown")
                if "chandra_rasi" in astrology_data["data"]:
                    rasi = astrology_data["data"]["chandra_rasi"].get("name", "Unknown")
            
            prompt = f"""You are Swami Jyotirananthan, a revered Tamil spiritual master and Jyotish expert.

User's Question: {question}

Astrological Information:
- Nakshatra: {nakshatra}
- Chandra Rasi: {rasi}
- Additional chart data: {astrology_data}

Provide comprehensive spiritual guidance in a warm, compassionate Tamil-influenced style. Include:
1. Direct response to their question
2. Astrological insights from their chart
3. Practical spiritual advice
4. Tamil wisdom where appropriate
5. Positive encouragement

Write in English but include Tamil spiritual concepts and blessings."""

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Swami Jyotirananthan, a compassionate Tamil spiritual guide combining ancient wisdom with modern understanding."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback guidance if OpenAI fails
            return f"""🕉️ Divine Guidance from Swami Jyotirananthan

Your Question: {question}

Though the cosmic energies are temporarily unclear, I offer you this guidance from the eternal Tamil wisdom:

Based on your birth nakshatra {nakshatra} and rasi {rasi}, remember that every soul's journey is unique and divinely guided.

The ancient Tamil text says: "அறிவுடையார் எல்லாம் அறிவார்" - The wise understand all things in their proper time.

May divine grace illuminate your path forward.

Om Namah Shivaya 🙏"""

# Global instance
prokerala_service = ProkeralaService()