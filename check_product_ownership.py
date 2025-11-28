import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User

app = create_app()
with app.app_context():
    # Check which products belong to seller 8
    seller_8_products = SellerProduct.query.filter_by(seller_id=8).all()
    print(f"Products owned by seller 8 (Avery_Cruz):")
    for p in seller_8_products:
        print(f"  ID: {p.id}, Name: {p.name}, Status: {p.status}, Is Draft: {p.is_draft}")
    
    # Check all products in database with owner info
    print(f"\nAll products in database:")
    all_products = SellerProduct.query.all()
    for p in all_products:
        owner = User.query.get(p.seller_id)
        owner_name = owner.username if owner else "Unknown"
        print(f"  ID: {p.id}, Name: {p.name}, Owner: {owner_name} (ID: {p.seller_id})")