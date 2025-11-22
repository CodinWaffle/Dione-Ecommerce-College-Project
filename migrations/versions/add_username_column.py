"""Add username column to user table

Revision ID: add_username_column
Revises: add_bank_fields
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_username_column'
down_revision = 'add_bank_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('username', sa.String(length=150), nullable=True))
    op.create_index('idx_user_username', 'user', ['username'], unique=False)


def downgrade():
    op.drop_index('idx_user_username', table_name='user')
    op.drop_column('user', 'username')
