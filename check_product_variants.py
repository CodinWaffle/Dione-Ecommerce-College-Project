#!/usr/bin/env python3
"""
Simple script to check what product variants exist in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from project.models import SellerProduct, db
    import json
    
    app = create_app()
    
    with app.app_context():
        print("Checking product variants in database...")
        
        # Get all products with variants
        products = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).limit(5).all()
        
        print(f"Found {len(products)} products with variants")
        
        for product in products:
            print(f"\nProduct: {product.name}")
            print(f"Variants: {product.variants}")
            
            if product.variants:
                try:
                    if isinstance(product.variants, str):
                        variants_data = json.loads(product.variants)
                    else:
                        variants_data = product.variants
                    
                    print(f"Parsed variants: {variants_data}")
                    
                    # Extract colors
                    colors = []
                    if isinstance(variants_data, list):
                        for variant in variants_data:
                            if isinstance(variant, dict) and 'color' in variant:
                                colors.append(variant['color'])
                    elif isinstance(variants_data, dict):
                        colors = list(variants_data.keys())
                    
                    print(f"Colors found: {colors}")
                    
                except Exception as e:
                    print(f"Error parsing variants: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()