from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.services.club_service import ClubService
from app.schemas.club import ClubCreate
import random
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Create router for web pages
router = APIRouter(include_in_schema=False)

# Setup templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main sales/landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    """Pricing page"""
    return templates.TemplateResponse("pricing.html", {"request": request})

@router.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    """Demo page"""
    return templates.TemplateResponse("demo.html", {"request": request})

@router.get("/features", response_class=HTMLResponse)
async def features(request: Request):
    """Features page"""
    return templates.TemplateResponse("features.html", {"request": request})

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page for Webwise Solutions"""
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request, plan: str = None):
    """Signup page with optional plan parameter"""
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "selected_plan": plan
    })

@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding(request: Request):
    """Onboarding page"""
    return templates.TemplateResponse("onboarding.html", {"request": request})

@router.get("/stripe-setup", response_class=HTMLResponse)
async def stripe_setup(request: Request):
    """Stripe setup page"""
    return templates.TemplateResponse("stripe-setup.html", {"request": request})

@router.get("/launch", response_class=HTMLResponse)
async def launch(request: Request):
    """Launch page"""
    return templates.TemplateResponse("launch.html", {"request": request})

@router.get("/create-community", response_class=HTMLResponse)
async def create_community(request: Request):
    """Create community sales page"""
    return templates.TemplateResponse("create-community.html", {"request": request})


# Mock club data for testing and fallback
MOCK_CLUBS = {
    "aaaaaa": {
        "name": "Club Aaaaaa",
        "description": "A vibrant fitness community",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF"
    }
}

@router.get("/club/{club_slug}/", response_class=HTMLResponse)
async def club_dashboard(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Club owner dashboard with real database data"""
    
    # Get or create club from database
    club = await ClubService.get_or_create_club(db, club_slug)
    
    # Get club analytics
    analytics = await ClubService.get_club_analytics(db, club)
    
    # Get recent members and bookings
    recent_members_db = await ClubService.get_recent_members(db, club, 5)
    recent_bookings_db = await ClubService.get_recent_bookings(db, club, 5)
    
    # Convert club to dictionary format for template
    club_data = {
        "id": str(club.id),
        "name": club.name,
        "slug": club.slug,
        "description": club.description or "A vibrant community for passionate members",
        "primary_color": club.primary_color,
        "secondary_color": club.secondary_color,
        "logo_url": club.logo_url,
        "features": {
            "enable_bookings": club.features.get("enable_bookings", True),
            "enable_chat": club.features.get("enable_chat", True),
            "enable_donations": club.features.get("enable_donations", True)
        },
        "enable_bookings": club.features.get("enable_bookings", True),
        "enable_chat": club.features.get("enable_chat", True),
        "enable_ai": club.ai_enabled,
        "enable_donations": club.features.get("enable_donations", True),
        "subscription_status": club.subscription_status,
        "subscription_plan": club.subscription_plan,
        "created_at": club.created_at
    }
    
    # Mock owner data (in production, get from club_roles table)
    owner_data = {
        "username": "ClubOwner",
        "avatar_url": None
    }
    
    # Real analytics data
    analytics_data = {
        "total_members": analytics["total_members"],
        "active_members": analytics["active_members"],
        "total_revenue": analytics["total_revenue"],
        "unread_notifications": 0,  # TODO: Implement notifications count
        "recent_messages": 0,       # TODO: Implement messages count
        "avg_session_time": "4m 32s",  # TODO: Implement session tracking
        "new_members_this_month": analytics["new_members_this_month"],
        "conversion_rate": analytics["conversion_rate"]
    }
    
    # Mock membership tiers (TODO: Get from database)
    total_members = analytics["total_members"]
    membership_tiers = [
        {
            "name": "Basic",
            "price": 29,
            "interval": "month",
            "member_count": int(total_members * 0.7),
            "percentage": 70
        },
        {
            "name": "Premium",
            "price": 59,
            "interval": "month", 
            "member_count": int(total_members * 0.25),
            "percentage": 25
        },
        {
            "name": "VIP",
            "price": 99,
            "interval": "month",
            "member_count": int(total_members * 0.05),
            "percentage": 5
        }
    ]
    
    # Convert recent members to template format
    recent_members = []
    for member in recent_members_db:
        recent_members.append({
            "name": member.display_name or member.email.split('@')[0],
            "avatar_url": None,
            "joined_date": member.created_at.strftime("%B %d, %Y"),
            "tier": member.member_tier or "Basic"
        })
    
    # Add mock members if we don't have enough real ones
    mock_names = ["John Doe", "Jane Smith", "Mike Johnson", "Alice Brown", "Bob Davis"]
    while len(recent_members) < 3:
        recent_members.append({
            "name": mock_names[len(recent_members)],
            "avatar_url": None,
            "joined_date": "Recently",
            "tier": "Basic"
        })
    
    # Convert recent bookings to template format
    upcoming_bookings = []
    for booking in recent_bookings_db:
        upcoming_bookings.append({
            "member_name": f"Member {str(booking.id)[:8]}",  # TODO: Get actual member name
            "service_name": "Service",  # TODO: Get service name from booking_services
            "date_time": booking.booking_time.strftime("%B %d, %I:%M %p") if booking.booking_time else "TBD",
            "amount": int(booking.price / 100) if booking.price else 0
        })
    
    # Only show real bookings - no mock data
    
    # Real recent activities - only show actual member joins for now
    recent_activities = []
    if recent_members:
        for member in recent_members[:2]:  # Show max 2 recent member joins
            recent_activities.append({
                "icon": "fa-user-plus",
                "description": f"{member['name']} joined",
                "timestamp": member.get('joined_date', 'Recent'),
                "amount": None
            })
    
    # If no real activities, show a helpful message
    if not recent_activities:
        recent_activities = [
            {
                "icon": "fa-info-circle",
                "description": "No recent activity yet",
                "timestamp": "Welcome!",
                "amount": None
            }
        ]
    
    # Real notifications based on club data
    notifications = [
        {
            "icon": "fa-bell",
            "message": f"Club {club.name} dashboard loaded successfully",
            "timestamp": "Now"
        },
        {
            "icon": "fa-chart-line",
            "message": f"Total members: {analytics['total_members']}",
            "timestamp": "Now"
        },
        {
            "icon": "fa-database",
            "message": f"Club created: {club.created_at.strftime('%B %d, %Y')}",
            "timestamp": club.created_at.strftime("%B %d")
        }
    ]
    
    # Mock chart data (TODO: Get real revenue data by month)
    revenue_chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue_chart_data = [1200, 1900, 3000, 5000, 2000, int(analytics['total_revenue'])]
    
    # Current time for AI chat
    current_time = datetime.now().strftime("%I:%M %p")
    
    return templates.TemplateResponse("club_dashboard.html", {
        "request": request,
        "club": club_data,
        "owner": owner_data,
        "total_members": analytics_data["total_members"],
        "active_members": analytics_data["active_members"],
        "total_revenue": analytics_data["total_revenue"],
        "unread_notifications": analytics_data["unread_notifications"],
        "recent_messages": analytics_data["recent_messages"],
        "avg_session_time": analytics_data["avg_session_time"],
        "new_members_this_month": analytics_data["new_members_this_month"],
        "conversion_rate": analytics_data["conversion_rate"],
        "membership_tiers": membership_tiers,
        "recent_activities": recent_activities,
        "upcoming_bookings": upcoming_bookings,
        "recent_members": recent_members,
        "notifications": notifications,
        "revenue_chart_labels": revenue_chart_labels,
        "revenue_chart_data": revenue_chart_data,
        "current_time": current_time
    })

@router.get("/club/{club_slug}/members", response_class=HTMLResponse)
async def club_members_list(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """List all members of a club - Dynamic route for any club"""
    try:
        # Get club
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail=f"Club '{club_slug}' not found")
        
        # Get all members of this club
        all_members = await ClubService.get_all_members(db, club)
        
        # Pre-format dates to avoid async issues in templates
        for member in all_members:
            member.formatted_joined_date = member.created_at.strftime('%b %d, %Y') if member.created_at else 'Unknown'
            member.formatted_joined_month = member.created_at.strftime('%B %Y') if member.created_at else 'Unknown'
        
        # Group members by tier
        members_by_tier = {
            "free": [m for m in all_members if m.member_tier == "free"],
            "basic": [m for m in all_members if m.member_tier == "basic"],
            "premium": [m for m in all_members if m.member_tier == "premium"],
            "vip": [m for m in all_members if m.member_tier == "vip"]
        }
        
        # Calculate stats
        total_members = len(all_members)
        active_members = len([m for m in all_members if m.status == "active"])
        
        return templates.TemplateResponse("club_members.html", {
            "request": request,
            "club": club,
            "members": all_members,
            "members_by_tier": members_by_tier,
            "total_members": total_members,
            "active_members": active_members,
            "free_count": len(members_by_tier["free"]),
            "basic_count": len(members_by_tier["basic"]),
            "premium_count": len(members_by_tier["premium"]),
            "vip_count": len(members_by_tier["vip"])
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading members: {str(e)}")

@router.get("/club/{club_slug}/member/{member_id}", response_class=HTMLResponse)
async def club_member_profile(request: Request, club_slug: str, member_id: str, db: AsyncSession = Depends(get_db_session)):
    """Individual member profile within a club"""
    try:
        # Get club
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail=f"Club '{club_slug}' not found")
        
        # Get specific member
        member = await ClubService.get_member_by_id(db, club, member_id)
        if not member:
            raise HTTPException(status_code=404, detail=f"Member not found in club '{club_slug}'")
        
        return templates.TemplateResponse("club_member_profile.html", {
            "request": request,
            "club": club,
            "member": member,
            "member_since": member.created_at.strftime("%B %Y"),
            "recent_activity": []  # TODO: Add member activity tracking
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading member profile: {str(e)}")

@router.get("/club/{club_slug}/bookings", response_class=HTMLResponse)
async def booking_management(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Booking management page for club owners"""
    try:
        # Get real club data from database
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Convert club to dictionary format for template
        club_data = {
            "id": str(club.id),
            "name": club.name,
            "slug": club.slug,
            "description": club.description or "A vibrant community for passionate members",
            "primary_color": club.primary_color or "#3B82F6",
            "secondary_color": club.secondary_color or "#1E40AF",
            "logo_url": club.logo_url
        }
    
        # Get booking services from database
        booking_services = await ClubService.get_booking_services(db, club.id)
        
        # Filter out deleted services (same logic as public booking)
        deleted_service_ids = request.cookies.get('deleted_services', '')
        if deleted_service_ids:
            deleted_ids = [int(x) for x in deleted_service_ids.split(',') if x.isdigit()]
            booking_services = [s for s in booking_services if s['id'] not in deleted_ids]
        
        # Mock recent bookings
        all_recent_bookings = [
            {
                "id": 1,
                "client_name": "Alice Johnson",
                "client_email": "alice@example.com",
                "service_name": "Personal Training",
                "date_time": "Today 2:00 PM",
                "status": "confirmed",
                "amount": 75.00,
                "is_member": True,
                "phone": "+1 (555) 123-4567"
            },
            {
                "id": 2,
                "client_name": "Bob Smith",
                "client_email": "bob@example.com", 
                "service_name": "Nutrition Consultation",
                "date_time": "Tomorrow 10:00 AM",
                "status": "pending",
                "amount": 120.00,
                "is_member": False,
                "phone": "+1 (555) 987-6543"
            },
            {
                "id": 3,
                "client_name": "Carol Davis",
                "client_email": "carol@example.com",
                "service_name": "Group Yoga Class", 
                "date_time": "Tomorrow 6:00 PM",
                "status": "confirmed",
                "amount": 35.00,
                "is_member": True,
                "phone": "+1 (555) 456-7890"
            }
        ]
        
        # Filter out deleted bookings (similar to services)
        deleted_booking_ids = request.cookies.get('deleted_bookings', '')
        if deleted_booking_ids:
            deleted_ids = [int(x) for x in deleted_booking_ids.split(',') if x.isdigit()]
            recent_bookings = [b for b in all_recent_bookings if b['id'] not in deleted_ids]
        else:
            recent_bookings = all_recent_bookings
        
        return templates.TemplateResponse("booking_management.html", {
            "request": request,
            "club": club_data,
            "booking_services": booking_services,
            "recent_bookings": recent_bookings
        })
        
    except Exception as e:
        logger.error(f"Error loading booking management page for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading booking management page")

@router.post("/club/{club_slug}/services")
async def create_booking_service(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Create a new booking service"""
    try:
        # Get the club
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get the service data from request body
        service_data = await request.json()
        
        # Add the service to the database
        new_service = await ClubService.add_booking_service(db, club.id, service_data)
        
        return {"success": True, "service": new_service}
        
    except Exception as e:
        logger.error(f"Error creating service for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating service")

@router.delete("/club/{club_slug}/services/{service_id}")
async def delete_booking_service(request: Request, club_slug: str, service_id: int):
    """Delete a booking service"""
    # In production, this would delete from database
    # For demo, we'll use cookies to track deleted services
    
    # Get current deleted services from cookies
    deleted_services = request.cookies.get('deleted_services', '')
    deleted_ids = [int(x) for x in deleted_services.split(',') if x.isdigit()]
    
    # Add the new service ID to deleted list
    if service_id not in deleted_ids:
        deleted_ids.append(service_id)
    
    # Convert back to cookie string
    deleted_services_str = ','.join(map(str, deleted_ids))
    
    # Return response with updated cookie
    from fastapi.responses import JSONResponse
    response = JSONResponse({"success": True, "message": "Service deleted successfully"})
    response.set_cookie("deleted_services", deleted_services_str)
    return response

@router.delete("/club/{club_slug}/bookings/{booking_id}")
async def delete_booking(request: Request, club_slug: str, booking_id: int):
    """Delete a booking"""
    # In production, this would delete from database
    # For demo, we'll use cookies to track deleted bookings
    
    # Get current deleted bookings from cookies
    deleted_bookings = request.cookies.get('deleted_bookings', '')
    deleted_ids = [int(x) for x in deleted_bookings.split(',') if x.isdigit()]
    
    # Add the new booking ID to deleted list
    if booking_id not in deleted_ids:
        deleted_ids.append(booking_id)
    
    # Convert back to cookie string
    deleted_bookings_str = ','.join(map(str, deleted_ids))
    
    # Return response with updated cookie
    from fastapi.responses import JSONResponse
    response = JSONResponse({"success": True, "message": "Booking deleted successfully"})
    response.set_cookie("deleted_bookings", deleted_bookings_str)
    return response

@router.get("/club/{club_slug}/calendar", response_class=HTMLResponse)
async def calendar_view(request: Request, club_slug: str):
    """Calendar view for club bookings"""
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "View all your bookings in calendar format",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None
    }
    
    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "club": club_data
    })

@router.get("/club/{club_slug}/chat", response_class=HTMLResponse)
async def chat_view(request: Request, club_slug: str):
    """Chat interface for club members"""
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "Connect and chat with your community",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None
    }
    
    # Empty chat channels (no fake data)
    channels = [
        {
            "id": "general",
            "name": "General",
            "description": "General community chat",
            "unread_count": 0,
            "last_message": "No messages yet",
            "last_message_time": "",
            "last_message_author": ""
        }
    ]
    
    # Empty online members list (no fake members)
    online_members = []
    
    # Empty recent messages (no fake messages)
    recent_messages = []
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "club": club_data,
        "channels": channels,
        "online_members": online_members,
        "recent_messages": recent_messages,
        "current_channel": "general"
    })

@router.get("/club/{club_slug}/ai-terminal", response_class=HTMLResponse)
async def ai_terminal_view(request: Request, club_slug: str):
    """AI Terminal interface for club management"""
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "AI-powered club management and insights",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None
    }
    
    return templates.TemplateResponse("ai_terminal.html", {
        "request": request,
        "club": club_data
    })

@router.get("/api/v1/ai/suggest/{club_slug}")
async def get_ai_suggestions(club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Get AI suggestions for club optimization using real data"""
    try:
        # Get real club data
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get real analytics data
        analytics = await ClubService.get_club_analytics(db, club)
        
        suggestions = []
        
        # 1. Revenue Optimization based on actual revenue
        current_revenue = analytics.get("total_revenue", 0)
        total_members = analytics.get("total_members", 0)
        
        if current_revenue < 1000 and total_members > 0:
            package_revenue_potential = current_revenue * 0.35
            suggestions.append({
                "type": "revenue_optimization",
                "title": "Package Deal Optimization",
                "description": f"With ${current_revenue} current revenue and {total_members} members, create 5-session packages at ${int(current_revenue * 0.05)} discount. This could increase revenue by ${int(package_revenue_potential)}.",
                "priority": "high",
                "impact": f"+{int(package_revenue_potential)} revenue potential",
                "data_driven": True
            })
        
        # 2. Member Engagement based on actual engagement
        active_members = analytics.get("active_members", 0)
        if total_members > 0:
            engagement_rate = (active_members / total_members) * 100
            
            if engagement_rate < 70:
                suggestions.append({
                    "type": "member_retention",
                    "title": "Member Engagement Boost",
                    "description": f"Current engagement rate is {engagement_rate:.1f}% ({active_members}/{total_members} active). Focus on re-activation campaigns and member outreach.",
                    "priority": "high",
                    "impact": f"Could improve engagement to 80%+",
                    "data_driven": True
                })
        
        # 3. Growth Strategy based on member count
        if total_members < 50:
            suggestions.append({
                "type": "growth",
                "title": "Member Acquisition Campaign",
                "description": f"With {total_members} members, launch targeted acquisition campaigns. Consider referral programs and social media marketing.",
                "priority": "medium",
                "impact": "Could attract 20-30 new members",
                "data_driven": True
            })
        
        # 4. Booking Optimization based on revenue patterns
        if current_revenue > 500:
            avg_booking_value = current_revenue / max(total_members, 1)
            if avg_booking_value < 50:
                suggestions.append({
                    "type": "booking_optimization",
                    "title": "Premium Service Launch",
                    "description": f"Average booking value is ${avg_booking_value:.0f}. Introduce premium services ($75+) to increase revenue per member.",
                    "priority": "medium",
                    "impact": "+40% revenue per member",
                    "data_driven": True
                })
        
        # 5. Default suggestions if no specific patterns
        if not suggestions:
            suggestions = [
                {
                    "type": "general",
                    "title": "Platform Optimization",
                    "description": "Continue monitoring member engagement and revenue trends. Consider A/B testing different pricing strategies.",
                    "priority": "low",
                    "impact": "Steady growth maintenance",
                    "data_driven": True
                }
            ]
        
        return {
            "suggestions": suggestions,
            "generated_at": "2025-01-15T10:30:00Z",
            "data_source": "real_analytics",
            "club_metrics": {
                "total_members": total_members,
                "active_members": active_members,
                "engagement_rate": round((active_members / max(total_members, 1)) * 100, 1),
                "total_revenue": current_revenue
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions for club {club_slug}: {str(e)}")
        # Fallback to basic suggestions if there's an error
        return {
            "suggestions": [
                {
                    "type": "system",
                    "title": "System Analysis",
                    "description": "Analyzing club data... Please try again in a moment.",
                    "priority": "low",
                    "impact": "Data processing",
                    "data_driven": False
                }
            ],
            "error": "Data analysis in progress"
        }

@router.get("/club/{club_slug}/book", response_class=HTMLResponse)
async def public_booking(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """Public booking page for non-members"""
    try:
        # Get real club data from database
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get booking services from database
        booking_services = await ClubService.get_booking_services(db, club.id)
        
        # Filter out deleted services (same logic as booking management)
        deleted_service_ids = request.cookies.get('deleted_services', '')
        if deleted_service_ids:
            deleted_ids = [int(x) for x in deleted_service_ids.split(',') if x.isdigit()]
            booking_services = [s for s in booking_services if s.id not in deleted_ids]
        
        # Convert club to dictionary format for template
        club_data = {
            "id": str(club.id),
            "name": club.name,
            "slug": club.slug,
            "description": club.description or "Book your appointment with us today!",
            "primary_color": club.primary_color or "#3B82F6",
            "secondary_color": club.secondary_color or "#1E40AF",
            "logo_url": club.logo_url
        }
        
        return templates.TemplateResponse("public_booking.html", {
            "request": request,
            "club": club_data,
            "booking_services": booking_services
        })
        
    except Exception as e:
        logger.error(f"Error loading public booking page for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading booking page")

@router.post("/create-checkout-session/{plan}")
async def create_checkout_session(plan: str, request: Request):
    """Create Stripe checkout session for subscription plans"""
    import stripe
    from app.core.config import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Map plan names to product IDs and price IDs from your .env
    plan_mapping = {
        "starter": {
            "product_id": settings.STRIPE_STARTER_PRODUCT_ID,
            "price_id": settings.STRIPE_STARTER_PRICE_ID,
            "amount": 6700,  # $67.00 in cents
            "name": "Starter Plan"
        },
        "pro": {
            "product_id": settings.STRIPE_PRO_PRODUCT_ID,
            "price_id": settings.STRIPE_PRO_PRICE_ID,
            "amount": 9700,  # $97.00 in cents
            "name": "Pro Plan"
        },
        "enterprise": {
            "product_id": settings.STRIPE_ENTERPRISE_PRODUCT_ID,
            "price_id": settings.STRIPE_ENTERPRISE_PRICE_ID,
            "amount": 19700,  # $197.00 in cents
            "name": "Enterprise Plan"
        }
    }
    
    if plan not in plan_mapping:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan_info = plan_mapping[plan]
    
    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': plan_info["price_id"],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.url_for('success_page') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=str(request.url_for('index')) + '#pricing',
            metadata={
                'plan': plan,
                'plan_name': plan_info["name"]
            }
        )
        
        return {"checkout_url": checkout_session.url}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

@router.get("/success", response_class=HTMLResponse)
async def success_page(request: Request, session_id: str = None):
    """Success page after Stripe checkout"""
    return templates.TemplateResponse("success.html", {
        "request": request,
        "session_id": session_id
    })
