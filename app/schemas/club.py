from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class ClubBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    primary_color: str = Field(default="#0075c4")
    secondary_color: str = Field(default="#0267C1")
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

    # Override base class fields to allow None values for existing data
    primary_color: str = "#0075c4"  
    secondary_color: str = "#0267C1"
    features: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Handle None values gracefully
        return cls(
            id=obj.id,
            name=obj.name,
            slug=obj.slug,
            description=obj.description,
            primary_color=obj.primary_color or "#0075c4",
            secondary_color=obj.secondary_color or "#0267C1", 
            logo_url=obj.logo_url,
            custom_domain=obj.custom_domain,
            features=obj.features or {},
            stripe_account_id=obj.stripe_account_id,
            stripe_onboarding_complete=obj.stripe_onboarding_complete or False,
            ai_enabled=obj.ai_enabled or False,
            subscription_status=obj.subscription_status or "trial",
            subscription_plan=obj.subscription_plan or "basic",
            subscription_ends_at=obj.subscription_ends_at,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
