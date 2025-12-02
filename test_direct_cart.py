#!/usr/bin/env python3
"""
Direct test of add-to-cart functionality without using requests library
"""
from project import create_app, db
from project.models import SellerProduct, CartItem, User
from flask import session
import json

def create_minimal_test_data():
    """Create minimal test data"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check if test product exists
            product = db.session.query(SellerProduct).first()
            if not product:
                print("Creating test product...")
                product = SellerProduct(
                    name='Test Product',
                    price=25.99,
                    description='Test description',
                    seller_id=1,  # Assuming seller exists
                    category='test',
                    is_active=True,
                    variants='[{"variant_name": "Red", "stock": {"S": 10, "M": 15}}, {"variant_name": "Blue", "stock": {"S": 5, "M": 12}}]'
                )
                db.session.add(product)
                db.session.commit()
                print(f"✅ Created product with ID: {product.id}")
            else:
                print(f"✅ Using existing product: {product.name} (ID: {product.id})")
            
            return product.id
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            return None

def test_add_to_cart_direct():
    """Test add to cart functionality directly"""
    app = create_app('development')
    
    with app.app_context():
        try:
            from project.routes.main_routes import add_to_cart
            from flask import request
            import json
            
            # Simulate the request
            test_data = {
                'product_id': 1,
                'color': 'Red',
                'size': 'M',
                'quantity': 1
            }
            
            with app.test_request_context(
                '/add-to-cart',
                method='POST',
                data=json.dumps(test_data),
                content_type='application/json'
            ):
                result = add_to_cart()
                print(f"🧪 Direct test result: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Error in direct test: {e}")
            import traceback
            traceback.print_exc()
            return None

def check_database_structure():
    """Check if all required tables exist"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check cart_items table structure
            from sqlalchemy import text
            result = db.session.execute(text("DESCRIBE cart_items")).fetchall()
            print("📋 cart_items table structure:")
            for row in result:
                print(f"  {row[0]}: {row[1]}")
            
            # Count existing items
            count = db.session.query(CartItem).count()
            print(f"🛒 Current cart items count: {count}")
            
            # Check for test products
            product_count = db.session.query(SellerProduct).count()
            print(f"📦 Products count: {product_count}")
            
            if product_count == 0:
                print("⚠️  No products found. Creating test product...")
                return create_minimal_test_data()
            else:
                first_product = db.session.query(SellerProduct).first()
                print(f"✅ Found product: {first_product.name} (ID: {first_product.id})")
                return first_product.id
                
        except Exception as e:
            print(f"❌ Database structure check failed: {e}")
            return None

if __name__ == '__main__':
    print("🔍 Checking cart functionality directly...\n")
    
    # Check database structure
    product_id = check_database_structure()
    print()
    
    if product_id:
        # Test add to cart directly
        print("🧪 Testing add to cart functionality...")
        result = test_add_to_cart_direct()
        
        print("\n📊 Test completed")
    else:
        print("❌ Cannot proceed without a product")