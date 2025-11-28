#!/usr/bin/env python3
"""
Test script to verify variant storage and retrieval
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct

def test_variant_storage():
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Variant Storage and Retrieval")
        print("=" * 50)
        
        # Test data - multiple sizes and stocks per variant
        test_variants = [
            {
                "sku": "PS-B01",
                "color": "Cool white",
                "colorHex": "#f5f5f5",
                "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD...",
                "sizeStocks": [
                    {"size": "XS", "stock": 15, "lowStock": 5},
                    {"size": "S", "stock": 0, "lowStock": 20},
                    {"size": "M", "stock": 25, "lowStock": 5}
                ]
            },
            {
                "sku": "PS-B02", 
                "color": "Silver",
                "colorHex": "#d1d1d1",
                "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD...",
                "sizeStocks": [
                    {"size": "S", "stock": 10, "lowStock": 5},
                    {"size": "M", "stock": 20, "lowStock": 5},
                    {"size": "L", "stock": 8, "lowStock": 5}
                ]
            }
        ]
        
        # Create a test product
        test_product = SellerProduct(
            seller_id=1,
            name="Test Product with Multiple Variants",
            description="Testing variant storage",
            category="clothing",
            subcategory="shirts",
            price=29.99,
            variants=test_variants,
            total_stock=78,
            status='active'
        )
        
        try:
            # Save to database
            db.session.add(test_product)
            db.session.commit()
            print(f"✅ Product saved with ID: {test_product.id}")
            
            # Retrieve from database
            retrieved_product = SellerProduct.query.get(test_product.id)
            
            print(f"\n📦 Retrieved Product:")
            print(f"Name: {retrieved_product.name}")
            print(f"Variants type: {type(retrieved_product.variants)}")
            print(f"Variants data: {retrieved_product.variants}")
            
            if isinstance(retrieved_product.variants, list):
                print(f"✅ Variants stored as list (correct)")
                print(f"Number of variants: {len(retrieved_product.variants)}")
                
                for i, variant in enumerate(retrieved_product.variants):
                    print(f"\nVariant {i+1}:")
                    print(f"  Color: {variant.get('color')}")
                    print(f"  SKU: {variant.get('sku')}")
                    if 'sizeStocks' in variant:
                        print(f"  Size stocks: {variant['sizeStocks']}")
                        total_variant_stock = sum(ss.get('stock', 0) for ss in variant['sizeStocks'])
                        print(f"  Total stock for this variant: {total_variant_stock}")
            else:
                print(f"❌ Variants stored as: {type(retrieved_product.variants)}")
                if isinstance(retrieved_product.variants, str):
                    try:
                        parsed = json.loads(retrieved_product.variants)
                        print(f"✅ Can parse as JSON: {parsed}")
                    except:
                        print(f"❌ Cannot parse as JSON")
            
            # Clean up
            db.session.delete(test_product)
            db.session.commit()
            print(f"\n🧹 Test product cleaned up")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        print("\n" + "=" * 50)
        print("✅ Test complete")

if __name__ == "__main__":
    test_variant_storage()