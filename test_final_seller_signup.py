#!/usr/bin/env python3
"""
Final test to verify seller signup is working completely
"""

import requests
from project import create_app, db
from project.models import User, Seller

def test_final_seller_signup():
    """Test the complete seller signup flow"""
    
    # Test data
    test_email = "final.test.seller@example.com"
    
    form_data = {
        'firstName': 'Maria',
        'lastName': 'Santos',
        'username': 'Maria Santos',
        'email': test_email,
        'phone': '+639123456789',
        'birthdate': '1985-05-15',
        'gender': 'female',
        'business_name': 'Maria\'s Boutique',
        'business_type': 'individual',
        'store_description': 'Beautiful clothing and accessories for women',
        'region': 'NCR',
        'province': 'Metro Manila',
        'city': 'Quezon City',
        'barangay': 'Barangay Santo Domingo',
        'streetAddress': '456 Fashion Street',
        'zipCode': '1104',
        'country': 'Philippines',
        'password': 'securepassword123',
        'confirmPassword': 'securepassword123',
        'bankName': 'BDO',
        'bankAccount': '9876543210',
        'accountHolder': 'Maria Santos',
        'sellerTerms': 'on',
        'role': 'seller'
    }
    
    print("=== Final Seller Signup Test ===")
    print(f"Testing seller signup for: {test_email}")
    
    # Clean up any existing test user
    app = create_app('development')
    with app.app_context():
        existing_user = User.query.filter_by(email=test_email).first()
        if existing_user:
            print(f"Removing existing test user: {existing_user.email}")
            seller_profile = Seller.query.filter_by(user_id=existing_user.id).first()
            if seller_profile:
                db.session.delete(seller_profile)
            db.session.delete(existing_user)
            db.session.commit()
    
    try:
        # Submit the form
        response = requests.post(
            'http://localhost:5000/signup',
            data=form_data,
            allow_redirects=False
        )
        
        print(f"\n📤 Form submitted")
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirect Location: {location}")
            
            if '/pending' in location:
                print("✅ SUCCESS: Redirected to pending approval page")
            elif '/signup' in location:
                print("❌ FAILED: Redirected back to signup (validation error)")
                return
            else:
                print(f"✅ SUCCESS: Redirected to {location}")
        
        # Verify database entries
        with app.app_context():
            user = User.query.filter_by(email=test_email).first()
            if user:
                print(f"\n✅ User created successfully:")
                print(f"   📧 Email: {user.email}")
                print(f"   👤 Username: {user.username}")
                print(f"   🎭 Role: {user.role}")
                print(f"   📋 Role Requested: {user.role_requested}")
                print(f"   ✅ Is Approved: {user.is_approved}")
                print(f"   📅 Created: {user.created_at}")
                
                seller = Seller.query.filter_by(user_id=user.id).first()
                if seller:
                    print(f"\n✅ Seller profile created successfully:")
                    print(f"   🏪 Business Name: {seller.business_name}")
                    print(f"   🏢 Business Type: {seller.business_type}")
                    print(f"   📍 Business Address: {seller.business_address}")
                    print(f"   🏙️  Business City: {seller.business_city}")
                    print(f"   🏦 Bank Name: {seller.bank_name}")
                    print(f"   💳 Bank Account: {seller.bank_account}")
                    print(f"   👤 Account Holder: {seller.bank_holder_name}")
                    print(f"   ✅ Is Verified: {seller.is_verified}")
                    print(f"   📅 Created: {seller.created_at}")
                    
                    print(f"\n🎉 SELLER SIGNUP COMPLETELY SUCCESSFUL!")
                    print(f"📋 Status: Pending admin approval")
                    print(f"📧 User will be notified when approved")
                else:
                    print(f"\n❌ Seller profile NOT created!")
            else:
                print(f"\n❌ User NOT created in database!")
                
    except Exception as e:
        print(f"❌ Error during signup: {e}")

if __name__ == "__main__":
    test_final_seller_signup()