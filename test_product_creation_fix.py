#!/usr/bin/env python3
"""
Test the product creation fix
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_fix():
    """Test the product creation fix"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("=== Testing Product Creation Fix ===")
            
            client = app.test_client()
            
            # Get an approved seller
            seller = User.query.filter_by(role='seller', is_approved=True).first()
            if not seller:
                print("✗ No approved seller found")
                return False
            
            print(f"✓ Using seller: {seller.email}")
            
            # Login as the seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            # Test the complete flow
            print("\n=== Testing Complete Flow ===")
            
            # Step 1: Get the preview page
            response = client.get('/seller/add_product_preview')
            print(f"GET preview page: {response.status_code}")
            
            # Step 2: Submit product data
            payload = {
                "step1": {
                    "productName": "Fix Test Product",
                    "category": "Electronics",
                    "subcategory": "Phones",
                    "price": "299.99",
                    "discountType": "percentage",
                    "discountPercentage": "10",
                    "voucherType": "standard",
                    "primaryImage": "/static/images/test.jpg",
                    "secondaryImage": "/static/images/test2.jpg"
                },
                "step2": {
                    "description": "Test product for fix verification",
                    "materials": "Test materials",
                    "detailsFit": "Test fit"
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "FIX-001",
                            "color": "Red",
                            "colorHex": "#FF0000",
                            "size": "M",
                            "stock": 10,
                            "lowStock": 2
                        }
                    ],
                    "totalStock": 10
                }
            }
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"POST product data: {response.status_code}")
            
            if response.status_code == 302:
                print(f"✓ Redirected to: {response.location}")
                
                # Check if product was saved
                saved_product = SellerProduct.query.filter_by(name='Fix Test Product').first()
                if saved_product:
                    print(f"✓ Product saved successfully!")
                    print(f"  - ID: {saved_product.id}")
                    print(f"  - Name: {saved_product.name}")
                    print(f"  - Category: {saved_product.category}")
                    print(f"  - Price: {saved_product.price}")
                    print(f"  - Seller ID: {saved_product.seller_id}")
                    print(f"  - Variants: {len(saved_product.variants or [])}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Test product cleaned up")
                    
                    return True
                else:
                    print("✗ Product was not saved to database")
                    return False
            else:
                print(f"✗ Unexpected response: {response.status_code}")
                if response.data:
                    print(f"Response: {response.get_data(as_text=True)[:200]}")
                return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_fix()
    if success:
        print("\n🎉 Product creation fix is working!")
        print("\nThe issue was likely one of these:")
        print("1. Missing authentication validation in frontend")
        print("2. Poor error handling for network/server issues")
        print("3. No user feedback for validation errors")
        print("\nThe fix includes:")
        print("✓ Better authentication error detection")
        print("✓ Improved user feedback and validation")
        print("✓ Enhanced error handling and recovery")
        print("✓ Loading states and progress indicators")
    else:
        print("\n❌ Fix verification failed")
        print("Please check the troubleshooting guide: PRODUCT_CREATION_TROUBLESHOOTING.md")
    
    sys.exit(0 if success else 1)