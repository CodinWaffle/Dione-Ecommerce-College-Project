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
        print("🔍 Testing Current Color and Size Selection Implementation...")
        
        # Get a product with variants
        with app.app_context():
            product = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).first()
            
            if not product:
                print("❌ No products with variants found")
                return
                
            print(f"📦 Testing product: {product.name} (ID: {product.id})")
            
            # Parse variants
            if isinstance(product.variants, str):
                try:
                    variants = json.loads(product.variants)
                    print(f"✅ Successfully parsed JSON variants: {len(variants)} variants")
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse variants JSON")
                    return
            else:
                variants = product.variants
            
            # Show variant structure
            if variants:
                print(f"📝 First variant example: {variants[0]}")
                
                # Group by color
                colors = {}
                for variant in variants:
                    color = variant.get('color')
                    if color not in colors:
                        colors[color] = []
                    colors[color].append(variant)
                
                print(f"🎨 Available colors: {list(colors.keys())}")
                for color, color_variants in colors.items():
                    sizes = [v.get('size') for v in color_variants]
                    total_stock = sum(v.get('stock', 0) for v in color_variants)
                    print(f"   {color}: {sizes} (Total stock: {total_stock})")
        
        # Test the product detail page
        response = client.get(f'/product/{product.id}')
        print(f"\n📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Check for current implementation elements
            checks = [
                ('class="color-section"', 'Color section'),
                ('class="size-section"', 'Size section'),
                ('class="color-options"', 'Color options container'),
                ('class="size-options"', 'Size options container'),
                ('class="color-option"', 'Color option buttons'),
                ('selectColor', 'Color selection function'),
                ('selectSize', 'Size selection function'),
                ('updateSizeAvailability', 'Update size availability function'),
                ('data-color=', 'Color data attributes'),
                ('data-stock=', 'Stock data attributes'),
            ]
            
            print("\n🔍 Checking HTML elements:")
            for element, description in checks:
                if element in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Check if stock data is properly embedded
            if 'stock_data' in html_content:
                print("\n✅ Stock data found in template")
                
                # Look for color buttons in HTML
                color_count = html_content.count('class="color-option')
                print(f"🎨 Found {color_count} color option buttons in HTML")
                
                # Look for size placeholder
                if 'Select a color to view available sizes' in html_content:
                    print("✅ Size placeholder text found")
                else:
                    print("❌ Size placeholder text not found")
            
            # Check JavaScript functions
            js_functions = [
                'function selectColor',
                'function selectSize', 
                'function updateSizeAvailability',
                'function updateColorAvailability',
                'function updateStockDisplay'
            ]
            
            print("\n🔧 Checking JavaScript functions:")
            for func in js_functions:
                if func in html_content:
                    print(f"✅ {func}")
                else:
                    print(f"❌ {func}")
                    
        else:
            print(f"❌ Failed to load product page: {response.status_code}")

if __name__ == '__main__':
    test_color_size_selection()