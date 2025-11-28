#!/usr/bin/env python3
"""
Clean up invalid products from the database
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def cleanup_invalid_products():
    """Remove products with invalid basic data"""
    
    try:
        from project import create_app, db
        from project.models import SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("=== Cleaning Up Invalid Products ===")
            
            # Find products with invalid data
            invalid_products = SellerProduct.query.filter(
                (SellerProduct.name == '-') | 
                (SellerProduct.name == '') | 
                (SellerProduct.name.is_(None)) |
                (SellerProduct.category == '-') | 
                (SellerProduct.category == '') | 
                (SellerProduct.category.is_(None)) |
                (SellerProduct.price == 0) |
                (SellerProduct.price.is_(None))
            ).all()
            
            print(f"Found {len(invalid_products)} invalid products")
            
            if invalid_products:
                print("\nInvalid products to be removed:")
                for product in invalid_products:
                    print(f"  - ID {product.id}: Name='{product.name}', Category='{product.category}', Price={product.price}")
                
                confirm = input("\nDo you want to delete these invalid products? (y/N): ")
                if confirm.lower() == 'y':
                    for product in invalid_products:
                        db.session.delete(product)
                    
                    db.session.commit()
                    print(f"✅ Deleted {len(invalid_products)} invalid products")
                else:
                    print("❌ Cleanup cancelled")
            else:
                print("✅ No invalid products found")
            
            # Show remaining products
            remaining_products = SellerProduct.query.all()
            print(f"\nRemaining products: {len(remaining_products)}")
            
            for product in remaining_products:
                status = "✅" if (product.name and product.name != '-' and 
                               product.category and product.category != '-' and 
                               product.price and product.price > 0) else "❌"
                print(f"  {status} ID {product.id}: '{product.name}' - {product.category} - ${product.price}")
            
            return True
            
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    cleanup_invalid_products()