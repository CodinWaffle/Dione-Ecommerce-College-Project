#!/usr/bin/env python3
"""
Test the actual add-to-cart HTTP endpoint.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app
import requests
import json

def test_cart_endpoint():
    """Test the add-to-cart endpoint via HTTP request."""
    
    print("=== Testing Add-to-Cart HTTP Endpoint ===")
    
    # Test data
    test_cases = [
        {
            'name': 'Basic add to cart',
            'data': {
                'product_id': 2,
                'color': 'Black',
                'size': 'M',
                'quantity': 1
            }
        },
        {
            'name': 'Add different color/size',
            'data': {
                'product_id': 2,
                'color': 'Wild Wind',
                'size': 'L',
                'quantity': 2
            }
        },
        {
            'name': 'Add different product',
            'data': {
                'product_id': 1,
                'color': 'Black',
                'size': 'S',
                'quantity': 1
            }
        }
    ]
    
    base_url = "http://localhost:5000"
    success_count = 0
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First visit homepage to establish session
        homepage_response = session.get(f"{base_url}/")
        if homepage_response.status_code != 200:
            print(f"❌ Failed to establish session: {homepage_response.status_code}")
            return False
        
        print("✅ Session established with Flask server")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_case['name']} ---")
            print(f"Data: {test_case['data']}")
            
            try:
                # Make the add-to-cart request
                response = session.post(
                    f"{base_url}/add-to-cart",
                    data=test_case['data'],
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'TestScript/1.0'
                    },
                    timeout=10
                )
                
                print(f"Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        if result.get('success'):
                            print(f"✅ SUCCESS: {result.get('message', 'No message')}")
                            print(f"   Cart count: {result.get('cart_count', 'N/A')}")
                            print(f"   Item added: {result.get('item', {}).get('product_name', 'N/A')}")
                            print(f"   Item quantity: {result.get('item', {}).get('quantity', 'N/A')}")
                            success_count += 1
                        else:
                            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
                            if 'error' in result:
                                print(f"   Error details: {result['error']}")
                            
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON response")
                        print(f"   Response text: {response.text[:300]}...")
                        
                elif response.status_code == 500:
                    print(f"❌ Server Error (500)")
                    print(f"   Response: {response.text[:300]}...")
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text[:300]}...")
                    
            except requests.exceptions.Timeout:
                print(f"❌ Request timed out")
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed - is Flask server running?")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
        
        print(f"\n=== Final Results ===")
        print(f"Successful tests: {success_count}/{len(test_cases)}")
        
        if success_count == len(test_cases):
            print("🎉 ALL TESTS PASSED - Add to cart functionality is working perfectly!")
        elif success_count > 0:
            print("⚠️ PARTIAL SUCCESS - Some cart operations worked")
        else:
            print("❌ ALL TESTS FAILED - Cart functionality has issues")
        
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

if __name__ == "__main__":
    test_cart_endpoint()