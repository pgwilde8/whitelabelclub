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
    
    # Stripe Mode
    STRIPE_MODE: str = "test"  # "test" or "live"
    
    # Stripe Test/Live variants
    STRIPE_PUBLISHABLE_KEY_LIVE: Optional[str] = None
    STRIPE_SECRET_KEY_LIVE: Optional[str] = None
    STRIPE_WEBHOOK_SECRET_LIVE: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY_TEST: Optional[str] = None
    STRIPE_SECRET_KEY_TEST: Optional[str] = None
    STRIPE_WEBHOOK_SECRET_TEST: Optional[str] = None

    # Stripe Connect Test/Live variants
    STRIPE_CONNECT_CLIENT_ID_LIVE: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_SECRET_LIVE: Optional[str] = None
    STRIPE_CONNECT_REDIRECT_URI_LIVE: Optional[str] = None
    STRIPE_CONNECT_CLIENT_ID_TEST: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_SECRET_TEST: Optional[str] = None
    STRIPE_CONNECT_REDIRECT_URI_TEST: Optional[str] = None
    
    # Shared Stripe Connect (fallback if mode-specific not set)
    STRIPE_CONNECT_REDIRECT_URI: Optional[str] = None
    
    # Webhook URLs (optional, for reference)
    STRIPE_WEBHOOK_URL_LIVE: Optional[str] = None
    STRIPE_WEBHOOK_URL_TEST: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_URL_LIVE: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_URL_TEST: Optional[str] = None
    
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
    
    # Commission/Fee Settings
    PLATFORM_COMMISSION_PERCENT: float = 3.0  # 3% commission on service bookings
    SUBSCRIPTION_COMMISSION_PERCENT: float = 3.0  # 3% commission on subscriptions
    ONE_TIME_FEE_CENTS: int = 200  # $2.00 flat fee for one-time payments
    
    class Config:
        env_file = ".env"

settings = Settings()
