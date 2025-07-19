"""
🎭 D-ID VALIDATOR - Validates D-ID avatar video generation
Ensures avatar video synthesis completed successfully.
"""

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class DIDValidator:
    """
    Validates D-ID avatar video generation integration
    """
    
    async def validate(self, input_data: Dict, output_data: Dict, session_context: Dict) -> Dict:
        """Validate D-ID avatar generation"""
        validation_result = {
            "passed": True,
            "validation_type": "did_avatar_generation",
            "errors": [],
            "warnings": [],
            "auto_fixable": False,
            "expected": {},
            "actual": output_data
        }
        
        try:
            # Check if API call was successful
            if output_data.get("error"):
                validation_result["passed"] = False
                validation_result["errors"].append(f"Avatar generation failed: {output_data.get('error')}")
                validation_result["severity"] = "warning"  # Not critical - can fall back to audio only
                validation_result["user_impact"] = "No avatar video available"
                
                # Check if it's a quota issue
                if "quota" in str(output_data.get("error", "")).lower() or "credit" in str(output_data.get("error", "")).lower():
                    validation_result["auto_fixable"] = True
                    validation_result["auto_fix_type"] = "use_fallback_avatar"
                
                return validation_result
            
            # Validate video URL
            video_url = output_data.get("video_url", "") or output_data.get("avatar_url", "")
            if not video_url:
                validation_result["passed"] = False
                validation_result["errors"].append("No video URL generated")
                validation_result["severity"] = "warning"
                return validation_result
            
            # Validate video metadata if available
            if "duration" in output_data:
                duration = output_data.get("duration", 0)
                if duration <= 0:
                    validation_result["warnings"].append("Invalid video duration")
                elif duration > 300:  # More than 5 minutes
                    validation_result["warnings"].append("Video duration exceeds 5 minutes")
            
            # Check lip sync quality if reported
            if "lip_sync_confidence" in output_data:
                confidence = output_data.get("lip_sync_confidence", 0)
                if confidence < 0.7:
                    validation_result["warnings"].append(f"Low lip sync confidence: {confidence}")
            
            # Check avatar consistency
            if "presenter_id" in output_data:
                expected_presenter = session_context.get("expected_presenter_id", "swami_avatar")
                if output_data["presenter_id"] != expected_presenter:
                    validation_result["warnings"].append(f"Presenter ID mismatch: expected {expected_presenter}")
            
            validation_result["expected"] = {
                "video_format": "mp4",
                "max_duration_seconds": 300,
                "avatar_profile": "swami_jyotirananthan",
                "background": "temple_setting"
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"D-ID validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def auto_fix(self, validation_result: Dict, session_context: Dict) -> Dict:
        """Attempt to auto-fix D-ID issues"""
        fix_result = {
            "fixed": False,
            "fix_type": None,
            "retry_needed": False
        }
        
        try:
            if validation_result.get("auto_fix_type") == "use_fallback_avatar":
                fix_result["fixed"] = True
                fix_result["fix_type"] = "fallback_to_audio"
                fix_result["message"] = "Will use audio-only response due to avatar quota"
                fix_result["fallback_mode"] = "audio_only"
                
                # Suggest using a static image with audio
                fix_result["static_image_url"] = "/assets/swami_default_avatar.jpg"
            
            return fix_result
            
        except Exception as e:
            logger.error(f"D-ID auto-fix error: {e}")
            return fix_result