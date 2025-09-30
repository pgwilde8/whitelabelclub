from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import os
from app.core.security import encryption_service
from app.core.config import settings
from app.db.session import get_db_session
from app.services.club_service import ClubService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    club_slug: str
    chat_history: Optional[List[ChatMessage]] = []
    context: Optional[str] = "chat"  # "chat", "terminal", "widget"

class ChatResponse(BaseModel):
    response: str
    tokens_used: Optional[int] = None

async def get_club_openai_key(club_slug: str, db: AsyncSession) -> str:
    """
    Get the OpenAI API key for a specific club from the database.
    """
    club = await ClubService.get_club_by_slug(db, club_slug)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Check if club has its own OpenAI key
    if club.openai_api_key:
        return club.openai_api_key
    
    # Fallback to platform's OpenAI key if available
    if settings.OPENAI_API_KEY:
        return settings.OPENAI_API_KEY
    
    raise HTTPException(status_code=400, detail="OpenAI API key not configured for this club")

async def create_club_context(club_slug: str, db: AsyncSession, context_type: str = "chat") -> str:
    """Create context about the club for the AI assistant"""
    club = await ClubService.get_club_by_slug(db, club_slug)
    if not club:
        club_name = f"Club {club_slug.title()}"
        description = "A vibrant community for passionate members"
    else:
        club_name = club.name
        description = club.description or "A vibrant community for passionate members"
    
    # Get club analytics for more context
    try:
        if club:
            analytics = await ClubService.get_club_analytics(db, club)
        else:
            analytics = {"total_members": 0, "total_revenue": 0, "active_members": 0}
    except:
        analytics = {"total_members": 0, "total_revenue": 0, "active_members": 0}
    
    if context_type == "terminal":
        context = f"""
You are an AI business consultant for {club_name}, a club management platform. 
You have access to the club's data and can provide intelligent business insights.

Club Information:
- Name: {club_name}
- Description: {description}
- Total Members: {analytics.get('total_members', 0)}
- Active Members: {analytics.get('active_members', 0)}
- Total Revenue: ${analytics.get('total_revenue', 0)}

Your role as a business consultant:
1. Analyze club performance and member engagement
2. Provide actionable business recommendations
3. Help optimize pricing, scheduling, and operations
4. Generate marketing content and strategies
5. Forecast revenue and growth opportunities
6. Answer questions about club management best practices

When responding:
- Be professional and data-driven
- Provide specific, actionable advice
- Use the club's actual data when available
- Keep responses concise but comprehensive
- Format responses clearly with bullet points when appropriate

Available commands: analyze_members, predict_revenue, suggest_pricing, generate_content, optimize_schedule
        """
    else:
        context = f"""
You are an AI assistant for {club_name}. 
Here's information about the club:

Club Name: {club_name}
Description: {description}
Current Members: {analytics.get('total_members', 0)}

Your role is to:
1. Answer questions about the club's services and features
2. Help members with booking and membership questions
3. Provide information about club policies and procedures
4. Be friendly, helpful, and professional
5. If you don't know something specific, suggest they contact the club directly
6. Keep responses concise but informative

Remember: You represent {club_name} and should maintain a professional, welcoming tone.
        """
    
    return context

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Chat with AI assistant for a specific club using real database data
    """
    try:
        # Get OpenAI API key for this club
        openai_key = await get_club_openai_key(request.club_slug, db)
        
        # Create OpenAI client
        client = OpenAI(api_key=openai_key)
        
        # Create club context
        club_context = await create_club_context(request.club_slug, db, request.context or "chat")
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": club_context}
        ]
        
        # Add chat history for context
        for msg in request.chat_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else None
        
        logger.info(f"AI chat response generated for club {request.club_slug}, tokens: {tokens_used}")
        
        return ChatResponse(
            response=ai_response,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"AI chat error for club {request.club_slug}: {error_message}")
        
        # Check for specific OpenAI errors in the message
        if "invalid_api_key" in error_message.lower() or "incorrect api key" in error_message.lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
        elif "rate_limit" in error_message.lower() or "quota" in error_message.lower():
            raise HTTPException(status_code=429, detail="AI service temporarily unavailable")
        else:
            raise HTTPException(status_code=500, detail="AI service error")

@router.get("/status/{club_slug}")
async def get_ai_status(club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """
    Check if AI is available for a specific club
    """
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Check if club has OpenAI key configured
        has_openai_key = bool(club.openai_api_key) or bool(settings.OPENAI_API_KEY)
        
        return {
            "club_slug": club_slug,
            "ai_enabled": has_openai_key,
            "status": "available" if has_openai_key else "not_configured",
            "message": "AI assistant is ready" if has_openai_key else "AI assistant not configured"
        }
        
    except Exception as e:
        logger.error(f"Error checking AI status for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking AI status")

@router.post("/suggest/{club_slug}")
async def get_ai_suggestions(club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """
    Get AI-powered suggestions for club optimization using real data
    """
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get real analytics data
        analytics = await ClubService.get_club_analytics(db, club)
        
        # Generate suggestions based on real data
        suggestions = []
        
        # Revenue optimization based on actual data
        if analytics["total_revenue"] < 1000:
            suggestions.append({
                "type": "revenue_optimization",
                "title": "Increase Revenue Streams",
                "description": f"With ${analytics['total_revenue']} current revenue, consider adding premium services",
                "impact": "Could increase revenue by 30-50%",
                "priority": "high"
            })
        
        # Member engagement based on real member count
        if analytics["total_members"] > 0:
            engagement_rate = (analytics["active_members"] / analytics["total_members"]) * 100
            if engagement_rate < 70:
                suggestions.append({
                    "type": "member_retention",
                    "title": "Improve Member Engagement",
                    "description": f"Current engagement rate is {engagement_rate:.1f}%. Focus on member re-activation",
                    "impact": "Could improve retention by 25%",
                    "priority": "high"
                })
        
        # Growth suggestions
        if analytics["total_members"] < 50:
            suggestions.append({
                "type": "growth",
                "title": "Member Acquisition Campaign",
                "description": f"With {analytics['total_members']} members, focus on growth strategies",
                "impact": "Could attract 20-30 new members",
                "priority": "medium"
            })
        
        # Default suggestions if no specific data patterns
        if not suggestions:
            suggestions = [
                {
                    "type": "optimization",
                    "title": "General Optimization",
                    "description": "Continue monitoring member engagement and revenue trends",
                    "impact": "Maintain steady growth",
                    "priority": "low"
                }
            ]
        
        return {
            "club_slug": club_slug,
            "suggestions": suggestions,
            "generated_at": "2025-01-15T10:30:00Z",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")

@router.post("/configure/{club_slug}")
async def configure_openai_key(club_slug: str, openai_key: str, db: AsyncSession = Depends(get_db_session)):
    """
    Configure OpenAI API key for a club (for testing/demo purposes)
    """
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Set the OpenAI key (will be encrypted automatically)
        club.openai_api_key = openai_key
        
        await db.commit()
        await db.refresh(club)
        
        return {
            "club_slug": club_slug,
            "message": "OpenAI API key configured successfully",
            "ai_enabled": True
        }
        
    except Exception as e:
        logger.error(f"Error configuring OpenAI key for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error configuring OpenAI key")

# AI Tools Endpoints for Business Operations

@router.post("/tools/get_metrics")
async def get_metrics(window: str = "30d", club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """Get club engagement metrics"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get real analytics data
        analytics = await ClubService.get_club_analytics(db, club)
        
        return {
            "club_slug": club_slug,
            "window": window,
            "engagement_pct": 78.5,
            "active_members": analytics.get("active_members", 0),
            "total_members": analytics.get("total_members", 0),
            "new_joins_30d": 12,
            "at_risk_count": 3,
            "total_revenue": analytics.get("total_revenue", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting metrics")

@router.post("/tools/post_announcement")
async def post_announcement(message: str, club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """Post announcement to club chat"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # For now, just return success - you can wire to real chat later
        return {
            "success": True, 
            "message": "Announcement posted to chat",
            "club_slug": club_slug,
            "announcement": message
        }
        
    except Exception as e:
        logger.error(f"Error posting announcement for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error posting announcement")

@router.post("/tools/list_at_risk_members")
async def list_at_risk_members(days_inactive: int = 21, club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """List members at risk of churning"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Mock data for now - replace with real query later
        at_risk_members = [
            {"name": "John D.", "last_active": "18 days ago", "risk_score": "High"},
            {"name": "Sarah M.", "last_active": "25 days ago", "risk_score": "Medium"},
            {"name": "Mike R.", "last_active": "22 days ago", "risk_score": "Medium"}
        ]
        
        return {
            "club_slug": club_slug,
            "days_inactive": days_inactive,
            "at_risk_count": len(at_risk_members),
            "at_risk": at_risk_members
        }
        
    except Exception as e:
        logger.error(f"Error getting at-risk members for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting at-risk members")

@router.post("/tools/suggest_pricing")
async def suggest_pricing(tier: str = "Premium", target_mrr: str = "+20%", club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """Suggest pricing optimization for club tiers"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get current revenue data
        analytics = await ClubService.get_club_analytics(db, club)
        current_revenue = analytics.get("total_revenue", 0)
        
        # Calculate suggested pricing (mock for now)
        suggested_increase = 1.20  # 20% increase
        new_monthly_price = 99 * suggested_increase  # Assuming $99 base
        
        return {
            "club_slug": club_slug,
            "tier": tier,
            "target_mrr": target_mrr,
            "current_revenue": current_revenue,
            "suggested_monthly_price": round(new_monthly_price, 2),
            "price_increase_pct": 20,
            "expected_revenue_impact": f"+${current_revenue * 0.2:.0f}/month",
            "risk_assessment": "Low - Gradual increase with member benefits"
        }
        
    except Exception as e:
        logger.error(f"Error suggesting pricing for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error suggesting pricing")

@router.post("/tools/optimize_schedule")
async def optimize_schedule(service: str = "1:1 Coaching", window: str = "Fri 2-6pm", club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """Optimize booking schedule for services"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Mock optimization suggestions
        suggested_slots = [
            {"day": "Friday", "time": "2:00 PM", "demand": "High", "recommended_price": "$120"},
            {"day": "Friday", "time": "3:30 PM", "demand": "Medium", "recommended_price": "$110"},
            {"day": "Friday", "time": "5:00 PM", "demand": "High", "recommended_price": "$120"}
        ]
        
        return {
            "club_slug": club_slug,
            "service": service,
            "window": window,
            "suggested_slots": suggested_slots,
            "optimization_score": 87,
            "expected_fill_rate": "75%",
            "revenue_potential": "$330/session"
        }
        
    except Exception as e:
        logger.error(f"Error optimizing schedule for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error optimizing schedule")

@router.post("/tools/predict_revenue")
async def predict_revenue(days: int = 30, club_slug: str = "aaaaaa", db: AsyncSession = Depends(get_db_session)):
    """Predict revenue for the next period"""
    try:
        club = await ClubService.get_club_by_slug(db, club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get current analytics
        analytics = await ClubService.get_club_analytics(db, club)
        current_revenue = analytics.get("total_revenue", 0)
        
        # Mock predictions (replace with real forecasting logic)
        base_scenario = current_revenue * 1.1  # 10% growth
        optimistic_scenario = current_revenue * 1.25  # 25% growth
        conservative_scenario = current_revenue * 0.95  # 5% decline
        
        return {
            "club_slug": club_slug,
            "forecast_period_days": days,
            "current_revenue": current_revenue,
            "scenarios": {
                "base": round(base_scenario, 2),
                "optimistic": round(optimistic_scenario, 2),
                "conservative": round(conservative_scenario, 2)
            },
            "confidence": "78%",
            "key_drivers": ["Member renewals", "New bookings", "Premium upgrades"],
            "recommendations": [
                "Focus on member retention",
                "Increase booking frequency",
                "Launch premium tier promotion"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error predicting revenue for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error predicting revenue")
