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
    # For now, we'll use a simple in-memory list that can be modified
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
    
    # Filter out deleted services (in production, this would query the database)
    # For demo purposes, we'll use a simple approach
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
    
    # Mock chat channels
    channels = [
        {
            "id": "general",
            "name": "General",
            "description": "General community chat",
            "unread_count": 5,
            "last_message": "Hey everyone! How's the new booking system working?",
            "last_message_time": "2 min ago",
            "last_message_author": "John"
        },
        {
            "id": "announcements",
            "name": "Announcements",
            "description": "Important club updates",
            "unread_count": 2,
            "last_message": "New booking system is live! Check it out.",
            "last_message_time": "1 hour ago",
            "last_message_author": "ClubOwner"
        },
        {
            "id": "events",
            "name": "Events",
            "description": "Event discussions and planning",
            "unread_count": 3,
            "last_message": "Who's coming to the weekend workshop?",
            "last_message_time": "30 min ago",
            "last_message_author": "Jane"
        },
        {
            "id": "help",
            "name": "Help & Support",
            "description": "Get help and support",
            "unread_count": 1,
            "last_message": "How do I cancel my booking?",
            "last_message_time": "15 min ago",
            "last_message_author": "Mike"
        },
        {
            "id": "introductions",
            "name": "Introductions",
            "description": "Welcome new members",
            "unread_count": 1,
            "last_message": "Hi everyone! New to the club.",
            "last_message_time": "45 min ago",
            "last_message_author": "Sarah"
        }
    ]
    
    # Mock online members
    online_members = [
        {"id": 1, "name": "John", "status": "online", "avatar": None},
        {"id": 2, "name": "Jane", "status": "online", "avatar": None},
        {"id": 3, "name": "Mike", "status": "away", "avatar": None},
        {"id": 4, "name": "Sarah", "status": "online", "avatar": None},
        {"id": 5, "name": "ClubOwner", "status": "online", "avatar": None}
    ]
    
    # Mock recent messages for general channel
    recent_messages = [
        {
            "id": 1,
            "author": "John",
            "author_id": 1,
            "content": "Hey everyone! How's the new booking system working?",
            "timestamp": "2025-01-27T19:25:00Z",
            "time_display": "2 min ago",
            "is_owner": False
        },
        {
            "id": 2,
            "author": "Jane",
            "author_id": 2,
            "content": "It's great! Just booked my personal training session.",
            "timestamp": "2025-01-27T19:26:00Z",
            "time_display": "1 min ago",
            "is_owner": False
        },
        {
            "id": 3,
            "author": "Mike",
            "author_id": 3,
            "content": "Same here! Much easier than before.",
            "timestamp": "2025-01-27T19:27:00Z",
            "time_display": "now",
            "is_owner": False
        }
    ]
    
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
async def get_ai_suggestions(club_slug: str):
    """Get AI suggestions for club optimization"""
    # Mock AI suggestions - in production, this would use real AI analysis
    suggestions = [
        {
            "type": "revenue_optimization",
            "title": "Package Deal Optimization",
            "description": "Create 5-session personal training packages at $425 (save $25). This could increase booking frequency by 35% and improve member retention.",
            "priority": "high",
            "impact": "+15% revenue potential"
        },
        {
            "type": "member_retention",
            "title": "Peak Hour Expansion",
            "description": "Add more evening classes (6-8 PM) when member activity is highest. Current utilization shows 89% capacity during these hours.",
            "priority": "medium",
            "impact": "+20% class attendance"
        }
    ]
    
    return {"suggestions": suggestions}

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
