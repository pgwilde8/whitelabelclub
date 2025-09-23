from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class ClubBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    primary_color: str = Field(default="#3B82F6")
    secondary_color: str = Field(default="#1E40AF")
    logo_url: Optional[str] = None
    custom_domain: Optional[str] = None
    features: Dict[str, Any] = Field(default_factory=dict)


class ClubCreate(ClubBase):
    openai_api_key: Optional[str] = None
    stripe_account_id: Optional[str] = None


class ClubUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    custom_domain: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    openai_api_key: Optional[str] = None


class ClubResponse(ClubBase):
    id: uuid.UUID
    stripe_account_id: Optional[str] = None
    stripe_onboarding_complete: bool = False
    ai_enabled: bool = False
    subscription_status: str = "trial"
    subscription_plan: str = "basic"
    subscription_ends_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
