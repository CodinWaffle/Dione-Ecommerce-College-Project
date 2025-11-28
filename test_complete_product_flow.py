#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct, User, Seller
import json

def test_complete_product_flow():
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Complete Product Creation Flow...")
        
        # Create a test seller user if it doesn't exist
        test_user = User.query.filter_by(email='test@seller.com').first()
        if not test_user:
            test_user = User(
                email='test@seller.com',
                role='seller',
                is_approved=True
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Create seller profile
            seller_profile = Seller(
                user_id=test_user.id,
                business_name='Test Store',
                business_address='123 Test St',
                business_city='Test City'
            )
            db.session.add(seller_profile)
            db.session.commit()
        
        # Create a product with variants directly in the database
        variants_data = [
            {
                'sku': 'TEST-001',
                'color': 'Blue',
                'colorHex': '#0066cc',
                'size': 'S',
                'stock': 10,
                'lowStock': 5
            },
            {
                'sku': 'TEST-001',
                'color': 'Blue', 
                'colorHex': '#0066cc',
                'size': 'M',
                'stock': 15,
                'lowStock': 5
            },
            {
                'sku': 'TEST-001',
                'color': 'Blue',
                'colorHex': '#0066cc', 
                'size': 'L',
                'stock': 8,
                'lowStock': 5
            },
            {
                'sku': 'TEST-002',
                'color': 'Red',
                'colorHex': '#cc0000',
                'size': 'S', 
                'stock': 12,
                'lowStock': 3
            },
            {
                'sku': 'TEST-002',
                'color': 'Red',
                'colorHex': '#cc0000',
                'size': 'M',
                'stock': 20,
                'lowStock': 3
            }
        ]
        
        # Calculate total stock
        total_stock = sum(v['stock'] for v in variants_data)
        
        # Create the product
        product = SellerProduct(
            seller_id=test_user.id,
            name='Test Multi-Variant Product',
            description='A test product with multiple colors and sizes',
            category='Clothing',
            subcategory='Shirts',
            price=29.99,
            total_stock=total_stock,
            variants=variants_data,  # This should be stored as JSON
            status='active'
        )
        
        db.session.add(product)
        db.session.commit()
        
        print(f"✅ Created product with ID: {product.id}")
        print(f"📦 Total stock: {total_stock}")
        
        # Verify the product was saved correctly
        saved_product = SellerProduct.query.get(product.id)
        if saved_product:
            print(f"✅ Product retrieved successfully")
            print(f"📝 Product name: {saved_product.name}")
            print(f"📊 Stored variants type: {type(saved_product.variants)}")
            
            # Check if variants is a string (JSON) or already parsed
            if isinstance(saved_product.variants, str):
                try:
                    parsed_variants = json.loads(saved_product.variants)
                    print(f"✅ Successfully parsed JSON variants")
                    variants_to_display = parsed_variants
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse variants JSON")
                    variants_to_display = []
            else:
                print(f"✅ Variants already parsed as: {type(saved_product.variants)}")
                variants_to_display = saved_product.variants
            
            print(f"📝 Number of variants: {len(variants_to_display)}")
            
            # Group variants by color
            color_groups = {}
            for variant in variants_to_display:
                color = variant.get('color')
                if color not in color_groups:
                    color_groups[color] = []
                color_groups[color].append(variant)
            
            for color, color_variants in color_groups.items():
                print(f"\n🎨 Color: {color}")
                color_total = 0
                for variant in color_variants:
                    size = variant.get('size')
                    stock = variant.get('stock', 0)
                    color_total += stock
                    print(f"   📏 Size {size}: {stock} units")
                print(f"   📦 Total for {color}: {color_total}")
        
        # Test the product detail route to make sure it can handle the new structure
        print(f"\n🔍 Testing product detail route...")
        with app.test_client() as client:
            response = client.get(f'/product/{product.id}')
            print(f"📊 Product detail response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Product detail page loads successfully")
                
                # Check if the HTML contains variant information
                html_content = response.get_data(as_text=True)
                if 'Blue' in html_content and 'Red' in html_content:
                    print("✅ Color variants found in HTML")
                else:
                    print("❌ Color variants not found in HTML")
            else:
                print(f"❌ Product detail page failed to load")
        
        print(f"\n🧹 Cleaning up test data...")
        # Clean up
        db.session.delete(saved_product)
        db.session.commit()
        print("✅ Test complete")

if __name__ == '__main__':
    test_complete_product_flow()