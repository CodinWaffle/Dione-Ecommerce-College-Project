"""Print recent cart_items rows for debugging persistence."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app, db

app = create_app('development')

with app.app_context():
    from project.models import CartItem, User
    items = CartItem.query.order_by(CartItem.id.desc()).limit(10).all()
    if not items:
        print('No cart_items found')
    for it in items:
        print('ID:', it.id, 'product_id:', it.product_id, 'product_name:', it.product_name,
              'quantity:', it.quantity, 'seller_id:', it.seller_id, 'user_id:', it.user_id,
              'session_id:', it.session_id, 'variant_image:', it.variant_image)

    # Also show count
    print('Total cart_items:', CartItem.query.count())
