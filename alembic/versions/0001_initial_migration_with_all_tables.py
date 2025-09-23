"""Initial migration with all tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clubs table
    op.create_table('clubs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('custom_domain', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo_url', sa.String(length=500), nullable=True),
    sa.Column('primary_color', sa.String(length=7), nullable=True),
    sa.Column('secondary_color', sa.String(length=7), nullable=True),
    sa.Column('stripe_account_id', sa.String(length=255), nullable=True),
    sa.Column('stripe_onboarding_complete', sa.Boolean(), nullable=True),
    sa.Column('openai_api_key_encrypted', sa.Text(), nullable=True),
    sa.Column('ai_enabled', sa.Boolean(), nullable=True),
    sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('subscription_status', sa.String(length=50), nullable=True),
    sa.Column('subscription_plan', sa.String(length=50), nullable=True),
    sa.Column('subscription_ends_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    
    # Create platform_users table
    op.create_table('platform_users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    
    # Create club_members table
    op.create_table('club_members',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('club_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('member_tier', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('external_id', sa.String(length=255), nullable=True),
    sa.Column('external_provider', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('club_id', 'email')
    )
    
    # Create club_roles table
    op.create_table('club_roles',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('club_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['platform_users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('club_id', 'user_id')
    )
    
    # Create membership_tiers table
    op.create_table('membership_tiers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('club_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price_monthly', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('price_yearly', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('max_bookings_per_month', sa.Integer(), nullable=True),
    sa.Column('max_storage_mb', sa.Integer(), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('club_id', 'slug')
    )
    
    # Create indexes
    op.create_index(op.f('ix_clubs_slug'), 'clubs', ['slug'], unique=True)
    op.create_index(op.f('ix_platform_users_email'), 'platform_users', ['email'], unique=True)
    op.create_index(op.f('ix_club_members_club_id'), 'club_members', ['club_id'])
    op.create_index(op.f('ix_club_roles_club_id'), 'club_roles', ['club_id'])
    op.create_index(op.f('ix_membership_tiers_club_id'), 'membership_tiers', ['club_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_membership_tiers_club_id'), table_name='membership_tiers')
    op.drop_index(op.f('ix_club_roles_club_id'), table_name='club_roles')
    op.drop_index(op.f('ix_club_members_club_id'), table_name='club_members')
    op.drop_index(op.f('ix_platform_users_email'), table_name='platform_users')
    op.drop_index(op.f('ix_clubs_slug'), table_name='clubs')
    
    # Drop tables
    op.drop_table('membership_tiers')
    op.drop_table('club_roles')
    op.drop_table('club_members')
    op.drop_table('platform_users')
    op.drop_table('clubs')
