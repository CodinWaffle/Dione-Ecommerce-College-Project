import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User
from decimal import Decimal
from datetime import datetime

app = create_app()
with app.app_context():
        # Get specific seller (Avery_Cruz)
        seller = User.query.filter_by(id=8, role='seller').first()
        if not seller:
            print("Seller with ID 8 not found!")
        else:
            print(f"Found seller: {seller.username} (ID: {seller.id})")        # Create a test product with stock
        test_product = SellerProduct(
            seller_id=seller.id,
            name="Test Product With Stock",
            description="This is a test product",
            category="Clothing",
            subcategory="T-Shirts",
            price=29.99,
            compare_at_price=39.99,
            primary_image="/static/image/banner.png",
            total_stock=10,  # This should make it active
            variants=[
                {"color": "Red", "size": "M", "stock": 5},
                {"color": "Blue", "size": "L", "stock": 5}
            ],
            is_draft=False,  # Set as NOT draft
            status='active',  # Set as active
            created_at=datetime.utcnow()
        )
        
        db.session.add(test_product)
        db.session.commit()
        
        print(f"Created test product:")
        print(f"  ID: {test_product.id}")
        print(f"  Name: {test_product.name}")
        print(f"  Status: {test_product.status}")
        print(f"  Is Draft: {test_product.is_draft}")
        print(f"  Total Stock: {test_product.total_stock}")
        print(f"  Seller ID: {test_product.seller_id}")
        
        # Also verify it was saved correctly
        saved_product = SellerProduct.query.filter_by(id=test_product.id).first()
        if saved_product:
            print("\nVerified in database:")
            print(f"  Status: {saved_product.status}")
            print(f"  Is Draft: {saved_product.is_draft}")
            print(f"  Total Stock: {saved_product.total_stock}")
            print(f"  to_dict(): {saved_product.to_dict()}")