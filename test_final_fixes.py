#!/usr/bin/env python3

import requests
import json

def test_final_fixes():
    """Test that all our fixes work correctly"""
    
    # Complete product data that should be saved as active
    complete_product_data = {
        "step1": {
            "productName": "Designer Premium Hoodie",
            "category": "Clothing", 
            "subcategory": "Hoodies",
            "price": "89.99"
        },
        "step2": {
            "description": "A high-quality designer hoodie with premium materials"
        },
        "step3": {
            "variants": [
                {
                    "color": "Navy Blue",
                    "primaryImage": "test-image-data",
                    "secondaryImage": None,
                    "sizeStocks": [
                        {"size": "M", "stock": 15},
                        {"size": "L", "stock": 12}
                    ]
                }
            ],
            "totalStock": 27
        }
    }
    
    print("=== Testing Complete Product Creation ===")
    print("Product Name:", complete_product_data["step1"]["productName"])
    print("Total Stock:", complete_product_data["step3"]["totalStock"])
    print("Expected: Active status, ₱89.99 price, single creation")
    print()
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/seller/add_product_stocks",
            json=complete_product_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Product saved successfully")
            print("✅ Check product list for:")
            print("  - Single entry (no duplicates)")
            print("  - ₱89.99 price format")
            print("  - 'Active' status (not 'Draft')")
        else:
            print(f"❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_final_fixes()