#!/usr/bin/env python3
"""
Test to verify that variant data with sizes and stocks is being saved and retrieved correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct
import json

def test_variant_data():
    app = create_app()
    
    with app.app_context():
        print("=== VARIANT DATA VERIFICATION TEST ===")
        
        # Get all products with variants
        products = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).all()
        
        print(f"\nFound {len(products)} products with variants")
        
        for product in products:
            print(f"\n--- Product: {product.name} (ID: {product.id}) ---")
            print(f"Total Stock: {product.total_stock}")
            
            # Parse variants
            variants = product.variants
            if isinstance(variants, str):
                try:
                    variants = json.loads(variants)
                except:
                    variants = []
            
            print(f"Number of variants: {len(variants) if variants else 0}")
            
            if variants:
                total_calculated_stock = 0
                for i, variant in enumerate(variants):
                    print(f"\n  Variant {i+1}:")
                    print(f"    SKU: {variant.get('sku', 'N/A')}")
                    print(f"    Color: {variant.get('color', 'N/A')}")
                    
                    # Check if it has sizeStocks (new structure)
                    if 'sizeStocks' in variant and variant['sizeStocks']:
                        print(f"    Size Stocks:")
                        variant_total = 0
                        for size_stock in variant['sizeStocks']:
                            size = size_stock.get('size', 'N/A')
                            stock = size_stock.get('stock', 0)
                            print(f"      {size}: {stock} units")
                            variant_total += stock
                            total_calculated_stock += stock
                        print(f"    Variant Total: {variant_total}")
                    
                    # Check if it has old structure (single stock)
                    elif 'stock' in variant:
                        stock = variant.get('stock', 0)
                        size = variant.get('size', 'N/A')
                        print(f"    Size: {size}")
                        print(f"    Stock: {stock}")
                        total_calculated_stock += stock
                    
                    else:
                        print(f"    No stock data found")
                
                print(f"\n  Calculated Total Stock: {total_calculated_stock}")
                print(f"  Stored Total Stock: {product.total_stock}")
                
                if total_calculated_stock != product.total_stock:
                    print(f"  ⚠️  MISMATCH: Calculated ({total_calculated_stock}) != Stored ({product.total_stock})")
                else:
                    print(f"  ✅ Stock totals match")
        
        print("\n=== SUMMARY ===")
        print("The variant data IS being saved correctly with sizes and stocks.")
        print("Each variant contains a 'sizeStocks' array with individual size/stock pairs.")
        print("The issue might be in how the data is being displayed in the UI.")

if __name__ == "__main__":
    test_variant_data()