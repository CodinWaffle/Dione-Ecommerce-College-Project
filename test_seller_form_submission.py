#!/usr/bin/env python3
"""
Test the actual seller form submission to debug the issue
"""

import requests
import json
from project import create_app, db
from project.models import User, Seller

def test_seller_form_submission():
    """Test submitting the seller form like the frontend does"""
    
    # Test data that matches the form fields
    form_data = {
        # Step 1: Personal Information
        'firstName': 'John',
        'lastName': 'Doe',
        'username': 'John Doe',  # This gets set by JavaScript
        'email': 'john.doe.seller@example.com',
        'phone': '+639123456789',
        'birthdate': '1990-01-01',
        'gender': 'male',
        
        # Step 2: Business Information
        'business_name': 'John\'s Store',
        'business_type': 'individual',
        'store_description': 'A great online store selling quality products',
        'region': 'NCR',
        'province': 'Metro Manila',
        'city': 'Manila',
        'barangay': 'Barangay 1',
        'streetAddress': '123 Main Street',
        'zipCode': '1000',
        'country': 'Philippines',
        
        # Step 3: Account Security
        'password': 'testpassword123',
        'confirmPassword': 'testpassword123',
        
        # Step 4: Banking Information
        'bankName': 'BPI',
        'bankAccount': '1234567890',
        'accountHolder': 'John Doe',
        'sellerTerms': 'on',  # Checkbox value
        
        # Hidden fields set by JavaScript
        'role': 'seller'
    }
    
    print("=== Testing Seller Form Submission ===")
    print(f"Submitting form data for: {form_data['email']}")
    
    # Clean up any existing test user first
    app = create_app('development')
    with app.app_context():
        existing_user = User.query.filter_by(email=form_data['email']).first()
        if existing_user:
            print(f"Removing existing test user: {existing_user.email}")
            seller_profile = Seller.query.filter_by(user_id=existing_user.id).first()
            if seller_profile:
                db.session.delete(seller_profile)
            db.session.delete(existing_user)
            db.session.commit()
    
    try:
        # Submit the form to the signup endpoint
        response = requests.post(
            'http://localhost:5000/signup',
            data=form_data,
            allow_redirects=False  # Don't follow redirects so we can see the response
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location')}")
        
        # Check if there are any error messages in the response
        if 'text/html' in response.headers.get('content-type', ''):
            response_text = response.text
            if 'flash' in response_text or 'error' in response_text.lower():
                print("Response contains potential error messages")
                # Look for flash messages
                import re
                flash_pattern = r'class="alert[^"]*"[^>]*>([^<]+)'
                matches = re.findall(flash_pattern, response_text)
                if matches:
                    print("Flash messages found:")
                    for match in matches:
                        print(f"  - {match.strip()}")
        
        # Check database after submission
        with app.app_context():
            user = User.query.filter_by(email=form_data['email']).first()
            if user:
                print(f"\n✅ User created in database:")
                print(f"   ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.role}")
                print(f"   Role Requested: {user.role_requested}")
                print(f"   Is Approved: {user.is_approved}")
                
                seller = Seller.query.filter_by(user_id=user.id).first()
                if seller:
                    print(f"\n✅ Seller profile created:")
                    print(f"   Business Name: {seller.business_name}")
                    print(f"   Business Type: {seller.business_type}")
                    print(f"   Business Address: {seller.business_address}")
                else:
                    print(f"\n❌ No seller profile found!")
            else:
                print(f"\n❌ User NOT created in database!")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error during form submission: {e}")

if __name__ == "__main__":
    test_seller_form_submission()