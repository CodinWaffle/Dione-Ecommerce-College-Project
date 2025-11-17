"""Add role-specific profile tables: Buyer, Seller, Rider

Revision ID: add_role_profiles
Revises: f01c49872ffb
Create Date: 2025-11-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_role_profiles'
down_revision = 'f01c49872ffb'
branch_labels = None
depends_on = None


def upgrade():
    # Create Buyer table
    op.create_table(
        'buyer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('preferred_language', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create Seller table
    op.create_table(
        'seller',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('business_type', sa.String(length=100), nullable=True),
        sa.Column('business_address', sa.Text(), nullable=True),
        sa.Column('business_city', sa.String(length=100), nullable=True),
        sa.Column('business_zip', sa.String(length=20), nullable=True),
        sa.Column('business_country', sa.String(length=100), nullable=True),
        sa.Column('bank_account', sa.String(length=100), nullable=True),
        sa.Column('bank_holder_name', sa.String(length=255), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('store_description', sa.Text(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create Rider table
    op.create_table(
        'rider',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('vehicle_type', sa.String(length=50), nullable=True),
        sa.Column('vehicle_number', sa.String(length=50), nullable=True),
        sa.Column('availability_status', sa.String(length=20), nullable=True),
        sa.Column('current_location', sa.String(length=255), nullable=True),
        sa.Column('delivery_zones', sa.Text(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('total_deliveries', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('rider')
    op.drop_table('seller')
    op.drop_table('buyer')
