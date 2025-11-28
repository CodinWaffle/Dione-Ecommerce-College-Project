#!/usr/bin/env python3
"""
Simple test to check if the signup endpoint is working at all
"""

import requests

def test_simple_signup():
    """Test a simple buyer signup first"""
    
    form_data = {
        'email': 'simple.test@example.com',
        'password': 'testpassword123',
        'username': 'Simple Test',
        'role': 'buyer'
    }
    
    print("=== Testing Simple Buyer Signup ===")
    print(f"Submitting: {form_data}")
    
    try:
        response = requests.post(
            'http://localhost:5000/signup',
            data=form_data,
            allow_redirects=False
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirect to: {location}")
            
            if '/pending' in location:
                print("✅ Redirected to pending - signup likely successful")
            elif '/signup' in location:
                print("❌ Redirected back to signup - validation error")
            else:
                print(f"✅ Redirected to: {location}")
        
        # Check response content for any error messages
        if response.text:
            print(f"Response length: {len(response.text)} characters")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_signup()