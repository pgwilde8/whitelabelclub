from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel
from typing import Optional
import uuid


class MediaFile(Base, BaseModel):
    __tablename__ = "media_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("club_roles.id", ondelete="SET NULL"), nullable=True)  # only club owners can upload
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)  # image/jpeg, video/mp4, application/pdf
    file_size = Column(Integer, nullable=False)
    
    # Storage
    storage_key = Column(String(500), nullable=False)  # key in DigitalOcean Spaces
    storage_url = Column(String(500), nullable=False)  # public URL
    storage_bucket = Column(String(100), default="white-label-club")
    
    # Access control
    visibility = Column(String(50), default="private")  # public, private, tier_restricted
    required_tier = Column(String(50), nullable=True)  # minimum tier to access
    
    # Metadata
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="media_files")
    uploaded_by_role = relationship("ClubRole", back_populates="uploaded_media")
    content_media = relationship("ContentMedia", back_populates="media_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}', club_id={self.club_id})>"


class ContentPage(Base, BaseModel):
    __tablename__ = "content_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("club_roles.id", ondelete="SET NULL"), nullable=True)
    
    # Content
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    
    # Access control
    visibility = Column(String(50), default="public")  # public, private, tier_restricted
    required_tier = Column(String(50), nullable=True)
    
    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="draft")  # draft, published, archived
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    club = relationship("Club", back_populates="content_pages")
    created_by_role = relationship("ClubRole", back_populates="created_content")
    content_media = relationship("ContentMedia", back_populates="content_page", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContentPage(id={self.id}, title='{self.title}', club_id={self.club_id})>"


class ContentMedia(Base, BaseModel):
    __tablename__ = "content_media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content_pages.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False)
    
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    content_page = relationship("ContentPage", back_populates="content_media")
    media_file = relationship("MediaFile", back_populates="content_media")
    
    def __repr__(self):
        return f"<ContentMedia(id={self.id}, content_id={self.content_id}, media_id={self.media_id})>"
