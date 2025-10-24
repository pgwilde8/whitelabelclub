from fastapi import APIRouter, HTTPException, Request, Depends
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.stripe_config import STRIPE_WEBHOOK_SECRET, STRIPE_CONNECT_WEBHOOK_SECRET
from app.db.session import get_db_session
from app.db.crud_platform_users import update_connect_status, get_user_by_stripe_account
from app.models.club import Club

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
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_CONNECT_WEBHOOK_SECRET)
    except Exception as e:
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

    if et == "application_fee.created":
        # Your platform fee recorded
        pass

    if et in ("payment_intent.succeeded", "charge.succeeded"):
        # Sales on/for the connected account
        pass

    return {"received": True}
