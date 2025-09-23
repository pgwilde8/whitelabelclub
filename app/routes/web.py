from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
    """About page"""
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
async def signup(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

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

@router.get("/club/{club_slug}/", response_class=HTMLResponse)
async def club_dashboard(request: Request, club_slug: str):
    """Club owner dashboard"""
    # In a real implementation, this would fetch data from the database
    # For now, we'll create mock data based on the club slug
    
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "A vibrant community for passionate members",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None,
        "enable_bookings": True,
        "enable_chat": True,
        "enable_ai": False,
        "enable_donations": True
    }
    
    # Mock owner data
    owner_data = {
        "username": "ClubOwner",
        "avatar_url": None
    }
    
    # Mock analytics data
    analytics_data = {
        "total_members": 1247,
        "active_members": 892,
        "total_revenue": 15420,
        "unread_notifications": 3,
        "recent_messages": 12,
        "avg_session_time": "4m 32s",
        "new_members_this_month": 47,
        "conversion_rate": 23.4
    }
    
    # Mock membership tiers
    membership_tiers = [
        {
            "name": "Basic",
            "price": 29,
            "interval": "month",
            "member_count": 856,
            "percentage": 68
        },
        {
            "name": "Premium",
            "price": 59,
            "interval": "month", 
            "member_count": 312,
            "percentage": 25
        },
        {
            "name": "VIP",
            "price": 99,
            "interval": "month",
            "member_count": 79,
            "percentage": 7
        }
    ]
    
    # Mock recent activities
    recent_activities = [
        {
            "icon": "fa-user-plus",
            "description": "New member John Doe joined",
            "timestamp": "2 minutes ago",
            "amount": None
        },
        {
            "icon": "fa-credit-card",
            "description": "Payment received from Jane Smith",
            "timestamp": "15 minutes ago",
            "amount": 59
        },
        {
            "icon": "fa-calendar-check",
            "description": "Booking confirmed for Mike Johnson",
            "timestamp": "1 hour ago",
            "amount": 85
        },
        {
            "icon": "fa-heart",
            "description": "Donation received from Sarah Wilson",
            "timestamp": "2 hours ago",
            "amount": 25
        }
    ]
    
    # Mock upcoming bookings
    upcoming_bookings = [
        {
            "member_name": "Alice Brown",
            "service_name": "Personal Training",
            "date_time": "Today 2:00 PM",
            "amount": 75
        },
        {
            "member_name": "Bob Davis",
            "service_name": "Nutrition Consultation",
            "date_time": "Tomorrow 10:00 AM",
            "amount": 120
        },
        {
            "member_name": "Carol Green",
            "service_name": "Group Class",
            "date_time": "Tomorrow 6:00 PM",
            "amount": 35
        }
    ]
    
    # Mock recent members
    recent_members = [
        {
            "name": "John Doe",
            "avatar_url": None,
            "joined_date": "2 hours ago",
            "tier": "Basic"
        },
        {
            "name": "Jane Smith",
            "avatar_url": None,
            "joined_date": "1 day ago",
            "tier": "Premium"
        },
        {
            "name": "Mike Johnson",
            "avatar_url": None,
            "joined_date": "2 days ago",
            "tier": "VIP"
        }
    ]
    
    # Mock notifications
    notifications = [
        {
            "icon": "fa-bell",
            "message": "New member subscription payment received",
            "timestamp": "5 minutes ago"
        },
        {
            "icon": "fa-calendar",
            "message": "Upcoming booking reminder",
            "timestamp": "1 hour ago"
        },
        {
            "icon": "fa-chart-line",
            "message": "Weekly analytics report ready",
            "timestamp": "3 hours ago"
        }
    ]
    
    # Mock chart data
    revenue_chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue_chart_data = [1200, 1900, 3000, 5000, 2000, 3000]
    
    # Current time for AI chat
    from datetime import datetime
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

@router.get("/club/{club_slug}/bookings", response_class=HTMLResponse)
async def booking_management(request: Request, club_slug: str):
    """Booking management page for club owners"""
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "A vibrant community for passionate members",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None
    }
    
    # Mock booking services - in production, this would come from database
    booking_services = [
        {
            "id": 1,
            "name": "Personal Training",
            "price": 75.00,
            "duration": 60,
            "description": "One-on-one personal training session",
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
            "description": "Comprehensive nutrition planning session",
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
            "description": "Relaxing yoga class for all levels",
            "bookings_count": 45,
            "revenue": 1575.00,
            "status": "active",
            "max_participants": 12,
            "allow_non_members": False
        }
    ]
    
    # Mock recent bookings
    recent_bookings = [
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
    
    return templates.TemplateResponse("booking_management.html", {
        "request": request,
        "club": club_data,
        "booking_services": booking_services,
        "recent_bookings": recent_bookings
    })

@router.get("/club/{club_slug}/book", response_class=HTMLResponse)
async def public_booking(request: Request, club_slug: str):
    """Public booking page for non-members"""
    # Mock club data
    club_data = {
        "name": f"Club {club_slug.title()}",
        "slug": club_slug,
        "description": "Book your appointment with us today!",
        "primary_color": "#3B82F6",
        "secondary_color": "#1E40AF",
        "logo_url": None
    }
    
    return templates.TemplateResponse("public_booking.html", {
        "request": request,
        "club": club_data
    })

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
            "price_id": "price_1SAavgRucl0nfsvSRSm6xfOt",  # From your .env comments
            "amount": 6700,  # $67.00 in cents
            "name": "Starter Plan"
        },
        "pro": {
            "product_id": settings.STRIPE_PRO_PRODUCT_ID,
            "price_id": "price_1SAavyRucl0nfsvScVAlRVXI",  # From your .env comments
            "amount": 9700,  # $97.00 in cents
            "name": "Pro Plan"
        },
        "enterprise": {
            "product_id": settings.STRIPE_ENTERPRISE_PRODUCT_ID,
            "price_id": "price_1SAawDRucl0nfsvS8L26yUCY",  # From your .env comments
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
