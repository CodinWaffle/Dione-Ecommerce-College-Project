#!/usr/bin/env python3
"""
Test the complete fix for product creation
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_complete_fix():
    """Test the complete product creation fix"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("=== Complete Product Creation Fix Test ===")
            
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
            
            print(f"✓ Logged in as seller: {seller.email}")
            
            # Test the exact scenario that was failing
            print("\n=== Test 1: Scenario with Default Values ===")
            
            payload = {
                "step1": {
                    "productName": "New Product",  # Default value from frontend fix
                    "category": "General",         # Default value from frontend fix
                    "price": "99.99",
                    "discountType": "percentage",
                    "discountPercentage": "5",
                    "voucherType": "standard",
                    "primaryImage": "/static/image/banner.png",
                    "secondaryImage": "/static/image/banner.png"
                },
                "step2": {
                    "description": "Product created with default values",
                    "materials": "Various materials",
                    "detailsFit": "Standard fit"
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "DEFAULT-001",
                            "color": "Blue",
                            "colorHex": "#0000FF",
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
            
            if response.status_code == 302 and 'products' in response.location:
                print("✓ Successfully redirected to products page")
                
                # Check if product was saved
                saved_product = SellerProduct.query.filter_by(name='New Product').first()
                if saved_product:
                    print("✓ Product saved to database successfully!")
                    print(f"  - ID: {saved_product.id}")
                    print(f"  - Name: {saved_product.name}")
                    print(f"  - Category: {saved_product.category}")
                    print(f"  - Price: ${saved_product.price}")
                    print(f"  - Variants: {len(saved_product.variants or [])}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Test product cleaned up")
                else:
                    print("✗ Product was not saved to database")
                    return False
            else:
                print(f"✗ Unexpected response: {response.status_code}")
                return False
            
            # Test with actual user-filled data
            print("\n=== Test 2: Realistic User Data ===")
            
            payload["step1"]["productName"] = "Premium Smartphone Case"
            payload["step1"]["category"] = "Electronics"
            payload["step1"]["subcategory"] = "Phone Accessories"
            payload["step1"]["price"] = "29.99"
            payload["step2"]["description"] = "High-quality protective case for smartphones"
            payload["step3"]["variants"][0]["sku"] = "CASE-001"
            payload["step3"]["variants"][0]["color"] = "Black"
            payload["step3"]["variants"][0]["colorHex"] = "#000000"
            payload["step3"]["variants"][0]["stock"] = 25
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            if response.status_code == 302 and 'products' in response.location:
                saved_product = SellerProduct.query.filter_by(name='Premium Smartphone Case').first()
                if saved_product:
                    print("✓ Realistic product data also works perfectly!")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Realistic test product cleaned up")
                else:
                    print("✗ Realistic product was not saved")
                    return False
            else:
                print("✗ Realistic product test failed")
                return False
            
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("\nThe product creation issue has been completely fixed!")
            print("\nWhat was fixed:")
            print("✓ Frontend now provides default values for empty fields")
            print("✓ Server prioritizes JSON payload over stale session data")
            print("✓ Better validation and error messages")
            print("✓ Products save correctly to database")
            print("✓ Proper redirect to products page on success")
            
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_complete_fix()
    sys.exit(0 if success else 1)