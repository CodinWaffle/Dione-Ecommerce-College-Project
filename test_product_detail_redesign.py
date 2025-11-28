#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from project import create_app, db
from project.models import SellerProduct

def test_product_detail_redesign():
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Testing Product Detail Redesign...")
        
        # Get a product
        with app.app_context():
            product = SellerProduct.query.first()
            
            if not product:
                print("❌ No products found")
                return
                
            print(f"📦 Testing product: {product.name} (ID: {product.id})")
        
        # Test the product detail page
        response = client.get(f'/product/{product.id}')
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Test store information section
            print("\n🏪 Testing Store Information Section:")
            
            checks = [
                ('store-profile-section', 'Store profile section'),
                ('store-profile-image', 'Store profile image'),
                ('store-name', 'Store name'),
                ('store-location', 'Store location'),
                ('store-stats', 'Store statistics'),
                ('rating-section', 'Rating section'),
                ('store-metrics', 'Store metrics'),
                ('follow-btn', 'Follow button'),
                ('chat-btn', 'Chat button'),
                ('verified-badge', 'Verified badge (optional)'),
            ]
            
            for class_name, description in checks:
                if class_name in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Test product information dropdowns
            print("\n📋 Testing Product Information Dropdowns:")
            
            dropdown_checks = [
                ('dropdown-item', 'Dropdown items'),
                ('dropdown-header', 'Dropdown headers'),
                ('dropdown-title', 'Dropdown titles'),
                ('dropdown-content', 'Dropdown content'),
                ('chevron', 'Chevron icons'),
                ('content-text', 'Content text'),
            ]
            
            for class_name, description in dropdown_checks:
                if class_name in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Test specific dropdown sections
            print("\n📝 Testing Specific Dropdown Sections:")
            
            section_checks = [
                ('Product Description', 'Product description section'),
                ('Materials & Care', 'Materials and care section'),
                ('Size & Fit', 'Size and fit section'),
                ('Shipping & Returns', 'Shipping and returns section'),
            ]
            
            for section_text, description in section_checks:
                if section_text in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Test JavaScript functionality
            print("\n🔧 Testing JavaScript Integration:")
            
            js_checks = [
                ('toggleDropdown', 'Toggle dropdown function'),
                ('followStore', 'Follow store function'),
                ('chatWithStore', 'Chat with store function'),
                ('onclick="toggleDropdown', 'Dropdown click handlers'),
                ('onclick="followStore', 'Follow button click handler'),
                ('onclick="chatWithStore', 'Chat button click handler'),
            ]
            
            for js_element, description in js_checks:
                if js_element in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Test responsive design elements
            print("\n📱 Testing Responsive Design Elements:")
            
            responsive_checks = [
                ('store-actions', 'Store action buttons'),
                ('store-details', 'Store details section'),
                ('product-info-content', 'Product info content'),
                ('info-section', 'Info sections'),
            ]
            
            for class_name, description in responsive_checks:
                if class_name in html_content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            print(f"\n📊 Total HTML size: {len(html_content)} characters")
            
        else:
            print(f"❌ Failed to load product page: {response.status_code}")

if __name__ == '__main__':
    test_product_detail_redesign()