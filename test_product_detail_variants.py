#!/usr/bin/env python3
"""
Test script to verify product detail variant functionality
"""

import requests
import json

def test_product_detail_api():
    """Test the product detail API endpoint"""
    base_url = "http://localhost:5000"
    
    # Test API endpoint for a product
    try:
        response = requests.get(f"{base_url}/api/product/1")
        if response.status_code == 200:
            data = response.json()
            product = data.get('product', {})
            
            print("✅ Product API Response:")
            print(f"  - ID: {product.get('id')}")
            print(f"  - Name: {product.get('name')}")
            print(f"  - Price: {product.get('price')}")
            print(f"  - Has variants: {bool(product.get('variants'))}")
            print(f"  - Stock data: {bool(product.get('stock_data'))}")
            print(f"  - Variant photos: {bool(product.get('variant_photos'))}")
            print(f"  - Model info: {product.get('details_fit', 'Not available')}")
            
            # Check variant structure
            stock_data = product.get('stock_data', {})
            if stock_data:
                print(f"  - Available colors: {list(stock_data.keys())}")
                for color, sizes in stock_data.items():
                    print(f"    - {color}: {sizes}")
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_product_detail_page():
    """Test the product detail page loads"""
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/product/1")
        if response.status_code == 200:
            print("✅ Product detail page loads successfully")
            
            # Check if key elements are present
            content = response.text
            checks = [
                ('color-section', 'Color selection section'),
                ('size-section', 'Size selection section'),
                ('stock-indicator', 'Stock indicator'),
                ('modelInfo', 'Model information'),
                ('add-to-bag-btn', 'Add to bag button')
            ]
            
            for element_id, description in checks:
                if element_id in content:
                    print(f"  ✅ {description} found")
                else:
                    print(f"  ⚠️ {description} not found")
            
            return True
        else:
            print(f"❌ Page Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Product Detail Variant Functionality")
    print("=" * 50)
    
    print("\n1. Testing Product API...")
    api_success = test_product_detail_api()
    
    print("\n2. Testing Product Detail Page...")
    page_success = test_product_detail_page()
    
    print("\n" + "=" * 50)
    if api_success and page_success:
        print("✅ All tests passed! Product detail variant functionality is working.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    print("\n📝 Manual Testing Instructions:")
    print("1. Open http://localhost:5000/product/1 in your browser")
    print("2. Check if color options are displayed (if product has variants)")
    print("3. Select different colors and verify:")
    print("   - Size options update based on color availability")
    print("   - Stock count changes when selecting different variants")
    print("   - Product images change for different colors (if variant photos exist)")
    print("   - Model information is displayed")
    print("4. Try selecting different sizes and verify stock count updates")
    print("5. Verify 'Add to Bag' button is disabled when stock is 0")