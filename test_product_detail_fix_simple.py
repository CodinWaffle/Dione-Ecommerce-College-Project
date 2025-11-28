#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct
import json

def test_product_detail():
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Product Detail Fix...")
        
        # Get a product with variants
        product = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).first()
        
        if not product:
            print("❌ No products with variants found")
            return
            
        print(f"📦 Testing product: {product.name} (ID: {product.id})")
        print(f"📊 Raw variants field type: {type(product.variants)}")
        
        # Test the parsing logic
        variants_data = product.variants
        if isinstance(variants_data, str):
            try:
                variants_data = json.loads(variants_data)
                print(f"✅ Successfully parsed JSON string to: {type(variants_data)}")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"❌ Failed to parse JSON: {e}")
                variants_data = []
        
        print(f"📋 Parsed variants type: {type(variants_data)}")
        
        if isinstance(variants_data, list):
            print(f"📝 Number of variants: {len(variants_data)}")
            for i, variant in enumerate(variants_data[:3]):  # Show first 3
                if isinstance(variant, dict):
                    color = variant.get('color', 'Unknown')
                    size = variant.get('size', 'Unknown')
                    stock = variant.get('stock', 0)
                    print(f"   Variant {i+1}: {color} - {size} (Stock: {stock})")
        elif isinstance(variants_data, dict):
            print(f"📝 Variants dict keys: {list(variants_data.keys())}")
        
        print("✅ Product detail parsing test complete")

if __name__ == '__main__':
    test_product_detail()