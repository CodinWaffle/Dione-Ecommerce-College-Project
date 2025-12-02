#!/usr/bin/env python3
"""
Test the API to see if colors are being returned correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    import json
    
    app = create_app()
    
    with app.test_client() as client:
        print("Testing API color variants...")
        
        # Test the products API
        response = client.get('/api/products?limit=3')
        
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            
            print(f"API returned {len(products)} products")
            
            for product in products:
                print(f"\nProduct: {product.get('name')} (ID: {product.get('id')})")
                colors = product.get('colors', [])
                variants = product.get('variants', [])
                
                print(f"  Colors: {colors}")
                print(f"  Variants: {len(variants)} items")
                
                for variant in variants:
                    color = variant.get('color')
                    colorHex = variant.get('colorHex')
                    image = variant.get('image')
                    print(f"    - {color} ({colorHex}): {image}")
        else:
            print(f"API request failed with status {response.status_code}")
            print(response.get_data(as_text=True))

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()