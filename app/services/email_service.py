import requests
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using Brevo API"""
    
    @staticmethod
    def send_contact_form_email(
        name: str,
        email: str,
        subject: str,
        message: str
    ) -> bool:
        """Send contact form submission email to support"""
        
        if not settings.BREVO_API_KEY:
            logger.error("BREVO_API_KEY not configured")
            return False
        
        try:
            # Brevo API endpoint
            url = "https://api.brevo.com/v3/smtp/email"
            
            # Email HTML template
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">
                            🚀 New Contact Form Submission
                        </h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #3B82F6; margin-top: 0;">Contact Details</h2>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; width: 120px;">Name:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Email:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                                    <a href="mailto:{email}" style="color: #3B82F6;">{email}</a>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Subject:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{subject}</td>
                            </tr>
                        </table>
                        
                        <h3 style="color: #3B82F6; margin-top: 30px; margin-bottom: 15px;">Message:</h3>
                        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #3B82F6;">
                            {message.replace(chr(10), '<br>')}
                        </div>
                        
                        <div style="margin-top: 30px; padding: 15px; background: #e3f2fd; border-radius: 8px;">
                            <p style="margin: 0; font-size: 14px; color: #666;">
                                <strong>💡 Quick Reply:</strong> Just hit reply to respond directly to {email}
                            </p>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px; text-align: center; color: #999; font-size: 12px;">
                        <p>Sent from EZCLUB.APP Contact Form</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            New Contact Form Submission
            
            Name: {name}
            Email: {email}
            Subject: {subject}
            
            Message:
            {message}
            
            ---
            Reply to this email to respond to {email}
            """
            
            # Brevo email payload
            payload = {
                "sender": {
                    "name": "EZCLUB Contact Form",
                    "email": settings.EMAIL_FROM
                },
                "to": [
                    {
                        "email": settings.EMAIL_SUPPORT,
                        "name": "EZCLUB Support"
                    }
                ],
                "replyTo": {
                    "email": email,
                    "name": name
                },
                "subject": f"[EZCLUB] Contact Form - {subject}",
                "htmlContent": html_content,
                "textContent": text_content
            }
            
            # Send via Brevo API
            headers = {
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 201:
                logger.info(f"Contact form email sent successfully to {settings.EMAIL_SUPPORT}")
                return True
            else:
                logger.error(f"Brevo API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send contact form email: {str(e)}")
            return False

