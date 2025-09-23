from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from decimal import Decimal


class BookingBase(BaseModel):
    notes: Optional[str] = None
    amount: Decimal = Field(..., ge=0)


class BookingCreate(BookingBase):
    service_id: uuid.UUID
    slot_id: uuid.UUID


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    payment_status: Optional[str] = None


class BookingResponse(BookingBase):
    id: uuid.UUID
    club_id: uuid.UUID
    member_id: uuid.UUID
    service_id: uuid.UUID
    slot_id: uuid.UUID
    status: str = "confirmed"
    payment_status: str = "pending"
    stripe_payment_intent_id: Optional[str] = None
    booked_at: datetime
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
