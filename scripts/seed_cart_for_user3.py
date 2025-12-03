"""Seed a temporary cart item for user 3 for testing checkout."""
import os
import sys
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app, db
from project.models import CartItem, SellerProduct

app = create_app('development')

with app.app_context():
    product = SellerProduct.query.first()
    if not product:
        raise SystemExit('No seller products available')

    cart = CartItem(
        user_id=3,
        seller_id=product.seller_id,
        product_id=product.id,
        product_name=product.name,
        product_price=product.price or Decimal('0'),
        color='Test Color',
        size='M',
        quantity=1,
        variant_image=product.primary_image or '/static/image/banner.png'
    )
    db.session.add(cart)
    db.session.commit()
    print(f"Inserted cart item {cart.id} for user 3")
