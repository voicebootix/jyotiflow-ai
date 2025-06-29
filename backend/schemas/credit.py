from pydantic import BaseModel
from typing import Optional
import uuid

# கிரெடிட் தொகுப்பு உருவாக்கம் - Credit Package Creation Schema
class CreditPackageCreate(BaseModel):
    name: str  # தொகுப்பின் பெயர்
    credits_amount: int  # கிரெடிட் அளவு
    price: float  # விலை
    bonus_credits: Optional[int] = 0  # போனஸ் கிரெடிட்கள்
    is_active: Optional[bool] = True  # செயலில் உள்ளதா

# கிரெடிட் தொகுப்பு புதுப்பிப்பு - Credit Package Update Schema
class CreditPackageUpdate(BaseModel):
    name: Optional[str]  # தொகுப்பின் பெயர்
    credits_amount: Optional[int]  # கிரெடிட் அளவு
    price: Optional[float]  # விலை
    bonus_credits: Optional[int]  # போனஸ் கிரெடிட்கள்
    is_active: Optional[bool]  # செயலில் உள்ளதா

# கிரெடிட் தொகுப்பு வெளியீடு - Credit Package Output Schema
class CreditPackageOut(BaseModel):
    id: uuid.UUID  # தனித்துவ அடையாளம்
    name: str  # தொகுப்பின் பெயர்
    credits_amount: int  # கிரெடிட் அளவு
    price: float  # விலை
    bonus_credits: int  # போனஸ் கிரெடிட்கள்
    stripe_product_id: Optional[str]  # Stripe தயாரிப்பு ID
    stripe_price_id: Optional[str]  # Stripe விலை ID
    is_active: bool  # செயலில் உள்ளதா
    created_at: Optional[str]  # உருவாக்கப்பட்ட நேரம் 