from sqlalchemy import Column, String, DateTime, DECIMAL, Integer, BigInteger, JSON, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class ClubAnalytics(Base, BaseModel):
    __tablename__ = "club_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    
    # Date range
    date = Column(Date, nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 4), nullable=False)
    
    # Dimensions
    dimensions = Column(JSON, default={})  # {"tier": "premium", "channel": "general"}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="analytics")
    
    def __repr__(self):
        return f"<ClubAnalytics(id={self.id}, club_id={self.club_id}, metric='{self.metric_name}')>"


class PlatformUsage(Base, BaseModel):
    __tablename__ = "platform_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    
    # Usage metrics
    api_calls = Column(Integer, default=0)
    ai_tokens_used = Column(Integer, default=0)
    storage_bytes = Column(BigInteger, default=0)
    bandwidth_bytes = Column(BigInteger, default=0)
    
    # Date
    date = Column(Date, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="platform_usage")
    
    def __repr__(self):
        return f"<PlatformUsage(id={self.id}, club_id={self.club_id}, date={self.date})>"
