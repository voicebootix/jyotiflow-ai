"""
🚀 SOCIAL MEDIA SCHEMAS

Complete schema definitions for social media marketing operations.
Supports all platforms: Facebook, Instagram, YouTube, Twitter, TikTok, LinkedIn.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class PlatformStatus(BaseModel):
    """Status of social media platform connection"""
    connected: bool = False
    username: Optional[str] = None
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None


class PlatformConfig(BaseModel):
    """Social media platform configuration"""
    facebook: PlatformStatus = PlatformStatus()
    instagram: PlatformStatus = PlatformStatus()
    twitter: PlatformStatus = PlatformStatus()
    youtube: PlatformStatus = PlatformStatus()
    linkedin: PlatformStatus = PlatformStatus()
    tiktok: PlatformStatus = PlatformStatus()


class TestConnectionRequest(BaseModel):
    """Request to test platform connection"""
    platform: str = Field(..., pattern=r'^(facebook|instagram|twitter|youtube|linkedin|tiktok)$')
    credentials: Optional[Dict[str, str]] = None


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
    """Social media campaign with strong date and status validation"""
    id: int
    name: str
    platform: str
    status: CampaignStatus
    start_date: date
    end_date: date
    budget: Optional[float] = None
    target_audience: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        """Ensure end_date is after start_date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('status')
    def validate_status_with_dates(cls, v, values):
        """Validate status consistency with dates"""
        if 'start_date' in values and 'end_date' in values:
            today = date.today()
            start_date = values['start_date']
            end_date = values['end_date']
            
            # If campaign hasn't started yet, status should be draft
            if start_date > today and v == CampaignStatus.COMPLETED:
                raise ValueError('Cannot mark future campaign as completed')
            
            # If campaign has ended, status should be completed or paused
            if end_date < today and v == CampaignStatus.ACTIVE:
                raise ValueError('Cannot mark past campaign as active')
                
        return v


class ContentStatus(str, Enum):
    """Content status enum for strict validation"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"


class ContentCalendarItem(BaseModel):
    """Content calendar item with proper datetime handling"""
    id: int
    date: date  # Changed from str to date for type safety
    platform: str
    content: str
    status: ContentStatus  # Changed from pattern to Enum
    content_type: Optional[str] = None
    media_url: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None  # Changed from str to datetime
    
    @validator('scheduled_time')
    def validate_scheduled_time_with_date(cls, v, values):
        """Ensure scheduled_time matches the date if provided"""
        if v and 'date' in values:
            if v.date() != values['date']:
                raise ValueError('scheduled_time date must match the date field')
        return v


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