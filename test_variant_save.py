#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct
import json

def test_variant_save():
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Testing Variant Save Functionality...")
        
        # Simulate form data that would be sent from the frontend
        form_data = {
            'sku_1': 'TEST-001',
            'color_1': 'Blue',
            'color_picker_1': '#0066cc',
            'lowStock_1': '5',
            'sizeStocks_1': json.dumps([
                {'size': 'S', 'stock': 10},
                {'size': 'M', 'stock': 15},
                {'size': 'L', 'stock': 8},
                {'size': 'XL', 'stock': 5}
            ]),
            'sku_2': 'TEST-002', 
            'color_2': 'Red',
            'color_picker_2': '#cc0000',
            'lowStock_2': '3',
            'sizeStocks_2': json.dumps([
                {'size': 'S', 'stock': 12},
                {'size': 'M', 'stock': 20},
                {'size': 'L', 'stock': 6}
            ])
        }
        
        print("📋 Form data being sent:")
        for key, value in form_data.items():
            if 'sizeStocks' in key:
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {value}")
        
        # Set up session data for the product workflow
        with client.session_transaction() as sess:
            sess['product_workflow'] = {
                'step1': {
                    'productName': 'Test Product',
                    'category': 'Clothing',
                    'price': '29.99'
                },
                'step2': {
                    'description': 'Test description'
                }
            }
        
        # Test the add_product_stocks route
        response = client.post('/seller/add_product_stocks', data=form_data)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect to preview
            print("✅ Successfully processed variant data")
            
            # Check what was stored in the session
            with client.session_transaction() as sess:
                step3_data = sess.get('product_workflow', {}).get('step3', {})
                variants = step3_data.get('variants', [])
                
                print(f"📝 Number of variants created: {len(variants)}")
                
                # Group variants by color to show the structure
                color_groups = {}
                for variant in variants:
                    color = variant.get('color')
                    if color not in color_groups:
                        color_groups[color] = []
                    color_groups[color].append(variant)
                
                for color, color_variants in color_groups.items():
                    print(f"\n🎨 Color: {color}")
                    total_stock = 0
                    for variant in color_variants:
                        size = variant.get('size')
                        stock = variant.get('stock', 0)
                        total_stock += stock
                        print(f"   📏 Size {size}: {stock} units")
                    print(f"   📦 Total stock for {color}: {total_stock}")
                
                total_stock = step3_data.get('totalStock', 0)
                print(f"\n📊 Total stock across all variants: {total_stock}")
                
        else:
            print(f"❌ Unexpected response status: {response.status_code}")
            print(response.get_data(as_text=True))

if __name__ == '__main__':
    test_variant_save()