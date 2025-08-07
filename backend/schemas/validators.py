"""
Shared Pydantic validators for common schema validation patterns.

This module contains reusable validator functions to avoid code duplication
and follow the DRY principle across schema modules.
"""

from datetime import datetime
from typing import Any, Union


def validate_datetime_fields(cls: Any, v: Union[datetime, str, None]) -> Union[str, None]:
    """
    Shared validator to ensure datetime fields are properly serialized as ISO-8601 strings.
    
    Handles both datetime objects and existing string values with robust error handling.
    Ensures consistent timezone representation using '+00:00' instead of 'Z' for UTC.
    
    Args:
        cls: The Pydantic model class (required for validator decorator)
        v: The value to validate (datetime, string, or None)
        
    Returns:
        ISO-8601 formatted string with consistent '+00:00' timezone or None
        
    Raises:
        ValueError: If the datetime format is invalid
    """
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, str):
        # Validate that it's a proper ISO-8601 format
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            # FIXED: Return consistent timezone format by replacing 'Z' with '+00:00'
            return v.replace('Z', '+00:00')
        except ValueError:
            # If it's not a valid ISO string, try to parse and convert
            try:
                parsed = datetime.fromisoformat(v)
                return parsed.isoformat()
            except ValueError as e:
                # Preserve exception chain for better debugging
                raise ValueError(f"Invalid datetime format: {v}") from e
    raise ValueError(f"Expected datetime, string, or None, got {type(v).__name__}: {v}")


# Common JSON encoders configuration for consistent datetime serialization
DATETIME_JSON_ENCODERS = {
    datetime: lambda v: v.isoformat() if v else None
}
