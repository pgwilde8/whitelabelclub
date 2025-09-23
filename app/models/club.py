from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from app.core.security import encryption_service
from typing import Optional
import uuid


class Club(Base, BaseModel):
    __tablename__ = "clubs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    custom_domain = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")
    secondary_color = Column(String(7), default="#1E40AF")
    
    # Stripe Connect
    stripe_account_id = Column(String(255), nullable=True)
    stripe_onboarding_complete = Column(Boolean, default=False)
    
    # OpenAI Integration (encrypted)
    _openai_api_key_encrypted = Column("openai_api_key_encrypted", Text, nullable=True)
    ai_enabled = Column(Boolean, default=False)
    
    # Feature toggles
    features = Column(JSON, default={})
    
    # Subscription
    subscription_status = Column(String(50), default="trial")  # trial, active, suspended, cancelled
    subscription_plan = Column(String(50), default="basic")  # basic, premium, enterprise
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    members = relationship("ClubMember", back_populates="club", cascade="all, delete-orphan")
    roles = relationship("ClubRole", back_populates="club", cascade="all, delete-orphan")
    membership_tiers = relationship("MembershipTier", back_populates="club", cascade="all, delete-orphan")
    booking_services = relationship("BookingService", back_populates="club", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="club", cascade="all, delete-orphan")
    chat_channels = relationship("ChatChannel", back_populates="club", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="club", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="club", cascade="all, delete-orphan")
    platform_subscriptions = relationship("PlatformSubscription", back_populates="club", cascade="all, delete-orphan")
    media_files = relationship("MediaFile", back_populates="club", cascade="all, delete-orphan")
    content_pages = relationship("ContentPage", back_populates="club", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="club", cascade="all, delete-orphan")
    analytics = relationship("ClubAnalytics", back_populates="club", cascade="all, delete-orphan")
    platform_usage = relationship("PlatformUsage", back_populates="club", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="club", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="club", cascade="all, delete-orphan")
    feature_flags = relationship("FeatureFlag", back_populates="club", cascade="all, delete-orphan")
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get decrypted OpenAI API key"""
        if not self._openai_api_key_encrypted:
            return None
        return encryption_service.decrypt(self._openai_api_key_encrypted)
    
    @openai_api_key.setter
    def openai_api_key(self, value: str):
        """Set encrypted OpenAI API key"""
        if value:
            self._openai_api_key_encrypted = encryption_service.encrypt(value)
            self.ai_enabled = True
        else:
            self._openai_api_key_encrypted = None
            self.ai_enabled = False
    
    def __repr__(self):
        return f"<Club(id={self.id}, name='{self.name}', slug='{self.slug}')>"
