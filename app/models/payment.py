from sqlalchemy import Column, String, Text, DateTime, DECIMAL, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class Payment(Base, BaseModel):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="SET NULL"), nullable=True)
    
    # Payment details
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_type = Column(String(50), nullable=False)  # subscription, booking, donation, platform_fee
    
    # Related records
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("member_subscriptions.id", ondelete="SET NULL"), nullable=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    
    # Stripe
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False)  # pending, succeeded, failed, cancelled
    failure_reason = Column(Text, nullable=True)
    
    # Platform fee
    platform_fee_amount = Column(DECIMAL(10, 2), default=0)
    club_earnings = Column(DECIMAL(10, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="payments")
    member = relationship("ClubMember", back_populates="payments")
    subscription = relationship("MemberSubscription", back_populates="payments")
    booking = relationship("Booking", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, club_id={self.club_id})>"


class Donation(Base, BaseModel):
    __tablename__ = "donations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    donor_name = Column(String(255), nullable=True)
    donor_email = Column(String(255), nullable=True)
    donor_message = Column(Text, nullable=True)
    
    amount = Column(DECIMAL(10, 2), nullable=False)
    is_anonymous = Column(Boolean, default=False)
    show_amount = Column(Boolean, default=True)
    
    # Stripe
    stripe_payment_intent_id = Column(String(255), nullable=True)
    payment_status = Column(String(50), default="pending")  # pending, succeeded, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="donations")
    
    def __repr__(self):
        return f"<Donation(id={self.id}, amount={self.amount}, club_id={self.club_id})>"


class PlatformSubscription(Base, BaseModel):
    __tablename__ = "platform_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    
    plan_name = Column(String(50), nullable=False)  # basic, premium, enterprise
    amount = Column(DECIMAL(10, 2), nullable=False)
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    
    status = Column(String(50), default="active")  # active, cancelled, past_due
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Stripe
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("PlatformUser", back_populates="platform_subscriptions")
    club = relationship("Club", back_populates="platform_subscriptions")
    
    def __repr__(self):
        return f"<PlatformSubscription(id={self.id}, plan_name='{self.plan_name}', user_id={self.user_id})>"
