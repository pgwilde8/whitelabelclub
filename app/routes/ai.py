from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from app.core.security import encryption_service
from app.core.config import settings
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

class ChatResponse(BaseModel):
    response: str
    tokens_used: Optional[int] = None

# Mock club data - in production, this would come from database
MOCK_CLUBS = {
    "aaaaaa": {
        "name": "Club Aaaaaa",
        "description": "A vibrant fitness community",
        "services": ["Personal Training", "Group Classes", "Nutrition Consultation", "Yoga"],
        "hours": "Mon-Fri: 6AM-10PM, Sat-Sun: 8AM-8PM",
        "location": "123 Main St, City, State",
        "membership_tiers": ["Basic ($29/month)", "Premium ($59/month)", "VIP ($99/month)"],
        "features": ["24/7 Access", "Personal Training", "Group Classes", "Nutrition Support"],
        "openai_key": "sk-test-key-encrypted"  # This would be encrypted in real implementation
    }
}

def get_club_openai_key(club_slug: str) -> str:
    """
    Get the OpenAI API key for a specific club.
    In production, this would decrypt the key from the database.
    """
    club = MOCK_CLUBS.get(club_slug)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # In production, decrypt the stored key
    # encrypted_key = club.get('openai_key')
    # if not encrypted_key:
    #     raise HTTPException(status_code=400, detail="OpenAI API key not configured for this club")
    
    # decrypted_key = encryption_service.decrypt(encrypted_key)
    # return decrypted_key
    
    # For demo purposes, use the platform's OpenAI key
    return settings.OPENAI_API_KEY

def create_club_context(club_slug: str) -> str:
    """Create context about the club for the AI assistant"""
    club = MOCK_CLUBS.get(club_slug, {})
    
    context = f"""
You are an AI assistant for {club.get('name', 'this club')}. 
Here's information about the club:

Club Name: {club.get('name', 'Unknown')}
Description: {club.get('description', 'No description available')}

Services Offered:
{chr(10).join([f"- {service}" for service in club.get('services', [])])}

Operating Hours: {club.get('hours', 'Contact for hours')}
Location: {club.get('location', 'Contact for location')}

Membership Options:
{chr(10).join([f"- {tier}" for tier in club.get('membership_tiers', [])])}

Club Features:
{chr(10).join([f"- {feature}" for feature in club.get('features', [])])}

Your role is to:
1. Answer questions about the club's services, hours, location, and membership
2. Help members understand how to book services
3. Provide information about membership benefits
4. Be friendly, helpful, and professional
5. If you don't know something specific, suggest they contact the club directly
6. Keep responses concise but informative

Remember: You represent {club.get('name', 'this club')} and should maintain a professional, welcoming tone.
"""
    return context

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI assistant for a specific club
    """
    try:
        # Get OpenAI API key for this club
        openai_key = get_club_openai_key(request.club_slug)
        
        # Set OpenAI API key
        openai.api_key = openai_key
        
        # Create club context
        club_context = create_club_context(request.club_slug)
        
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
        
        logger.info(f"AI chat response generated for club {request.club_slug}, tokens: {tokens_used}")
        
        return ChatResponse(
            response=ai_response,
            tokens_used=tokens_used
        )
        
    except openai.error.AuthenticationError:
        logger.error(f"OpenAI authentication failed for club {request.club_slug}")
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
    
    except openai.error.RateLimitError:
        logger.error(f"OpenAI rate limit exceeded for club {request.club_slug}")
        raise HTTPException(status_code=429, detail="AI service temporarily unavailable")
    
    except openai.error.APIError as e:
        logger.error(f"OpenAI API error for club {request.club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="AI service error")
    
    except Exception as e:
        logger.error(f"Unexpected error in AI chat for club {request.club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{club_slug}")
async def get_ai_status(club_slug: str):
    """
    Check if AI is available for a specific club
    """
    try:
        club = MOCK_CLUBS.get(club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Check if club has OpenAI key configured
        has_openai_key = bool(club.get('openai_key'))
        
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
async def get_ai_suggestions(club_slug: str):
    """
    Get AI-powered suggestions for club optimization
    """
    try:
        club = MOCK_CLUBS.get(club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Mock AI suggestions - in production, this would use actual data analysis
        suggestions = [
            {
                "type": "revenue_optimization",
                "title": "Peak Hour Analysis",
                "description": "Consider adding more classes during 6-8 PM when member activity is highest",
                "impact": "Could increase revenue by 15-20%",
                "priority": "high"
            },
            {
                "type": "member_retention",
                "title": "New Member Onboarding",
                "description": "Implement a 7-day welcome series for new members",
                "impact": "Could improve retention by 25%",
                "priority": "medium"
            },
            {
                "type": "service_expansion",
                "title": "Popular Service Addition",
                "description": "Members frequently ask about yoga classes - consider adding more sessions",
                "impact": "Could attract 30+ new members",
                "priority": "high"
            }
        ]
        
        return {
            "club_slug": club_slug,
            "suggestions": suggestions,
            "generated_at": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating AI suggestions for club {club_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")
