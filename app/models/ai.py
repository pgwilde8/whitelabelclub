from sqlalchemy import Column, String, Text, DateTime, DECIMAL, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class AIConversation(Base, BaseModel):
    __tablename__ = "ai_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    
    # Conversation context
    context_type = Column(String(50), default="general")  # general, booking, support, qa
    title = Column(String(255), nullable=True)
    
    # AI settings
    model = Column(String(50), default="gpt-3.5-turbo")
    temperature = Column(DECIMAL(3, 2), default=0.7)
    max_tokens = Column(Integer, default=1000)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="ai_conversations")
    member = relationship("ClubMember", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, club_id={self.club_id}, member_id={self.member_id})>"


class AIMessage(Base, BaseModel):
    __tablename__ = "ai_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost tracking
    cost_usd = Column(DECIMAL(10, 6), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")
    
    def __repr__(self):
        return f"<AIMessage(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"
