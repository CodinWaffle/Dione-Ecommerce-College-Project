#!/usr/bin/env python3
"""
Check current database structure and existing data for variants
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct, Product
import json

def check_database():
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE STRUCTURE CHECK ===")
        
        # Check if we have any products
        seller_products = SellerProduct.query.all()
        print(f"\nSellerProduct table has {len(seller_products)} records")
        
        if seller_products:
            print("\nSample SellerProduct records:")
            for i, product in enumerate(seller_products[:3]):
                print(f"\nProduct {i+1}:")
                print(f"  ID: {product.id}")
                print(f"  Name: {product.name}")
                print(f"  Total Stock: {product.total_stock}")
                print(f"  Variants type: {type(product.variants)}")
                print(f"  Variants content: {product.variants}")
                if product.variants:
                    try:
                        if isinstance(product.variants, str):
                            parsed = json.loads(product.variants)
                        else:
                            parsed = product.variants
                        print(f"  Parsed variants: {json.dumps(parsed, indent=2)}")
                    except Exception as e:
                        print(f"  Error parsing variants: {e}")
        
        # Check Product table too
        products = Product.query.all()
        print(f"\nProduct table has {len(products)} records")
        
        if products:
            print("\nSample Product records:")
            for i, product in enumerate(products[:3]):
                print(f"\nProduct {i+1}:")
                print(f"  ID: {product.id}")
                print(f"  Name: {product.name}")
                print(f"  Stock: {product.stock}")
                print(f"  Attributes: {product.attributes}")
        
        # Check table structure
        print("\n=== TABLE COLUMNS ===")
        print("\nSellerProduct columns:")
        for column in SellerProduct.__table__.columns:
            print(f"  {column.name}: {column.type}")
            
        print("\nProduct columns:")
        for column in Product.__table__.columns:
            print(f"  {column.name}: {column.type}")

if __name__ == "__main__":
    check_database()