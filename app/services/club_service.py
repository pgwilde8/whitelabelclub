from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import re

from app.models.club import Club
from app.models.user import ClubMember
from app.models.booking import Booking
from app.models.payment import Payment
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse


class ClubService:
    """Service layer for club management operations"""
    
    @staticmethod
    def validate_slug(slug: str) -> str:
        """Validate and sanitize club slug"""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\-_]', '-', slug.lower())
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        if len(slug) < 1 or len(slug) > 100:
            raise ValueError("Slug must be between 1 and 100 characters")
        
        return slug

    @staticmethod
    async def create_club(db: AsyncSession, club_data: ClubCreate) -> Club:
        """Create a new club with validation"""
        # Validate and sanitize slug
        validated_slug = ClubService.validate_slug(club_data.slug)
        
        # Check if slug already exists
        existing_club = await db.execute(
            select(Club).where(Club.slug == validated_slug)
        )
        if existing_club.scalar_one_or_none():
            raise ValueError(f"Club with slug '{validated_slug}' already exists")
        
        # Create new club
        new_club = Club(
            id=uuid.uuid4(),
            name=club_data.name,
            slug=validated_slug,
            description=club_data.description,
            primary_color=club_data.primary_color,
            secondary_color=club_data.secondary_color,
            logo_url=club_data.logo_url,
            custom_domain=club_data.custom_domain,
            features=club_data.features or {},
            stripe_account_id=club_data.stripe_account_id,
        )
        
        # Set OpenAI API key if provided (will be encrypted automatically)
        if club_data.openai_api_key:
            new_club.openai_api_key = club_data.openai_api_key
        
        db.add(new_club)
        await db.commit()
        await db.refresh(new_club)
        
        return new_club

    @staticmethod
    async def get_club_by_slug(db: AsyncSession, club_slug: str) -> Optional[Club]:
        """Get a club by its slug"""
        result = await db.execute(
            select(Club).where(
                Club.slug == club_slug,
                Club.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_or_create_club(db: AsyncSession, club_slug: str) -> Club:
        """Get existing club or create a new one for demo purposes"""
        club = await ClubService.get_club_by_slug(db, club_slug)
        
        if not club:
            # Create club for demo purposes
            club_data = ClubCreate(
                name=f"Club {club_slug.title()}",
                slug=club_slug,
                description="A vibrant community for passionate members",
                primary_color="#3B82F6",
                secondary_color="#1E40AF",
                features={
                    "enable_bookings": True,
                    "enable_chat": True,
                    "enable_ai": False,
                    "enable_donations": True
                }
            )
            club = await ClubService.create_club(db, club_data)
        
        return club

    @staticmethod
    async def get_club_analytics(db: AsyncSession, club: Club) -> Dict[str, Any]:
        """Get analytics data for a club"""
        # Get club member count
        member_count_result = await db.execute(
            select(func.count(ClubMember.id)).where(ClubMember.club_id == club.id)
        )
        total_members = member_count_result.scalar() or 0
        
        # Get recent member activity (last 30 days) - using updated_at since last_active_at doesn't exist
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_members_result = await db.execute(
            select(func.count(ClubMember.id)).where(
                and_(
                    ClubMember.club_id == club.id,
                    ClubMember.updated_at >= thirty_days_ago
                )
            )
        )
        active_members = active_members_result.scalar() or 0
        
        # Calculate total revenue from payments
        revenue_result = await db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.club_id == club.id,
                    Payment.status == 'succeeded'
                )
            )
        )
        total_revenue_cents = revenue_result.scalar() or 0
        total_revenue = total_revenue_cents / 100  # Convert from cents to dollars
        
        # Get new members this month
        this_month = datetime.now().replace(day=1)
        new_members_result = await db.execute(
            select(func.count(ClubMember.id)).where(
                and_(
                    ClubMember.club_id == club.id,
                    ClubMember.created_at >= this_month
                )
            )
        )
        new_members_this_month = new_members_result.scalar() or 0
        
        return {
            "total_members": total_members,
            "active_members": active_members,
            "total_revenue": int(total_revenue),
            "new_members_this_month": new_members_this_month,
            "conversion_rate": (active_members / total_members * 100) if total_members > 0 else 0
        }

    @staticmethod
    async def get_recent_members(db: AsyncSession, club: Club, limit: int = 5) -> List[ClubMember]:
        """Get recent club members"""
        result = await db.execute(
            select(ClubMember)
            .where(ClubMember.club_id == club.id)
            .order_by(ClubMember.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_recent_bookings(db: AsyncSession, club: Club, limit: int = 5) -> List[Booking]:
        """Get recent bookings for a club"""
        result = await db.execute(
            select(Booking)
            .where(Booking.club_id == club.id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_club(db: AsyncSession, club: Club, club_data: ClubUpdate) -> Club:
        """Update a club with validation"""
        # Update fields that are provided
        update_data = club_data.dict(exclude_unset=True)
        
        # Handle OpenAI API key specially
        if "openai_api_key" in update_data:
            club.openai_api_key = update_data.pop("openai_api_key")
        
        # Update other fields
        for field, value in update_data.items():
            setattr(club, field, value)
        
        await db.commit()
        await db.refresh(club)
        
        return club

    @staticmethod
    async def delete_club(db: AsyncSession, club: Club) -> None:
        """Soft delete a club"""
        club.deleted_at = datetime.now()
        await db.commit()

    # Simple in-memory storage for demo purposes
    _services_storage = {}
    
    @staticmethod
    async def get_booking_services(db: AsyncSession, club_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get booking services for a club"""
        club_id_str = str(club_id)
        
        # Check if we have custom services for this club
        if club_id_str in ClubService._services_storage:
            return ClubService._services_storage[club_id_str]
        
        # Return default services for new clubs (restore placeholders)
        default_services = [
            {
                "id": 1,
                "name": "Personal Training",
                "price": 75.00,
                "duration": 60,
                "description": "One-on-one personal training session with certified trainer",
                "bookings_count": 23,
                "revenue": 1725.00,
                "status": "active",
                "max_participants": 1,
                "allow_non_members": True
            },
            {
                "id": 2,
                "name": "Nutrition Consultation", 
                "price": 120.00,
                "duration": 90,
                "description": "Comprehensive nutrition planning and meal prep guidance",
                "bookings_count": 8,
                "revenue": 960.00,
                "status": "active",
                "max_participants": 1,
                "allow_non_members": True
            },
            {
                "id": 3,
                "name": "Group Yoga Class",
                "price": 35.00,
                "duration": 60,
                "description": "Relaxing yoga class for all skill levels",
                "bookings_count": 45,
                "revenue": 1575.00,
                "status": "active",
                "max_participants": 12,
                "allow_non_members": False
            }
        ]
        
        # Store default services for this club
        ClubService._services_storage[club_id_str] = default_services
        return default_services
    
    @staticmethod
    async def add_booking_service(db: AsyncSession, club_id: uuid.UUID, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new booking service"""
        club_id_str = str(club_id)
        
        # Get current services
        current_services = ClubService._services_storage.get(club_id_str, [])
        
        # Generate new ID
        new_id = max([s.get("id", 0) for s in current_services], default=0) + 1
        
        # Create new service
        new_service = {
            "id": new_id,
            "name": service_data.get("name", "New Service"),
            "price": float(service_data.get("price", 0)),
            "duration": int(service_data.get("duration", 60)),
            "description": service_data.get("description", ""),
            "bookings_count": 0,
            "revenue": 0.00,
            "status": "active",
            "max_participants": int(service_data.get("max_participants", 1)),
            "allow_non_members": service_data.get("allow_non_members", True)
        }
        
        # Add to storage
        current_services.append(new_service)
        ClubService._services_storage[club_id_str] = current_services
        
        return new_service

    @staticmethod
    async def get_all_clubs(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Club]:
        """Get all clubs with pagination"""
        result = await db.execute(
            select(Club)
            .where(Club.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(Club.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_members(db: AsyncSession, club: Club) -> List[ClubMember]:
        """Get all members for a specific club"""
        result = await db.execute(
            select(ClubMember)
            .where(ClubMember.club_id == club.id)
            .order_by(ClubMember.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_member_by_id(db: AsyncSession, club: Club, member_id: str) -> Optional[ClubMember]:
        """Get a specific member by ID within a club"""
        result = await db.execute(
            select(ClubMember)
            .where(
                and_(
                    ClubMember.club_id == club.id,
                    ClubMember.id == member_id
                )
            )
        )
        return result.scalar_one_or_none()