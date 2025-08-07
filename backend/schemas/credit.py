from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator

# கிரெடிட் தொகுப்பு உருவாக்கம் - Credit Package Creation Schema
class CreditPackageCreate(BaseModel):
    name: str  # தொகுப்பின் பெயர்
    credits_amount: int  # கிரெடிட் அளவு
    price_usd: float  # விலை (matches database column name)
    bonus_credits: Optional[int] = 0  # போனஸ் கிரெடிட்கள்
    description: Optional[str] = None  # விளக்கம்
    enabled: Optional[bool] = True  # செயலில் உள்ளதா (matches database column name)

# கிரெடிட் தொகுப்பு புதுப்பிப்பு - Credit Package Update Schema
class CreditPackageUpdate(BaseModel):
    name: Optional[str] = None  # தொகுப்பின் பெயர்
    credits_amount: Optional[int] = None  # கிரெடிட் அளவு
    price_usd: Optional[float] = None  # விலை (matches database column name)
    bonus_credits: Optional[int] = None  # போனஸ் கிரெடிட்கள்
    description: Optional[str] = None  # விளக்கம்
    enabled: Optional[bool] = None  # செயலில் உள்ளதா (matches database column name)

# கிரெடிட் தொகுப்பு வெளியீடு - Credit Package Output Schema
# FIXED: Aligned with actual database structure (evidence from migrations/002_fix_missing_tables_and_columns.sql)
class CreditPackageOut(BaseModel):
    id: int  # தனித்துவ அடையாளம் - FIXED: Database uses SERIAL (INTEGER), not UUID
    name: str  # தொகுப்பின் பெயர்
    credits_amount: int  # கிரெடிட் அளவு
    price_usd: float  # விலை - FIXED: Database column is 'price_usd', not 'price'
    bonus_credits: int  # போனஸ் கிரெடிட்கள்
    description: Optional[str] = None  # விளக்கம்
    enabled: bool  # செயலில் உள்ளதா - FIXED: Database column is 'enabled', not 'is_active'
    stripe_product_id: Optional[str] = None  # Stripe தயாரிப்பு ID
    stripe_price_id: Optional[str] = None  # Stripe விலை ID
    created_at: Optional[str] = None  # உருவாக்கப்பட்ட நேரம் - FIXED: Convert datetime to string
    updated_at: Optional[str] = None  # புதுப்பிக்கப்பட்ட நேரம் - FIXED: Convert datetime to string
    
    # Backwards compatibility fields for existing frontend code
    price: Optional[float] = None  # Legacy field mapping to price_usd
    is_active: Optional[bool] = None  # Legacy field mapping to enabled 

    
    # ENHANCED: Pydantic validators for robust datetime handling
    @validator('created_at', 'updated_at', pre=True)
    def validate_datetime_fields(cls, v):
        """
        ENHANCED: Validator to ensure datetime fields are properly serialized as ISO-8601 strings.
        Handles both datetime objects and existing string values.
        """
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        if isinstance(v, str):
            # Validate that it's a proper ISO-8601 format
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
                return v
            except ValueError:
                # If it's not a valid ISO string, try to parse and convert
                try:
                    parsed = datetime.fromisoformat(v)
                    return parsed.isoformat()
                except ValueError as e:
                    raise ValueError(f"Invalid datetime format: {v}") from e
        return v
    
    class Config:
        # ENHANCED: Configure JSON encoders for consistent datetime serialization
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }