# Import all models to ensure they are registered with SQLAlchemy
from .club import Club
from .user import PlatformUser, ClubMember, ClubRole
from .membership import MembershipTier, MemberSubscription
from .booking import BookingService, BookingSlot, Booking
from .chat import ChatChannel, ChatMessage, MessageReaction, MemberChannelAccess
from .payment import Payment, Donation, PlatformSubscription
from .media import MediaFile, ContentPage, ContentMedia
from .ai import AIConversation, AIMessage
from .analytics import ClubAnalytics, PlatformUsage
from .notification import Notification, AuditLog, FeatureFlag

__all__ = [
    "Club",
    "PlatformUser", 
    "ClubMember",
    "ClubRole",
    "MembershipTier",
    "MemberSubscription",
    "BookingService",
    "BookingSlot", 
    "Booking",
    "ChatChannel",
    "ChatMessage",
    "MessageReaction",
    "MemberChannelAccess",
    "Payment",
    "Donation",
    "PlatformSubscription",
    "MediaFile",
    "ContentPage",
    "ContentMedia",
    "AIConversation",
    "AIMessage",
    "ClubAnalytics",
    "PlatformUsage",
    "Notification",
    "AuditLog",
    "FeatureFlag",
]
