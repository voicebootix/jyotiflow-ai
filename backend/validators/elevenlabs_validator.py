"""
🎙️ ELEVENLABS VALIDATOR - Validates ElevenLabs voice generation
Ensures voice synthesis completed successfully.
"""

import logging
from typing import Dict, Optional, Any

import logging
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class ElevenLabsValidator:
    """
    Validates ElevenLabs voice generation integration
    """
    
    async def validate(self, input_data: Dict, output_data: Dict, session_context: Dict) -> Dict:
        """Validate ElevenLabs voice generation"""
        validation_result = {
            "passed": True,
            "validation_type": "elevenlabs_voice_generation",
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
                validation_result["errors"].append(f"Voice generation failed: {output_data.get('error')}")
                validation_result["severity"] = "warning"  # Not critical - can fall back to text
                validation_result["user_impact"] = "No voice narration available"
                
                # Check if it's a quota issue
                if "quota" in str(output_data.get("error", "")).lower():
                    validation_result["auto_fixable"] = True
                    validation_result["auto_fix_type"] = "use_fallback_voice"
                
                return validation_result
            
            # Validate audio URL
            audio_url = output_data.get("audio_url", "") or output_data.get("voice_url", "")
            if not audio_url:
                validation_result["passed"] = False
                validation_result["errors"].append("No audio URL generated")
                validation_result["severity"] = "warning"
                return validation_result
            
            # Validate audio metadata if available
            if "duration" in output_data:
                duration = output_data.get("duration", 0)
                if duration <= 0:
                    validation_result["warnings"].append("Invalid audio duration")
                elif duration > 300:  # More than 5 minutes
                    validation_result["warnings"].append("Audio duration exceeds 5 minutes")
            
            # Check voice consistency
            if "voice_id" in output_data:
                expected_voice = session_context.get("expected_voice_id", "swami_voice")
                if output_data["voice_id"] != expected_voice:
                    validation_result["warnings"].append(f"Voice ID mismatch: expected {expected_voice}")
            
            validation_result["expected"] = {
                "audio_format": "mp3",
                "max_duration_seconds": 300,
                "voice_profile": "swami_jyotirananthan"
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"ElevenLabs validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def auto_fix(self, validation_result: Dict, session_context: Dict) -> Dict:
        """Attempt to auto-fix ElevenLabs issues"""
        fix_result = {
            "fixed": False,
            "fix_type": None,
            "retry_needed": False
        }
        
        try:
            if validation_result.get("auto_fix_type") == "use_fallback_voice":
                fix_result["fixed"] = True
                fix_result["fix_type"] = "fallback_to_text"
                fix_result["message"] = "Will use text-only response due to voice quota"
                fix_result["fallback_mode"] = "text_only"
            
            return fix_result
            
        except Exception as e:
            logger.error(f"ElevenLabs auto-fix error: {e}")
            return fix_result