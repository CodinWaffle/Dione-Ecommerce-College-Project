#!/usr/bin/env python3
"""
Debug server-side validation issues
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_server_validation():
    """Debug what's happening on the server side"""
    
    try:
        from project import create_app, db
        from project.models import User
        
        app = create_app()
        
        with app.app_context():
            print("=== Server-Side Validation Debug ===")
            
            client = app.test_client()
            
            # Get an approved seller
            seller = User.query.filter_by(role='seller', is_approved=True).first()
            if not seller:
                print("✗ No approved seller found")
                return False
            
            # Login as the seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            # Test with the exact payload that's failing
            payload = {
                "step1": {
                    "productName": "",  # Empty string - this is the problem
                    "category": "",     # Empty string - this is the problem
                    "price": "199.99",
                    "discountType": "percentage",
                    "discountPercentage": "10",
                    "voucherType": "standard",
                    "primaryImage": "/static/image/banner.png",
                    "secondaryImage": "/static/image/banner.png"
                },
                "step2": {
                    "description": "Test description",
                    "materials": "Test materials",
                    "detailsFit": "Test fit"
                },
                "step3": {
                    "variants": [],
                    "totalStock": 0
                }
            }
            
            print("Testing with empty productName and category...")
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302 and 'add_product' in response.location:
                print("✓ Confirmed: Server is redirecting back to add_product due to validation")
                print("This happens when productName or category are empty")
            
            # Test with valid data
            print("\nTesting with valid productName and category...")
            payload["step1"]["productName"] = "Valid Test Product"
            payload["step1"]["category"] = "Electronics"
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302 and 'products' in response.location:
                print("✓ Confirmed: Server accepts valid data and redirects to products page")
                
                # Check if product was saved
                from project.models import SellerProduct
                saved_product = SellerProduct.query.filter_by(name='Valid Test Product').first()
                if saved_product:
                    print("✓ Product was saved to database successfully")
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Test product cleaned up")
                else:
                    print("✗ Product was not saved despite successful response")
            
            return True
            
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_server_validation()