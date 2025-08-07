from pydantic import BaseModel, validator
from typing import Optional, Any
from datetime import datetime
from .validators import validate_datetime_fields, DATETIME_JSON_ENCODERS

# சந்தா திட்டம் உருவாக்கம் - Subscription Plan Creation Schema
class SubscriptionPlanCreate(BaseModel):
    name: str  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    price_usd: float  # FIXED: Database column is 'price_usd'
    billing_period: Optional[str] = None  # FIXED: Database has 'billing_period'
    credits_per_period: int  # FIXED: Database column is 'credits_per_period', not 'credits_per_month'
    features: Optional[Any]  # அம்சங்கள்
    plan_id: Optional[str] = None  # FIXED: Database has 'plan_id'
    stripe_product_id: Optional[str] = None  # FIXED: Database has 'stripe_product_id'
    stripe_price_id: Optional[str] = None  # FIXED: Database has 'stripe_price_id'
    is_active: Optional[bool] = None  # செயலில் உள்ளதா

# சந்தா திட்டம் புதுப்பிப்பு - Subscription Plan Update Schema
class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str]  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    price_usd: Optional[float]  # FIXED: Database column is 'price_usd'
    billing_period: Optional[str]  # FIXED: Database has 'billing_period'
    credits_per_period: Optional[int]  # FIXED: Database column is 'credits_per_period'
    features: Optional[Any]  # அம்சங்கள்
    plan_id: Optional[str]  # FIXED: Database has 'plan_id'
    stripe_product_id: Optional[str]  # FIXED: Database has 'stripe_product_id'
    stripe_price_id: Optional[str]  # FIXED: Database has 'stripe_price_id'
    is_active: Optional[bool]  # செயலில் உள்ளதா

# சந்தா திட்டம் வெளியீடு - Subscription Plan Output Schema
# ROOT CAUSE FIX: Aligned with ACTUAL database structure from your evidence
class SubscriptionPlanOut(BaseModel):
    id: int  # FIXED: Database uses SERIAL (INTEGER), not UUID
    name: str  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    features: Optional[Any]  # அம்சங்கள்
    stripe_product_id: Optional[str]  # FIXED: Database has 'stripe_product_id'
    stripe_price_id: Optional[str]  # FIXED: Database has 'stripe_price_id'
    is_active: bool  # செயலில் உள்ளதா
    created_at: Optional[str] = None  # FIXED: Convert datetime to ISO-8601 string
    updated_at: Optional[str] = None  # FIXED: Convert datetime to ISO-8601 string
    plan_id: Optional[str] = None  # FIXED: Database has 'plan_id'
    price_usd: float  # FIXED: Database column is 'price_usd'
    billing_period: Optional[str] = None  # FIXED: Database has 'billing_period'
    credits_per_period: int  # FIXED: Database column is 'credits_per_period'
    
    # Backwards compatibility fields for existing frontend code
    monthly_price: Optional[float] = None  # Legacy field mapping to price_usd
    credits_per_month: Optional[int] = None  # Legacy field mapping to credits_per_period
    
    # FIXED: Use shared validator to avoid code duplication (DRY principle)
    @validator('created_at', 'updated_at', pre=True)
    def validate_datetime_fields(cls, v):
        """
        FIXED: Use shared validator from validators.py to avoid code duplication.
        Ensures datetime fields are properly serialized as ISO-8601 strings.
        """
        return validate_datetime_fields(cls, v)
    
    class Config:
        # FIXED: Use shared JSON encoders configuration
        json_encoders = DATETIME_JSON_ENCODERS 

        

