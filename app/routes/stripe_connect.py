from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import stripe
from pydantic import BaseModel
from urllib.parse import urlencode
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.stripe_config import (
    stripe_client,
    STRIPE_CONNECT_CLIENT_ID,
    STRIPE_CONNECT_REDIRECT_URI,
)
from app.db.session import get_db_session
from app.db.crud_platform_users import set_connect_account, get_user_by_stripe_account

router = APIRouter(prefix="/stripe", tags=["stripe-connect"])

# --------- Express (recommended) ---------
class CreateExpressAccountIn(BaseModel):
    display_name: str
    owner_email: str
    country: str = "US"
    user_id: str  # Platform user ID who owns this account

@router.post("/connect/express/accounts")
async def create_express_account(body: CreateExpressAccountIn, db: AsyncSession = Depends(get_db_session)):
    try:
        acct = stripe_client.accounts.create({
            "dashboard": "express",
            "defaults": {
                "responsibilities": {
                    "losses_collector": "application",
                    "fees_collector": "application",
                }
            },
            "display_name": body.display_name,
            "contact_email": body.owner_email,
            "identity": {"country": body.country.lower()},
            "configuration": {
                "merchant": {"capabilities": {"card_payments": {"requested": True}}},
            },
        })
        
        # Save account to platform user
        user_id = uuid.UUID(body.user_id)
        await set_connect_account(db, user_id, acct["id"], "express")
        
        return {"account_id": acct["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/connect/express/accounts/{account_id}/onboard")
def create_account_onboarding_link(account_id: str):
    try:
        link = stripe_client.account_links.create({
            "account": account_id,
            "type": "account_onboarding",
            "refresh_url": "https://ezclub.app/stripe-setup/callback?stripe_return=error",
            "return_url": "https://ezclub.app/stripe-setup/callback?stripe_return=success",
        })
        return {"url": link["url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------- Standard (OAuth) ---------
@router.get("/connect/oauth/start")
def connect_oauth_start(state: Optional[str] = None):
    params = {
        "response_type": "code",
        "client_id": STRIPE_CONNECT_CLIENT_ID,
        "scope": "read_write",
        "redirect_uri": STRIPE_CONNECT_REDIRECT_URI,
    }
    if state:
        params["state"] = state
    url = "https://connect.stripe.com/oauth/authorize?" + urlencode(params)
    return {"authorize_url": url}

@router.get("/connect/oauth/callback")
async def connect_oauth_callback(
    code: Optional[str] = None, 
    error: Optional[str] = None, 
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not state:
        raise HTTPException(status_code=400, detail="Missing state parameter (user_id)")
        
    try:
        resp = stripe.OAuth.token(grant_type="authorization_code", code=code)
        account_id = resp["stripe_user_id"]  # e.g., acct_xxx
        
        # Save account to platform user (state should contain user_id)
        user_id = uuid.UUID(state)
        await set_connect_account(db, user_id, account_id, "standard")
        
        return {"connected_account_id": account_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
