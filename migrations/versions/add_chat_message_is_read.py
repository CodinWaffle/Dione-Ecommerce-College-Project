"""Add is_read column to chat_messages

Revision ID: add_chat_message_is_read
Revises: add_chat_attachment
Create Date: 2025-11-24 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_chat_message_is_read'
down_revision = 'add_chat_attachment'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('chat_messages', sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    # remove server_default for future inserts
    op.alter_column('chat_messages', 'is_read', server_default=None)


def downgrade():
    op.drop_column('chat_messages', 'is_read')
