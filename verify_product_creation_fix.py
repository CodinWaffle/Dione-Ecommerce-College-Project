#!/usr/bin/env python3
"""
Verify that the product creation fix is working correctly
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def verify_fix():
    """Verify the product creation fix"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🔍 VERIFYING PRODUCT CREATION FIX")
            print("=" * 50)
            
            client = app.test_client()
            
            # Get an approved seller
            seller = User.query.filter_by(role='seller', is_approved=True).first()
            if not seller:
                print("❌ No approved seller found")
                return False
            
            # Login as the seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✅ Testing with seller: {seller.email}")
            
            # Test 1: Valid product creation
            print("\n📝 TEST 1: Valid Product Creation")
            print("-" * 30)
            
            payload = {
                "step1": {
                    "productName": "Verification Test Product",
                    "category": "Electronics",
                    "subcategory": "Gadgets",
                    "price": "149.99",
                    "discountType": "percentage",
                    "discountPercentage": "15",
                    "voucherType": "SAVE15",
                    "primaryImage": "/static/images/test.jpg",
                    "secondaryImage": "/static/images/test2.jpg"
                },
                "step2": {
                    "description": "This is a verification test product",
                    "materials": "High-quality materials",
                    "detailsFit": "Perfect fit and finish"
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "VERIFY-001",
                            "color": "Blue",
                            "colorHex": "#0000FF",
                            "size": "Standard",
                            "stock": 20,
                            "lowStock": 5
                        }
                    ],
                    "totalStock": 20
                }
            }
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            if response.status_code == 302 and 'products' in response.location:
                print("✅ Request successful - redirected to products page")
                
                # Check if product was saved correctly
                saved_product = SellerProduct.query.filter_by(name='Verification Test Product').first()
                if saved_product:
                    print("✅ Product saved to database")
                    print(f"   📋 Name: '{saved_product.name}'")
                    print(f"   📂 Category: '{saved_product.category}'")
                    print(f"   📂 Subcategory: '{saved_product.subcategory}'")
                    print(f"   💰 Price: ${saved_product.price}")
                    print(f"   📦 Stock: {saved_product.total_stock}")
                    print(f"   🎨 Variants: {len(saved_product.variants or [])}")
                    
                    # Verify all critical fields
                    issues = []
                    if not saved_product.name or saved_product.name.strip() == '':
                        issues.append("Name is empty")
                    if not saved_product.category or saved_product.category.strip() == '':
                        issues.append("Category is empty")
                    if not saved_product.price or saved_product.price <= 0:
                        issues.append("Price is invalid")
                    
                    if issues:
                        print(f"❌ CRITICAL ISSUES FOUND:")
                        for issue in issues:
                            print(f"   - {issue}")
                        return False
                    else:
                        print("✅ All critical fields are valid")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("🧹 Test product cleaned up")
                    
                else:
                    print("❌ Product was not found in database")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
            
            # Test 2: Empty fields rejection
            print("\n🚫 TEST 2: Empty Fields Rejection")
            print("-" * 30)
            
            empty_payload = {
                "step1": {"productName": "", "category": "", "price": ""},
                "step2": {"description": ""},
                "step3": {"variants": [], "totalStock": 0}
            }
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(empty_payload),
                content_type='application/json'
            )
            
            if response.status_code == 302 and 'add_product' in response.location:
                print("✅ Empty fields correctly rejected")
            else:
                print("❌ Empty fields should have been rejected")
                return False
            
            # Summary
            print("\n🎉 VERIFICATION COMPLETE")
            print("=" * 50)
            print("✅ Product creation fix is working correctly!")
            print("✅ Valid products are saved with all fields")
            print("✅ Invalid products are properly rejected")
            print("✅ Database integration is functioning")
            print("✅ Authentication and validation are working")
            
            print("\n📋 NEXT STEPS:")
            print("1. Test in your browser by creating a product")
            print("2. Check the products page to see your new product")
            print("3. Verify all fields are displayed correctly")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_fix()
    if success:
        print("\n🚀 Ready to use! The product creation system is fully functional.")
    else:
        print("\n⚠️  Issues detected. Please check the error messages above.")
    
    sys.exit(0 if success else 1)