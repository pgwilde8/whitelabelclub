from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from decimal import Decimal


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    payment_type: str = Field(..., min_length=1, max_length=50)


class PaymentCreate(PaymentBase):
    member_id: Optional[uuid.UUID] = None
    subscription_id: Optional[uuid.UUID] = None
    booking_id: Optional[uuid.UUID] = None


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    failure_reason: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    club_id: uuid.UUID
    member_id: Optional[uuid.UUID] = None
    subscription_id: Optional[uuid.UUID] = None
    booking_id: Optional[uuid.UUID] = None
    status: str
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    failure_reason: Optional[str] = None
    platform_fee_amount: Decimal = 0
    club_earnings: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
