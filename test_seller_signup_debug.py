#!/usr/bin/env python3
"""
Debug script to test seller signup process
"""

from project import create_app, db
from project.models import User, Seller
from project.services.auth_service import AuthService

def test_seller_signup():
    """Test the seller signup process step by step"""
    
    app = create_app('development')
    
    with app.app_context():
        print("=== Testing Seller Signup Process ===")
        
        # Test data
        test_email = "test_seller@example.com"
        test_password = "testpassword123"
        test_role = "seller"
        
        # Clean up any existing test user
        existing_user = User.query.filter_by(email=test_email).first()
        if existing_user:
            print(f"Removing existing test user: {existing_user.email}")
            # Remove seller profile if exists
            seller_profile = Seller.query.filter_by(user_id=existing_user.id).first()
            if seller_profile:
                db.session.delete(seller_profile)
            db.session.delete(existing_user)
            db.session.commit()
        
        print(f"\n1. Creating user with email: {test_email}, role: {test_role}")
        
        # Step 1: Create user
        user, error = AuthService.create_user(test_email, test_password, role=test_role, username="Test Seller")
        
        if error:
            print(f"❌ Error creating user: {error}")
            return
        
        print(f"✅ User created successfully!")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Role: {user.role}")
        print(f"   - Role Requested: {user.role_requested}")
        print(f"   - Is Approved: {user.is_approved}")
        
        # Step 2: Create seller profile
        print(f"\n2. Creating seller profile...")
        
        seller_data = {
            'business_name': 'Test Business',
            'business_type': 'individual',
            'business_address': '123 Test Street',
            'business_city': 'Test City',
            'business_zip': '12345',
            'business_country': 'Philippines',
            'bank_name': 'Test Bank',
            'bank_account': '1234567890',
            'bank_holder_name': 'Test Seller',
            'tax_id': 'TAX123456',
            'store_description': 'Test store description'
        }
        
        profile, profile_error = AuthService.create_seller_profile(user.id, seller_data)
        
        if profile_error:
            print(f"❌ Error creating seller profile: {profile_error}")
        else:
            print(f"✅ Seller profile created successfully!")
            print(f"   - ID: {profile.id}")
            print(f"   - User ID: {profile.user_id}")
            print(f"   - Business Name: {profile.business_name}")
            print(f"   - Is Verified: {profile.is_verified}")
        
        # Step 3: Verify data in database
        print(f"\n3. Verifying data in database...")
        
        # Check user table
        db_user = User.query.filter_by(email=test_email).first()
        if db_user:
            print(f"✅ User found in database:")
            print(f"   - ID: {db_user.id}")
            print(f"   - Email: {db_user.email}")
            print(f"   - Role: {db_user.role}")
            print(f"   - Role Requested: {db_user.role_requested}")
            print(f"   - Is Approved: {db_user.is_approved}")
        else:
            print(f"❌ User NOT found in database!")
        
        # Check seller table
        db_seller = Seller.query.filter_by(user_id=user.id).first()
        if db_seller:
            print(f"✅ Seller profile found in database:")
            print(f"   - ID: {db_seller.id}")
            print(f"   - User ID: {db_seller.user_id}")
            print(f"   - Business Name: {db_seller.business_name}")
            print(f"   - Business Type: {db_seller.business_type}")
            print(f"   - Is Verified: {db_seller.is_verified}")
        else:
            print(f"❌ Seller profile NOT found in database!")
        
        # Step 4: Check all users and sellers in database
        print(f"\n4. All users in database:")
        all_users = User.query.all()
        for u in all_users:
            print(f"   - User {u.id}: {u.email} (role: {u.role}, requested: {u.role_requested})")
        
        print(f"\n5. All sellers in database:")
        all_sellers = Seller.query.all()
        for s in all_sellers:
            print(f"   - Seller {s.id}: {s.business_name} (user_id: {s.user_id})")

if __name__ == "__main__":
    test_seller_signup()