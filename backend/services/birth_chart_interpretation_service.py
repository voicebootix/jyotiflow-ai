"""
🔮 Birth Chart Interpretation Service

This service acts as the brain for interpreting raw astrological data from Prokerala.
It uses the RAG knowledge engine to transform raw data (e.g., "Mars in Leo")
into meaningful, wise interpretations in Swamiji's voice.
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging

# Assuming the RAG engine can be accessed.
# This might need to be passed in via dependency injection.
from backend.enhanced_rag_knowledge_engine import get_rag_enhanced_guidance, rag_engine

logger = logging.getLogger(__name__)

class BirthChartInterpretationService:
    """
    Transforms raw birth chart data into a comprehensive, RAG-powered interpretation.
    """

    def __init__(self):
        if not rag_engine:
            # In a real FastAPI app, the engine would be initialized on startup.
            # This is a fallback for direct script execution.
            logger.warning("RAG Engine not initialized. Interpretations will be limited.")
        logger.info("Birth Chart Interpretation Service initialized.")

    async def get_comprehensive_interpretation(self, prokerala_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main method to generate a full birth chart interpretation.

        Args:
            prokerala_data: The raw JSON response from the Prokerala API.

        Returns:
            A dictionary containing detailed interpretations for each planet and aspect.
        """
        if not rag_engine:
            return {
                "error": "RAG Engine is not available.",
                "summary": "Could not perform interpretation."
            }
            
        interpretations = {}
        
        # 1. Interpret Planetary Positions in Signs
        planetary_positions = prokerala_data.get("planets", [])
        if planetary_positions:
            interpretations["planetary_positions"] = await self._interpret_planetary_positions(planetary_positions)

        # 2. Interpret Planetary Positions in Houses (if available)
        # Assuming house data is part of the planetary_positions structure
        if planetary_positions:
             interpretations["house_positions"] = await self._interpret_house_positions(planetary_positions)

        # 3. Generate a summary
        interpretations["summary"] = await self._generate_summary(interpretations)
        
        return interpretations

    async def _interpret_planetary_positions(self, planets: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Queries the RAG engine for the meaning of each planet in its sign.
        """
        tasks = []
        for planet in planets:
            planet_name = planet.get("name")
            sign = planet.get("sign")
            if planet_name and sign:
                query = f"In Vedic astrology, what does it mean for a person to have {planet_name} in the sign of {sign}? Explain the positive and negative traits, and provide a wise spiritual perspective like a Swamiji."
                tasks.append(self._query_rag_for_interpretation(f"{planet_name}_in_{sign}", query))
        
        results = await asyncio.gather(*tasks)
        return {k: v for d in results for k, v in d.items()}

    async def _interpret_house_positions(self, planets: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Queries the RAG engine for the meaning of each planet in its house.
        """
        tasks = []
        for planet in planets:
            planet_name = planet.get("name")
            house_number = planet.get("house")
            if planet_name and house_number:
                query = f"In a birth chart, what are the effects of planet {planet_name} being in house number {house_number}? Describe the impact on life areas like career, relationships, and health from a spiritual master's viewpoint."
                tasks.append(self._query_rag_for_interpretation(f"{planet_name}_in_house_{house_number}", query))

        results = await asyncio.gather(*tasks)
        return {k: v for d in results for k, v in d.items()}

    async def _query_rag_for_interpretation(self, key: str, query: str) -> Dict[str, str]:
        """
        Helper function to query the RAG engine and handle potential errors.
        """
        try:
            response = await get_rag_enhanced_guidance(
                user_query=query,
                birth_details=None, # We are asking conceptual questions, not for a specific person
                service_type="astrological_interpretation"
            )
            interpretation_text = response.get("enhanced_guidance", "No specific guidance available.")
            return {key: interpretation_text}
        except Exception as e:
            logger.error(f"RAG query failed for key '{key}': {e}")
            return {key: "Could not retrieve interpretation due to an internal error."}

    async def _generate_summary(self, interpretations: Dict[str, Any]) -> str:
        """
        Uses the collected interpretations to generate a holistic summary.
        """
        # Combine all the individual interpretations into one context block
        full_context = ""
        for section, interpretations_dict in interpretations.items():
            full_context += f"## {section.replace('_', ' ').title()}:\n"
            for key, text in interpretations_dict.items():
                full_context += f"- **{key.replace('_', ' ').title()}:** {text}\n"

        summary_query = f"""
        Based on the following detailed astrological interpretations, please write a holistic, compassionate summary for a spiritual seeker.
        Act as Swami Jyotirananthan. Identify the most significant strengths and challenges in the chart and provide one key piece of advice.

        DETAILED INTERPRETATIONS:
        ---
        {full_context}
        ---
        """

        response = await get_rag_enhanced_guidance(
            user_query=summary_query,
            birth_details=None,
            service_type="astrological_summary"
        )
        return response.get("enhanced_guidance", "A summary could not be generated.")

# Example Usage
async def main():
    # This is a sample Prokerala-like data structure.
    sample_prokerala_data = {
        "planets": [
            {"name": "Sun", "sign": "Aries", "house": 1},
            {"name": "Moon", "sign": "Taurus", "house": 2},
            {"name": "Mars", "sign": "Leo", "house": 5},
            {"name": "Saturn", "sign": "Capricorn", "house": 10},
        ]
    }

    interpretation_service = BirthChartInterpretationService()
    full_interpretation = await interpretation_service.get_comprehensive_interpretation(sample_prokerala_data)

    print("--- COMPREHENSIVE BIRTH CHART INTERPRETATION ---")
    print("\n## Summary by Swamiji:")
    print(full_interpretation.get("summary"))

    print("\n## Detailed Planetary Positions:")
    for key, value in full_interpretation.get("planetary_positions", {}).items():
        print(f"\n### {key.replace('_', ' ').title()}")
        print(value)
        
    print("\n## Detailed House Positions:")
    for key, value in full_interpretation.get("house_positions", {}).items():
        print(f"\n### {key.replace('_', ' ').title()}")
        print(value)


if __name__ == "__main__":
    # This requires the main application's event loop and RAG initialization.
    # To run this standalone, you'd need to mock `get_rag_enhanced_guidance`
    # or set up a minimal app context.
    print("This script is intended to be used within the JyotiFlow application context.")
    # For a demonstration, you could potentially run a mocked version.
    # asyncio.run(main())
