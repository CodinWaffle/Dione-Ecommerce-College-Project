#!/usr/bin/env python3
"""
Check the current state of the database to understand what's happening
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def check_database_state():
    """Check what's currently in the database"""
    
    try:
        from project import create_app, db
        from project.models import SellerProduct, User
        
        app = create_app()
        
        with app.app_context():
            print("=== Database State Check ===")
            
            # Get all products
            products = SellerProduct.query.all()
            print(f"Total products in database: {len(products)}")
            
            if products:
                print("\n=== All Products ===")
                for i, product in enumerate(products, 1):
                    print(f"\n--- Product {i} (ID: {product.id}) ---")
                    print(f"Seller ID: {product.seller_id}")
                    print(f"Name: '{product.name}' (length: {len(product.name or '')})")
                    print(f"Description: '{product.description}' (length: {len(product.description or '')})")
                    print(f"Category: '{product.category}' (length: {len(product.category or '')})")
                    print(f"Subcategory: '{product.subcategory}' (length: {len(product.subcategory or '') if product.subcategory else 0})")
                    print(f"Price: {product.price}")
                    print(f"Compare at price: {product.compare_at_price}")
                    print(f"Discount type: '{product.discount_type}'")
                    print(f"Discount value: {product.discount_value}")
                    print(f"Voucher type: '{product.voucher_type}'")
                    print(f"Materials: '{product.materials}' (length: {len(product.materials or '')})")
                    print(f"Details fit: '{product.details_fit}' (length: {len(product.details_fit or '')})")
                    print(f"Primary image: '{product.primary_image}'")
                    print(f"Secondary image: '{product.secondary_image}'")
                    print(f"Total stock: {product.total_stock}")
                    print(f"Low stock threshold: {product.low_stock_threshold}")
                    print(f"Variants: {product.variants}")
                    print(f"Attributes: {product.attributes}")
                    print(f"Status: '{product.status}'")
                    print(f"Created at: {product.created_at}")
                    print(f"Updated at: {product.updated_at}")
                    
                    # Check for issues
                    issues = []
                    if not product.name or product.name.strip() == '':
                        issues.append("Name is empty")
                    if not product.category or product.category.strip() == '':
                        issues.append("Category is empty")
                    if product.price is None or product.price == 0:
                        issues.append("Price is zero/None")
                    
                    if issues:
                        print(f"❌ ISSUES: {', '.join(issues)}")
                    else:
                        print("✅ Basic fields look good")
            
            # Check users
            print(f"\n=== Users ===")
            users = User.query.all()
            sellers = [u for u in users if u.role == 'seller']
            print(f"Total users: {len(users)}")
            print(f"Total sellers: {len(sellers)}")
            
            for seller in sellers:
                seller_products = SellerProduct.query.filter_by(seller_id=seller.id).all()
                print(f"Seller {seller.id} ({seller.email}): {len(seller_products)} products")
            
            return True
            
    except Exception as e:
        print(f"✗ Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    check_database_state()