from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.services.club_service import ClubService
from app.models.user import PlatformUser, ClubMember
from app.models.club import Club
from sqlalchemy import select
from typing import Optional

# Create router for user routes
router = APIRouter(prefix="/user", tags=["users"], include_in_schema=False)

# Setup templates
templates = Jinja2Templates(directory="templates")

@router.get("/{username}/profile", response_class=HTMLResponse)
async def user_profile(request: Request, username: str, db: AsyncSession = Depends(get_db_session)):
    """Dynamic user profile page - ONE route serves ALL users"""
    try:
        # Get user from database
        result = await db.execute(
            select(PlatformUser).where(PlatformUser.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        # Pre-format dates to avoid async issues in templates
        member_since = user.created_at.strftime('%B %Y') if user.created_at else 'Unknown'
        
        # For now, return basic user info without complex relationships
        # TODO: Add club ownership and membership queries when we have proper relationships set up
        owned_clubs = []  # Will implement when needed
        memberships = []  # Will implement when needed
        
        return templates.TemplateResponse("user_profile.html", {
            "request": request,
            "user": user,
            "member_since": member_since,
            "owned_clubs": owned_clubs,
            "memberships": memberships,
            "total_clubs": len(owned_clubs),
            "total_memberships": len(memberships)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading profile: {str(e)}")

@router.get("/{username}/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, username: str, db: AsyncSession = Depends(get_db_session)):
    """User dashboard showing their clubs and activities"""
    try:
        result = await db.execute(
            select(PlatformUser).where(PlatformUser.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        # For now, return basic user info without complex relationships
        # TODO: Add club ownership queries when we have proper relationships set up
        owned_clubs = []  # Will implement when needed
        
        # Calculate summary stats
        total_clubs = len(owned_clubs)
        total_members = 0
        total_revenue = 0
        
        return templates.TemplateResponse("user_dashboard.html", {
            "request": request,
            "user": user,
            "clubs": owned_clubs,
            "total_clubs": total_clubs,
            "total_members": total_members,
            "total_revenue": total_revenue
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")

@router.get("/{username}/settings", response_class=HTMLResponse)
async def user_settings(request: Request, username: str, db: AsyncSession = Depends(get_db_session)):
    """User settings page"""
    try:
        result = await db.execute(
            select(PlatformUser).where(PlatformUser.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        return templates.TemplateResponse("user_settings.html", {
            "request": request,
            "user": user
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading settings: {str(e)}")

@router.post("/{username}/settings")
async def update_user_settings(
    request: Request,
    username: str,
    db: AsyncSession = Depends(get_db_session),
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None)
):
    """Update user settings"""
    try:
        result = await db.execute(
            select(PlatformUser).where(PlatformUser.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        # Update user fields if provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        
        await db.commit()
        await db.refresh(user)
        
        return templates.TemplateResponse("user_settings.html", {
            "request": request,
            "user": user,
            "success": "Settings updated successfully!"
        })
        
    except Exception as e:
        return templates.TemplateResponse("user_settings.html", {
            "request": request,
            "error": f"Failed to update settings: {str(e)}"
        })

# MEMBER ROUTES (Within clubs)
@router.get("/community/{club_slug}/member/{member_id}", response_class=HTMLResponse)
async def member_profile(request: Request, club_slug: str, member_id: str, db: AsyncSession = Depends(get_db_session)):
    """Dynamic member profile within a club - ONE route serves ALL members"""
    try:
        # Get club
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail=f"Club '{club_slug}' not found")
        
        # Get member
        result = await db.execute(
            select(ClubMember).where(
                ClubMember.id == member_id,
                ClubMember.club_id == club.id
            )
        )
        member = result.scalar_one_or_none()
        
        if not member:
            raise HTTPException(status_code=404, detail=f"Member not found in club '{club_slug}'")
        
        # Get member's bookings - simplified for now since we don't have the full booking system linked
        recent_bookings = []  # TODO: Implement when booking system is connected
        
        return templates.TemplateResponse("member_profile.html", {
            "request": request,
            "club": club,
            "member": member,
            "recent_bookings": recent_bookings,
            "member_since": member.created_at.strftime("%B %Y")
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading member profile: {str(e)}")

@router.get("/community/{club_slug}/members", response_class=HTMLResponse)
async def club_members_list(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """List all members of a club - ONE route serves ALL clubs"""
    try:
        # Get club
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail=f"Club '{club_slug}' not found")
        
        # Get all members of this club
        result = await db.execute(
            select(ClubMember)
            .where(ClubMember.club_id == club.id)
            .order_by(ClubMember.created_at.desc())
        )
        members = result.scalars().all()
        
        # Group members by tier
        members_by_tier = {
            "free": [m for m in members if m.member_tier == "free"],
            "premium": [m for m in members if m.member_tier == "premium"],
            "vip": [m for m in members if m.member_tier == "vip"]
        }
        
        return templates.TemplateResponse("club_members.html", {
            "request": request,
            "club": club,
            "members": members,
            "members_by_tier": members_by_tier,
            "total_members": len(members),
            "free_count": len(members_by_tier["free"]),
            "premium_count": len(members_by_tier["premium"]),
            "vip_count": len(members_by_tier["vip"])
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading members: {str(e)}")

@router.get("/signup", response_class=HTMLResponse)
async def user_signup_form(request: Request):
    """User registration form"""
    return templates.TemplateResponse("user_signup.html", {
        "request": request
    })

@router.post("/signup")
async def create_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(None),
    last_name: str = Form(None)
):
    """Create a new user account"""
    try:
        # Check if username or email already exists
        existing_user = await db.execute(
            select(PlatformUser).where(
                (PlatformUser.username == username) | (PlatformUser.email == email)
            )
        )
        if existing_user.scalar_one_or_none():
            return templates.TemplateResponse("user_signup.html", {
                "request": request,
                "error": "Username or email already exists"
            })
        
        # Create new user (password should be hashed in production)
        new_user = PlatformUser(
            username=username,
            email=email,
            password_hash=password,  # TODO: Hash password properly
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return RedirectResponse(url=f"/user/{username}/dashboard", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse("user_signup.html", {
            "request": request,
            "error": f"Failed to create account: {str(e)}"
        })

@router.get("/login", response_class=HTMLResponse)
async def user_login_form(request: Request):
    """User login form"""
    return templates.TemplateResponse("user_login.html", {
        "request": request
    })

@router.post("/login")
async def login_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    username: str = Form(...),
    password: str = Form(...)
):
    """User login"""
    try:
        result = await db.execute(
            select(PlatformUser).where(PlatformUser.username == username)
        )
        user = result.scalar_one_or_none()
        
        # Simple password check (use proper hashing in production)
        if not user or user.password_hash != password:
            return templates.TemplateResponse("user_login.html", {
                "request": request,
                "error": "Invalid username or password"
            })
        
        # In production, set up proper session management
        return RedirectResponse(url=f"/user/{username}/dashboard", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse("user_login.html", {
            "request": request,
            "error": f"Login failed: {str(e)}"
        })