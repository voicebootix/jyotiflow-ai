"""
🌟 PROKERALA VALIDATOR - Validates Prokerala API integration
Ensures birth chart data is complete and accurate.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

import logging
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class ProkeralaValidator:
    """
    Validates Prokerala API responses for completeness and accuracy
    """
    
    def __init__(self):
        self.required_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        self.required_fields = ["planets", "nakshatra", "rasi", "navamsa"]
        
    async def validate(self, input_data: Dict, output_data: Dict, session_context: Dict) -> Dict:
        """Validate Prokerala API integration"""
        validation_result = {
            "passed": True,
            "validation_type": "prokerala_birth_chart",
            "errors": [],
            "warnings": [],
            "auto_fixable": False,
            "expected": {},
            "actual": output_data
        }
        
        try:
            # Check if API call was successful
            if not output_data or output_data.get("error"):
                validation_result["passed"] = False
                validation_result["errors"].append(f"API call failed: {output_data.get('error', 'Unknown error')}")
                validation_result["severity"] = "critical"
                validation_result["user_impact"] = "Cannot provide accurate astrological guidance"
                return validation_result
            
            # Validate birth details input
            birth_validation = self._validate_birth_details(input_data)
            if not birth_validation["valid"]:
                validation_result["warnings"].extend(birth_validation["issues"])
            
            # Validate response structure
            structure_validation = self._validate_response_structure(output_data)
            if not structure_validation["valid"]:
                validation_result["passed"] = False
                validation_result["errors"].extend(structure_validation["errors"])
            
            # Validate planetary data
            if "planets" in output_data:
                planets_validation = self._validate_planetary_data(output_data["planets"])
                if not planets_validation["valid"]:
                    validation_result["warnings"].extend(planets_validation["warnings"])
                    if planets_validation.get("critical"):
                        validation_result["passed"] = False
                        validation_result["errors"].extend(planets_validation.get("errors", []))
            
            # Validate nakshatra data
            if "nakshatra" in output_data:
                nakshatra_validation = self._validate_nakshatra(output_data["nakshatra"])
                if not nakshatra_validation["valid"]:
                    validation_result["warnings"].append(nakshatra_validation["warning"])
            
            # Check data completeness
            completeness = self._check_data_completeness(output_data)
            validation_result["completeness_score"] = completeness["score"]
            
            if completeness["score"] < 0.7:
                validation_result["warnings"].append(f"Birth chart data only {completeness['score']*100:.0f}% complete")
                if completeness["score"] < 0.5:
                    validation_result["passed"] = False
                    validation_result["severity"] = "error"
            
            # Set expected values for comparison
            validation_result["expected"] = {
                "required_fields": self.required_fields,
                "required_planets": self.required_planets,
                "minimum_completeness": 0.7
            }
            
            # Determine if issues are auto-fixable
            if not validation_result["passed"] and "rate limit" in str(validation_result.get("errors", [])).lower():
                validation_result["auto_fixable"] = True
                validation_result["auto_fix_type"] = "retry_with_backoff"
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Prokerala validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def auto_fix(self, validation_result: Dict, session_context: Dict) -> Dict:
        """Attempt to auto-fix Prokerala API issues"""
        fix_result = {
            "fixed": False,
            "fix_type": None,
            "retry_needed": False
        }
        
        try:
            if validation_result.get("auto_fix_type") == "retry_with_backoff":
                # Suggest retry with exponential backoff
                fix_result["fixed"] = True
                fix_result["fix_type"] = "retry_with_backoff"
                fix_result["retry_needed"] = True
                fix_result["retry_delay_ms"] = 2000  # 2 second delay
                fix_result["message"] = "Rate limited - will retry with backoff"
            
            elif "incomplete data" in str(validation_result.get("errors", [])).lower():
                # Try to enhance the request
                fix_result["fix_type"] = "enhance_request"
                fix_result["enhanced_params"] = {
                    "detailed": True,
                    "system": "vedic",
                    "coordinates": self._extract_coordinates(session_context.get("birth_details", {}))
                }
                fix_result["fixed"] = True
                fix_result["retry_needed"] = True
            
            return fix_result
            
        except Exception as e:
            logger.error(f"Prokerala auto-fix error: {e}")
            return fix_result
    
    def _validate_birth_details(self, birth_details: Dict) -> Dict:
        """Validate input birth details"""
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check required fields
        required = ["date", "time", "location"]
        for field in required:
            if field not in birth_details or not birth_details[field]:
                validation["valid"] = False
                validation["issues"].append(f"Missing birth {field}")
        
        # Validate date format
        if "date" in birth_details:
            try:
                # Try to parse date
                if isinstance(birth_details["date"], str):
                    datetime.strptime(birth_details["date"], "%Y-%m-%d")
            except ValueError:
                validation["issues"].append("Invalid date format (expected YYYY-MM-DD)")
        
        # Validate time format
        if "time" in birth_details:
            try:
                if isinstance(birth_details["time"], str) and ":" in birth_details["time"]:
                    hours, minutes = birth_details["time"].split(":")[:2]
                    if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                        validation["issues"].append("Invalid time format")
            except:
                validation["issues"].append("Invalid time format (expected HH:MM)")
        
        return validation
    
    def _validate_response_structure(self, response: Dict) -> Dict:
        """Validate Prokerala response structure"""
        validation = {
            "valid": True,
            "errors": []
        }
        
        # Check for essential fields
        essential_fields = ["planets", "nakshatra"]
        for field in essential_fields:
            if field not in response:
                validation["valid"] = False
                validation["errors"].append(f"Missing essential field: {field}")
        
        return validation
    
    def _validate_planetary_data(self, planets: List[Dict]) -> Dict:
        """Validate planetary positions data"""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "critical": False
        }
        
        if not planets:
            validation["valid"] = False
            validation["critical"] = True
            validation["errors"].append("No planetary data provided")
            return validation
        
        # Check if all major planets are present
        planet_names = [p.get("name", "").lower() for p in planets if isinstance(p, dict)]
        missing_planets = [p for p in self.required_planets if p not in planet_names]
        
        if missing_planets:
            validation["warnings"].append(f"Missing planets: {', '.join(missing_planets)}")
            if len(missing_planets) > 3:  # Critical if too many missing
                validation["critical"] = True
                validation["errors"].append(f"Too many missing planets ({len(missing_planets)})")
        
        # Validate planetary position data
        for planet in planets:
            if isinstance(planet, dict):
                # Check required planet fields
                if "name" not in planet:
                    validation["warnings"].append("Planet missing name field")
                if "degree" not in planet and "longitude" not in planet:
                    validation["warnings"].append(f"Planet {planet.get('name', 'unknown')} missing position data")
                
                # Validate degree range
                degree = planet.get("degree") or planet.get("longitude")
                if degree is not None:
                    try:
                        deg_value = float(degree)
                        if not (0 <= deg_value <= 360):
                            validation["warnings"].append(f"Invalid degree for {planet.get('name', 'unknown')}: {deg_value}")
                    except:
                        pass
        
        return validation
    
    def _validate_nakshatra(self, nakshatra: Any) -> Dict:
        """Validate nakshatra data"""
        validation = {
            "valid": True,
            "warning": None
        }
        
        if not nakshatra:
            validation["valid"] = False
            validation["warning"] = "No nakshatra data"
            return validation
        
        # List of valid nakshatras
        valid_nakshatras = [
            "ashwini", "bharani", "krittika", "rohini", "mrigashira", "ardra",
            "punarvasu", "pushya", "ashlesha", "magha", "purva phalguni", "uttara phalguni",
            "hasta", "chitra", "swati", "vishakha", "anuradha", "jyeshtha",
            "mula", "purva ashadha", "uttara ashadha", "shravana", "dhanishta",
            "shatabhisha", "purva bhadrapada", "uttara bhadrapada", "revati"
        ]
        
        if isinstance(nakshatra, str):
            if nakshatra.lower() not in valid_nakshatras:
                validation["warning"] = f"Unrecognized nakshatra: {nakshatra}"
        elif isinstance(nakshatra, dict):
            nakshatra_name = nakshatra.get("name", "").lower()
            if nakshatra_name and nakshatra_name not in valid_nakshatras:
                validation["warning"] = f"Unrecognized nakshatra: {nakshatra_name}"
        
        return validation
    
    def _check_data_completeness(self, response: Dict) -> Dict:
        """Check overall data completeness"""
        total_checks = 0
        passed_checks = 0
        
        # Check required fields
        for field in self.required_fields:
            total_checks += 1
            if field in response and response[field]:
                passed_checks += 1
        
        # Check planetary completeness
        if "planets" in response and isinstance(response["planets"], list):
            planet_names = [p.get("name", "").lower() for p in response["planets"] if isinstance(p, dict)]
            for planet in self.required_planets:
                total_checks += 1
                if planet in planet_names:
                    passed_checks += 1
        
        # Check additional data
        additional_fields = ["houses", "aspects", "dashas"]
        for field in additional_fields:
            total_checks += 1
            if field in response and response[field]:
                passed_checks += 1
        
        completeness_score = passed_checks / total_checks if total_checks > 0 else 0
        
        return {
            "score": completeness_score,
            "passed_checks": passed_checks,
            "total_checks": total_checks
        }
    
    def _extract_coordinates(self, birth_details: Dict) -> Optional[Dict]:
        """Extract coordinates from location"""
        # This would be enhanced with actual geocoding
        location = birth_details.get("location", "").lower()
        
        # Common Indian cities coordinates
        city_coords = {
            "chennai": {"latitude": 13.0827, "longitude": 80.2707},
            "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
            "delhi": {"latitude": 28.7041, "longitude": 77.1025},
            "bangalore": {"latitude": 12.9716, "longitude": 77.5946},
            "kolkata": {"latitude": 22.5726, "longitude": 88.3639}
        }
        
        for city, coords in city_coords.items():
            if city in location:
                return coords
        
        return None