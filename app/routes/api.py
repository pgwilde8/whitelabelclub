from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List
from app.db.session import get_db_session
from app.models.club import Club
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse
from app.services.club_service import ClubService

# Create router for API endpoints
router = APIRouter(prefix="/api/v1", tags=["api"])

# Create router for API endpoints
router = APIRouter(prefix="/api/v1", tags=["api"])

@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "service": "ClubLaunch API"}

@router.post("/clubs", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    club_data: ClubCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new club"""
    try:
        from app.core.config import settings
        from sqlalchemy import select, func
        from app.models.club import Club
        
        # Check if promo code is valid for beta program
        promo_code = club_data.promo_code
        is_beta_tester = False
        
        if promo_code and promo_code in settings.BETA_PROMO_CODES:
            # Check beta tester limit
            result = await db.execute(
                select(func.count(Club.id)).where(Club.account_type == "lifetime_free")
            )
            beta_count = result.scalar() or 0
            
            if beta_count >= settings.BETA_TESTER_LIMIT:
                raise HTTPException(
                    status_code=400,
                    detail=f"Beta tester limit reached ({settings.BETA_TESTER_LIMIT} spots). Try again later!"
                )
            
            is_beta_tester = True
        
        # Create the club
        club = await ClubService.create_club(db, club_data)
        
        # Set beta tester status if promo code was valid
        if is_beta_tester:
            club.account_type = "lifetime_free"
            club.promo_code_used = promo_code
            await db.commit()
            await db.refresh(club)
        
        return ClubResponse.from_orm(club)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create club: {str(e)}"
        )

@router.post("/clubs/{club_slug}/send-welcome-email")
async def send_welcome_email(club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Send beta welcome email to club owner (triggered from launch page)"""
    try:
        from sqlalchemy import select, func
        from app.models.club import Club
        from app.services.email_service import EmailService
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get the club
        result = await db.execute(select(Club).where(Club.slug == club_slug))
        club = result.scalar_one_or_none()
        
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Only send to beta testers who haven't received email yet
        if club.account_type != "lifetime_free":
            return {"message": "Not a beta tester, email not sent"}
        
        if club.welcome_email_sent:
            return {"message": "Welcome email already sent"}
        
        if not club.owner_email:
            logger.warning(f"Cannot send welcome email to {club.slug} - no owner_email")
            raise HTTPException(status_code=400, detail="No owner email on file")
        
        # Mark Stripe as complete
        club.stripe_onboarding_complete = True
        
        # Count beta testers to get their number
        count_result = await db.execute(
            select(func.count(Club.id)).where(Club.account_type == "lifetime_free")
        )
        beta_number = count_result.scalar() or 1
        
        logger.info(f"API: Sending welcome email to {club.owner_email} (Beta Tester #{beta_number})...")
        
        # Send email
        email_sent = EmailService.send_beta_welcome_email(
            club_name=club.name,
            club_slug=club.slug,
            owner_email=club.owner_email,
            beta_number=beta_number
        )
        
        if email_sent:
            from datetime import datetime
            club.welcome_email_sent = True
            club.welcome_email_sent_at = datetime.utcnow()
            await db.commit()
            logger.info(f"✅ Welcome email sent to {club.owner_email}")
            return {"message": "Welcome email sent successfully"}
        else:
            logger.error(f"❌ Failed to send welcome email to {club.owner_email}")
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_welcome_email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )

@router.get("/clubs", response_model=List[ClubResponse])
async def get_clubs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all clubs with pagination"""
    try:
        clubs = await ClubService.get_all_clubs(db, skip, limit)
        return [ClubResponse.from_orm(club) for club in clubs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch clubs: {str(e)}"
        )

@router.get("/clubs/{club_slug}", response_model=ClubResponse)
async def get_club_by_slug(
    club_slug: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a club by its slug"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Club with slug '{club_slug}' not found"
            )
        return ClubResponse.from_orm(club)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch club: {str(e)}"
        )

@router.put("/clubs/{club_slug}", response_model=ClubResponse)
async def update_club(
    club_slug: str,
    club_data: ClubUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a club"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Club with slug '{club_slug}' not found"
            )
        
        updated_club = await ClubService.update_club(db, club, club_data)
        return ClubResponse.from_orm(updated_club)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update club: {str(e)}"
        )

@router.delete("/clubs/{club_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_slug: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Soft delete a club"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Club with slug '{club_slug}' not found"
            )
        
        await ClubService.delete_club(db, club)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete club: {str(e)}"
        )

@router.get("/users")
async def get_users():
    """Get all platform users"""
    return {"message": "Users endpoint - coming soon"}

@router.post("/members/join", status_code=status.HTTP_201_CREATED)
async def join_community(
    request: dict,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new community member"""
    try:
        from app.models.user import ClubMember
        from app.core.security import get_password_hash
        import uuid
        
        # Get club
        club_slug = request.get("club_slug")
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Community '{club_slug}' not found"
            )
        
        # Create new member
        new_member = ClubMember(
            id=uuid.uuid4(),
            club_id=club.id,
            username=request.get("username"),
            email=request.get("email"),
            password_hash=get_password_hash(request.get("password")),
            first_name=request.get("first_name"),
            last_name=request.get("last_name"),
            phone=request.get("phone"),
            role="member",
            subscription_status="active",
            subscription_tier="free"
        )
        
        db.add(new_member)
        await db.commit()
        await db.refresh(new_member)
        
        return {
            "success": True,
            "message": "Member created successfully",
            "member_id": str(new_member.id),
            "username": new_member.username
        }
        
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create member: {str(e)}"
        )
