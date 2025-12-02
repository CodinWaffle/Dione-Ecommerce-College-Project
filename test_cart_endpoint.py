#!/usr/bin/env python3
"""
Simple test to verify the add-to-cart endpoint functionality
"""
import requests
import json

def test_add_to_cart():
    """Test the add to cart endpoint"""
    base_url = 'http://localhost:5000'
    
    # Test payload
    test_data = {
        'product_id': 1,
        'color': 'Red',
        'size': 'M', 
        'quantity': 1
    }
    
    try:
        print(f"🧪 Testing add-to-cart endpoint with data: {test_data}")
        
        # Make POST request to add-to-cart endpoint
        response = requests.post(
            f'{base_url}/add-to-cart',
            headers={
                'Content-Type': 'application/json',
            },
            json=test_data,
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"📄 Response Text: {response.text}")
        else:
            print(f"❌ Error Response: {response.text}")
            
        return response.status_code, response.text
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure Flask server is running on http://localhost:5000")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None

def test_home_page():
    """Test if the home page is accessible"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"🏠 Home page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Home page is accessible")
        else:
            print(f"❌ Home page error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Home page test failed: {e}")

def test_cart_page():
    """Test if the cart page is accessible"""
    try:
        response = requests.get('http://localhost:5000/cart', timeout=5)
        print(f"🛒 Cart page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Cart page is accessible")
        else:
            print(f"❌ Cart page error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Cart page test failed: {e}")

if __name__ == '__main__':
    print("🚀 Starting cart functionality tests...\n")
    
    # Test home page
    test_home_page()
    print()
    
    # Test cart page 
    test_cart_page()
    print()
    
    # Test add to cart
    status, response = test_add_to_cart()
    
    print("\n📊 Test Summary:")
    if status == 200:
        print("✅ Add to cart functionality appears to be working")
    elif status == 404:
        print("❌ Product not found - need to create test products")
    elif status == 400:
        print("❌ Bad request - check request parameters")
    elif status is None:
        print("❌ Cannot connect to server")
    else:
        print(f"❌ Unexpected status code: {status}")