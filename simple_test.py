#!/usr/bin/env python3
"""
Simple Product Creation Test

This script tests the product creation endpoint directly.
"""

import requests
import json

# Test data
TEST_DATA = {
    "step1": {
        "productName": "Test Premium T-Shirt",
        "category": "Fashion",
        "subcategory": "T-Shirts",
        "price": "49.99",
        "discountType": "percentage",
        "discountPercentage": "10",
        "voucherType": "",
        "lowStockThreshold": "5",
        "primaryImage": "data:image/jpeg;base64,/9j/test_image_data...",
        "secondaryImage": None,
        "subitem": []
    },
    "step2": {
        "description": "Premium quality cotton t-shirt with modern fit",
        "materials": "100% Organic Cotton",
        "detailsFit": "Modern fit, pre-shrunk",
        "sizeGuide": ["XS", "S", "M", "L", "XL"],
        "certifications": ["OEKO-TEX", "Organic Cotton"]
    },
    "step3": {
        "variants": [
            {
                "sku": "PTS-BLK-01",
                "color": "Black",
                "colorHex": "#000000",
                "lowStock": 5,
                "photo": "data:image/jpeg;base64,/9j/test_variant_data...",
                "sizeStocks": [
                    {"size": "S", "stock": 10},
                    {"size": "M", "stock": 15},
                    {"size": "L", "stock": 8}
                ]
            }
        ],
        "totalStock": 33
    }
}

def test_endpoint():
    """Test the product creation endpoint"""
    try:
        print("🧪 Testing product creation endpoint...")
        print(f"📤 Sending data: {json.dumps(TEST_DATA, indent=2)}")
        
        response = requests.post(
            'http://localhost:5000/seller/add_product_stocks',
            json=TEST_DATA,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Test-Script/1.0'
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"✅ Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ SUCCESS: Endpoint is working!")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is Flask running on localhost:5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()