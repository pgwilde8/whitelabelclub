from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, DECIMAL, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class MembershipTier(Base, BaseModel):
    __tablename__ = "membership_tiers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False)  # free, premium, vip
    description = Column(Text, nullable=True)
    price_monthly = Column(DECIMAL(10, 2), default=0)
    price_yearly = Column(DECIMAL(10, 2), default=0)
    
    # Permissions/features
    features = Column(JSON, default={})  # {"chat": true, "bookings": 5, "storage_mb": 1000}
    max_bookings_per_month = Column(Integer, nullable=True)
    max_storage_mb = Column(Integer, nullable=True)
    
    # Display
    color = Column(String(7), nullable=True)  # hex color
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="membership_tiers")
    subscriptions = relationship("MemberSubscription", back_populates="tier", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MembershipTier(id={self.id}, name='{self.name}', club_id={self.club_id})>"


class MemberSubscription(Base, BaseModel):
    __tablename__ = "member_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    tier_id = Column(UUID(as_uuid=True), ForeignKey("membership_tiers.id", ondelete="CASCADE"), nullable=False)
    
    # Subscription details
    status = Column(String(50), default="active")  # active, cancelled, expired, trial
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Dates
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Stripe
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    member = relationship("ClubMember", back_populates="subscriptions")
    tier = relationship("MembershipTier", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MemberSubscription(id={self.id}, member_id={self.member_id}, tier_id={self.tier_id})>"
