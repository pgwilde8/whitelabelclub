from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class ChatChannel(Base, BaseModel):
    __tablename__ = "chat_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    channel_type = Column(String(50), default="public")  # public, private, tier_restricted
    required_tier = Column(String(50), nullable=True)  # minimum tier to access
    
    # Moderation
    is_moderated = Column(Boolean, default=False)
    allow_file_uploads = Column(Boolean, default=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="chat_channels")
    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")
    member_access = relationship("MemberChannelAccess", back_populates="channel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatChannel(id={self.id}, name='{self.name}', club_id={self.club_id})>"


class ChatMessage(Base, BaseModel):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("chat_channels.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, image, file, system
    file_url = Column(String(500), nullable=True)  # for file attachments
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Moderation
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Replies
    reply_to_message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    channel = relationship("ChatChannel", back_populates="messages")
    member = relationship("ClubMember", back_populates="chat_messages")
    reply_to = relationship("ChatMessage", remote_side=[id])
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, channel_id={self.channel_id}, member_id={self.member_id})>"


class MessageReaction(Base, BaseModel):
    __tablename__ = "message_reactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    emoji = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="reactions")
    member = relationship("ClubMember", back_populates="message_reactions")
    
    def __repr__(self):
        return f"<MessageReaction(id={self.id}, message_id={self.message_id}, member_id={self.member_id})>"


class MemberChannelAccess(Base, BaseModel):
    __tablename__ = "member_channel_access"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("club_members.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("chat_channels.id", ondelete="CASCADE"), nullable=False)
    access_type = Column(String(50), default="read_write")  # read_only, read_write, banned
    
    # Timestamps
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    member = relationship("ClubMember", back_populates="channel_access")
    channel = relationship("ChatChannel", back_populates="member_access")
    
    def __repr__(self):
        return f"<MemberChannelAccess(id={self.id}, member_id={self.member_id}, channel_id={self.channel_id})>"
