#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct, User, Seller

def test_seller_info():
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Testing Seller Information Fetching...")
        
        # Get a product with variants
        with app.app_context():
            product = SellerProduct.query.first()
            
            if not product:
                print("❌ No products found")
                return
                
            print(f"📦 Testing product: {product.name} (ID: {product.id})")
            print(f"📊 Seller ID: {product.seller_id}")
            
            # Check if seller exists
            seller_user = User.query.get(product.seller_id)
            if seller_user:
                print(f"✅ Found seller user: {seller_user.email}")
                
                if hasattr(seller_user, 'seller_profile') and seller_user.seller_profile:
                    # seller_profile is a list due to backref, get the first one
                    seller_profiles = seller_user.seller_profile
                    if seller_profiles:
                        seller_profile = seller_profiles[0]
                        print(f"✅ Found seller profile: {seller_profile.business_name}")
                        print(f"📍 Business address: {seller_profile.business_address}")
                        print(f"🏙️ Business city: {seller_profile.business_city}")
                        print(f"✅ Verified: {seller_profile.is_verified}")
                    else:
                        print("❌ No seller profile found in list")
                else:
                    print("❌ No seller profile found")
            else:
                print("❌ No seller user found")
        
        # Test the actual route
        response = client.get(f'/product/{product.id}')
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Check if seller info is in the template
            if 'store-profile-section' in html_content:
                print("✅ Found store profile section in HTML")
            else:
                print("❌ Store profile section not found in HTML")
                
            if 'store-name' in html_content:
                print("✅ Found store name in HTML")
            else:
                print("❌ Store name not found in HTML")
                
        else:
            print(f"❌ Failed to load product page: {response.status_code}")

if __name__ == '__main__':
    test_seller_info()