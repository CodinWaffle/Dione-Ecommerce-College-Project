#!/usr/bin/env python3
"""
Test script to verify that store info is properly fetched from database
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_seller_info_from_database():
    """Test that seller info is properly fetched from database"""
    try:
        from project import create_app, db
        from project.models import User, Seller, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Testing Seller Info Database Integration")
            print("=" * 50)
            
            # Check if we have any sellers in the database
            sellers = Seller.query.all()
            print(f"📊 Found {len(sellers)} sellers in database")
            
            if sellers:
                for seller in sellers[:3]:  # Show first 3 sellers
                    user = User.query.get(seller.user_id)
                    print(f"\n👤 Seller ID: {seller.id}")
                    print(f"   User ID: {seller.user_id}")
                    print(f"   Business Name: {seller.business_name}")
                    print(f"   Business City: {seller.business_city}")
                    print(f"   Business Country: {seller.business_country}")
                    print(f"   Is Verified: {seller.is_verified}")
                    print(f"   Products Count: {seller.products_count}")
                    print(f"   Followers Count: {seller.followers_count}")
                    print(f"   Rating Count: {seller.rating_count}")
                    
                    # Check if this seller has products
                    products = SellerProduct.query.filter_by(seller_id=seller.user_id).all()
                    print(f"   Products: {len(products)}")
                    
                    if products:
                        print(f"   Sample Product: {products[0].name} (ID: {products[0].id})")
            else:
                print("⚠️  No sellers found in database")
                print("   Creating a test seller...")
                
                # Create a test user and seller
                test_user = User(
                    email='teststore@example.com',
                    role='seller',
                    is_approved=True
                )
                db.session.add(test_user)
                db.session.flush()  # Get the ID
                
                test_seller = Seller(
                    user_id=test_user.id,
                    business_name='Test Fashion Store',
                    business_city='Manila',
                    business_country='Philippines',
                    store_description='A test fashion store for demonstration',
                    is_verified=True,
                    products_count=0,
                    followers_count=0,
                    rating_count=0
                )
                db.session.add(test_seller)
                
                # Create a test product
                test_product = SellerProduct(
                    seller_id=test_user.id,
                    name='Test Product',
                    description='A test product for demonstration',
                    price=999.00,
                    status='active'
                )
                db.session.add(test_product)
                
                try:
                    db.session.commit()
                    print(f"✅ Created test seller: {test_seller.business_name}")
                    print(f"   Location: {test_seller.business_city}, {test_seller.business_country}")
                    print(f"   Product: {test_product.name} (ID: {test_product.id})")
                except Exception as e:
                    print(f"❌ Error creating test data: {e}")
                    db.session.rollback()
            
            print("\n" + "=" * 50)
            print("✅ Database test completed")
            
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_seller_info_from_database()