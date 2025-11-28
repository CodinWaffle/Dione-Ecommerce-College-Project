#!/usr/bin/env python3
"""
Test the scenario where empty fields are being sent
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_empty_fields():
    """Test what happens when empty fields are sent"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("=== Empty Fields Test ===")
            
            client = app.test_client()
            
            # Get seller ID 8 (the one having issues)
            seller = User.query.get(8)
            if not seller:
                print("✗ Seller ID 8 not found")
                return False
            
            # Login as that seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✓ Logged in as seller: {seller.email}")
            
            # Test 1: Completely empty basic fields
            print("\n=== Test 1: Empty Basic Fields ===")
            
            payload = {
                "step1": {
                    "productName": "",
                    "category": "",
                    "subcategory": "",
                    "price": "",
                    "discountType": "",
                    "discountPercentage": "",
                    "voucherType": "",
                    "primaryImage": "",
                    "secondaryImage": ""
                },
                "step2": {
                    "description": "",
                    "materials": "",
                    "detailsFit": ""
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "TEST-EMPTY",
                            "color": "Red",
                            "colorHex": "#FF0000",
                            "size": "M",
                            "stock": 5,
                            "lowStock": 1
                        }
                    ],
                    "totalStock": 5
                }
            }
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302 and 'add_product' in response.location:
                print("✅ Correctly rejected empty fields and redirected to add_product")
            else:
                print("❌ Should have rejected empty fields")
                return False
            
            # Test 2: Fields with dash values
            print("\n=== Test 2: Dash Values ===")
            
            payload["step1"]["productName"] = "-"
            payload["step1"]["category"] = "-"
            payload["step1"]["price"] = "0"
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302 and 'add_product' in response.location:
                print("✅ Correctly rejected dash values and redirected to add_product")
            else:
                print("❌ Should have rejected dash values")
                return False
            
            # Test 3: Valid data to make sure it still works
            print("\n=== Test 3: Valid Data ===")
            
            payload["step1"]["productName"] = "Valid Test Product"
            payload["step1"]["category"] = "Electronics"
            payload["step1"]["price"] = "99.99"
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302 and 'products' in response.location:
                print("✅ Valid data accepted and redirected to products")
                
                # Check if product was saved correctly
                saved_product = SellerProduct.query.filter_by(name='Valid Test Product').first()
                if saved_product:
                    print(f"✅ Product saved with correct data:")
                    print(f"  - Name: '{saved_product.name}'")
                    print(f"  - Category: '{saved_product.category}'")
                    print(f"  - Price: {saved_product.price}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Test product cleaned up")
                else:
                    print("❌ Product was not saved")
                    return False
            else:
                print("❌ Valid data should have been accepted")
                return False
            
            print("\n✅ All validation tests passed!")
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_empty_fields()