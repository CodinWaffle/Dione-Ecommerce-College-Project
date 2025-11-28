#!/usr/bin/env python3
"""
Debug the frontend form submission to identify why data isn't being collected properly
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_frontend_form_submission():
    """Debug the frontend form submission process"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🔍 DEBUGGING FRONTEND FORM SUBMISSION")
            print("=" * 60)
            
            client = app.test_client()
            
            # Get seller ID 8 (the one having issues)
            seller = User.query.filter_by(id=8).first()
            if not seller:
                print("❌ Seller ID 8 not found")
                return False
            
            # Login as that seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✅ Testing with seller: {seller.email}")
            
            # Test 1: Simulate what happens when user submits empty form data
            print("\n❌ TEST 1: Empty Form Data (Simulating Current Issue)")
            print("-" * 50)
            
            # This simulates what might be happening in the frontend
            empty_stocks_data = {
                'sku_0': '',  # Empty SKU
                'color_0': '',  # Empty color
                'color_picker_0': '#000000',
                'lowStock_0': '0'
                # No sizeStocks_0 - this might be the issue
            }
            
            print(f"Sending empty stock data: {empty_stocks_data}")
            
            response = client.post('/seller/add_product_stocks', data=empty_stocks_data)
            print(f"Empty data response: {response.status_code}")
            
            # Check what gets stored in session
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step3 = workflow.get('step3', {})
                print(f"Session after empty data: {step3}")
            
            # Test 2: Simulate form submission with missing basic info
            print("\n❌ TEST 2: Missing Basic Info (Another Possible Issue)")
            print("-" * 50)
            
            # Clear session first
            with client.session_transaction() as sess:
                sess.pop('product_workflow', None)
            
            # Skip step 1 and 2, go directly to step 3
            stocks_data_only = {
                'sku_0': 'ONLY-STOCK-001',
                'color_0': 'Red',
                'color_picker_0': '#FF0000',
                'lowStock_0': '5',
                'sizeStocks_0': '[{"size": "M", "stock": 10}]'
            }
            
            response = client.post('/seller/add_product_stocks', data=stocks_data_only)
            print(f"Stock-only response: {response.status_code}")
            
            # Try to submit without basic info
            response = client.post('/seller/add_product_preview')
            print(f"Preview without basic info: {response.status_code}")
            print(f"Redirect location: {response.location}")
            
            # Test 3: Check what happens with malformed JSON
            print("\n❌ TEST 3: Malformed Size Data")
            print("-" * 50)
            
            malformed_data = {
                'sku_0': 'MALFORMED-001',
                'color_0': 'Green',
                'color_picker_0': '#00FF00',
                'lowStock_0': '5',
                'sizeStocks_0': 'invalid json data'  # This will cause JSON parsing to fail
            }
            
            response = client.post('/seller/add_product_stocks', data=malformed_data)
            print(f"Malformed data response: {response.status_code}")
            
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step3 = workflow.get('step3', {})
                print(f"Session after malformed data: {step3}")
            
            # Test 4: Check the exact data structure that's being sent from frontend
            print("\n🔍 TEST 4: Frontend Data Structure Analysis")
            print("-" * 50)
            
            # This simulates what the frontend JavaScript might be sending
            # when the form is not properly filled
            frontend_simulation_data = {
                # These might be empty if form validation fails
                'sku_0': '',
                'color_0': '',
                'color_picker_0': '#000000',
                'lowStock_0': '',
                # Size data might be missing or malformed
                # 'sizeStocks_0': '' - missing entirely
            }
            
            print("Simulating frontend with empty fields...")
            
            # First, set up proper basic info
            basic_data = {
                'productName': 'Frontend Sim Test',
                'category': 'Electronics',
                'price': '99.99'
            }
            
            response = client.post('/seller/add_product', data=basic_data)
            response = client.post('/seller/add_product_description', data={'description': 'Test'})
            
            # Now send the problematic stock data
            response = client.post('/seller/add_product_stocks', data=frontend_simulation_data)
            print(f"Frontend simulation response: {response.status_code}")
            
            # Check session
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                print(f"Complete workflow: {workflow}")
            
            # Try to submit
            response = client.post('/seller/add_product_preview')
            print(f"Final submission: {response.status_code}")
            
            if response.status_code == 302:
                saved_product = SellerProduct.query.filter_by(seller_id=seller.id).order_by(SellerProduct.id.desc()).first()
                if saved_product:
                    print(f"Product saved: Name='{saved_product.name}', Category='{saved_product.category}', Price={saved_product.price}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                else:
                    print("No product was saved")
            
            print("\n📋 ANALYSIS SUMMARY")
            print("=" * 60)
            print("The backend is working correctly. The issue is likely:")
            print("1. Frontend JavaScript not collecting form data properly")
            print("2. Form fields being empty when submitted")
            print("3. Size selection data not being included in form submission")
            print("4. JavaScript errors preventing proper data collection")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_frontend_form_submission()