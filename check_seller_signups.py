#!/usr/bin/env python3
"""
Check existing seller signups in the database
"""

from project import create_app, db
from project.models import User, Seller

def check_seller_signups():
    """Check all seller signups in the database"""
    
    app = create_app('development')
    
    with app.app_context():
        print("=== Checking Seller Signups in Database ===")
        
        # Check all users with seller role or seller role requested
        print("\n1. Users with seller role or seller role requested:")
        seller_users = User.query.filter(
            (User.role == 'seller') | (User.role_requested == 'seller')
        ).all()
        
        if not seller_users:
            print("   ❌ No seller users found!")
        else:
            for user in seller_users:
                print(f"   - User {user.id}: {user.email}")
                print(f"     Role: {user.role}")
                print(f"     Role Requested: {user.role_requested}")
                print(f"     Is Approved: {user.is_approved}")
                print(f"     Created: {user.created_at}")
                print()
        
        # Check all seller profiles
        print("2. Seller profiles in database:")
        seller_profiles = Seller.query.all()
        
        if not seller_profiles:
            print("   ❌ No seller profiles found!")
        else:
            for seller in seller_profiles:
                print(f"   - Seller {seller.id}: {seller.business_name}")
                print(f"     User ID: {seller.user_id}")
                print(f"     Business Type: {seller.business_type}")
                print(f"     Business Address: {seller.business_address}")
                print(f"     Business City: {seller.business_city}")
                print(f"     Bank Name: {seller.bank_name}")
                print(f"     Is Verified: {seller.is_verified}")
                print(f"     Created: {seller.created_at}")
                print()
        
        # Check for pending approvals
        print("3. Pending seller approvals:")
        pending_sellers = User.query.filter(
            User.role_requested == 'seller',
            User.is_approved == False
        ).all()
        
        if not pending_sellers:
            print("   ✅ No pending seller approvals")
        else:
            print(f"   📋 {len(pending_sellers)} pending seller approval(s):")
            for user in pending_sellers:
                print(f"     - {user.email} (ID: {user.id}) - Created: {user.created_at}")
        
        # Check approved sellers
        print("\n4. Approved sellers:")
        approved_sellers = User.query.filter(
            User.role == 'seller',
            User.is_approved == True
        ).all()
        
        if not approved_sellers:
            print("   ✅ No approved sellers yet")
        else:
            print(f"   ✅ {len(approved_sellers)} approved seller(s):")
            for user in approved_sellers:
                print(f"     - {user.email} (ID: {user.id}) - Created: {user.created_at}")

if __name__ == "__main__":
    check_seller_signups()