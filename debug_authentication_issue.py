#!/usr/bin/env python3
"""
Debug authentication issue in add_product_preview route
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_authentication():
    """Debug authentication issue"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        from flask_login import current_user
        
        app = create_app()
        
        with app.app_context():
            print("=== Authentication Debug ===")
            
            client = app.test_client()
            
            # Test without authentication
            print("\n=== Test 1: No Authentication ===")
            
            payload = {
                "step1": {"productName": "No Auth Test", "category": "Test", "price": "100"},
                "step2": {"description": "Test"},
                "step3": {"variants": [], "totalStock": 0}
            }
            
            # Capture what happens in the route
            with app.test_request_context('/seller/add_product_preview', method='POST', 
                                        data=json.dumps(payload), content_type='application/json'):
                from flask_login import current_user
                print(f"current_user.is_authenticated: {current_user.is_authenticated}")
                print(f"current_user.id: {getattr(current_user, 'id', 'No ID')}")
                print(f"current_user type: {type(current_user)}")
            
            # Test with authentication
            print("\n=== Test 2: With Authentication ===")
            
            # Get a test seller
            test_seller = User.query.filter_by(role='seller', is_approved=True).first()
            if not test_seller:
                print("✗ No approved seller found")
                return False
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_seller.id)
                sess['_fresh'] = True
            
            # Make request and check current_user
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response location: {response.location}")
            
            # Check if product was actually created
            test_product = SellerProduct.query.filter_by(name='No Auth Test').first()
            if test_product:
                print(f"✓ Product created with seller_id: {test_product.seller_id}")
                db.session.delete(test_product)
                db.session.commit()
            else:
                print("✗ No product was created")
            
            # Test the actual route logic manually
            print("\n=== Test 3: Manual Route Logic ===")
            
            # Simulate the route logic
            from project.routes.seller_routes import _to_decimal, _to_int
            
            workflow_data = {
                'step1': {"productName": "Manual Test", "category": "Test", "price": "200"},
                'step2': {"description": "Manual test"},
                'step3': {"variants": [], "totalStock": 0}
            }
            
            step1 = workflow_data.get('step1', {})
            step2 = workflow_data.get('step2', {})
            step3 = workflow_data.get('step3', {})
            
            product_name = step1.get('productName', '').strip()
            category = step1.get('category', '').strip()
            
            print(f"Product name: {product_name}")
            print(f"Category: {category}")
            
            if not product_name or not category:
                print("✗ Validation would fail")
                return False
            
            base_price = _to_decimal(step1.get('price'))
            print(f"Base price: {base_price}")
            
            # Try to create product manually
            try:
                product = SellerProduct(
                    seller_id=test_seller.id,  # Use known seller ID
                    name=product_name,
                    description=step2.get('description', ''),
                    category=category,
                    subcategory=step1.get('subcategory'),
                    price=float(base_price),
                    compare_at_price=None,
                    discount_type=None,
                    discount_value=None,
                    voucher_type=step1.get('voucherType'),
                    materials=step2.get('materials', ''),
                    details_fit=step2.get('detailsFit', ''),
                    primary_image=step1.get('primaryImage', '/static/image/banner.png'),
                    secondary_image=step1.get('secondaryImage'),
                    total_stock=step3.get('totalStock', 0),
                    low_stock_threshold=5,
                    variants=step3.get('variants', []),
                    attributes={
                        'subitems': step1.get('subitem', []),
                        'size_guides': step2.get('sizeGuide', []),
                        'certifications': step2.get('certifications', []),
                    },
                )
                
                db.session.add(product)
                db.session.commit()
                
                print(f"✓ Manual product creation successful: ID {product.id}")
                
                # Clean up
                db.session.delete(product)
                db.session.commit()
                
            except Exception as e:
                print(f"✗ Manual product creation failed: {e}")
                db.session.rollback()
                return False
            
            return True
            
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_authentication()