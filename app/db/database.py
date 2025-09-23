from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models.club import Club
        from app.models.user import PlatformUser, ClubMember, ClubRole
        from app.models.membership import MembershipTier, MemberSubscription
        from app.models.booking import BookingService, BookingSlot, Booking
        from app.models.chat import ChatChannel, ChatMessage, MessageReaction, MemberChannelAccess
        from app.models.payment import Payment, Donation, PlatformSubscription
        from app.models.media import MediaFile, ContentPage, ContentMedia
        from app.models.ai import AIConversation, AIMessage
        from app.models.analytics import ClubAnalytics, PlatformUsage
        from app.models.notification import Notification, AuditLog, FeatureFlag
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
