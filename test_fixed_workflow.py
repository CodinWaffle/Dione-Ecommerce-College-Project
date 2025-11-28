#!/usr/bin/env python
"""
Test the fixed product creation workflow
"""

import requests
import json

# Test data with actual user input (not fallback values)
TEST_DATA = {
    "step1": {
        "productName": "Custom Designer Hoodie",
        "category": "Clothing",
        "subcategory": "Hoodies",
        "price": "79.99",
        "discountType": "percentage",
        "discountPercentage": "15",
        "voucherType": "",
        "lowStockThreshold": "3",
        "primaryImage": "data:image/jpeg;base64,/9j/test_image_data...",
        "secondaryImage": None,
        "subitem": []
    },
    "step2": {
        "description": "Premium designer hoodie with custom embroidery",
        "materials": "80% Cotton, 20% Polyester",
        "detailsFit": "Relaxed fit, pre-washed",
        "sizeGuide": ["XS", "S", "M", "L", "XL", "XXL"],
        "certifications": ["Ethically Made", "Sustainable Materials"]
    },
    "step3": {
        "variants": [
            {
                "sku": "CDH-GRY-01",
                "color": "Charcoal Grey",
                "colorHex": "#36454F",
                "lowStock": 3,
                "photo": "data:image/jpeg;base64,/9j/test_variant_data...",
                "sizeStocks": [
                    {"size": "S", "stock": 5},
                    {"size": "M", "stock": 12},
                    {"size": "L", "stock": 8},
                    {"size": "XL", "stock": 4}
                ]
            },
            {
                "sku": "CDH-BLK-02",
                "color": "Midnight Black",
                "colorHex": "#000000",
                "lowStock": 3,
                "photo": "data:image/jpeg;base64,/9j/test_variant2_data...",
                "sizeStocks": [
                    {"size": "S", "stock": 8},
                    {"size": "M", "stock": 15},
                    {"size": "L", "stock": 10},
                    {"size": "XL", "stock": 6}
                ]
            }
        ],
        "totalStock": 68
    }
}

def test_fixed_product_creation():
    """Test the fixed product creation with real user data"""
    try:
        print("=== Testing Fixed Product Creation ===")
        print(f"Testing with real user input:")
        print(f"  Product Name: {TEST_DATA['step1']['productName']}")
        print(f"  Category: {TEST_DATA['step1']['category']}")
        print(f"  Price: ${TEST_DATA['step1']['price']}")
        print(f"  Variants: {len(TEST_DATA['step3']['variants'])}")
        print(f"  Total Stock: {TEST_DATA['step3']['totalStock']}")
        print("")

        # Send the request
        response = requests.post(
            'http://localhost:5000/seller/add_product_stocks',
            json=TEST_DATA,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! Product created with ID: {result.get('product_id')}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('product_id')
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_with_fallback_values():
    """Test that fallback values are now rejected"""
    try:
        print("\n=== Testing Fallback Value Rejection ===")
        
        # Test data with fallback values that should be rejected
        fallback_data = {
            "step1": {
                "productName": "Premium T-Shirt",  # This should be rejected
                "category": "Fashion",
                "subcategory": "T-Shirts", 
                "price": "29.99"
            },
            "step2": {
                "description": "High-quality product with premium materials and modern design"
            },
            "step3": {
                "variants": [],
                "totalStock": 0
            }
        }

        response = requests.post(
            'http://localhost:5000/seller/add_product_stocks',
            json=fallback_data,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

        if response.status_code != 200:
            print("✅ SUCCESS! Fallback values were properly rejected")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
        else:
            print("❌ FAILED! Fallback values were not rejected")
            print(f"Response: {response.json()}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    # Test the fixed workflow
    product_id = test_fixed_product_creation()
    
    # Test fallback rejection
    test_with_fallback_values()
    
    if product_id:
        print(f"\n=== Verification ===")
        print(f"Product created with ID: {product_id}")
        print("Run 'python check_current_data.py' to see the new product in database")
    
    print("\n=== Test Complete ===")