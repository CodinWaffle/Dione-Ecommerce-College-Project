"""Add attachment column to chat_messages

Revision ID: add_chat_attachment
Revises: add_username_column
Create Date: 2025-11-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chat_attachment'
down_revision = 'add_username_column'
branch_labels = None
depends_on = None


def upgrade():
    # Add nullable attachment column for uploaded file path
    op.add_column('chat_messages', sa.Column('attachment', sa.String(length=512), nullable=True))


def downgrade():
    op.drop_column('chat_messages', 'attachment')
