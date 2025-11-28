#!/usr/bin/env python3
"""
Debug script to check user session and authentication flow
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_user_session():
    """Debug user session and authentication issues"""
    
    try:
        from project import create_app, db
        from project.models import User
        
        app = create_app()
        
        with app.app_context():
            print("=== User Session Debug ===")
            
            # Check all users in database
            users = User.query.all()
            print(f"Total users in database: {len(users)}")
            
            sellers = User.query.filter_by(role='seller').all()
            print(f"Total sellers: {len(sellers)}")
            
            approved_sellers = User.query.filter_by(role='seller', is_approved=True).all()
            print(f"Approved sellers: {len(approved_sellers)}")
            
            if approved_sellers:
                print("\nApproved sellers:")
                for seller in approved_sellers:
                    print(f"  - ID: {seller.id}, Email: {seller.email}, Username: {seller.username}")
            else:
                print("✗ No approved sellers found!")
                print("This could be why products aren't saving - user might not be authenticated properly")
            
            # Check for any existing products
            from project.models import SellerProduct
            products = SellerProduct.query.all()
            print(f"\nTotal products in database: {len(products)}")
            
            if products:
                print("Existing products:")
                for product in products[:5]:  # Show first 5
                    print(f"  - ID: {product.id}, Name: {product.name}, Seller ID: {product.seller_id}")
            
            # Test client with different authentication states
            client = app.test_client()
            
            print("\n=== Authentication Tests ===")
            
            # Test 1: No authentication
            response = client.get('/seller/add_product_preview')
            print(f"No auth - GET preview: {response.status_code}")
            
            # Test 2: With authentication but no session data
            if approved_sellers:
                test_seller = approved_sellers[0]
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(test_seller.id)
                    sess['_fresh'] = True
                
                response = client.get('/seller/add_product_preview')
                print(f"With auth - GET preview: {response.status_code}")
                
                # Test 3: POST without session workflow data
                payload = {
                    "step1": {"productName": "Auth Test", "category": "Test", "price": "100"},
                    "step2": {"description": "Test"},
                    "step3": {"variants": [], "totalStock": 0}
                }
                
                response = client.post(
                    '/seller/add_product_preview',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                print(f"With auth - POST JSON: {response.status_code}")
                
                if response.status_code == 302:
                    # Check if product was saved
                    test_product = SellerProduct.query.filter_by(name='Auth Test').first()
                    if test_product:
                        print("✓ Product saved successfully with JSON payload")
                        db.session.delete(test_product)
                        db.session.commit()
                    else:
                        print("✗ Product not saved despite successful response")
                
                # Test 4: Check session workflow
                print("\n=== Session Workflow Test ===")
                
                # Simulate the multi-step workflow
                with client.session_transaction() as sess:
                    sess['product_workflow'] = {
                        'step1': {"productName": "Session Test", "category": "Test", "price": "150"},
                        'step2': {"description": "Session test"},
                        'step3': {"variants": [], "totalStock": 0}
                    }
                
                response = client.post('/seller/add_product_preview')
                print(f"Session workflow POST: {response.status_code}")
                
                if response.status_code == 302:
                    test_product = SellerProduct.query.filter_by(name='Session Test').first()
                    if test_product:
                        print("✓ Product saved with session workflow")
                        db.session.delete(test_product)
                        db.session.commit()
                    else:
                        print("✗ Product not saved with session workflow")
            
            print("\n=== JavaScript Debug Suggestions ===")
            print("1. Check browser console for JavaScript errors")
            print("2. Verify localStorage/sessionStorage has the form data")
            print("3. Check network tab for failed requests")
            print("4. Verify user is logged in and has seller role")
            print("5. Check if session cookies are being sent")
            
            return True
            
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_user_session()