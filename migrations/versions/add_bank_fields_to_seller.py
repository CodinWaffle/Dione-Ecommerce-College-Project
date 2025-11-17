"""Add bank_type and bank_name columns to seller table

Revision ID: add_bank_fields
Revises: add_role_profiles
Create Date: 2025-11-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_bank_fields'
down_revision = 'add_role_profiles'
branch_labels = None
depends_on = None


def upgrade():
    # Add bank_type and bank_name columns to seller table
    op.add_column('seller', sa.Column('bank_type', sa.String(length=50), nullable=True))
    op.add_column('seller', sa.Column('bank_name', sa.String(length=255), nullable=True))


def downgrade():
    # Remove bank_type and bank_name columns from seller table
    op.drop_column('seller', 'bank_name')
    op.drop_column('seller', 'bank_type')
