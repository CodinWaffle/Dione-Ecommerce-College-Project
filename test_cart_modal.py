#!/usr/bin/env python3
"""
Test script to verify cart modal enhancements work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    
    app = create_app()
    
    with app.test_client() as client:
        print("Testing cart modal enhancements...")
        
        # Test the seller products API
        response = client.get('/api/seller/8/products?limit=4&exclude_id=1')
        
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            
            print(f"✅ Seller products API works: {len(products)} products returned")
            
            for product in products:
                print(f"  - {product.get('name')} (₱{product.get('price')})")
        else:
            print(f"❌ Seller products API failed: {response.status_code}")
        
        # Test the main products API to check if sellerId is included
        response = client.get('/api/products?limit=2')
        
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            
            print(f"\n✅ Main products API works: {len(products)} products returned")
            
            for product in products:
                seller_id = product.get('sellerId')
                print(f"  - {product.get('name')} (Seller ID: {seller_id})")
                
                if seller_id:
                    print("    ✅ Seller ID included in product data")
                else:
                    print("    ❌ Seller ID missing from product data")
        else:
            print(f"❌ Main products API failed: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()