from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class PlatformUser(Base, BaseModel):
    __tablename__ = "platform_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)  # Added username field
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)  # Added bio field
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club_roles = relationship("ClubRole", back_populates="user", cascade="all, delete-orphan")
    platform_subscriptions = relationship("PlatformSubscription", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlatformUser(id={self.id}, email='{self.email}')>"


class ClubMember(Base, BaseModel):
    __tablename__ = "club_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=True)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Membership info
    member_tier = Column(String(50), default="free")  # free, premium, vip
    status = Column(String(50), default="active")  # active, suspended, banned
    
    # External auth (optional)
    external_id = Column(String(255), nullable=True)
    external_provider = Column(String(50), nullable=True)  # google, facebook, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="members")
    subscriptions = relationship("MemberSubscription", back_populates="member", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="member", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="member", cascade="all, delete-orphan")
    message_reactions = relationship("MessageReaction", back_populates="member", cascade="all, delete-orphan")
    channel_access = relationship("MemberChannelAccess", back_populates="member", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="member", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="member", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClubMember(id={self.id}, email='{self.email}', club_id={self.club_id})>"


class ClubRole(Base, BaseModel):
    __tablename__ = "club_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # owner, admin, moderator
    permissions = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="roles")
    user = relationship("PlatformUser", back_populates="club_roles")
    uploaded_media = relationship("MediaFile", back_populates="uploaded_by_role", cascade="all, delete-orphan")
    created_content = relationship("ContentPage", back_populates="created_by_role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClubRole(id={self.id}, club_id={self.club_id}, user_id={self.user_id}, role='{self.role}')>"
