import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User
from decimal import Decimal
from datetime import datetime

app = create_app()
with app.app_context():
    # Create a test product for deletion testing
    seller = User.query.filter_by(id=8, role='seller').first()
    
    if seller:
        test_product = SellerProduct(
            seller_id=seller.id,
            name="Test Delete Product",
            description="This product will be deleted to test the functionality",
            category="Testing",
            subcategory="Delete Test",
            price=99.99,
            primary_image="/static/image/banner.png",
            total_stock=1,
            variants=[{"color": "Test", "size": "Delete", "stock": 1}],
            is_draft=False,
            status='active',
            created_at=datetime.utcnow()
        )
        
        db.session.add(test_product)
        db.session.commit()
        
        print(f"Created test product for deletion testing:")
        print(f"  ID: {test_product.id}")
        print(f"  Name: {test_product.name}")
        print(f"  Status: {test_product.status}")
        print(f"  Total Stock: {test_product.total_stock}")
        print(f"\nYou can now test the delete functionality with this product.")
        print(f"After testing, the product should be immediately removed from the table.")
    else:
        print("No seller found with ID 8")