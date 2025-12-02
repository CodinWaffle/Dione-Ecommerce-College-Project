#!/usr/bin/env python3
"""
Test the fixed add to cart functionality
"""
import requests
import json
import time

def test_fixed_cart_functionality():
    """Test the add to cart with the fixes applied"""
    base_url = 'http://localhost:5000'
    
    # Test data with a product that exists
    test_data = {
        'product_id': 1,  # The Pirouette Skort that exists
        'color': 'Navy Blue',  # Different color to avoid conflicts
        'size': 'S',
        'quantity': 1
    }
    
    try:
        print(f"🧪 Testing fixed add-to-cart functionality...")
        print(f"📦 Test payload: {json.dumps(test_data, indent=2)}")
        
        # Make the request
        response = requests.post(
            f'{base_url}/add-to-cart',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"📄 Response JSON: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ SUCCESS: Item added to cart successfully!")
                print(f"   - Cart count: {data.get('cart_count', 'N/A')}")
                print(f"   - Item details: {json.dumps(data.get('item', {}), indent=4)}")
            else:
                print(f"❌ FAILURE: {data.get('error', 'Unknown error')}")
                
        except json.JSONDecodeError:
            print(f"❌ Non-JSON response: {response.text}")
            
        return response.status_code == 200 and response.json().get('success', False)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_cart_page():
    """Test the cart page to see current items"""
    try:
        print(f"\n🛒 Testing cart page...")
        response = requests.get('http://localhost:5000/cart', timeout=10)
        
        print(f"📡 Cart page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Cart page accessible")
            # Check if response contains cart items
            content = response.text
            if 'cart-item' in content.lower() or 'cart item' in content.lower():
                print("✅ Cart appears to have items")
            else:
                print("ℹ️  Cart appears to be empty or items not rendered")
        else:
            print(f"❌ Cart page error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cart page test failed: {e}")

def test_multiple_add_scenarios():
    """Test various scenarios"""
    scenarios = [
        {
            'name': 'Standard Add',
            'data': {'product_id': 1, 'color': 'Red', 'size': 'M', 'quantity': 1}
        },
        {
            'name': 'Different Size',
            'data': {'product_id': 1, 'color': 'Blue', 'size': 'L', 'quantity': 2}
        },
        {
            'name': 'Invalid Product',
            'data': {'product_id': 999, 'color': 'Red', 'size': 'M', 'quantity': 1}
        }
    ]
    
    print(f"\n🧪 Testing multiple scenarios...")
    
    success_count = 0
    for scenario in scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        try:
            response = requests.post(
                'http://localhost:5000/add-to-cart',
                headers={'Content-Type': 'application/json'},
                json=scenario['data'],
                timeout=5
            )
            
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Success: {data.get('message', 'Added to cart')}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(scenarios)} scenarios passed")

if __name__ == '__main__':
    print("🚀 Testing FIXED cart functionality...\n")
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    # Test main functionality
    success = test_fixed_cart_functionality()
    
    # Test cart page
    test_cart_page()
    
    # Test multiple scenarios
    test_multiple_add_scenarios()
    
    print(f"\n📊 FINAL RESULT:")
    if success:
        print("✅ Add to cart functionality is working correctly!")
    else:
        print("❌ Add to cart functionality still has issues.")
        
    print("\n🎯 Next steps:")
    print("1. Open http://localhost:5000 in browser")
    print("2. Navigate to a product page")  
    print("3. Select color and size")
    print("4. Click 'ADD TO BAG' button")
    print("5. Verify the cart popup appears with item details")