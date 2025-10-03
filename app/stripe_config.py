import os
from dotenv import load_dotenv
import stripe
from stripe import StripeClient

load_dotenv()  # loads .env at project root

STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET")

# Only needed if you also support Standard (OAuth)
STRIPE_CONNECT_CLIENT_ID = os.getenv("STRIPE_CONNECT_CLIENT_ID")
STRIPE_CONNECT_REDIRECT_URI = os.getenv("STRIPE_CONNECT_REDIRECT_URI")

# v1 endpoints use global stripe
stripe.api_key = STRIPE_SECRET_KEY

# v2 endpoints use a client instance
stripe_client = StripeClient(STRIPE_SECRET_KEY)
