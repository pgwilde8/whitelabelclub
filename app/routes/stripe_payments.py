from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe

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
