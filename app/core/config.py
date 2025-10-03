# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/white_label_club"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = "your-32-byte-base64-encryption-key-here"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # ✅ NEW: Stripe Connect
    STRIPE_CONNECT_CLIENT_ID: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CONNECT_REDIRECT_URI: Optional[str] = None
    
    # Stripe Product IDs
    STRIPE_STARTER_PRODUCT_ID: Optional[str] = None
    STRIPE_PRO_PRODUCT_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRODUCT_ID: Optional[str] = None
    
    # Stripe Price IDs
    STRIPE_STARTER_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRICE_ID: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # DigitalOcean Spaces
    DO_SPACES_KEY: Optional[str] = None
    DO_SPACES_SECRET: Optional[str] = None
    DO_SPACES_ENDPOINT: str = "https://white-label-club.sfo3.digitaloceanspaces.com"
    DO_SPACES_REGION: str = "sfo3"
    DO_SPACES_BUCKET: str = "white-label-club"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Platform Settings
    PLATFORM_DOMAIN: str = "ezclub.app"
    PLATFORM_NAME: str = "White Label Club Platform"
    
    class Config:
        env_file = ".env"

settings = Settings()
