from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/contact", tags=["contact"])

class ContactSubmission(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    subject: str
    message: str
    newsletter: bool = False

@router.post("/submit")
async def submit_contact_form(data: ContactSubmission):
    """Handle contact form submission and send email"""
    try:
        # Format full name
        full_name = f"{data.firstName} {data.lastName}".strip()
        
        # Send email via Brevo
        email_sent = EmailService.send_contact_form_email(
            name=full_name,
            email=data.email,
            subject=data.subject,
            message=data.message
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email. Please try again later."
            )
        
        logger.info(f"Contact form submitted by {data.email} - Subject: {data.subject}")
        
        return {
            "success": True,
            "message": "Your message has been sent successfully! We'll get back to you within 24 hours."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request."
        )

