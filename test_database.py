#!/usr/bin/env python3
"""
Test script to check if the database is properly configured and cart functionality works
"""
from project import create_app, db
from project.models import SellerProduct, CartItem, User, ProductVariant
from sqlalchemy import text

def test_database():
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test database connection
            result = db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check if tables exist
            print("\n📊 Checking database tables...")
            
            # Check cart_items table
            cart_count = db.session.execute(text('SELECT COUNT(*) FROM cart_items')).scalar()
            print(f"✅ cart_items table exists with {cart_count} items")
            
            # Check users table
            user_count = db.session.execute(text('SELECT COUNT(*) FROM users')).scalar()
            print(f"✅ users table exists with {user_count} users")
            
            # Check products table
            product_count = db.session.execute(text('SELECT COUNT(*) FROM seller_products')).scalar()
            print(f"✅ seller_products table exists with {product_count} products")
            
            # List some sample products
            print("\n🛍️ Sample products:")
            products = db.session.query(SellerProduct).limit(5).all()
            for product in products:
                print(f"  - ID: {product.id}, Name: {product.name}, Price: {product.price}")
            
            # Test cart items
            print("\n🛒 Current cart items:")
            cart_items = db.session.query(CartItem).limit(10).all()
            if cart_items:
                for item in cart_items:
                    print(f"  - Cart ID: {item.id}, Product: {item.product_name}, Qty: {item.quantity}")
            else:
                print("  No cart items found")
                
            # Test product variants
            print("\n🎨 Sample product variants:")
            variants = db.session.query(ProductVariant).limit(5).all()
            for variant in variants:
                print(f"  - ID: {variant.id}, Product: {variant.product_id}, Variant: {variant.variant_name}")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("\nCreating tables...")
            db.create_all()
            print("✅ Tables created successfully")

if __name__ == '__main__':
    test_database()