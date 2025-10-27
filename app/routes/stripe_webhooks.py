from fastapi import APIRouter, HTTPException, Request, Depends
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.stripe_config import STRIPE_WEBHOOK_SECRET, STRIPE_CONNECT_WEBHOOK_SECRET
from app.db.session import get_db_session
from app.db.crud_platform_users import update_connect_status, get_user_by_stripe_account
from app.models.club import Club
from app.models.payment import Payment
from decimal import Decimal
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
        # One-time payment or subscription checkout completed
        session_id = data.get("id")
        payment_intent_id = data.get("payment_intent")
        payment_status = data.get("payment_status")
        amount_total = data.get("amount_total")  # in cents
        metadata = data.get("metadata", {})
        
        logger.info(f"Checkout session completed: {session_id}, status: {payment_status}, amount: {amount_total}")
        
        # Extract club info from metadata
        club_slug = metadata.get("club_slug")
        
        if club_slug and payment_status == "paid" and amount_total:
            # Look up the club
            result = await db.execute(
                select(Club).where(Club.slug == club_slug)
            )
            club = result.scalar_one_or_none()
            
            if club:
                # Create payment record
                payment = Payment(
                    club_id=club.id,
                    amount=Decimal(amount_total) / 100,  # Convert cents to dollars
                    currency="usd",
                    payment_type="booking",
                    stripe_payment_intent_id=payment_intent_id,
                    stripe_customer_id=data.get("customer"),
                    status="succeeded",
                    platform_fee_amount=Decimal(0),  # Will be updated if we have fee info
                    club_earnings=Decimal(amount_total) / 100
                )
                db.add(payment)
                await db.commit()
                logger.info(f"✅ Payment recorded: ${payment.amount} for club {club.slug}")
            else:
                logger.warning(f"Club not found for slug: {club_slug}")

    if et == "invoice.payment_succeeded":
        # Recurring subscription payment succeeded
        invoice_id = data.get("id")
        amount_paid = data.get("amount_paid")  # in cents
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        
        logger.info(f"Invoice payment succeeded: {invoice_id}, amount: {amount_paid}")
        # TODO: extend access for subscriber, record payment

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
        fee_amount = data.get("amount")  # in cents
        charge_id = data.get("charge")
        logger.info(f"💰 Platform fee created: ${fee_amount / 100} for charge {charge_id}")

    if et in ("payment_intent.succeeded", "charge.succeeded"):
        # Sales on/for the connected account
        logger.info(f"Payment event received: {et}")
        
        # Extract payment details
        payment_id = data.get("id")
        amount = data.get("amount")  # in cents
        currency = data.get("currency", "usd")
        metadata = data.get("metadata", {})
        
        # For charge.succeeded, get the payment_intent if available
        payment_intent_id = data.get("payment_intent") if et == "charge.succeeded" else payment_id
        
        logger.info(f"Payment amount: ${amount / 100}, currency: {currency}, metadata: {metadata}")
        
        # Extract club info from metadata
        club_slug = metadata.get("club_slug")
        
        if club_slug and amount and account:
            # Look up the club by Stripe account ID
            result = await db.execute(
                select(Club).where(Club.stripe_account_id == account)
            )
            club = result.scalar_one_or_none()
            
            if club:
                # Check if payment already exists (avoid duplicates from multiple events)
                existing_payment = await db.execute(
                    select(Payment).where(
                        Payment.stripe_payment_intent_id == payment_intent_id
                    )
                )
                if existing_payment.scalar_one_or_none():
                    logger.info(f"Payment {payment_intent_id} already recorded, skipping")
                else:
                    # Calculate platform fee and club earnings
                    # Get application fee if available
                    application_fee = data.get("application_fee_amount", 0)
                    platform_fee = Decimal(application_fee) / 100 if application_fee else Decimal(0)
                    total_amount = Decimal(amount) / 100
                    club_earnings = total_amount - platform_fee
                    
                    # Create payment record
                    payment = Payment(
                        club_id=club.id,
                        amount=total_amount,
                        currency=currency,
                        payment_type=metadata.get("payment_type", "booking"),
                        stripe_payment_intent_id=payment_intent_id,
                        stripe_charge_id=data.get("id") if et == "charge.succeeded" else None,
                        stripe_customer_id=data.get("customer"),
                        status="succeeded",
                        platform_fee_amount=platform_fee,
                        club_earnings=club_earnings
                    )
                    db.add(payment)
                    await db.commit()
                    logger.info(f"✅ Payment recorded: ${total_amount} for club {club.slug} (club gets ${club_earnings}, platform fee ${platform_fee})")
            else:
                logger.warning(f"Club not found for Stripe account: {account}")
        else:
            logger.warning(f"Missing data: club_slug={club_slug}, amount={amount}, account={account}")

    return {"received": True}
