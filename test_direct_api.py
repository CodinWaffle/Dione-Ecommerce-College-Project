#!/usr/bin/env python
"""Direct API testing without authentication"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint that doesn't require authentication"""
    try:
        response = requests.get('http://localhost:5000/seller/debug/recent-products')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {len(data.get('products', []))} products in database:")
            for product in data.get('products', []):
                print(f"  - Product ID: {product.get('id')}")
                print(f"    Base SKU: {product.get('base_sku')}")
                print(f"    Draft Data: {product.get('draft_data_preview', 'N/A')}")
                print(f"    Is Draft: {product.get('is_draft')}")
                print("    ---")
        else:
            print(f"Failed to get data: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_test_page():
    """Test the test page endpoint"""
    try:
        response = requests.get('http://localhost:5000/seller/test-page')
        print(f"\nTest page status: {response.status_code}")
        print(f"Test page accessible: {'Yes' if response.status_code == 200 else 'No'}")
        
    except Exception as e:
        print(f"Test page error: {e}")

if __name__ == "__main__":
    print("=== Testing Direct API Endpoints ===")
    test_debug_endpoint()
    test_test_page()
    print("\n=== Test Complete ===")