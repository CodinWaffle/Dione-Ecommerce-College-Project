#!/usr/bin/env python3
"""
Complete test for the fixed multi-step product creation flow
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import User, SellerProduct

def test_complete_flow():
    """Test the complete product creation flow"""
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            # Create tables
            db.create_all()
            
            # Create test seller user
            seller = User(
                email='testseller@example.com',
                username='testseller',
                role='seller',
                is_approved=True
            )
            db.session.add(seller)
            db.session.commit()
            
            print("=== Testing Complete Product Creation Flow ===")
            
            # Step 1: Login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print("✅ User logged in")
            
            # Step 2: Test add_product_stocks with complete payload
            payload = {
                'step1': {
                    'productName': 'Test Product',
                    'price': '99.99',
                    'category': 'clothing',
                    'subcategory': 'shirts',
                    'discountType': 'percentage',
                    'discountPercentage': '10',
                    'voucherType': 'seasonal',
                    'primaryImage': '/static/uploads/test_primary.jpg',
                    'secondaryImage': '/static/uploads/test_secondary.jpg',
                    'subitem': ['casual', 'formal']
                },
                'step2': {
                    'description': 'A high-quality test product with excellent features.',
                    'materials': '100% Cotton\nMachine wash cold',
                    'detailsFit': 'Regular fit\nCrew neckline\nShort sleeves',
                    'sizeGuide': [],
                    'certifications': ['organic']
                },
                'step3': {
                    'variants': [
                        {
                            'sku': 'TEST-BLK-001',
                            'color': 'Black',
                            'colorHex': '#000000',
                            'sizeStocks': [
                                {'size': 'S', 'stock': 10},
                                {'size': 'M', 'stock': 15},
                                {'size': 'L', 'stock': 8}
                            ],
                            'lowStock': 5,
                            'photo': '/static/uploads/variant_black.jpg'
                        },
                        {
                            'sku': 'TEST-WHT-001',
                            'color': 'White',
                            'colorHex': '#FFFFFF',
                            'sizeStocks': [
                                {'size': 'S', 'stock': 12},
                                {'size': 'M', 'stock': 20},
                                {'size': 'L', 'stock': 6}
                            ],
                            'lowStock': 5,
                            'photo': '/static/uploads/variant_white.jpg'
                        }
                    ],
                    'totalStock': 71
                }
            }
            
            print("📦 Submitting complete product data...")
            
            # Submit to add_product_stocks (which now saves as draft)
            response = client.post(
                '/seller/add_product_stocks',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.get_json()
                print(f"Response: {result}")
                
                if result.get('success'):
                    product_id = result.get('product_id')
                    print(f"✅ Product draft saved with ID: {product_id}")
                    
                    # Step 3: Check that product was saved as draft
                    product = SellerProduct.query.get(product_id)
                    if product:
                        print(f"✅ Product found in database:")
                        print(f"   Name: {product.name}")
                        print(f"   Category: {product.category}")
                        print(f"   Price: ₱{product.price}")
                        print(f"   Total Stock: {product.total_stock}")
                        print(f"   Is Draft: {product.is_draft}")
                        print(f"   Status: {product.status}")
                        print(f"   Variants: {len(product.variants)} variants")
                        
                        # Verify variant data
                        for i, variant in enumerate(product.variants):
                            print(f"   Variant {i+1}: {variant.get('color')} - {len(variant.get('sizeStocks', []))} sizes")
                        
                        # Step 4: Test preview page
                        preview_url = result.get('next')
                        print(f"\n📋 Testing preview page: {preview_url}")
                        
                        preview_response = client.get(preview_url)
                        print(f"Preview page status: {preview_response.status_code}")
                        
                        if preview_response.status_code == 200:
                            print("✅ Preview page loads successfully")
                            
                            # Step 5: Test committing the product
                            print("\n🚀 Testing product commit...")
                            
                            commit_response = client.post(
                                f'/seller/products/{product_id}/commit',
                                content_type='application/json'
                            )
                            
                            print(f"Commit response status: {commit_response.status_code}")
                            
                            if commit_response.status_code == 200:
                                commit_result = commit_response.get_json()
                                print(f"Commit result: {commit_result}")
                                
                                if commit_result.get('success'):
                                    # Verify product is now active
                                    db.session.refresh(product)
                                    print(f"✅ Product committed successfully!")
                                    print(f"   Is Draft: {product.is_draft}")
                                    print(f"   Status: {product.status}")
                                    
                                    # Step 6: Test product management page
                                    print("\n📊 Testing product management page...")
                                    
                                    mgmt_response = client.get('/seller/products')
                                    print(f"Management page status: {mgmt_response.status_code}")
                                    
                                    if mgmt_response.status_code == 200:
                                        print("✅ Product management page loads successfully")
                                        
                                        # Check if product appears in list
                                        active_products = SellerProduct.query.filter_by(
                                            seller_id=seller.id,
                                            is_draft=False
                                        ).all()
                                        
                                        print(f"✅ Found {len(active_products)} active products")
                                        
                                        if active_products:
                                            print("🎉 COMPLETE FLOW TEST PASSED!")
                                            return True
                                        else:
                                            print("❌ No active products found")
                                    else:
                                        print("❌ Product management page failed to load")
                                else:
                                    print(f"❌ Product commit failed: {commit_result}")
                            else:
                                print(f"❌ Product commit request failed")
                        else:
                            print("❌ Preview page failed to load")
                    else:
                        print("❌ Product not found in database")
                else:
                    print(f"❌ Product save failed: {result}")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")
            
            return False

def test_api_endpoints():
    """Test individual API endpoints"""
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create test seller
            seller = User(
                email='apiseller@example.com',
                username='apiseller',
                role='seller',
                is_approved=True
            )
            db.session.add(seller)
            db.session.commit()
            
            print("\n=== Testing API Endpoints ===")
            
            # Login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            # Test draft creation
            draft_data = {
                'step1': {
                    'productName': 'API Test Product',
                    'price': '49.99',
                    'category': 'accessories',
                    'subcategory': 'bags'
                },
                'step2': {
                    'description': 'API test description'
                },
                'step3': {
                    'variants': [
                        {
                            'sku': 'API-001',
                            'color': 'Blue',
                            'colorHex': '#0000FF',
                            'sizeStocks': [{'size': 'One Size', 'stock': 25}],
                            'lowStock': 3
                        }
                    ],
                    'totalStock': 25
                }
            }
            
            # Create draft
            response = client.post(
                '/seller/add_product_stocks',
                data=json.dumps(draft_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                result = response.get_json()
                if result.get('success'):
                    product_id = result.get('product_id')
                    print(f"✅ Draft API endpoint works - Product ID: {product_id}")
                    
                    # Test preview API
                    preview_response = client.get(f'/seller/products/preview/{product_id}')
                    if preview_response.status_code == 200:
                        print("✅ Preview API endpoint works")
                        
                        # Test commit API
                        commit_response = client.post(
                            f'/seller/products/{product_id}/commit',
                            content_type='application/json'
                        )
                        
                        if commit_response.status_code == 200:
                            commit_result = commit_response.get_json()
                            if commit_result.get('success'):
                                print("✅ Commit API endpoint works")
                                print("🎉 ALL API TESTS PASSED!")
                                return True
                            else:
                                print(f"❌ Commit API failed: {commit_result}")
                        else:
                            print(f"❌ Commit API returned {commit_response.status_code}")
                    else:
                        print(f"❌ Preview API returned {preview_response.status_code}")
                else:
                    print(f"❌ Draft API failed: {result}")
            else:
                print(f"❌ Draft API returned {response.status_code}")
            
            return False

if __name__ == '__main__':
    print("🧪 Running Complete Product Flow Tests")
    print("=" * 50)
    
    # Test complete flow
    flow_success = test_complete_flow()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Complete Flow: {'✅ PASS' if flow_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if flow_success and api_success:
        print("\n🎉 ALL TESTS PASSED! The product creation flow is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")