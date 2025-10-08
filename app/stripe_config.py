import os
from pathlib import Path
from dotenv import load_dotenv
import stripe
from stripe import StripeClient

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Determine which Stripe mode to use (test or live)
STRIPE_MODE = os.getenv("STRIPE_MODE", "test").lower()  # Default to test mode

# Load appropriate keys based on mode
if STRIPE_MODE == "live":
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY_LIVE")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY_LIVE")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET_LIVE")
    STRIPE_CONNECT_CLIENT_ID = os.getenv("STRIPE_CONNECT_CLIENT_ID_LIVE")
    STRIPE_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET_LIVE")
    STRIPE_CONNECT_REDIRECT_URI = os.getenv("STRIPE_CONNECT_REDIRECT_URI_LIVE") or os.getenv("STRIPE_CONNECT_REDIRECT_URI")
    print(f"🔴 STRIPE MODE: LIVE - Using production keys")
else:
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY_TEST")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY_TEST")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET_TEST")
    STRIPE_CONNECT_CLIENT_ID = os.getenv("STRIPE_CONNECT_CLIENT_ID_TEST")
    STRIPE_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET_TEST")
    STRIPE_CONNECT_REDIRECT_URI = os.getenv("STRIPE_CONNECT_REDIRECT_URI_TEST") or os.getenv("STRIPE_CONNECT_REDIRECT_URI")
    print(f"🟢 STRIPE MODE: TEST - Using test keys")

# v1 endpoints use global stripe
stripe.api_key = STRIPE_SECRET_KEY

# v2 endpoints use a client instance
stripe_client = StripeClient(STRIPE_SECRET_KEY)
