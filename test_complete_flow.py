#!/usr/bin/env python3
"""
Complete Product Creation Test Script

This script tests the entire product creation flow by:
1. Simulating a user going through the multi-step form
2. Creating proper workflow data
3. Sending it to the backend
4. Verifying database storage

Run this script to ensure the complete flow works.
"""

import requests
import json
import mysql.connector
from mysql.connector import Error

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = 1  # Change this to match your test seller user

# Test data that matches the expected workflow structure
TEST_WORKFLOW_DATA = {
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
            },
            {
                "sku": "PTS-WHT-02", 
                "color": "White",
                "colorHex": "#ffffff",
                "lowStock": 3,
                "photo": "data:image/jpeg;base64,/9j/test_variant2_data...",
                "sizeStocks": [
                    {"size": "S", "stock": 12},
                    {"size": "M", "stock": 20},
                    {"size": "L", "stock": 6}
                ]
            }
        ],
        "totalStock": 71
    }
}

def test_database_connection():
    """Test if we can connect to the database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='dione_data',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("✅ Database connection successful")
            cursor = connection.cursor()
            
            # Check if seller_product_management table exists
            cursor.execute("SHOW TABLES LIKE 'seller_product_management'")
            result = cursor.fetchone()
            if result:
                print("✅ seller_product_management table found")
                
                # Check table structure
                cursor.execute("DESCRIBE seller_product_management")
                columns = cursor.fetchall()
                print("📋 Table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
                    
            else:
                print("❌ seller_product_management table not found")
                return False
                
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_product_creation_endpoint():
    """Test the product creation endpoint"""
    print("\n🧪 Testing product creation endpoint...")
    
    # Test with session to maintain cookies
    session = requests.Session()
    
    # First, try to access the application
    try:
        response = session.get(f"{BASE_URL}/")
        print(f"✅ Application accessible (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure Flask is running on http://localhost:5000")
        return False
    
    # Test the product stocks endpoint
    try:
        response = session.post(
            f"{BASE_URL}/seller/add_product_stocks",
            json=TEST_WORKFLOW_DATA,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📤 Sent request to /seller/add_product_stocks")
        print(f"📊 Response status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📄 Response data: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200 and response_data.get('success'):
                print("✅ Product creation successful!")
                return response_data.get('product_id')
            else:
                print(f"❌ Product creation failed: {response_data}")
                return None
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def verify_database_entry(product_id=None):
    """Verify that data was properly saved to database"""
    print("\n🔍 Verifying database entries...")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='dione_data',
            user='root',
            password=''
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Get all products (or specific one if product_id provided)
        if product_id:
            cursor.execute("SELECT * FROM seller_product_management WHERE id = %s", (product_id,))
        else:
            cursor.execute("SELECT * FROM seller_product_management ORDER BY id DESC LIMIT 5")
            
        products = cursor.fetchall()
        
        if not products:
            print("❌ No products found in database")
            return False
            
        print(f"📦 Found {len(products)} product(s):")
        for product in products:
            print(f"\n📋 Product ID: {product['id']}")
            print(f"   📝 Base SKU: {product.get('base_sku', 'N/A')}")
            print(f"   🏷️  Name: Stored in draft_data")
            print(f"   📊 Draft: {product.get('is_draft', 'Unknown')}")
            
            # Parse draft_data if it exists
            if product.get('draft_data'):
                try:
                    draft_data = json.loads(product['draft_data'])
                    step1 = draft_data.get('step1', {})
                    step3 = draft_data.get('step3', {})
                    
                    print(f"   📝 Product Name: {step1.get('productName', 'N/A')}")
                    print(f"   🏷️  Category: {step1.get('category', 'N/A')}")
                    print(f"   💰 Price: ${step1.get('price', 'N/A')}")
                    print(f"   📦 Variants: {len(step3.get('variants', []))}")
                    print(f"   📊 Total Stock: {step3.get('totalStock', 0)}")
                    
                except json.JSONDecodeError:
                    print("   ❌ Could not parse draft_data JSON")
                    
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Database verification error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Starting Complete Product Creation Flow Test")
    print("=" * 60)
    
    # Step 1: Test database connection
    if not test_database_connection():
        print("❌ Database tests failed. Exiting.")
        return
    
    # Step 2: Test product creation endpoint
    product_id = test_product_creation_endpoint()
    
    # Step 3: Verify database entry
    verify_database_entry(product_id)
    
    print("\n" + "=" * 60)
    print("🧪 Test complete!")
    
    if product_id:
        print("✅ SUCCESS: Product was created and saved to database")
        print(f"📦 Product ID: {product_id}")
    else:
        print("❌ FAILED: Product creation failed")
        print("🔍 Check the Flask application logs for more details")

if __name__ == "__main__":
    main()