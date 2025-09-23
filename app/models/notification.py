from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class Notification(Base, BaseModel):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_type = Column(String(50), nullable=False)  # platform_user, club_member
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    
    # Notification content
    type = Column(String(100), nullable=False)  # booking_confirmed, payment_received, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Action
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', recipient_id={self.recipient_id})>"


class AuditLog(Base, BaseModel):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # can be platform_user or club_member
    user_type = Column(String(50), nullable=True)  # platform_user, club_member
    
    # Action details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)  # booking, payment, member, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, default={})
    
    # Request info
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', club_id={self.club_id})>"


class FeatureFlag(Base, BaseModel):
    __tablename__ = "feature_flags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    
    flag_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)
    
    # Targeting
    target_tiers = Column(JSON, default=[])
    target_members = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="feature_flags")
    
    def __repr__(self):
        return f"<FeatureFlag(id={self.id}, flag_name='{self.flag_name}', club_id={self.club_id})>"
