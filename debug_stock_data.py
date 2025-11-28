#!/usr/bin/env python3
"""
Debug script to check stock data being passed to product detail template
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct
import json

def debug_stock_data():
    """Debug stock data for products"""
    app = create_app()
    
    with app.app_context():
        # Get first few products with variants
        products = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).limit(3).all()
        
        for product in products:
            print(f"\n=== Product: {product.name} (ID: {product.id}) ===")
            print(f"Status: {product.status}")
            print(f"Total Stock: {product.total_stock}")
            
            # Check variants
            variants = product.variants
            print(f"Raw variants: {variants}")
            print(f"Variants type: {type(variants)}")
            
            if isinstance(variants, str):
                try:
                    variants = json.loads(variants)
                    print(f"Parsed variants: {variants}")
                except:
                    print("Failed to parse variants JSON")
                    continue
            
            # Build stock_data like the route does
            stock_data = {}
            variant_photos = {}
            
            if isinstance(variants, list):
                print("Processing list format variants...")
                for variant in variants:
                    if isinstance(variant, dict):
                        color = variant.get('color', 'Unknown')
                        size = variant.get('size', 'OS')
                        stock = variant.get('stock', 0)
                        color_hex = variant.get('colorHex', '#000000')
                        
                        if color not in stock_data:
                            stock_data[color] = {}
                        
                        stock_data[color][size] = stock
                        
                        if color not in variant_photos:
                            variant_photos[color] = {
                                'primary': product.primary_image or '/static/image/banner.png',
                                'secondary': product.secondary_image or product.primary_image or '/static/image/banner.png',
                                'color_hex': color_hex
                            }
            
            print(f"Built stock_data: {stock_data}")
            print(f"Built variant_photos: {variant_photos}")
            
            # Check if any stock is available
            total_available = 0
            for color, sizes in stock_data.items():
                color_total = sum(sizes.values())
                total_available += color_total
                print(f"Color '{color}': {sizes} (total: {color_total})")
            
            print(f"Total available stock: {total_available}")

if __name__ == "__main__":
    debug_stock_data()