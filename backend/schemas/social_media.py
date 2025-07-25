"""
🚀 SOCIAL MEDIA SCHEMAS

Complete schema definitions for social media marketing operations.
Supports all platforms: Facebook, Instagram, YouTube, Twitter, TikTok, LinkedIn.
"""

# Pydantic v2 compatible imports
try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    from pydantic import ValidationInfo
    PYDANTIC_V2 = True
except ImportError:
    # Fallback to Pydantic v1
    from pydantic import BaseModel, Field, validator, root_validator
    PYDANTIC_V2 = False

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class PlatformStatus(BaseModel):
    """Status of social media platform connection"""
    connected: bool = False
    username: Optional[str] = None
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None

    # YouTube
    api_key: Optional[str] = None
    channel_id: Optional[str] = None

    # Facebook
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    page_access_token: Optional[str] = None

    # Instagram
    access_token: Optional[str] = None

    # TikTok
    client_key: Optional[str] = None
    client_secret: Optional[str] = None

    class Config:
        extra = 'ignore'


class PlatformConfig(BaseModel):
    """Social media platform configuration"""
    facebook: PlatformStatus = Field(default_factory=PlatformStatus)
    instagram: PlatformStatus = Field(default_factory=PlatformStatus)
    twitter: PlatformStatus = Field(default_factory=PlatformStatus)
    youtube: PlatformStatus = Field(default_factory=PlatformStatus)
    linkedin: PlatformStatus = Field(default_factory=PlatformStatus)
    tiktok: PlatformStatus = Field(default_factory=PlatformStatus)

    class Config:
        extra = 'ignore'


class PlatformConfigUpdate(BaseModel):
    """Model for updating a single platform's configuration."""
    facebook: Optional[PlatformStatus] = None
    instagram: Optional[PlatformStatus] = None
    twitter: Optional[PlatformStatus] = None
    youtube: Optional[PlatformStatus] = None
    linkedin: Optional[PlatformStatus] = None
    tiktok: Optional[PlatformStatus] = None


class TestConnectionRequest(BaseModel):
    """Request to test platform connection"""
    platform: str = Field(..., pattern=r'^(facebook|instagram|twitter|youtube|linkedin|tiktok)$')
    # REFRESH.MD: Changed from Dict[str, str] to Dict[str, Any] to support mixed types from frontend.
    config: Optional[Dict[str, Any]] = None


class MarketingOverview(BaseModel):
    """Marketing overview dashboard data"""
    total_campaigns: int = 0
    active_campaigns: int = 0
    total_posts: int = 0
    total_engagement: int = 0
    reach: int = 0
    follower_growth: Optional[int] = 0
    engagement_rate: Optional[float] = 0.0
    top_performing_platform: Optional[str] = None


class CampaignStatus(str, Enum):
    """Campaign status enum for strict validation"""
    ACTIVE = "active"
    PAUSED = "paused" 
    COMPLETED = "completed"
    DRAFT = "draft"


class Campaign(BaseModel):
    """Social media campaign with strong date and status validation
    
    FIXED: Field order and validator issues resolved for Pydantic v1/v2 compatibility.
    Uses @model_validator for Pydantic v2 or @root_validator for v1.
    """
    id: int
    name: str
    platform: str
    # REORDERED: Dates first, then status for proper validation
    start_date: date
    end_date: date
    status: CampaignStatus
    budget: Optional[float] = None
    target_audience: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    if PYDANTIC_V2:
        @field_validator('end_date')
        @classmethod
        def end_date_must_be_after_start_date(cls, v: date, info: ValidationInfo) -> date:
            """Ensure end_date is after start_date"""
            if 'start_date' in info.data and v <= info.data['start_date']:
                raise ValueError('end_date must be after start_date')
            return v
        
        @model_validator(mode='after')
        def validate_status_with_dates(self):
            """Validate status consistency with dates using model_validator (Pydantic v2)"""
            if self.start_date and self.end_date and self.status:
                today = date.today()
                
                # If campaign hasn't started yet, cannot be completed
                if self.start_date > today and self.status == CampaignStatus.COMPLETED:
                    raise ValueError('Cannot mark future campaign as completed')
                
                # If campaign has ended, cannot be active
                if self.end_date < today and self.status == CampaignStatus.ACTIVE:
                    raise ValueError('Cannot mark past campaign as active')
                    
            return self
    else:
        @validator('end_date')
        def end_date_must_be_after_start_date(cls, v, values):
            """Ensure end_date is after start_date"""
            if 'start_date' in values and v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
            return v
        
        @root_validator(skip_on_failure=True)
        def validate_status_with_dates(cls, values):
            """Validate status consistency with dates using root_validator (Pydantic v1)"""
            start_date = values.get('start_date')
            end_date = values.get('end_date')
            status = values.get('status')
            
            if start_date and end_date and status:
                today = date.today()
                
                # If campaign hasn't started yet, cannot be completed
                if start_date > today and status == CampaignStatus.COMPLETED:
                    raise ValueError('Cannot mark future campaign as completed')
                
                # If campaign has ended, cannot be active
                if end_date < today and status == CampaignStatus.ACTIVE:
                    raise ValueError('Cannot mark past campaign as active')
                    
            return values


class ContentStatus(str, Enum):
    """Content status enum for strict validation"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"


class ContentCalendarItem(BaseModel):
    """Content calendar item with proper datetime handling
    
    FIXED: Using proper validator approach for Pydantic v1/v2 compatibility.
    """
    id: int
    date: date  # Changed from str to date for type safety
    platform: str
    content: str
    status: ContentStatus  # Changed from pattern to Enum
    content_type: Optional[str] = None
    media_url: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None  # Changed from str to datetime
    
    if PYDANTIC_V2:
        @model_validator(mode='after')
        def validate_scheduled_time_with_date(self):
            """Ensure scheduled_time matches the date if provided (Pydantic v2)"""
            if self.scheduled_time and self.date:
                if self.scheduled_time.date() != self.date:
                    raise ValueError('scheduled_time date must match the date field')
            return self
    else:
        @root_validator(skip_on_failure=True)
        def validate_scheduled_time_with_date(cls, values):
            """Ensure scheduled_time matches the date if provided (Pydantic v1)"""
            scheduled_time = values.get('scheduled_time')
            date_value = values.get('date')
            
            if scheduled_time and date_value:
                if scheduled_time.date() != date_value:
                    raise ValueError('scheduled_time date must match the date field')
            
            return values


class MarketingAssetCreate(BaseModel):
    """Create new marketing asset"""
    title: str
    description: Optional[str] = None
    content_type: str = Field(..., pattern=r'^(image|video|text|carousel)$')
    platform: str = Field(..., pattern=r'^(facebook|instagram|twitter|youtube|linkedin|tiktok)$')
    file_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MarketingAsset(MarketingAssetCreate):
    """Marketing asset response"""
    id: int
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    performance_score: Optional[float] = None


class PostExecutionRequest(BaseModel):
    """Request to execute social media posts"""
    campaign_id: Optional[int] = None
    platforms: List[str] = Field(..., min_items=1)
    content: str
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None
    target_audience: Optional[Dict[str, Any]] = None


class PostExecutionResult(BaseModel):
    """Result of post execution"""
    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class GenerateAvatarPreviewRequest(BaseModel):
    """Request to generate avatar preview"""
    text: str = Field(..., min_length=10, max_length=500)
    voice_id: str = "swamiji_voice_v1"
    style: str = Field(default="traditional", pattern=r'^(traditional|modern|default)$')
    background: Optional[str] = None
    duration: Optional[int] = Field(default=30, ge=10, le=120)


class GenerateAllAvatarPreviewsRequest(BaseModel):
    """Request to generate all avatar previews for different styles"""
    text: str = Field(..., min_length=10, max_length=500)
    voice_id: str = "swamiji_voice_v1"
    styles: List[str] = Field(default=["traditional", "modern", "default"])
    background: Optional[str] = None


class ContentGenerationRequest(BaseModel):
    """Request for AI content generation"""
    content_type: str = Field(..., pattern=r'^(daily_wisdom|spiritual_quote|satsang_promo|festival_greeting|user_testimonial)$')
    platform: str = Field(..., pattern=r'^(facebook|instagram|twitter|youtube|linkedin|tiktok|all)$')
    target_audience: Optional[str] = None
    tone: Optional[str] = Field(default="spiritual", pattern=r'^(spiritual|inspirational|educational|celebratory)$')
    language: Optional[str] = Field(default="en", pattern=r'^(en|ta|hi)$')
    include_hashtags: bool = True
    include_media_suggestions: bool = True


class ContentGenerationResponse(BaseModel):
    """Response from AI content generation"""
    success: bool
    content: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    estimated_engagement: Optional[float] = None
    optimal_posting_time: Optional[str] = None
    error_message: Optional[str] = None


class AnalyticsRequest(BaseModel):
    """Request for analytics data"""
    platform: Optional[str] = None
    date_range: str = Field(default="7d", pattern=r'^(1d|7d|30d|90d|1y)$')
    metrics: List[str] = Field(default=["engagement", "reach", "followers"])
    campaign_id: Optional[int] = None


class AnalyticsResponse(BaseModel):
    """Analytics response data"""
    success: bool
    data: Dict[str, Any]
    summary: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None 