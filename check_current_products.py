import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User

app = create_app()
with app.app_context():
    print('=== CURRENT PRODUCTS IN DATABASE ===')
    products = SellerProduct.query.all()
    for p in products:
        print(f'ID: {p.id}')
        print(f'  Name: {p.name}')
        print(f'  Seller ID: {p.seller_id}')
        print(f'  Status: {p.status}')
        print(f'  Is Draft: {p.is_draft}')
        print(f'  Total Stock: {p.total_stock}')
        print(f'  Price: {p.price}')
        print()