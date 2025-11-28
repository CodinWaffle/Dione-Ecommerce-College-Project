#!/usr/bin/env python3
"""
Debug script to check variant data in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct, User, Seller
import json

def debug_variant_data():
    app = create_app()
    
    with app.app_context():
        print("🔍 Debugging Variant Data in Database")
        print("=" * 50)
        
        # Get all seller products
        products = SellerProduct.query.all()
        print(f"Found {len(products)} seller products in database")
        
        for i, product in enumerate(products[:5]):  # Check first 5 products
            print(f"\n📦 Product {i+1}: {product.name} (ID: {product.id})")
            print(f"   Status: {product.status}")
            print(f"   Price: ₱{product.price}")
            print(f"   Seller ID: {product.seller_id}")
            
            # Check variants data
            print(f"   Variants (raw): {product.variants}")
            print(f"   Variants type: {type(product.variants)}")
            
            if product.variants:
                try:
                    if isinstance(product.variants, str):
                        variants_data = json.loads(product.variants)
                        print(f"   Variants (parsed): {variants_data}")
                        print(f"   Variants structure: {type(variants_data)}")
                        
                        if isinstance(variants_data, list):
                            print(f"   Number of variants: {len(variants_data)}")
                            for j, variant in enumerate(variants_data):
                                print(f"     Variant {j+1}: {variant}")
                                if isinstance(variant, dict):
                                    color = variant.get('color', 'No color')
                                    size = variant.get('size', 'No size')
                                    stock = variant.get('stock', 0)
                                    size_stocks = variant.get('sizeStocks', [])
                                    print(f"       Color: {color}")
                                    print(f"       Size: {size}")
                                    print(f"       Stock: {stock}")
                                    print(f"       Size Stocks: {size_stocks}")
                        elif isinstance(variants_data, dict):
                            print(f"   Variant keys: {list(variants_data.keys())}")
                            for key, value in variants_data.items():
                                print(f"     {key}: {value}")
                    else:
                        print(f"   Variants is not a string: {product.variants}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {e}")
                except Exception as e:
                    print(f"   ❌ Error processing variants: {e}")
            else:
                print("   ⚠️  No variants data found")
            
            print("-" * 30)
        
        # Check if there are any products with variants
        products_with_variants = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).all()
        print(f"\n📊 Summary:")
        print(f"   Total products: {len(products)}")
        print(f"   Products with variants: {len(products_with_variants)}")
        
        if len(products_with_variants) == 0:
            print("\n🔧 Creating sample product with variants for testing...")
            create_sample_product_with_variants()

def create_sample_product_with_variants():
    """Create a sample product with proper variant data"""
    try:
        # Find a seller
        seller = User.query.filter_by(role='seller').first()
        if not seller:
            print("❌ No seller found in database")
            return
        
        # Create sample variants data
        sample_variants = [
            {
                "color": "Red",
                "colorHex": "#FF0000",
                "sizeStocks": [
                    {"size": "S", "stock": 10},
                    {"size": "M", "stock": 15},
                    {"size": "L", "stock": 8}
                ]
            },
            {
                "color": "Blue",
                "colorHex": "#0000FF",
                "sizeStocks": [
                    {"size": "S", "stock": 5},
                    {"size": "M", "stock": 12},
                    {"size": "L", "stock": 7}
                ]
            },
            {
                "color": "Black",
                "colorHex": "#000000",
                "sizeStocks": [
                    {"size": "S", "stock": 20},
                    {"size": "M", "stock": 25},
                    {"size": "L", "stock": 18},
                    {"size": "XL", "stock": 10}
                ]
            }
        ]
        
        # Create or update a product
        product = SellerProduct.query.first()
        if not product:
            product = SellerProduct(
                seller_id=seller.id,
                name="Sample T-Shirt with Variants",
                description="A sample t-shirt with multiple color and size variants",
                category="clothing",
                subcategory="tops",
                price=29.99,
                status="active"
            )
            db.session.add(product)
        
        # Set variants data
        product.variants = json.dumps(sample_variants)
        
        # Calculate total stock
        total_stock = 0
        for variant in sample_variants:
            for size_stock in variant.get('sizeStocks', []):
                total_stock += size_stock.get('stock', 0)
        
        product.total_stock = total_stock
        
        db.session.commit()
        print(f"✅ Created/updated sample product with ID: {product.id}")
        print(f"   Variants: {product.variants}")
        print(f"   Total stock: {product.total_stock}")
        
    except Exception as e:
        print(f"❌ Error creating sample product: {e}")
        db.session.rollback()

if __name__ == "__main__":
    debug_variant_data()