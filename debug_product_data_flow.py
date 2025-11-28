#!/usr/bin/env python3
"""
Debug the exact data flow to see why basic product info isn't being saved
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_data_flow():
    """Debug what data is actually being processed"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("=== Product Data Flow Debug ===")
            
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
            
            # Create a payload that matches what the frontend should send
            payload = {
                "step1": {
                    "productName": "Debug Test Product",
                    "category": "Electronics",
                    "subcategory": "Phones",
                    "price": "199.99",
                    "discountType": "percentage",
                    "discountPercentage": "10",
                    "voucherType": "standard",
                    "primaryImage": "/static/images/test.jpg",
                    "secondaryImage": "/static/images/test2.jpg",
                    "subitem": ["Feature1", "Feature2"]
                },
                "step2": {
                    "description": "Debug test product description",
                    "materials": "Test materials",
                    "detailsFit": "Test fit details",
                    "sizeGuide": ["/static/images/size1.jpg"],
                    "certifications": ["/static/images/cert1.jpg"]
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "DEBUG-001",
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
            
            print("Sending payload:")
            print(json.dumps(payload, indent=2))
            
            # Add temporary debug logging to the route
            import logging
            logging.basicConfig(level=logging.DEBUG)
            
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"\nResponse status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            if response.status_code == 302:
                # Check what was actually saved
                saved_product = SellerProduct.query.filter_by(seller_id=seller.id).order_by(SellerProduct.id.desc()).first()
                
                if saved_product:
                    print(f"\n=== Saved Product Data ===")
                    print(f"ID: {saved_product.id}")
                    print(f"Name: '{saved_product.name}'")
                    print(f"Description: '{saved_product.description}'")
                    print(f"Category: '{saved_product.category}'")
                    print(f"Subcategory: '{saved_product.subcategory}'")
                    print(f"Price: {saved_product.price}")
                    print(f"Compare at price: {saved_product.compare_at_price}")
                    print(f"Discount type: '{saved_product.discount_type}'")
                    print(f"Discount value: {saved_product.discount_value}")
                    print(f"Voucher type: '{saved_product.voucher_type}'")
                    print(f"Materials: '{saved_product.materials}'")
                    print(f"Details fit: '{saved_product.details_fit}'")
                    print(f"Primary image: '{saved_product.primary_image}'")
                    print(f"Secondary image: '{saved_product.secondary_image}'")
                    print(f"Total stock: {saved_product.total_stock}")
                    print(f"Variants: {saved_product.variants}")
                    print(f"Attributes: {saved_product.attributes}")
                    
                    # Check if basic fields are empty
                    issues = []
                    if not saved_product.name or saved_product.name.strip() == '':
                        issues.append("Name is empty")
                    if not saved_product.category or saved_product.category.strip() == '':
                        issues.append("Category is empty")
                    if not saved_product.price or saved_product.price == 0:
                        issues.append("Price is zero/empty")
                    
                    if issues:
                        print(f"\n❌ ISSUES FOUND:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print(f"\n✅ All basic fields saved correctly!")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print(f"\n✓ Test product cleaned up")
                    
                else:
                    print("✗ No product was saved at all")
                    return False
            else:
                print("✗ Request failed")
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_data_flow()