#!/usr/bin/env python3

import requests
import json

def test_fixes():
    """Simple test to verify our fixes work"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Test payload with real user data (not fallback values)
    real_user_data = {
        "productName": "Custom Designer Hoodie",
        "category": "Clothing", 
        "subcategory": "Hoodies",
        "subItems": "Designer Collection",
        "productDescription": "A comfortable premium hoodie with custom design",
        "basePrice": "79.99",
        "variants": [
            {
                "color": "Red",
                "primaryImage": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMC...",
                "secondaryImage": None,
                "sizeStocks": [
                    {"size": "M", "stock": 25},
                    {"size": "L", "stock": 20},
                    {"size": "XL", "stock": 23}
                ]
            }
        ],
        "totalStock": 68
    }
    
    # Test payload with fallback values (should be rejected)
    fallback_data = {
        "productName": "Premium T-Shirt", 
        "category": "Fashion",
        "subcategory": "Clothing",
        "subItems": "Basic Collection", 
        "productDescription": "A premium quality t-shirt",
        "basePrice": "29.99",
        "variants": [
            {
                "color": "Blue",
                "primaryImage": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMC...",
                "secondaryImage": None,
                "sizeStocks": [
                    {"size": "S", "stock": 10}
                ]
            }
        ],
        "totalStock": 10
    }
    
    print("=== Testing Backend Validation ===")
    
    # Test 1: Real user data should be accepted
    print("\n1. Testing with real user data...")
    try:
        response = requests.post(
            f"{base_url}/seller/add_product_stocks",
            json=real_user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ SUCCESS: Real user data accepted")
        else:
            print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Fallback data should be rejected  
    print("\n2. Testing with fallback values...")
    try:
        response = requests.post(
            f"{base_url}/seller/add_product_stocks", 
            json=fallback_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ SUCCESS: Fallback values properly rejected")
        else:
            print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_fixes()