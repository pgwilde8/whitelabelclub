from fastapi import APIRouter, HTTPException, Request, Depends
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.stripe_config import STRIPE_WEBHOOK_SECRET, STRIPE_CONNECT_WEBHOOK_SECRET
from app.db.session import get_db_session
from app.db.crud_platform_users import update_connect_status, get_user_by_stripe_account
from app.models.club import Club
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["stripe-webhooks"])

@router.post("/stripe")
async def webhooks_core(request: Request, db: AsyncSession = Depends(get_db_session)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    et = event["type"]
    data = event["data"]["object"]

    if et == "checkout.session.completed":
        # mode: payment|subscription
        # payment_intent or subscription present accordingly
        # TODO: mark order active; map to owner via your DB
        pass

    if et == "invoice.payment_succeeded":
        # TODO: extend access for subscriber
        pass

    return {"received": True}

@router.post("/stripe/connect")
async def webhooks_connect(request: Request, db: AsyncSession = Depends(get_db_session)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    
    logger.info(f"Received Connect webhook. Signature present: {sig is not None}")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_CONNECT_WEBHOOK_SECRET)
        logger.info(f"Webhook validated successfully. Event type: {event.get('type')}")
    except Exception as e:
        logger.error(f"Webhook signature validation failed: {str(e)}")
        logger.error(f"Signature: {sig}")
        logger.error(f"Secret being used: {STRIPE_CONNECT_WEBHOOK_SECRET[:10]}...")
        raise HTTPException(status_code=400, detail=str(e))

    account = event.get("account")  # acct_...
    et = event["type"]
    data = event["data"]["object"]

    if et == "account.updated":
        # Update Connect status for the owner (platform_users table)
        charges_enabled = data.get("charges_enabled")
        details_submitted = data.get("details_submitted")
        
        # Sometimes country/currency are nested; adapt if your payload differs:
        country = data.get("country")
        default_currency = data.get("default_currency")
        
        await update_connect_status(
            db,
            account,
            charges_enabled=charges_enabled,
            details_submitted=details_submitted,
            country=country,
            default_currency=default_currency,
        )
        
        # Also update club if this account is linked to a club
        if account and details_submitted:
            result = await db.execute(
                select(Club).where(Club.stripe_account_id == account)
            )
            club = result.scalar_one_or_none()
            if club:
                club.stripe_onboarding_complete = True
                await db.commit()
                
                # Send beta welcome email to beta testers (only once)
                if club.account_type == "lifetime_free" and not club.welcome_email_sent:
                    logger.info(f"Club {club.slug} is a beta tester, preparing to send welcome email...")
                    
                    from app.services.email_service import EmailService
                    from sqlalchemy import func
                    
                    if not club.owner_email:
                        logger.warning(f"Cannot send welcome email to {club.slug} - no owner_email set")
                    else:
                        # Count beta testers to get their number
                        count_result = await db.execute(
                            select(func.count(Club.id)).where(Club.account_type == "lifetime_free")
                        )
                        beta_number = count_result.scalar() or 1
                        
                        logger.info(f"Sending beta welcome email to {club.owner_email} (Beta Tester #{beta_number})...")
                        
                        # Send welcome email
                        email_sent = EmailService.send_beta_welcome_email(
                            club_name=club.name,
                            club_slug=club.slug,
                            owner_email=club.owner_email,
                            beta_number=beta_number
                        )
                        
                        if email_sent:
                            from datetime import datetime
                            club.welcome_email_sent = True
                            club.welcome_email_sent_at = datetime.utcnow()
                            await db.commit()
                            logger.info(f"✅ Beta welcome email sent successfully to {club.owner_email} for club {club.slug}")
                        else:
                            logger.error(f"❌ Failed to send beta welcome email to {club.owner_email}")

    if et == "application_fee.created":
        # Your platform fee recorded
        pass

    if et in ("payment_intent.succeeded", "charge.succeeded"):
        # Sales on/for the connected account
        pass

    return {"received": True}
