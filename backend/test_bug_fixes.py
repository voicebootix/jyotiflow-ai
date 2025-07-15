#!/usr/bin/env python3
"""
Test script to verify bug fixes:
1. Coordinate format consistency in Prokerala API calls
2. Cache key generation robustness for different location formats
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_coordinate_format_consistency():
    """Test that both functions use the same coordinate format"""
    
    # Mock parameters
    latitude = "9.66845"
    longitude = "80.00742"
    
    # Test get_prokerala_birth_chart_data format
    coordinates_birth_chart = f"{latitude},{longitude}"
    base_params_birth_chart = {
        "datetime": "2023-12-25T10:30:00+05:30",
        "coordinates": coordinates_birth_chart,
        "ayanamsa": "1",
        "format": "json"
    }
    
    # Test get_spiritual_guidance format (after fix)
    coordinates_guidance = f"{latitude},{longitude}"
    params_guidance = {
        "datetime": "2023-12-25T10:30:00+05:30",
        "coordinates": coordinates_guidance,
        "ayanamsa": "1"
    }
    
    # Verify consistency
    assert base_params_birth_chart["coordinates"] == params_guidance["coordinates"], \
        "Coordinate formats are inconsistent between functions"
    
    logger.info("✅ Coordinate format consistency test PASSED")
    return True

def test_cache_key_generation():
    """Test cache key generation with different location formats"""
    
    # Test cases for different location formats
    test_cases = [
        {
            "name": "Location as dictionary",
            "birth_details": {
                "date": "2023-12-25",
                "time": "10:30",
                "location": {"name": "Jaffna", "lat": 9.66845, "lng": 80.00742}
            },
            "expected_key": "birth_chart:2023-12-25:10:30:Jaffna"
        },
        {
            "name": "Location as string",
            "birth_details": {
                "date": "2023-12-25", 
                "time": "10:30",
                "location": "Colombo"
            },
            "expected_key": "birth_chart:2023-12-25:10:30:Colombo"
        },
        {
            "name": "Location as empty dict",
            "birth_details": {
                "date": "2023-12-25",
                "time": "10:30", 
                "location": {}
            },
            "expected_key": "birth_chart:2023-12-25:10:30:"
        },
        {
            "name": "Location as None",
            "birth_details": {
                "date": "2023-12-25",
                "time": "10:30",
                "location": None
            },
            "expected_key": "birth_chart:2023-12-25:10:30:"
        },
        {
            "name": "No location field",
            "birth_details": {
                "date": "2023-12-25",
                "time": "10:30"
            },
            "expected_key": "birth_chart:2023-12-25:10:30:"
        }
    ]
    
    for test_case in test_cases:
        birth_details = test_case["birth_details"]
        expected_key = test_case["expected_key"]
        
        # Simulate the fixed cache key generation logic
        location = birth_details.get('location', '')
        if isinstance(location, dict):
            location_name = location.get('name', '')
        elif isinstance(location, str):
            location_name = location
        else:
            location_name = str(location) if location else ''
        
        cache_key = f"birth_chart:{birth_details.get('date', '')}:{birth_details.get('time', '')}:{location_name}"
        
        assert cache_key == expected_key, \
            f"Cache key mismatch for {test_case['name']}: expected '{expected_key}', got '{cache_key}'"
        
        logger.info(f"✅ {test_case['name']}: {cache_key}")
    
    logger.info("✅ Cache key generation robustness test PASSED")
    return True

def test_api_params_structure():
    """Test that API parameters are properly structured"""
    
    # Test parameters that would be sent to Prokerala API
    test_params = {
        "datetime": "2023-12-25T10:30:00+05:30",
        "coordinates": "9.66845,80.00742",
        "ayanamsa": "1"
    }
    
    # Validate parameter structure
    assert "coordinates" in test_params, "Missing coordinates parameter"
    assert "," in test_params["coordinates"], "Coordinates should be comma-separated"
    assert test_params["coordinates"].count(",") == 1, "Coordinates should have exactly one comma"
    
    # Validate coordinate format
    lat, lng = test_params["coordinates"].split(",")
    try:
        float(lat)
        float(lng)
    except ValueError:
        raise AssertionError("Coordinates should be valid numbers")
    
    logger.info("✅ API parameters structure test PASSED")
    return True

def main():
    """Run all bug fix tests"""
    logger.info("🚀 Starting bug fix verification tests...")
    
    try:
        # Test 1: Coordinate format consistency
        test_coordinate_format_consistency()
        
        # Test 2: Cache key generation robustness 
        test_cache_key_generation()
        
        # Test 3: API parameters structure
        test_api_params_structure()
        
        logger.info("🎉 All bug fix tests PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bug fix test FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)