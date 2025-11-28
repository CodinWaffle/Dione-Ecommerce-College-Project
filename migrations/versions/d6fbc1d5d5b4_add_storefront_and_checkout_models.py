"""add storefront, cart, review, and tracking models

Revision ID: d6fbc1d5d5b4
Revises: 8c2c815a9a10
Create Date: 2025-11-27 16:25:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6fbc1d5d5b4'
down_revision = '8c2c815a9a10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'store_profile',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('seller_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, unique=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=160), nullable=False, unique=True),
        sa.Column('tagline', sa.String(length=255)),
        sa.Column('description', sa.Text()),
        sa.Column('contact_email', sa.String(length=150)),
        sa.Column('contact_phone', sa.String(length=50)),
        sa.Column('theme_color', sa.String(length=20), server_default='#111827'),
        sa.Column('logo_image', sa.String(length=255)),
        sa.Column('banner_image', sa.String(length=255)),
        sa.Column('social_links', sa.Text()),
        sa.Column('shipping_policy', sa.Text()),
        sa.Column('return_policy', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'product_variant',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('attribute', sa.String(length=80), nullable=False, server_default='Size'),
        sa.Column('value', sa.String(length=80), nullable=False),
        sa.Column('price_delta', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'cart',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'review',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('store_profile.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=150)),
        sa.Column('body', sa.Text()),
        sa.Column('media_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'cart_item',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cart_id', sa.Integer(), sa.ForeignKey('cart.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variant.id')),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False, server_default='0'),
    )

    op.create_table(
        'review_media',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('review.id'), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=False, server_default='image'),
    )

    op.create_table(
        'review_response',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('review.id'), nullable=False, unique=True),
        sa.Column('seller_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'order_tracking_event',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('order.id'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.add_column('order_item', sa.Column('variant_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_order_item_variant', 'order_item', 'product_variant', ['variant_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_order_item_variant', 'order_item', type_='foreignkey')
    op.drop_column('order_item', 'variant_id')
    op.drop_table('order_tracking_event')
    op.drop_table('review_response')
    op.drop_table('review_media')
    op.drop_table('cart_item')
    op.drop_table('review')
    op.drop_table('cart')
    op.drop_table('product_variant')
    op.drop_table('store_profile')
