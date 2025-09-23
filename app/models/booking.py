from sqlalchemy import Column, String, Text, Boolean, DateTime, DECIMAL, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class BookingService(Base, BaseModel):
    __tablename__ = "booking_services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), default=0)
    
    # Availability
    is_active = Column(Boolean, default=True)
    max_advance_days = Column(Integer, default=30)
    min_advance_hours = Column(Integer, default=2)
    
    # Requirements
    requires_membership_tier = Column(String(50), nullable=True)  # minimum tier required
    max_participants = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="booking_services")
    slots = relationship("BookingSlot", back_populates="service", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BookingService(id={self.id}, name='{self.name}', club_id={self.club_id})>"


class BookingSlot(Base, BaseModel):
    __tablename__ = "booking_slots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("booking_services.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_available = Column(Boolean, default=True)
    max_capacity = Column(Integer, default=1)
    current_bookings = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    service = relationship("BookingService", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BookingSlot(id={self.id}, service_id={self.service_id}, start_time={self.start_time})>"


class Booking(Base, BaseModel):
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("booking_services.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("booking_slots.id", ondelete="CASCADE"), nullable=False)
    
    # Booking details
    status = Column(String(50), default="confirmed")  # confirmed, cancelled, completed, no_show
    notes = Column(Text, nullable=True)
    
    # Payment
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(String(50), default="pending")  # pending, paid, refunded
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Timestamps
    booked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="bookings")
    member = relationship("ClubMember", back_populates="bookings")
    service = relationship("BookingService", back_populates="bookings")
    slot = relationship("BookingSlot", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, member_id={self.member_id}, service_id={self.service_id})>"
