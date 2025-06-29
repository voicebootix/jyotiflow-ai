from pydantic import BaseModel
from typing import Optional
import uuid

# சமூக ஊடக உள்ளடக்கம் உருவாக்கம் - Social Content Creation Schema
class SocialContentCreate(BaseModel):
    platform: str  # தளம் (Facebook, Instagram, etc.)
    content_type: str  # உள்ளடக்க வகை
    content_text: Optional[str]  # உள்ளடக்க உரை
    media_url: Optional[str]  # ஊடக URL
    scheduled_at: Optional[str]  # திட்டமிடப்பட்ட நேரம்
    status: Optional[str] = 'draft'  # நிலை

# சமூக ஊடக உள்ளடக்கம் வெளியீடு - Social Content Output Schema
class SocialContentOut(BaseModel):
    id: uuid.UUID  # தனித்துவ அடையாளம்
    platform: str  # தளம்
    content_type: str  # உள்ளடக்க வகை
    content_text: Optional[str]  # உள்ளடக்க உரை
    media_url: Optional[str]  # ஊடக URL
    scheduled_at: Optional[str]  # திட்டமிடப்பட்ட நேரம்
    published_at: Optional[str]  # வெளியிடப்பட்ட நேரம்
    engagement_metrics: Optional[dict]  # ஈடுபாட்டு அளவீடுகள்
    status: str  # நிலை
    created_at: Optional[str]  # உருவாக்கப்பட்ட நேரம்

# சத்சங்க் நிகழ்வு உருவாக்கம் - Satsang Event Creation Schema
class SatsangEventCreate(BaseModel):
    title: str  # நிகழ்வின் தலைப்பு
    description: Optional[str]  # விளக்கம்
    event_date: str  # நிகழ்வு தேதி
    duration_minutes: Optional[int] = 90  # கால அளவு (நிமிடங்கள்)
    max_attendees: Optional[int]  # அதிகபட்ச பங்கேற்பாளர்கள்
    zoom_link: Optional[str]  # Zoom இணைப்பு
    status: Optional[str] = 'scheduled'  # நிலை

# சத்சங்க் நிகழ்வு வெளியீடு - Satsang Event Output Schema
class SatsangEventOut(BaseModel):
    id: uuid.UUID  # தனித்துவ அடையாளம்
    title: str  # நிகழ்வின் தலைப்பு
    description: Optional[str]  # விளக்கம்
    event_date: str  # நிகழ்வு தேதி
    duration_minutes: int  # கால அளவு (நிமிடங்கள்)
    max_attendees: Optional[int]  # அதிகபட்ச பங்கேற்பாளர்கள்
    current_attendees: Optional[int]  # தற்போதைய பங்கேற்பாளர்கள்
    zoom_link: Optional[str]  # Zoom இணைப்பு
    recording_url: Optional[str]  # பதிவு URL
    status: str  # நிலை
    created_at: Optional[str]  # உருவாக்கப்பட்ட நேரம் 