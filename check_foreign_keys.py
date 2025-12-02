#!/usr/bin/env python3
"""Check foreign key constraints for cart functionality."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import User, SellerProduct, CartItem

def main():
    app = create_app()
    
    with app.app_context():
        print("=== Checking User Table ===")
        users = User.query.all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {getattr(user, 'role', 'N/A')}")
        
        print("\n=== Checking SellerProduct Table ===")
        products = SellerProduct.query.all()
        print(f"Total products: {len(products)}")
        for product in products[:5]:  # Show first 5 products
            print(f"Product ID: {product.id}, Name: {product.name}, Seller ID: {product.seller_id}")
        
        print("\n=== Checking Cart Items ===")
        cart_items = CartItem.query.all()
        print(f"Total cart items: {len(cart_items)}")
        for item in cart_items[-5:]:  # Show last 5 items
            print(f"Cart ID: {item.id}, User ID: {item.user_id}, Seller ID: {item.seller_id}, Product: {item.product_name}")
        
        print("\n=== Checking Foreign Key Consistency ===")
        # Check if seller_ids in products exist in users table
        invalid_sellers = []
        for product in products:
            if product.seller_id:
                seller_exists = User.query.get(product.seller_id)
                if not seller_exists:
                    invalid_sellers.append((product.id, product.seller_id))
        
        if invalid_sellers:
            print(f"Found {len(invalid_sellers)} products with invalid seller_id:")
            for prod_id, seller_id in invalid_sellers[:5]:
                print(f"  Product ID {prod_id} has seller_id {seller_id} (user doesn't exist)")
        else:
            print("All product seller_ids are valid")
        
        # Test specific values from the error
        test_user_id = 3
        test_seller_id = 1
        
        print(f"\n=== Testing Specific Values ===")
        user_3 = User.query.get(test_user_id)
        user_1 = User.query.get(test_seller_id)
        
        print(f"User ID {test_user_id} exists: {user_3 is not None}")
        if user_3:
            print(f"  Username: {user_3.username}, Email: {user_3.email}")
        
        print(f"User ID {test_seller_id} exists: {user_1 is not None}")
        if user_1:
            print(f"  Username: {user_1.username}, Email: {user_1.email}")

if __name__ == "__main__":
    main()