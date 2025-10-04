from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.db.crud_platform_users import get_user_by_stripe_account
from app.services.club_service import ClubService

router = APIRouter(prefix="/stripe", tags=["stripe-payments"])

class OneTimeCheckoutIn(BaseModel):
    price_id: str
    connected_account_id: str
    fee_cents: int = 200  # your cut, e.g. $2.00

@router.post("/checkout/one-time")
def create_one_time_checkout(body: OneTimeCheckoutIn):
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": body.price_id, "quantity": 1}],
            payment_intent_data={
                "application_fee_amount": body.fee_cents,
                "transfer_data": {"destination": body.connected_account_id},
            },
            success_url="https://example.com/success?sid={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={"site": "ezplatform"},
        )
        return {"id": session["id"], "url": session["url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------- Service Booking Payments ---------
class ServiceCheckoutIn(BaseModel):
    club_slug: str
    service_id: int
    service_name: str
    price_cents: int
    customer_email: str
    customer_name: str
    booking_datetime: str
    notes: str = ""
    metadata: dict = {}

@router.post("/checkout/service")
async def create_service_checkout(body: ServiceCheckoutIn, db: AsyncSession = Depends(get_db_session)):
    """Create Stripe checkout session for service booking"""
    try:
        # Get the club and its owner's Stripe account
        club = await ClubService.get_club_by_slug(db, body.club_slug)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        
        # Get the club owner's Stripe account ID
        if not club.stripe_account_id:
            raise HTTPException(status_code=400, detail="Club owner has not connected their Stripe account yet")
        
        connected_account_id = club.stripe_account_id
        
        # Calculate platform fee (3% of service price)
        platform_fee_cents = int(body.price_cents * 0.03)  # 3% platform fee
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': body.service_name,
                        'description': f'Service booking for {body.club_slug}'
                    },
                    'unit_amount': body.price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=body.customer_email,
            payment_intent_data={
                'application_fee_amount': platform_fee_cents,
                'transfer_data': {'destination': connected_account_id},
                'metadata': {
                    'club_slug': body.club_slug,
                    'service_id': str(body.service_id),
                    'booking_datetime': body.booking_datetime,
                    'customer_name': body.customer_name,
                    'notes': body.notes,
                    **body.metadata
                }
            },
            success_url=f"https://ezclub.app/booking/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://ezclub.app/club/{body.club_slug}/book",
            metadata={
                'club_slug': body.club_slug,
                'service_id': str(body.service_id),
                'booking_datetime': body.booking_datetime,
                'customer_name': body.customer_name,
                'notes': body.notes
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id,
            "platform_fee_cents": platform_fee_cents,
            "club_owner_receives_cents": body.price_cents - platform_fee_cents
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SubscriptionCheckoutIn(BaseModel):
    price_id: str
    connected_account_id: str
    fee_percent: float = 3.0  # your cut in percent

@router.post("/checkout/subscription")
def create_subscription_checkout(body: SubscriptionCheckoutIn):
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": body.price_id, "quantity": 1}],
            subscription_data={
                "application_fee_percent": body.fee_percent,
                "transfer_data": {"destination": body.connected_account_id},
            },
            success_url="https://example.com/sub-success?sid={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/sub-cancel",
            metadata={"site": "ezplatform"},
        )
        return {"id": session["id"], "url": session["url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
