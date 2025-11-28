#!/usr/bin/env python3
"""
Test the JSON form submission fix
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_json_form_submission_fix():
    """Test both JSON and form submissions to add_product_stocks"""
    
    try:
        from project import create_app, db
        from project.models import User
        
        app = create_app()
        
        with app.app_context():
            print("🧪 TESTING JSON FORM SUBMISSION FIX")
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
            
            # Test 1: JSON submission (should return JSON response)
            print("\n📤 TEST 1: JSON Submission")
            print("-" * 30)
            
            json_data = {
                'variants': [
                    {
                        'sku': 'JSON-TEST-001',
                        'color': 'Blue',
                        'sizes': [
                            {'size': 'M', 'stock': 10}
                        ]
                    }
                ],
                'totalStock': 10
            }
            
            response = client.post(
                '/seller/add_product_stocks',
                data=json.dumps(json_data),
                content_type='application/json'
            )
            
            print(f"JSON response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.get_json()
                    print(f"JSON response data: {response_data}")
                    print("✅ JSON submission handled correctly")
                except:
                    print("❌ Response is not valid JSON")
                    print(f"Response text: {response.get_data(as_text=True)}")
                    return False
            else:
                print(f"❌ JSON submission failed: {response.status_code}")
                return False
            
            # Test 2: Form submission (should redirect)
            print("\n📝 TEST 2: Form Submission")
            print("-" * 30)
            
            form_data = {
                'sku_0': 'FORM-TEST-001',
                'color_0': 'Red',
                'color_picker_0': '#FF0000',
                'lowStock_0': '5',
                'sizeStocks_0': json.dumps([
                    {'size': 'L', 'stock': 15}
                ])
            }
            
            response = client.post('/seller/add_product_stocks', data=form_data)
            
            print(f"Form response status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"Form redirect location: {response.location}")
                print("✅ Form submission handled correctly")
            else:
                print(f"❌ Form submission failed: {response.status_code}")
                return False
            
            # Test 3: Malformed JSON (should handle gracefully)
            print("\n❌ TEST 3: Malformed JSON")
            print("-" * 30)
            
            response = client.post(
                '/seller/add_product_stocks',
                data='{"invalid": json}',  # Malformed JSON
                content_type='application/json'
            )
            
            print(f"Malformed JSON response: {response.status_code}")
            
            if response.status_code in [200, 400]:
                print("✅ Malformed JSON handled gracefully")
            else:
                print(f"❌ Malformed JSON not handled properly")
                return False
            
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ JSON submissions return JSON responses")
            print("✅ Form submissions redirect properly")
            print("✅ Error handling works correctly")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_json_form_submission_fix()
    
    if success:
        print("\n🚀 JSON FORM SUBMISSION FIX SUCCESSFUL!")
        print("The route now properly handles both JSON and form submissions.")
    else:
        print("\n❌ JSON FORM SUBMISSION FIX FAILED")
        print("There are still issues with the form submission handling.")
    
    sys.exit(0 if success else 1)