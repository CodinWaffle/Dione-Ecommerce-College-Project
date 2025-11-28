#!/usr/bin/env python3
"""
Check existing products and their variant structures
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct

def check_existing_variants():
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Existing Product Variants")
        print("=" * 50)
        
        # Get all products
        products = SellerProduct.query.all()
        
        if not products:
            print("No products found in database")
            return
        
        print(f"Found {len(products)} products")
        
        for product in products:
            print(f"\n📦 Product ID: {product.id}")
            print(f"Name: {product.name}")
            print(f"Variants type: {type(product.variants)}")
            
            if product.variants:
                if isinstance(product.variants, str):
                    print(f"⚠️  Variants stored as string: {product.variants[:100]}...")
                    try:
                        parsed = json.loads(product.variants)
                        print(f"✅ Can parse as JSON. Type: {type(parsed)}")
                        if isinstance(parsed, list):
                            print(f"   Contains {len(parsed)} variants")
                            for i, variant in enumerate(parsed[:2]):  # Show first 2
                                print(f"   Variant {i+1}: {variant}")
                    except Exception as e:
                        print(f"❌ Cannot parse as JSON: {e}")
                        
                elif isinstance(product.variants, list):
                    print(f"✅ Variants stored as list with {len(product.variants)} items")
                    for i, variant in enumerate(product.variants[:2]):  # Show first 2
                        print(f"   Variant {i+1}: {variant}")
                        
                else:
                    print(f"❓ Variants stored as: {type(product.variants)}")
                    print(f"   Value: {product.variants}")
            else:
                print("   No variants data")
        
        print("\n" + "=" * 50)
        print("✅ Check complete")

if __name__ == "__main__":
    check_existing_variants()