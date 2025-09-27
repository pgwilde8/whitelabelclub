from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.services.club_service import ClubService
from app.schemas.club import ClubCreate

# Create router for admin routes
router = APIRouter(prefix="/admin", tags=["admin"], include_in_schema=False)

# Setup templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Main admin dashboard"""
    clubs = await ClubService.get_all_clubs(db, skip=0, limit=100)
    
    # Calculate summary stats
    total_clubs = len(clubs)
    total_members = sum([0] * total_clubs)  # TODO: Sum actual member counts
    total_revenue = sum([0] * total_clubs)  # TODO: Sum actual revenue
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "total_clubs": total_clubs,
        "total_members": total_members, 
        "total_revenue": total_revenue,
        "recent_clubs": clubs[:5]
    })

@router.get("/clubs", response_class=HTMLResponse)
async def admin_clubs_list(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Admin page to list all clubs"""
    clubs = await ClubService.get_all_clubs(db, skip=0, limit=100)
    
    # Convert clubs to template format
    clubs_data = []
    for club in clubs:
        analytics = await ClubService.get_club_analytics(db, club)
        clubs_data.append({
            "id": str(club.id),
            "name": club.name,
            "slug": club.slug,
            "description": club.description,
            "total_members": analytics["total_members"],
            "total_revenue": analytics["total_revenue"],
            "subscription_status": club.subscription_status,
            "subscription_plan": club.subscription_plan,
            "created_at": club.created_at.strftime("%B %d, %Y")
        })
    
    return templates.TemplateResponse("admin_clubs.html", {
        "request": request,
        "clubs": clubs_data
    })

@router.get("/clubs/create", response_class=HTMLResponse)
async def admin_create_club_form(request: Request):
    """Admin form to create a new club"""
    return templates.TemplateResponse("admin_create_club.html", {
        "request": request
    })

@router.post("/clubs/create")
async def admin_create_club(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Admin endpoint to create a new club"""
    try:
        form_data = await request.form()
        
        club_data = ClubCreate(
            name=form_data.get("name"),
            slug=form_data.get("slug"),
            description=form_data.get("description"),
            primary_color=form_data.get("primary_color", "#3B82F6"),
            secondary_color=form_data.get("secondary_color", "#1E40AF"),
            features={
                "enable_bookings": form_data.get("enable_bookings") == "on",
                "enable_chat": form_data.get("enable_chat") == "on", 
                "enable_donations": form_data.get("enable_donations") == "on"
            }
        )
        
        club = await ClubService.create_club(db, club_data)
        
        # Redirect to the new club dashboard
        return templates.TemplateResponse("admin_create_club.html", {
            "request": request,
            "success": True,
            "club": {
                "name": club.name,
                "slug": club.slug,
                "url": f"/club/{club.slug}"
            }
        })
        
    except ValueError as e:
        return templates.TemplateResponse("admin_create_club.html", {
            "request": request,
            "error": str(e)
        })
    except Exception as e:
        return templates.TemplateResponse("admin_create_club.html", {
            "request": request,
            "error": f"Failed to create club: {str(e)}"
        })

@router.get("/clubs/{club_slug}", response_class=HTMLResponse)
async def admin_club_details(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Admin detailed view of a specific club"""
    club = await ClubService.get_club_by_slug(db, club_slug)
    
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    analytics = await ClubService.get_club_analytics(db, club)
    recent_members = await ClubService.get_recent_members(db, club, 10)
    recent_bookings = await ClubService.get_recent_bookings(db, club, 10)
    
    return templates.TemplateResponse("admin_club_details.html", {
        "request": request,
        "club": club,
        "analytics": analytics,
        "recent_members": recent_members,
        "recent_bookings": recent_bookings
    })

@router.get("/clubs/{club_slug}/edit", response_class=HTMLResponse)
async def admin_edit_club_form(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Admin form to edit a club"""
    club = await ClubService.get_club_by_slug(db, club_slug)
    
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    return templates.TemplateResponse("admin_edit_club.html", {
        "request": request,
        "club": club
    })

@router.post("/clubs/{club_slug}/delete")
async def admin_delete_club(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Admin endpoint to delete a club"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        await ClubService.delete_club(db, club)
        
        # Redirect back to clubs list with success message
        clubs = await ClubService.get_all_clubs(db, skip=0, limit=100)
        clubs_data = []
        for c in clubs:
            analytics = await ClubService.get_club_analytics(db, c)
            clubs_data.append({
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "total_members": analytics["total_members"],
                "total_revenue": analytics["total_revenue"],
                "subscription_status": c.subscription_status,
                "subscription_plan": c.subscription_plan,
                "created_at": c.created_at.strftime("%B %d, %Y")
            })
        
        return templates.TemplateResponse("admin_clubs.html", {
            "request": request,
            "clubs": clubs_data,
            "success": f"Club '{club.name}' has been deleted successfully."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete club: {str(e)}")

@router.get("/users", response_class=HTMLResponse)
async def admin_users_list(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Admin page to list all platform users"""
    # TODO: Implement user management
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": []  # TODO: Get actual users
    })

@router.get("/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Admin analytics dashboard"""
    clubs = await ClubService.get_all_clubs(db, skip=0, limit=100)
    
    # Calculate platform-wide analytics
    total_clubs = len(clubs)
    total_members = 0
    total_revenue = 0
    
    for club in clubs:
        analytics = await ClubService.get_club_analytics(db, club)
        total_members += analytics["total_members"]
        total_revenue += analytics["total_revenue"]
    
    return templates.TemplateResponse("admin_analytics.html", {
        "request": request,
        "total_clubs": total_clubs,
        "total_members": total_members,
        "total_revenue": total_revenue,
        "clubs": clubs
    })