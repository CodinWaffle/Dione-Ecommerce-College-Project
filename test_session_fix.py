#!/usr/bin/env python3

import requests
import json
import time

def test_session_storage_fix():
    """Test the session storage and validation fixes"""
    
    # First, let's simulate some session data being set
    # This would normally happen in step 1 and step 2 of the workflow
    
    test_data = {
        "productName": "Custom Designer Hoodie",
        "category": "Clothing", 
        "subcategory": "Hoodies",
        "description": "A comfortable premium hoodie with custom design",
        "price": "79.99",
        "variants": [
            {
                "color": "Red",
                "primaryImage": "test-image-data",
                "secondaryImage": None,
                "sizeStocks": [
                    {"size": "M", "stock": 25},
                    {"size": "L", "stock": 20}
                ]
            }
        ],
        "totalStock": 45
    }
    
    print("=== Testing Session Storage Fix ===")
    print("Test data:", json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/seller/add_product_stocks",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Form data processed correctly")
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_session_storage_fix()