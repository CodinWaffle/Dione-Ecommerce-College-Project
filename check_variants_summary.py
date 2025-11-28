#!/usr/bin/env python3
"""
Check existing products and their variant structures - summary
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct

def check_variants_summary():
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Product Variants Summary")
        print("=" * 50)
        
        # Get first 3 products
        products = SellerProduct.query.limit(3).all()
        
        if not products:
            print("No products found in database")
            return
        
        print(f"Checking first {len(products)} products")
        
        for product in products:
            print(f"\n📦 Product ID: {product.id} - {product.name}")
            
            if product.variants:
                if isinstance(product.variants, str):
                    print(f"⚠️  Stored as STRING")
                    try:
                        parsed = json.loads(product.variants)
                        print(f"✅ Parseable JSON with {len(parsed)} variants")
                        # Show structure of first variant
                        if parsed and len(parsed) > 0:
                            first_variant = parsed[0]
                            print(f"   First variant keys: {list(first_variant.keys())}")
                            if 'sizeStocks' in first_variant:
                                print(f"   Has sizeStocks: {len(first_variant['sizeStocks'])} sizes")
                    except Exception as e:
                        print(f"❌ Cannot parse: {e}")
                        
                elif isinstance(product.variants, list):
                    print(f"✅ Stored as LIST with {len(product.variants)} variants")
                    if product.variants and len(product.variants) > 0:
                        first_variant = product.variants[0]
                        print(f"   First variant keys: {list(first_variant.keys())}")
                        if 'sizeStocks' in first_variant:
                            print(f"   Has sizeStocks: {len(first_variant['sizeStocks'])} sizes")
                else:
                    print(f"❓ Stored as: {type(product.variants)}")
            else:
                print("   No variants data")
        
        print("\n" + "=" * 50)
        print("✅ Summary complete")

if __name__ == "__main__":
    check_variants_summary()