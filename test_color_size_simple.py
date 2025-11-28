#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct
import json

def test_color_size_selection():
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Testing Color and Size Selection...")
        
        # Get a product with variants
        with app.app_context():
            product = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).first()
            
            if not product:
                print("❌ No products with variants found")
                return
                
            print(f"📦 Testing product: {product.name} (ID: {product.id})")
        
        # Test the product detail page
        response = client.get(f'/product/{product.id}')
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Check for essential elements
            checks = [
                ('selectColor', 'Color selection function'),
                ('selectSize', 'Size selection function'),
                ('updateSizeOptions', 'Update size options function'),
                ('onclick="selectColor(this)"', 'Color button click handler'),
                ('class="color-option"', 'Color option buttons'),
                ('id="sizeOptions"', 'Size options container'),
            ]
            
            print("\n🔍 Checking essential elements:")
            for element, description in checks:
                if element in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    
            # Count color buttons
            color_count = html_content.count('class="color-option')
            print(f"\n🎨 Found {color_count} color buttons")
            
            if color_count > 0:
                print("✅ Color buttons are being generated")
            else:
                print("❌ No color buttons found")
                
        else:
            print(f"❌ Failed to load product page: {response.status_code}")

if __name__ == '__main__':
    test_color_size_selection()