from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime

# சந்தா திட்டம் உருவாக்கம் - Subscription Plan Creation Schema
class SubscriptionPlanCreate(BaseModel):
    name: str  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    monthly_price: float  # மாதாந்திர விலை
    credits_per_month: int  # மாதத்திற்கான கிரெடிட்கள்
    features: Optional[Any]  # அம்சங்கள்
    is_active: Optional[bool] = True  # செயலில் உள்ளதா

# சந்தா திட்டம் புதுப்பிப்பு - Subscription Plan Update Schema
class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str]  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    monthly_price: Optional[float]  # மாதாந்திர விலை
    credits_per_month: Optional[int]  # மாதத்திற்கான கிரெடிட்கள்
    features: Optional[Any]  # அம்சங்கள்
    is_active: Optional[bool]  # செயலில் உள்ளதா

# சந்தா திட்டம் வெளியீடு - Subscription Plan Output Schema
class SubscriptionPlanOut(BaseModel):
    id: uuid.UUID  # தனித்துவ அடையாளம்
    name: str  # திட்டத்தின் பெயர்
    description: Optional[str]  # விளக்கம்
    monthly_price: float  # மாதாந்திர விலை
    credits_per_month: int  # மாதத்திற்கான கிரெடிட்கள்
    features: Optional[Any]  # அம்சங்கள்
    stripe_product_id: Optional[str]  # Stripe தயாரிப்பு ID
    stripe_price_id: Optional[str]  # Stripe விலை ID
    is_active: bool  # செயலில் உள்ளதா
    created_at: Optional[datetime]  # உருவாக்கப்பட்ட நேரம்
    updated_at: Optional[datetime]  # புதுப்பிக்கப்பட்ட நேரம் 