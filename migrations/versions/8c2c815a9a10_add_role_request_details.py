"""add role_request_details column

Revision ID: 8c2c815a9a10
Revises: f01c49872ffb
Create Date: 2025-11-25 15:05:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c2c815a9a10'
down_revision = 'f01c49872ffb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('role_request_details', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('user', 'role_request_details')
