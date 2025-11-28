import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User
from decimal import Decimal
from datetime import datetime

app = create_app()
with app.app_context():
    seller = User.query.filter_by(id=8, role='seller').first()
    
    if seller:
        # Create a draft product
        draft_product = SellerProduct(
            seller_id=seller.id,
            name="Draft Product",
            description="This is a draft product",
            category="Clothing",
            subcategory="T-Shirts",
            price=19.99,
            primary_image="/static/image/banner.png",
            total_stock=5,  # Has stock but still draft
            variants=[{"color": "Red", "size": "M", "stock": 5}],
            is_draft=True,  # Set as draft
            status='draft',  # Set as draft
            created_at=datetime.utcnow()
        )
        
        # Create a zero-stock product
        zero_stock_product = SellerProduct(
            seller_id=seller.id,
            name="Zero Stock Product",
            description="This has zero stock",
            category="Clothing",
            subcategory="T-Shirts",
            price=39.99,
            primary_image="/static/image/banner.png",
            total_stock=0,  # No stock
            variants=[{"color": "Red", "size": "M", "stock": 0}],
            is_draft=False,  # Not draft
            status='active',  # But active
            created_at=datetime.utcnow()
        )
        
        db.session.add(draft_product)
        db.session.add(zero_stock_product)
        db.session.commit()
        
        print("Created test products:")
        
        # Test draft product
        draft_data = draft_product.to_dict()
        is_draft = draft_data.get('is_draft', False)
        totalStock = draft_data.get('total_stock', 0)
        status = draft_data.get('status', '')
        
        if is_draft:
            displayStatus = "draft"
        elif totalStock == 0:
            displayStatus = "Not Active"
        elif status == 'active':
            displayStatus = "Active"
        else:
            displayStatus = status or "draft"
            
        print(f"\nDraft Product (ID: {draft_product.id}):")
        print(f"  Backend: is_draft={is_draft}, status='{status}', stock={totalStock}")
        print(f"  Frontend display: '{displayStatus}'")
        
        # Test zero stock product
        zero_data = zero_stock_product.to_dict()
        is_draft = zero_data.get('is_draft', False)
        totalStock = zero_data.get('total_stock', 0)
        status = zero_data.get('status', '')
        
        if is_draft:
            displayStatus = "draft"
        elif totalStock == 0:
            displayStatus = "Not Active"
        elif status == 'active':
            displayStatus = "Active"
        else:
            displayStatus = status or "draft"
            
        print(f"\nZero Stock Product (ID: {zero_stock_product.id}):")
        print(f"  Backend: is_draft={is_draft}, status='{status}', stock={totalStock}")
        print(f"  Frontend display: '{displayStatus}'")