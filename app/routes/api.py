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
        club = await ClubService.create_club(db, club_data)
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
