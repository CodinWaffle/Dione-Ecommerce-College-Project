#!/usr/bin/env python3
"""
Debug the current issues with data saving and variant functionality
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_current_issues():
    """Debug the current data saving and variant issues"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🔍 DEBUGGING CURRENT ISSUES")
            print("=" * 50)
            
            client = app.test_client()
            
            # Get seller ID 8 (the one having issues)
            seller = User.query.get(8)  # averycruz011@gmail.com
            if not seller:
                print("❌ Seller ID 8 not found")
                return False
            
            # Login as that seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✅ Testing with seller: {seller.email}")
            
            # Test 1: Check current session workflow
            print("\n📋 TEST 1: Session Workflow Check")
            print("-" * 40)
            
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                print(f"Current workflow in session: {workflow}")
            
            # Test 2: Simulate the exact flow that's failing
            print("\n🧪 TEST 2: Complete Flow Simulation")
            print("-" * 40)
            
            # Step 1: Basic info
            basic_data = {
                'productName': 'Debug Flow Test',
                'category': 'Electronics',
                'subcategory': 'Gadgets',
                'price': '99.99',
                'discountType': 'percentage',
                'discountPercentage': '5',
                'voucherType': 'SAVE5',
                'primaryImage': '/static/images/test.jpg'
            }
            
            response = client.post('/seller/add_product', data=basic_data)
            print(f"Step 1 response: {response.status_code}")
            
            # Check session after step 1
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step1 = workflow.get('step1', {})
                print(f"Step 1 data in session: {step1}")
            
            # Step 2: Description
            description_data = {
                'description': 'Debug test description',
                'materials': 'Test materials',
                'detailsFit': 'Test fit'
            }
            
            response = client.post('/seller/add_product_description', data=description_data)
            print(f"Step 2 response: {response.status_code}")
            
            # Check session after step 2
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step2 = workflow.get('step2', {})
                print(f"Step 2 data in session: {step2}")
            
            # Step 3: Stocks (this is where the issue might be)
            print("\n📦 TEST 3: Stock Data Processing")
            print("-" * 40)
            
            # Test with the exact data structure that should work
            stocks_data = {
                'sku_0': 'DEBUG-001',
                'color_0': 'Blue',
                'color_picker_0': '#0000FF',
                'lowStock_0': '5',
                'sizeStocks_0': json.dumps([
                    {'size': 'M', 'stock': 10},
                    {'size': 'L', 'stock': 15}
                ])
            }
            
            print(f"Sending stock data: {stocks_data}")
            
            response = client.post('/seller/add_product_stocks', data=stocks_data)
            print(f"Step 3 response: {response.status_code}")
            
            # Check session after step 3
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step3 = workflow.get('step3', {})
                print(f"Step 3 data in session: {step3}")
            
            # Step 4: Preview and submit
            print("\n👁️ TEST 4: Preview and Submit")
            print("-" * 40)
            
            response = client.post('/seller/add_product_preview')
            print(f"Preview response: {response.status_code}")
            print(f"Preview location: {response.location}")
            
            if response.status_code == 302:
                # Check what was actually saved
                saved_product = SellerProduct.query.filter_by(seller_id=seller.id).order_by(SellerProduct.id.desc()).first()
                
                if saved_product:
                    print(f"\n📊 SAVED PRODUCT ANALYSIS")
                    print("-" * 40)
                    print(f"ID: {saved_product.id}")
                    print(f"Name: '{saved_product.name}' (expected: 'Debug Flow Test')")
                    print(f"Category: '{saved_product.category}' (expected: 'Electronics')")
                    print(f"Subcategory: '{saved_product.subcategory}' (expected: 'Gadgets')")
                    print(f"Price: {saved_product.price} (expected: ~95.00)")
                    print(f"Description: '{saved_product.description}' (expected: 'Debug test description')")
                    print(f"Materials: '{saved_product.materials}' (expected: 'Test materials')")
                    print(f"Total Stock: {saved_product.total_stock} (expected: 25)")
                    print(f"Variants: {saved_product.variants}")
                    
                    # Identify specific issues
                    issues = []
                    if saved_product.name == '-' or not saved_product.name:
                        issues.append("Name not saved correctly")
                    if saved_product.category == '-' or not saved_product.category:
                        issues.append("Category not saved correctly")
                    if saved_product.price == 0:
                        issues.append("Price not saved correctly")
                    if not saved_product.description:
                        issues.append("Description not saved correctly")
                    if saved_product.total_stock == 0:
                        issues.append("Stock not saved correctly")
                    
                    if issues:
                        print(f"\n❌ ISSUES IDENTIFIED:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print(f"\n✅ All data saved correctly!")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("🧹 Test product cleaned up")
                    
                else:
                    print("❌ No product was saved")
            
            # Test 5: Check if the issue is with the route processing
            print("\n🔧 TEST 5: Route Processing Analysis")
            print("-" * 40)
            
            # Check if the issue is in the add_product_preview route
            # by sending a direct JSON payload
            payload = {
                "step1": {
                    "productName": "Direct JSON Test",
                    "category": "Electronics",
                    "price": "199.99"
                },
                "step2": {
                    "description": "Direct JSON description"
                },
                "step3": {
                    "variants": [
                        {
                            "sku": "JSON-001",
                            "color": "Red",
                            "colorHex": "#FF0000",
                            "sizeStocks": [
                                {"size": "M", "stock": 5}
                            ]
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
            
            print(f"Direct JSON response: {response.status_code}")
            
            if response.status_code == 302:
                saved_product = SellerProduct.query.filter_by(name='Direct JSON Test').first()
                if saved_product:
                    print("✅ Direct JSON payload works correctly")
                    print(f"  - Name: '{saved_product.name}'")
                    print(f"  - Category: '{saved_product.category}'")
                    print(f"  - Price: {saved_product.price}")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                else:
                    print("❌ Direct JSON payload failed to save")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_current_issues()