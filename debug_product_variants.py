#!/usr/bin/env python3
"""
Debug script to check product variant data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct, Product

def debug_product_variants():
    app = create_app()
    
    with app.app_context():
        print("🔍 Debugging Product Variant Data")
        print("=" * 50)
        
        # Check SellerProduct variants
        print("\n📦 SellerProduct Data:")
        seller_products = SellerProduct.query.limit(5).all()
        
        for sp in seller_products:
            print(f"\nProduct ID: {sp.id}")
            print(f"Name: {sp.name}")
            print(f"Variants: {sp.variants}")
            print(f"Variants type: {type(sp.variants)}")
            
            if sp.variants:
                if isinstance(sp.variants, list):
                    print(f"Variant count: {len(sp.variants)}")
                    for i, variant in enumerate(sp.variants):
                        print(f"  Variant {i+1}: {variant}")
                elif isinstance(sp.variants, dict):
                    print(f"Variant keys: {list(sp.variants.keys())}")
                    for key, value in sp.variants.items():
                        print(f"  {key}: {value}")
            else:
                print("  No variants found")
        
        # Check legacy Product data
        print("\n📦 Legacy Product Data:")
        products = Product.query.limit(3).all()
        
        for p in products:
            print(f"\nProduct ID: {p.id}")
            print(f"Name: {p.name}")
            print(f"Stock: {p.stock}")
            print(f"Attributes: {p.attributes}")
        
        print("\n" + "=" * 50)
        print("✅ Debug complete")

if __name__ == "__main__":
    debug_product_variants()