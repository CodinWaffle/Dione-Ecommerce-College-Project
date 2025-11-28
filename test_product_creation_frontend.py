#!/usr/bin/env python3
"""
Test script to simulate the exact frontend product creation flow
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_frontend_flow():
    """Test the exact frontend flow that's failing"""
    
    try:
        from project import create_app, db
        from project.models import SellerProduct, User
        from flask import url_for
        
        app = create_app()
        
        with app.app_context():
            print("=== Frontend Flow Test ===")
            
            # Create test client
            client = app.test_client()
            
            # Create or get test user
            test_user = User.query.filter_by(email='test@seller.com').first()
            if not test_user:
                test_user = User(
                    username='testseller',
                    email='test@seller.com',
                    password='dummy_hash',
                    role='seller',
                    is_approved=True
                )
                db.session.add(test_user)
                db.session.commit()
                print("✓ Test seller created")
            
            # Simulate login session
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
                sess['_fresh'] = True
            
            print("✓ User session created")
            
            # Test 1: Check if the preview page loads
            print("\n=== Test 1: Preview Page Load ===")
            response = client.get('/seller/add_product_preview')
            print(f"GET /seller/add_product_preview: {response.status_code}")
            
            if response.status_code != 200:
                print(f"✗ Preview page failed to load: {response.status_code}")
                return False
            
            # Test 2: Simulate the exact JSON payload from frontend
            print("\n=== Test 2: JSON Payload Submission ===")
            
            payload = {
                "step1": {
                    "productName": "Frontend Test Product",
                    "category": "Electronics",
                    "subcategory": "Phones",
                    "price": "199.99",
                    "discountType": "percentage",
                    "discountPercentage": "15",
                    "voucherType": "standard",
                    "primaryImage": "/static/images/test.jpg",
                    "secondaryImage": "/static/images/test2.jpg",
                    "subitem": ["Feature1", "Feature2"]
                },
                "step2": {
                    "description": "Frontend test product description",
                    "materials": "Test materials",
                    "detailsFit": "Test fit details",
                    "sizeGuide": ["/static/images/size1.jpg"],
                    "certifications": ["/static/images/cert1.jpg"]
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "FRONT-001",
                            "color": "Blue",
                            "colorHex": "#0000FF",
                            "size": "L",
                            "stock": 15,
                            "lowStock": 3
                        }
                    ],
                    "totalStock": 15
                }
            }
            
            # Simulate the exact fetch request from frontend
            response = client.post(
                '/seller/add_product_preview',
                data=json.dumps(payload),
                content_type='application/json',
                headers={
                    'Accept': 'application/json, text/html'
                }
            )
            
            print(f"POST /seller/add_product_preview (JSON): {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 302:
                print(f"✓ Redirect to: {response.location}")
                
                # Check if product was actually saved
                saved_product = SellerProduct.query.filter_by(name='Frontend Test Product').first()
                if saved_product:
                    print(f"✓ Product saved successfully with ID: {saved_product.id}")
                    
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
                print(f"Response data: {response.get_data(as_text=True)[:500]}")
                return False
            
            # Test 3: Check session workflow data
            print("\n=== Test 3: Session Workflow Test ===")
            
            # First, populate session with workflow data (simulate multi-step flow)
            with client.session_transaction() as sess:
                sess['product_workflow'] = {
                    'step1': payload['step1'],
                    'step2': payload['step2'],
                    'step3': payload['step3']
                }
            
            # Now try POST without JSON payload (should use session data)
            response = client.post('/seller/add_product_preview')
            print(f"POST /seller/add_product_preview (session): {response.status_code}")
            
            if response.status_code == 302:
                print(f"✓ Session-based redirect to: {response.location}")
                
                # Check if product was saved
                saved_product = SellerProduct.query.filter_by(name='Frontend Test Product').first()
                if saved_product:
                    print(f"✓ Session-based product saved with ID: {saved_product.id}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Session test product cleaned up")
                else:
                    print("✗ Session-based product was not saved")
                    return False
            else:
                print(f"✗ Session-based submission failed: {response.status_code}")
                return False
            
            print("\n=== All frontend tests passed! ===")
            return True
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_frontend_flow()
    if not success:
        print("\n=== Frontend Flow Issues Detected ===")
        print("1. Check JavaScript console for errors")
        print("2. Verify session data is being set correctly")
        print("3. Check network requests in browser dev tools")
        print("4. Verify user authentication state")
        sys.exit(1)
    else:
        print("\nFrontend flow is working correctly!")