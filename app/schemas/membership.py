from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal


class MembershipTierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    price_monthly: Decimal = Field(default=0, ge=0)
    price_yearly: Decimal = Field(default=0, ge=0)
    features: Dict[str, Any] = Field(default_factory=dict)
    max_bookings_per_month: Optional[int] = None
    max_storage_mb: Optional[int] = None
    color: Optional[str] = None
    sort_order: int = Field(default=0)
    is_active: bool = True


class MembershipTierCreate(MembershipTierBase):
    pass


class MembershipTierUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = None
    price_yearly: Optional[Decimal] = None
    features: Optional[Dict[str, Any]] = None
    max_bookings_per_month: Optional[int] = None
    max_storage_mb: Optional[int] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MembershipTierResponse(MembershipTierBase):
    id: uuid.UUID
    club_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
