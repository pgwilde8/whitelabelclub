# app/db/crud_platform_users.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import PlatformUser
from typing import Optional
import uuid


async def set_connect_account(
    db: AsyncSession, user_id: uuid.UUID, acct_id: str, dashboard_type: str | None = None
):
    """Set Stripe Connect account for a platform user"""
    await db.execute(
        update(PlatformUser)
        .where(PlatformUser.id == user_id)
        .values(
            stripe_account_id=acct_id,
            connect_dashboard_type=dashboard_type
        )
    )
    await db.commit()


async def get_user_by_stripe_account(db: AsyncSession, acct_id: str) -> Optional[PlatformUser]:
    """Get platform user by their Stripe Connect account ID"""
    result = await db.execute(
        select(PlatformUser).where(PlatformUser.stripe_account_id == acct_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[PlatformUser]:
    """Get platform user by ID"""
    result = await db.execute(
        select(PlatformUser).where(PlatformUser.id == user_id)
    )
    return result.scalar_one_or_none()


async def update_connect_status(
    db: AsyncSession,
    acct_id: str,
    *,
    charges_enabled: bool | None = None,
    details_submitted: bool | None = None,
    country: str | None = None,
    default_currency: str | None = None,
):
    """Update Stripe Connect status for a user by their account ID"""
    values = {}
    if charges_enabled is not None:
        values["charges_enabled"] = charges_enabled
    if details_submitted is not None:
        values["details_submitted"] = details_submitted
    if country is not None:
        values["country"] = country
    if default_currency is not None:
        values["default_currency"] = default_currency

    if values:
        await db.execute(
            update(PlatformUser)
            .where(PlatformUser.stripe_account_id == acct_id)
            .values(**values)
        )
        await db.commit()


async def get_connect_ready_users(db: AsyncSession) -> list[PlatformUser]:
    """Get all platform users who are ready to process payments (charges enabled + details submitted)"""
    result = await db.execute(
        select(PlatformUser).where(
            PlatformUser.charges_enabled == True,
            PlatformUser.details_submitted == True
        )
    )
    return result.scalars().all()
