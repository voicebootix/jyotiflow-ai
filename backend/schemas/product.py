from pydantic import BaseModel
from typing import Optional
import uuid

# தயாரிப்பு உருவாக்கம் - Product Creation Schema
class ProductCreate(BaseModel):
    sku_code: str  # தயாரிப்பு குறியீடு
    name: str  # தயாரிப்பு பெயர்
    description: Optional[str]  # விளக்கம்
    price: float  # விலை
    credits_allocated: int  # ஒதுக்கப்பட்ட கிரெடிட்கள்
    is_active: Optional[bool] = True  # செயலில் உள்ளதா

# தயாரிப்பு புதுப்பிப்பு - Product Update Schema
class ProductUpdate(BaseModel):
    name: Optional[str]  # தயாரிப்பு பெயர்
    description: Optional[str]  # விளக்கம்
    price: Optional[float]  # விலை
    credits_allocated: Optional[int]  # ஒதுக்கப்பட்ட கிரெடிட்கள்
    is_active: Optional[bool]  # செயலில் உள்ளதா

# தயாரிப்பு வெளியீடு - Product Output Schema
class ProductOut(BaseModel):
    id: uuid.UUID  # தனித்துவ அடையாளம்
    sku_code: str  # தயாரிப்பு குறியீடு
    name: str  # தயாரிப்பு பெயர்
    description: Optional[str]  # விளக்கம்
    price: float  # விலை
    credits_allocated: int  # ஒதுக்கப்பட்ட கிரெடிட்கள்
    stripe_product_id: Optional[str]  # Stripe தயாரிப்பு ID
    stripe_price_id: Optional[str]  # Stripe விலை ID
    is_active: bool  # செயலில் உள்ளதா
    created_at: Optional[str]  # உருவாக்கப்பட்ட நேரம்
    updated_at: Optional[str]  # புதுப்பிக்கப்பட்ட நேரம் 