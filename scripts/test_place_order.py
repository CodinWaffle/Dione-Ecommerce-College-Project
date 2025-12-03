import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app, db
from project.models import CartItem, SellerProduct

app = create_app('development')


def ensure_sample_cart(user_id=3):
    with app.app_context():
        if CartItem.query.filter_by(user_id=user_id).count() > 0:
            return
        product = SellerProduct.query.first()
        if not product:
            raise SystemExit('No seller products available to seed cart')
        cart = CartItem(
            user_id=user_id,
            seller_id=product.seller_id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            color='Test Color',
            size='M',
            quantity=1,
            variant_image=product.primary_image or '/static/image/banner.png'
        )
        db.session.add(cart)
        db.session.commit()


ensure_sample_cart()

payload = {
    "email": "precioushanny22@gmail.com",
    "firstName": "Precious",
    "lastName": "Rondilla",
    "address": "Test Street",
    "apartment": "",
    "city": "Luisiana",
    "state": "Laguna",
    "zipCode": "4032",
    "phone": "09123456789",
    "country": "Philippines",
    "region": "CALABARZON",
    "barangay": "Barangay Zone I",
    "paymentMethod": "cod"
}

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['_user_id'] = '3'
        sess['_fresh'] = True

    response = client.post('/place-order', data=json.dumps(payload), content_type='application/json')
    print('Status:', response.status_code)
    print('Response:', response.json)

    if response.json and response.json.get('success'):
        success_page = client.get('/order-success')
        print('Order success status:', success_page.status_code)
        print('Order success snippet:', success_page.data[:200])
