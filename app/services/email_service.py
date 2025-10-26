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
                    <div style="background: linear-gradient(135deg, #0075c4 0%, #0267C1 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">
                            🚀 New Contact Form Submission
                        </h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #0075c4; margin-top: 0;">Contact Details</h2>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold; width: 120px;">Name:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Email:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                                    <a href="mailto:{email}" style="color: #0075c4;">{email}</a>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Subject:</td>
                                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{subject}</td>
                            </tr>
                        </table>
                        
                        <h3 style="color: #0075c4; margin-top: 30px; margin-bottom: 15px;">Message:</h3>
                        <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #0075c4;">
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
    
    @staticmethod
    def send_beta_welcome_email(
        club_name: str,
        club_slug: str,
        owner_email: str,
        beta_number: int
    ) -> bool:
        """Send welcome email to beta testers after Stripe onboarding"""
        
        if not settings.BREVO_API_KEY:
            logger.error("BREVO_API_KEY not configured")
            return False
        
        try:
            # Dashboard and booking URLs
            dashboard_url = f"https://ezclub.app/community/{club_slug}"
            booking_url = f"https://ezclub.app/community/{club_slug}/book"
            
            # Brevo API endpoint
            url = "https://api.brevo.com/v3/smtp/email"
            
            # Email HTML template
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #0075c4 0%, #0267C1 100%); padding: 40px 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: #f8f9fa; padding: 30px; }}
                    .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #0075c4; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                    .steps {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .step {{ padding: 15px; margin: 10px 0; background: #e3f2fd; border-radius: 6px; }}
                    .btn {{ display: inline-block; padding: 15px 30px; background: #0075c4; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px 5px; }}
                    .benefits {{ background: #d1f2eb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: white; margin: 0; font-size: 32px;">🎉 Welcome to EZCLUB Beta!</h1>
                        <p style="color: rgba(255,255,255,0.9); font-size: 18px; margin: 10px 0 0 0;">
                            You're Beta Tester #{beta_number} of 10
                        </p>
                    </div>
                    
                    <div class="content">
                        <p style="font-size: 18px; margin-top: 0;">
                            Hi there! 👋
                        </p>
                        
                        <p>
                            <strong>Congratulations!</strong> You're officially part of the EZCLUB Beta Program. 
                            Thank you for being an early supporter of <strong>{club_name}</strong>!
                        </p>
                        
                        <div class="warning">
                            <h3 style="margin-top: 0; color: #856404;">
                                🧪 IMPORTANT: You're in TEST Mode
                            </h3>
                            <p style="margin-bottom: 0; color: #856404;">
                                During beta, we're using Stripe's test mode for safety:<br>
                                • <strong>No real money</strong> will be processed<br>
                                • Use test card: <strong>4242 4242 4242 4242</strong><br>
                                • Test bank accounts are provided by Stripe<br><br>
                                When we launch (4-6 weeks), you'll connect your real bank account. 
                                Your <strong>lifetime free access stays active!</strong> 🌟
                            </p>
                        </div>
                        
                        <div class="section">
                            <h2 style="color: #0075c4; margin-top: 0;">🚀 Quick Start Guide (5 minutes)</h2>
                            
                            <div class="steps">
                                <div class="step">
                                    <strong>1️⃣ Visit Your Dashboard</strong><br>
                                    <a href="{dashboard_url}" style="color: #0075c4;">{dashboard_url}</a>
                                </div>
                                
                                <div class="step">
                                    <strong>2️⃣ Create a Service</strong><br>
                                    Add a service like "Personal Training - $50" or "Monthly Membership - $30"
                                </div>
                                
                                <div class="step">
                                    <strong>3️⃣ Share Your Booking Page</strong><br>
                                    <a href="{booking_url}" style="color: #0075c4;">{booking_url}</a>
                                </div>
                                
                                <div class="step">
                                    <strong>4️⃣ Test a Booking</strong><br>
                                    Use test card: <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">4242 4242 4242 4242</code><br>
                                    Any future date for expiry, any 3-digit CVC
                                </div>
                                
                                <div class="step">
                                    <strong>5️⃣ Check Your Dashboard</strong><br>
                                    See the payment appear and check the 3% commission split!
                                </div>
                            </div>
                            
                            <div style="text-align: center; margin-top: 20px;">
                                <a href="{dashboard_url}" class="btn">Open My Dashboard →</a>
                            </div>
                        </div>
                        
                        <div class="section">
                            <h2 style="color: #0075c4; margin-top: 0;">❤️ What We Need From You</h2>
                            <ul style="line-height: 2;">
                                <li><strong>15 minutes of testing</strong> - Try the core features</li>
                                <li><strong>One bug report OR feature request</strong> - What's broken? What's missing?</li>
                                <li><strong>Honest feedback</strong> - What's confusing? What do you love?</li>
                            </ul>
                        </div>
                        
                        <div class="section">
                            <h2 style="color: #0075c4; margin-top: 0;">🐛 Found a Bug? Have Feedback?</h2>
                            <p>
                                <strong>Just reply to this email!</strong> I personally read every message and respond within 24 hours.
                            </p>
                            <p>
                                You can also:<br>
                                • Email: <a href="mailto:support@ezclub.app">support@ezclub.app</a><br>
                                • Use the feedback button in your dashboard
                            </p>
                        </div>
                        
                        <div class="benefits">
                            <h2 style="color: #0a9396; margin-top: 0;">🎁 Your Beta Tester Benefits</h2>
                            <ul style="margin: 0; line-height: 2;">
                                <li>✓ <strong>Lifetime free account</strong> (forever!)</li>
                                <li>✓ <strong>Priority support</strong> (direct access to founder)</li>
                                <li>✓ <strong>Your feature requests built first</strong></li>
                                <li>✓ <strong>Founding member badge</strong></li>
                                <li>✓ <strong>Early access</strong> to all new features</li>
                            </ul>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                            <p style="font-size: 18px; margin-bottom: 20px;">
                                <strong>Ready to explore?</strong>
                            </p>
                            <a href="{dashboard_url}" class="btn" style="font-size: 18px;">
                                🚀 Launch My Club/Membership Site
                            </a>
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            Thanks for being part of the EZCLUB journey! 🙌<br>
                            <strong>- The EZCLUB Team</strong>
                        </p>
                        
                        <p style="font-size: 12px; color: #666; text-align: center; margin-top: 20px;">
                            P.S. Want to see how the 3% platform fee works? Check your dashboard after 
                            a test booking - you'll see the commission split in action!
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>&copy; 2025 EZCLUB.APP. All rights reserved.</p>
                        <p style="margin-top: 10px;">
                            <a href="https://ezclub.app" style="color: #0075c4;">ezclub.app</a> • 
                            <a href="mailto:support@ezclub.app" style="color: #0075c4;">support@ezclub.app</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
🎉 Welcome to EZCLUB Beta!

You're Beta Tester #{beta_number} of 10

Hi there!

Congratulations! You're officially part of the EZCLUB Beta Program. 
Thank you for being an early supporter of {club_name}!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 IMPORTANT: You're in TEST Mode

During beta, we're using Stripe's test mode for safety:
• No real money will be processed
• Use test card: 4242 4242 4242 4242
• Test bank accounts are provided by Stripe

When we launch (4-6 weeks), you'll connect your real bank account.
Your lifetime free access stays active! 🌟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Quick Start Guide (5 minutes):

1. Visit Your Dashboard
   {dashboard_url}

2. Create a Service
   Add a service like "Personal Training - $50"

3. Share Your Booking Page
   {booking_url}

4. Test a Booking
   Use test card: 4242 4242 4242 4242
   Any future date, any CVC

5. Check Your Dashboard
   See the payment and 3% commission split!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❤️ What We Need From You:

• 15 minutes of testing
• One bug report OR feature request
• Honest feedback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 Found a Bug? Have Feedback?

Just reply to this email! I personally read every message.

Or email: support@ezclub.app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 Your Beta Tester Benefits:

✓ Lifetime free account (forever!)
✓ Priority support
✓ Your feature requests built first
✓ Founding member badge
✓ Early access to new features

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thanks for being part of the EZCLUB journey!

- The EZCLUB Team

P.S. Want to see the 3% commission? Check your dashboard 
after a test booking!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

© 2025 EZCLUB.APP
https://ezclub.app • support@ezclub.app
            """
            
            # Brevo email payload
            payload = {
                "sender": {
                    "name": "EZCLUB Team",
                    "email": settings.EMAIL_FROM
                },
                "to": [
                    {
                        "email": owner_email,
                        "name": club_name
                    }
                ],
                "replyTo": {
                    "email": settings.EMAIL_SUPPORT,
                    "name": "EZCLUB Support"
                },
                "subject": f"🎉 Welcome to EZCLUB Beta! You're Tester #{beta_number}",
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
                logger.info(f"Beta welcome email sent successfully to {owner_email}")
                return True
            else:
                logger.error(f"Brevo API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send beta welcome email: {str(e)}")
            return False

