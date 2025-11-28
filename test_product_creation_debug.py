#!/usr/bin/env python3
"""
Debug script to test the complete product creation flow and identify issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct, User
from sqlalchemy import text
import json

def test_product_creation_flow():
    """Test the complete product creation flow"""
    app = create_app('development')
    
    with app.app_context():
        print("🔍 Testing Product Creation Flow")
        print("=" * 50)
        
        # 1. Check database structure
        print("\n1. Checking database structure...")
        try:
            # Check if SellerProduct table exists and its columns (MySQL/MariaDB)
            result = db.session.execute(text("DESCRIBE seller_product"))
            columns = result.fetchall()
            
            print(f"✅ SellerProduct table found with {len(columns)} columns:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
                
        except Exception as e:
            print(f"❌ Error checking database structure: {e}")
            print("   Trying to create tables...")
            try:
                db.create_all()
                print("✅ Tables created successfully")
            except Exception as create_error:
                print(f"❌ Error creating tables: {create_error}")
                return
        
        # 2. Check if we have any test sellers
        print("\n2. Checking for test sellers...")
        sellers = User.query.filter_by(role='seller').all()
        print(f"Found {len(sellers)} sellers in database")
        
        if not sellers:
            print("❌ No sellers found. Creating a test seller...")
            test_seller = User(
                username='test_seller',
                email='test@seller.com',
                role='seller',
                is_approved=True
            )
            test_seller.set_password('password123')
            db.session.add(test_seller)
            db.session.commit()
            sellers = [test_seller]
            print("✅ Test seller created")
        
        seller = sellers[0]
        print(f"Using seller: {seller.username} (ID: {seller.id})")
        
        # 3. Test creating a product with all fields
        print("\n3. Testing product creation...")
        try:
            test_product = SellerProduct(
                seller_id=seller.id,
                name="Test Product",
                description="Test description",
                category="Clothing",
                subcategory="Shirts",
                price=29.99,
                compare_at_price=39.99,
                discount_type="percentage",
                discount_value=25.0,
                voucher_type="SAVE25",
                materials="100% Cotton",
                details_fit="Regular fit",
                primary_image="/static/image/test.jpg",
                secondary_image="/static/image/test2.jpg",
                total_stock=100,
                low_stock_threshold=10,
                variants=[
                    {
                        "sku": "TEST-001-RED-M",
                        "color": "Red",
                        "colorHex": "#FF0000",
                        "sizeStocks": [
                            {"size": "S", "stock": 10},
                            {"size": "M", "stock": 15},
                            {"size": "L", "stock": 20}
                        ],
                        "lowStock": 5
                    },
                    {
                        "sku": "TEST-001-BLUE-M",
                        "color": "Blue", 
                        "colorHex": "#0000FF",
                        "sizeStocks": [
                            {"size": "S", "stock": 12},
                            {"size": "M", "stock": 18},
                            {"size": "L", "stock": 25}
                        ],
                        "lowStock": 5
                    }
                ],
                attributes={
                    "subitems": ["Premium", "Eco-friendly"],
                    "size_guides": ["Size chart available"],
                    "certifications": ["OEKO-TEX Standard 100"]
                }
            )
            
            db.session.add(test_product)
            db.session.commit()
            
            print("✅ Product created successfully!")
            print(f"   Product ID: {test_product.id}")
            print(f"   Name: {test_product.name}")
            print(f"   Price: ${test_product.price}")
            print(f"   Total Stock: {test_product.total_stock}")
            print(f"   Variants: {len(test_product.variants) if test_product.variants else 0}")
            
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            db.session.rollback()
            return
        
        # 4. Test retrieving and displaying the product
        print("\n4. Testing product retrieval...")
        try:
            retrieved_product = SellerProduct.query.filter_by(id=test_product.id).first()
            if retrieved_product:
                print("✅ Product retrieved successfully!")
                print(f"   All fields populated: {bool(retrieved_product.name and retrieved_product.description)}")
                print(f"   Variants stored: {len(retrieved_product.variants) if retrieved_product.variants else 0}")
                print(f"   Attributes stored: {bool(retrieved_product.attributes)}")
                
                # Check variants structure
                if retrieved_product.variants:
                    print("\n   Variant details:")
                    for i, variant in enumerate(retrieved_product.variants):
                        print(f"     Variant {i+1}: {variant}")
                        
                # Check attributes structure  
                if retrieved_product.attributes:
                    print(f"\n   Attributes: {retrieved_product.attributes}")
                    
            else:
                print("❌ Product not found after creation!")
                
        except Exception as e:
            print(f"❌ Error retrieving product: {e}")
        
        # 5. Test the to_dict method (used by frontend)
        print("\n5. Testing to_dict serialization...")
        try:
            product_dict = retrieved_product.to_dict()
            print("✅ Product serialized successfully!")
            print(f"   Dict keys: {list(product_dict.keys())}")
            print(f"   Has variants: {'variants' in product_dict}")
            print(f"   Has attributes: {'attributes' in product_dict}")
            
        except Exception as e:
            print(f"❌ Error serializing product: {e}")
        
        # 6. Check all products for the seller
        print("\n6. Checking all seller products...")
        all_products = SellerProduct.query.filter_by(seller_id=seller.id).all()
        print(f"Total products for seller: {len(all_products)}")
        
        for product in all_products:
            print(f"   - {product.name} (ID: {product.id}, Stock: {product.total_stock})")
        
        print("\n" + "=" * 50)
        print("✅ Product creation flow test completed!")

def test_photo_upload_simulation():
    """Test photo upload functionality simulation"""
    print("\n🖼️  Testing Photo Upload Simulation")
    print("=" * 50)
    
    # This would normally test actual file upload, but we'll simulate the process
    print("1. Simulating photo upload process...")
    
    # Check if upload directory exists
    upload_dir = "project/static/uploads"
    if not os.path.exists(upload_dir):
        print(f"❌ Upload directory doesn't exist: {upload_dir}")
        print("   Creating upload directory...")
        os.makedirs(upload_dir, exist_ok=True)
        print("✅ Upload directory created")
    else:
        print("✅ Upload directory exists")
    
    # Check permissions
    try:
        test_file = os.path.join(upload_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Upload directory is writable")
    except Exception as e:
        print(f"❌ Upload directory not writable: {e}")
    
    print("✅ Photo upload simulation completed!")

if __name__ == "__main__":
    test_product_creation_flow()
    test_photo_upload_simulation()