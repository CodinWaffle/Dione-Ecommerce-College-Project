#!/usr/bin/env python3
"""Test cart item creation step by step to identify the issue."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import User, SellerProduct, CartItem
from datetime import datetime

def main():
    app = create_app()
    
    with app.app_context():
        print("=== Testing Cart Item Creation ===")
        
        # Test data from the error logs
        user_id = 3  # precioushanny22
        seller_id = 1  # Avery_Cruz
        product_id = 1  # Pirouette Skort
        
        print(f"Testing with user_id={user_id}, seller_id={seller_id}, product_id={product_id}")
        
        # Verify users exist
        user = User.query.get(user_id)
        seller = User.query.get(seller_id)
        product = SellerProduct.query.get(product_id)
        
        print(f"User exists: {user is not None}")
        print(f"Seller exists: {seller is not None}")
        print(f"Product exists: {product is not None}")
        
        if not (user and seller and product):
            print("ERROR: Required records not found!")
            return
        
        try:
            # Test 1: Try creating with both user_id and seller_id
            print("\n--- Test 1: Creating with user_id and seller_id ---")
            test_cart_item = CartItem(
                user_id=user_id,
                session_id=None,
                product_id=product_id,
                product_name=product.name,
                product_price=product.price,
                color="Black",
                size="M",
                quantity=1,
                variant_image=None,
                seller_id=seller_id
            )
            
            db.session.add(test_cart_item)
            db.session.commit()
            print(f"SUCCESS: Created cart item with ID {test_cart_item.id}")
            
            # Clean up
            db.session.delete(test_cart_item)
            db.session.commit()
            print("Cleanup: Deleted test item")
            
        except Exception as e:
            print(f"ERROR in Test 1: {e}")
            db.session.rollback()
        
        try:
            # Test 2: Try creating without seller_id
            print("\n--- Test 2: Creating without seller_id ---")
            test_cart_item = CartItem(
                user_id=user_id,
                session_id=None,
                product_id=product_id,
                product_name=product.name,
                product_price=product.price,
                color="Black",
                size="M",
                quantity=1,
                variant_image=None,
                seller_id=None
            )
            
            db.session.add(test_cart_item)
            db.session.commit()
            print(f"SUCCESS: Created cart item with ID {test_cart_item.id}")
            
            # Clean up
            db.session.delete(test_cart_item)
            db.session.commit()
            print("Cleanup: Deleted test item")
            
        except Exception as e:
            print(f"ERROR in Test 2: {e}")
            db.session.rollback()
        
        try:
            # Test 3: Try creating with session_id (guest user)
            print("\n--- Test 3: Creating with session_id (guest) ---")
            test_cart_item = CartItem(
                user_id=None,
                session_id="test_session_123",
                product_id=product_id,
                product_name=product.name,
                product_price=product.price,
                color="Black",
                size="M",
                quantity=1,
                variant_image=None,
                seller_id=seller_id
            )
            
            db.session.add(test_cart_item)
            db.session.commit()
            print(f"SUCCESS: Created cart item with ID {test_cart_item.id}")
            
            # Clean up
            db.session.delete(test_cart_item)
            db.session.commit()
            print("Cleanup: Deleted test item")
            
        except Exception as e:
            print(f"ERROR in Test 3: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()