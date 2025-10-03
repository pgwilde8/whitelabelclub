# -*- coding: utf-8 -*-
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision = "791a0d35baa4"
down_revision = "3aa4f5c402ac"
branch_labels = None
depends_on = None


def upgrade():
    # --- platform_users: store each owner's Connect status/ids (guard against pre-existing columns) ---
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS stripe_account_id TEXT")
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS connect_dashboard_type TEXT")
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS charges_enabled BOOLEAN DEFAULT false NOT NULL")
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS details_submitted BOOLEAN DEFAULT false NOT NULL")
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS country TEXT")
    op.execute("ALTER TABLE platform_users ADD COLUMN IF NOT EXISTS default_currency TEXT")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_platform_users_stripe_account_id ON platform_users (stripe_account_id)")

    # --- clubs: guard against pre-existing columns/indexes ---
    op.execute("ALTER TABLE clubs ADD COLUMN IF NOT EXISTS stripe_account_id TEXT")
    op.execute("ALTER TABLE clubs ADD COLUMN IF NOT EXISTS payouts_enabled BOOLEAN DEFAULT false")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_clubs_stripe_account_id ON clubs (stripe_account_id)")

    # --- payments: enrich for reconciliation (guard against pre-existing columns) ---
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS site TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS mode TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS currency TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS connected_account_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS checkout_session_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS payment_intent_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS subscription_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS invoice_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS application_fee_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS application_fee_amount BIGINT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS application_fee_percent NUMERIC(5,2)")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS transfer_id TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS gross_amount BIGINT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS net_amount_to_owner BIGINT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS status TEXT")
    op.execute("ALTER TABLE payments ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb NOT NULL")

    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_checkout_session_id ON payments (checkout_session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_payment_intent_id ON payments (payment_intent_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_subscription_id ON payments (subscription_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_invoice_id ON payments (invoice_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payments_connected_account_id ON payments (connected_account_id)")

    # --- member_subscriptions: tie to Stripe subs (guard against pre-existing columns) ---
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT")
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT")
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS stripe_price_id TEXT")
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS status TEXT")
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMPTZ")
    op.execute("ALTER TABLE member_subscriptions ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT false NOT NULL")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_member_subscriptions_stripe_subscription_id ON member_subscriptions (stripe_subscription_id)")


def downgrade():
    # member_subscriptions (safe downgrades)
    op.execute("DROP INDEX IF EXISTS ix_member_subscriptions_stripe_subscription_id")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS cancel_at_period_end")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS current_period_end")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS stripe_price_id")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS stripe_customer_id")
    op.execute("ALTER TABLE member_subscriptions DROP COLUMN IF EXISTS stripe_subscription_id")

    # payments (safe downgrades)
    op.execute("DROP INDEX IF EXISTS ix_payments_connected_account_id")
    op.execute("DROP INDEX IF EXISTS ix_payments_invoice_id")
    op.execute("DROP INDEX IF EXISTS ix_payments_subscription_id")
    op.execute("DROP INDEX IF EXISTS ix_payments_payment_intent_id")
    op.execute("DROP INDEX IF EXISTS ix_payments_checkout_session_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS metadata")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS net_amount_to_owner")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS gross_amount")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS transfer_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS application_fee_percent")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS application_fee_amount")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS application_fee_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS invoice_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS subscription_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS payment_intent_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS checkout_session_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS connected_account_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS currency")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS mode")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS site")

    # clubs (safe downgrades)
    op.execute("DROP INDEX IF EXISTS ix_clubs_stripe_account_id")
    op.execute("ALTER TABLE clubs DROP COLUMN IF EXISTS payouts_enabled")
    # NOTE: we do NOT drop stripe_account_id unconditionally because it already existed on your DB.
    # If you really want to drop it when created by this migration only, we'd need a more complex check.
    # For safety, leave it in place:
    # op.execute("ALTER TABLE clubs DROP COLUMN IF EXISTS stripe_account_id")

    # platform_users (safe downgrades)
    op.execute("DROP INDEX IF EXISTS ix_platform_users_stripe_account_id")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS default_currency")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS country")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS details_submitted")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS charges_enabled")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS connect_dashboard_type")
    op.execute("ALTER TABLE platform_users DROP COLUMN IF EXISTS stripe_account_id")
