#!/usr/bin/env python3
"""
Debug script to check product workflow session data
"""

import os
import sys
from flask import Flask
from project import create_app

def debug_product_workflow():
    """Debug the product workflow to see what's happening"""
    
    print("🔍 Debugging Product Workflow")
    print("=" * 50)
    
    # Check if the route files exist and have the right structure
    print("\n1. 📋 Checking Route Files...")
    
    route_file = "project/routes/seller_routes.py"
    if not os.path.exists(route_file):
        print("❌ Route file not found")
        return False
    
    with open(route_file, 'r', encoding='utf-8') as f:
        route_content = f.read()
    
    # Check for key components
    checks = [
        ('add_product route', 'def add_product():'),
        ('add_product_preview route', 'def add_product_preview():'),
        ('Session workflow storage', "session['product_workflow']"),
        ('Database insertion', 'SellerProduct('),
        ('Photo URL storage', 'primary_image='),
        ('Variants storage', 'variants='),
        ('Database commit', 'db.session.commit()'),
        ('Error handling', 'except SQLAlchemyError'),
    ]
    
    route_ok = True
    for check_name, pattern in checks:
        if pattern in route_content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            route_ok = False
    
    # Check template files
    print("\n2. 🌐 Checking Template Files...")
    
    template_files = [
        "project/templates/seller/add_product.html",
        "project/templates/seller/add_product_description.html", 
        "project/templates/seller/add_product_stocks.html",
        "project/templates/seller/add_product_preview.html"
    ]
    
    template_ok = True
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✅ {template_file}: Found")
        else:
            print(f"❌ {template_file}: NOT FOUND")
            template_ok = False
    
    # Check JavaScript files
    print("\n3. 📜 Checking JavaScript Files...")
    
    js_files = [
        "project/static/js/seller_scripts/add_product.js",
        "project/static/js/seller_scripts/add_product_description.js",
        "project/static/js/seller_scripts/add_product_stocks.js", 
        "project/static/js/seller_scripts/add_product_preview.js",
        "project/static/js/seller_scripts/add_product_flow.js"
    ]
    
    js_ok = True
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ {js_file}: Found")
        else:
            print(f"❌ {js_file}: NOT FOUND")
            js_ok = False
    
    # Check database model
    print("\n4. 🗄️ Checking Database Model...")
    
    model_file = "project/models.py"
    if os.path.exists(model_file):
        with open(model_file, 'r', encoding='utf-8') as f:
            model_content = f.read()
        
        model_checks = [
            ('SellerProduct class', 'class SellerProduct'),
            ('Primary image field', 'primary_image'),
            ('Secondary image field', 'secondary_image'),
            ('Variants field', 'variants'),
            ('JSON column type', 'JSON'),
        ]
        
        model_ok = True
        for check_name, pattern in model_checks:
            if pattern in model_content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: NOT FOUND")
                model_ok = False
    else:
        print("❌ Model file not found")
        model_ok = False
    
    # Check for common issues
    print("\n5. 🔍 Common Issues Check...")
    
    issues_found = []
    
    # Check if session is properly configured
    if 'session.modified = True' not in route_content:
        issues_found.append("Session modification not marked - data might not persist")
    
    # Check if redirect URLs are correct
    if 'add_product_preview' not in route_content:
        issues_found.append("Preview redirect might be missing")
    
    # Check if database session is properly handled
    if 'db.session.rollback()' not in route_content:
        issues_found.append("Database rollback on error might be missing")
    
    if issues_found:
        print("⚠️ Potential Issues Found:")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("✅ No obvious issues found")
    
    # Summary
    print(f"\n📊 Summary:")
    print("=" * 30)
    
    overall_ok = route_ok and template_ok and js_ok and model_ok
    
    if overall_ok:
        print("🎉 OVERALL STATUS: ✅ All components found")
        print("\n🔧 Debugging Steps:")
        print("1. Check browser console for JavaScript errors")
        print("2. Check Flask logs for server errors")
        print("3. Verify session data is being stored correctly")
        print("4. Check if photos are being compressed properly")
        print("5. Verify database connection and permissions")
        
        print("\n🧪 Test Steps:")
        print("1. Fill out add_product form with photos")
        print("2. Fill out description form")
        print("3. Add variants with photos in stocks form")
        print("4. Check preview page shows all data")
        print("5. Click Add Product and check database")
        
    else:
        print("❌ OVERALL STATUS: Missing components found")
        print("Please fix the missing files/components above")
    
    return overall_ok

def create_test_product_data():
    """Create test product data for debugging"""
    
    print("\n📝 Creating Test Product Data...")
    
    test_data = {
        'step1': {
            'productName': 'Test Product',
            'price': '29.99',
            'discountPercentage': '10',
            'discountType': 'percentage',
            'voucherType': 'seasonal',
            'category': 'clothing',
            'subcategory': 'shirts',
            'subitem': ['casual', 'cotton'],
            'primaryImage': '/static/uploads/products/test_primary.jpg',
            'secondaryImage': '/static/uploads/products/test_secondary.jpg',
        },
        'step2': {
            'description': 'This is a test product description.',
            'materials': '100% Cotton\nMachine wash cold',
            'detailsFit': 'Relaxed fit\nCrew neckline',
            'sizeGuide': [],
            'certifications': [],
        },
        'step3': {
            'variants': [
                {
                    'sku': 'TEST-001',
                    'color': 'Red',
                    'colorHex': '#ff0000',
                    'sizeStocks': [
                        {'size': 'M', 'stock': 10},
                        {'size': 'L', 'stock': 15}
                    ],
                    'lowStock': 5,
                    'photo': '/static/uploads/variants/test_variant.jpg'
                }
            ],
            'totalStock': 25,
        }
    }
    
    print("✅ Test data structure created:")
    print(f"   - Product: {test_data['step1']['productName']}")
    print(f"   - Price: ₱{test_data['step1']['price']}")
    print(f"   - Category: {test_data['step1']['category']}")
    print(f"   - Variants: {len(test_data['step3']['variants'])}")
    print(f"   - Total Stock: {test_data['step3']['totalStock']}")
    
    return test_data

def main():
    """Main debug function"""
    
    print("🚀 Product Workflow Debug Tool")
    print("=" * 50)
    
    success = debug_product_workflow()
    test_data = create_test_product_data()
    
    if success:
        print(f"\n🎊 All components found! The workflow should work.")
        print(f"\n💡 If you're still having issues:")
        print("1. Check browser developer tools console")
        print("2. Check Flask application logs")
        print("3. Verify database connection")
        print("4. Test with smaller image files")
        print("5. Check session configuration")
    else:
        print(f"\n❌ Some components are missing. Fix them first.")
    
    return success

if __name__ == "__main__":
    main()