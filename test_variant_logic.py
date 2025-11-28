#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app
import json

def _to_int(value, default=0):
    """Helper function to convert to int safely"""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default

def test_variant_logic():
    """Test the variant processing logic directly"""
    print("🔍 Testing Variant Processing Logic...")
    
    # Simulate form data
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
    
    # Extract row indices (same logic as in the route)
    row_indices = set()
    for key in form_data.keys():
        parts = key.split('_')
        if len(parts) >= 2 and parts[-1].isdigit():
            row_indices.add(int(parts[-1]))
    
    print(f"📋 Found row indices: {sorted(row_indices)}")
    
    variants = []
    
    for idx in sorted(row_indices):
        # Get basic variant info
        sku = form_data.get(f'sku_{idx}', '').strip()
        color = form_data.get(f'color_{idx}', '').strip()
        color_hex = form_data.get(f'color_picker_{idx}', '#000000')
        low_stock = _to_int(form_data.get(f'lowStock_{idx}'), 0)
        
        print(f"\n🎨 Processing row {idx}:")
        print(f"   SKU: {sku}")
        print(f"   Color: {color}")
        print(f"   Color Hex: {color_hex}")
        print(f"   Low Stock: {low_stock}")
        
        # Parse per-size stocks sent as JSON
        size_stocks_raw = form_data.get(f'sizeStocks_{idx}')
        print(f"   Size Stocks Raw: {size_stocks_raw}")
        
        if size_stocks_raw:
            try:
                parsed = json.loads(size_stocks_raw)
                print(f"   Parsed JSON: {parsed}")
                
                # ensure parsed is a list of dicts with size and stock
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and 'size' in item:
                            # Create a separate variant entry for each size
                            variant_data = {
                                'sku': sku,
                                'color': color,
                                'colorHex': color_hex,
                                'size': str(item.get('size')),
                                'stock': _to_int(item.get('stock', 0), 0),
                                'lowStock': low_stock,
                            }
                            print(f"   📦 Created variant: {variant_data}")
                            
                            # Only add if there's meaningful data
                            if variant_data['color'] or variant_data['size'] or variant_data['stock'] > 0:
                                variants.append(variant_data)
                                print(f"   ✅ Added variant to list")
                            else:
                                print(f"   ❌ Skipped variant (no meaningful data)")
            except Exception as e:
                print(f"   ❌ Error parsing JSON: {e}")
        else:
            print(f"   ℹ️ No sizeStocks data for row {idx}")
    
    # Calculate total stock
    total_stock = sum(v['stock'] for v in variants)
    
    print(f"\n📊 Final Results:")
    print(f"   Total variants created: {len(variants)}")
    print(f"   Total stock: {total_stock}")
    
    # Group by color for display
    color_groups = {}
    for variant in variants:
        color = variant.get('color')
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append(variant)
    
    for color, color_variants in color_groups.items():
        print(f"\n🎨 {color}:")
        color_total = 0
        for variant in color_variants:
            size = variant.get('size')
            stock = variant.get('stock', 0)
            color_total += stock
            print(f"   📏 Size {size}: {stock} units")
        print(f"   📦 Total for {color}: {color_total}")

if __name__ == '__main__':
    test_variant_logic()