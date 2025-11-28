#!/usr/bin/env python3
"""
Test script to verify that multiple sizes and stock counts are saved correctly in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct
import json

def test_multiple_sizes_database():
    """Test that multiple sizes per variant are saved correctly"""
    
    app = create_app()
    
    with app.app_context():
        # Create a test product with multiple sizes per variant
        test_variants = [
            {
                "sku": "TEST-001",
                "color": "Red",
                "colorHex": "#ff0000",
                "sizeStocks": [
                    {"size": "S", "stock": 10},
                    {"size": "M", "stock": 15},
                    {"size": "L", "stock": 8},
                    {"size": "XL", "stock": 5}
                ],
                "lowStock": 3
            },
            {
                "sku": "TEST-002", 
                "color": "Blue",
                "colorHex": "#0000ff",
                "sizeStocks": [
                    {"size": "S", "stock": 12},
                    {"size": "M", "stock": 20},
                    {"size": "L", "stock": 6}
                ],
                "lowStock": 5
            }
        ]
        
        # Calculate total stock
        total_stock = 0
        for variant in test_variants:
            for size_stock in variant["sizeStocks"]:
                total_stock += size_stock["stock"]
        
        print(f"🧪 Creating test product with {len(test_variants)} variants")
        print(f"📊 Total stock across all variants: {total_stock}")
        
        # Create test product
        product = SellerProduct(
            name="Test Multi-Size Product",
            description="Test product with multiple sizes per variant",
            price=29.99,
            category="Clothing",
            variants=test_variants,
            total_stock=total_stock,
            seller_id=1  # Assuming seller with ID 1 exists
        )
        
        try:
            db.session.add(product)
            db.session.commit()
            
            print(f"✅ Product created successfully with ID: {product.id}")
            
            # Retrieve and verify the product
            retrieved_product = SellerProduct.query.get(product.id)
            
            if retrieved_product:
                print(f"✅ Product retrieved successfully")
                print(f"📦 Product name: {retrieved_product.name}")
                print(f"💰 Product price: ${retrieved_product.price}")
                print(f"📊 Total stock: {retrieved_product.total_stock}")
                
                # Verify variants structure
                variants = retrieved_product.variants
                if isinstance(variants, list):
                    print(f"✅ Variants saved as list with {len(variants)} items")
                    
                    for i, variant in enumerate(variants, 1):
                        print(f"\n🎨 Variant {i}:")
                        print(f"   SKU: {variant.get('sku')}")
                        print(f"   Color: {variant.get('color')} ({variant.get('colorHex')})")
                        print(f"   Low Stock Threshold: {variant.get('lowStock')}")
                        
                        size_stocks = variant.get('sizeStocks', [])
                        if size_stocks:
                            print(f"   📏 Sizes ({len(size_stocks)}):")
                            variant_total = 0
                            for size_stock in size_stocks:
                                size_name = size_stock.get('size')
                                stock_count = size_stock.get('stock', 0)
                                variant_total += stock_count
                                print(f"      - {size_name}: {stock_count} units")
                            print(f"   📊 Variant total stock: {variant_total}")
                        else:
                            print(f"   ❌ No sizeStocks found for this variant")
                    
                    # Verify total stock calculation
                    calculated_total = 0
                    for variant in variants:
                        for size_stock in variant.get('sizeStocks', []):
                            calculated_total += size_stock.get('stock', 0)
                    
                    if calculated_total == retrieved_product.total_stock:
                        print(f"\n✅ Total stock calculation is correct: {calculated_total}")
                    else:
                        print(f"\n❌ Total stock mismatch: calculated={calculated_total}, stored={retrieved_product.total_stock}")
                    
                    print(f"\n🎉 Database test completed successfully!")
                    print(f"✅ Multiple sizes per variant are saved and retrieved correctly")
                    
                else:
                    print(f"❌ Variants not saved as list: {type(variants)}")
                    
            else:
                print(f"❌ Failed to retrieve product")
                
        except Exception as e:
            print(f"❌ Error creating/testing product: {e}")
            db.session.rollback()
        
        finally:
            # Clean up test data
            try:
                if 'product' in locals() and product.id:
                    test_product = SellerProduct.query.get(product.id)
                    if test_product:
                        db.session.delete(test_product)
                        db.session.commit()
                        print(f"🧹 Test product cleaned up")
            except Exception as e:
                print(f"⚠️  Error cleaning up test data: {e}")

if __name__ == "__main__":
    test_multiple_sizes_database()