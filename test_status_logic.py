import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import SellerProduct, User
import json

app = create_app()
with app.app_context():
    # Test the to_dict output for our test product
    product = SellerProduct.query.filter_by(id=31).first()
    if product:
        product_data = product.to_dict()
        print("Product data from to_dict():")
        print(json.dumps(product_data, indent=2))
        
        print(f"\nKey fields:")
        print(f"  status: {product_data['status']}")
        print(f"  is_draft: {product_data['is_draft']}")
        print(f"  total_stock: {product_data['total_stock']}")
        
        # Test the JavaScript normalization logic in Python
        totalStock = product_data.get('total_stock', 0)
        is_draft = product_data.get('is_draft', False)
        status = product_data.get('status', '')
        
        if is_draft:
            displayStatus = "draft"
        elif totalStock == 0:
            displayStatus = "Not Active"
        elif status == 'active':
            displayStatus = "Active"
        else:
            displayStatus = status or "draft"
            
        print(f"\nExpected frontend display status: {displayStatus}")
    else:
        print("Test product not found")