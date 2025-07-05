from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum

class FollowUpType(Enum):
    """Follow-up types"""
    SESSION_FOLLOWUP = "session_followup"
    REMINDER = "reminder"
    CHECK_IN = "check_in"
    OFFER = "offer"
    SUPPORT = "support"
    CUSTOM = "custom"

class FollowUpStatus(Enum):
    """Follow-up status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FollowUpChannel(Enum):
    """Follow-up channels"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"

class FollowUpTemplate(BaseModel):
    """Follow-up template model"""
    id: Optional[str] = None
    name: str
    tamil_name: Optional[str] = None
    description: str
    template_type: FollowUpType
    channel: FollowUpChannel
    subject: str
    content: str
    tamil_content: Optional[str] = None
    variables: List[str] = Field(default_factory=list)
    credits_cost: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FollowUpSchedule(BaseModel):
    """Follow-up schedule model"""
    id: Optional[str] = None
    user_email: EmailStr
    session_id: Optional[str] = None
    template_id: str
    channel: FollowUpChannel
    scheduled_at: datetime
    status: FollowUpStatus = FollowUpStatus.PENDING
    credits_charged: int = 0
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FollowUpRequest(BaseModel):
    """Follow-up request model"""
    user_email: EmailStr
    session_id: Optional[str] = None
    template_id: str
    channel: FollowUpChannel
    scheduled_at: Optional[datetime] = None
    custom_variables: Optional[Dict[str, Any]] = None
    credits_to_charge: Optional[int] = None

class FollowUpResponse(BaseModel):
    """Follow-up response model"""
    success: bool
    message: str
    followup_id: Optional[str] = None
    credits_charged: int = 0
    scheduled_at: Optional[datetime] = None

class FollowUpAnalytics(BaseModel):
    """Follow-up analytics model"""
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    total_credits_charged: int = 0
    revenue_generated: float = 0.0
    top_templates: List[Dict[str, Any]] = Field(default_factory=list)
    channel_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class FollowUpSettings(BaseModel):
    """Follow-up system settings"""
    auto_followup_enabled: bool = True
    default_credits_cost: int = 5
    max_followups_per_session: int = 3
    min_interval_hours: int = 24
    max_interval_days: int = 30
    auto_cancel_after_days: int = 7
    enable_smart_scheduling: bool = True
    enable_credit_charging: bool = True
    enable_analytics: bool = True 