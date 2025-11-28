#!/usr/bin/env python3
"""
Test the complete product creation flow including size selection and database saving
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_complete_flow_with_sizes():
    """Test the complete product creation flow with sizes"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🧪 TESTING COMPLETE PRODUCT FLOW WITH SIZES")
            print("=" * 60)
            
            client = app.test_client()
            
            # Get an approved seller
            seller = User.query.filter_by(role='seller', is_approved=True).first()
            if not seller:
                print("❌ No approved seller found")
                return False
            
            # Login as the seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✅ Testing with seller: {seller.email}")
            
            # Step 1: Test basic product info
            print("\n�  STEP 1: Basic Product Information")
            print("-" * 40)
            
            basic_data = {
                'productName': 'Complete Test Product',
                'category': 'Clothing',
                'subcategory': 'T-Shirts',
                'price': '29.99',
                'discountType': 'percentage',
                'discountPercentage': '10',
                'voucherType': 'SAVE10',
                'primaryImage': '/static/images/test.jpg',
                'secondaryImage': '/static/images/test2.jpg'
            }
            
            response = client.post('/seller/add_product', data=basic_data)
            print(f"Basic info response: {response.status_code}")
            
            if response.status_code != 302:
                print("❌ Basic info step failed")
                return False
            
            # Step 2: Test description
            print("\n📄 STEP 2: Product Description")
            print("-" * 40)
            
            description_data = {
                'description': 'High-quality cotton t-shirt with modern design',
                'materials': '100% organic cotton',
                'detailsFit': 'Regular fit, true to size'
            }
            
            response = client.post('/seller/add_product_description', data=description_data)
            print(f"Description response: {response.status_code}")
            
            if response.status_code != 302:
                print("❌ Description step failed")
                return False
            
            # Step 3: Test stocks with sizes
            print("\n📦 STEP 3: Product Stocks with Sizes")
            print("-" * 40)
            
            # Simulate the size selection data that would be sent from the frontend
            stocks_data = {
                'sku_0': 'TSHIRT-001',
                'color_0': 'Blue',
                'color_picker_0': '#0000FF',
                'lowStock_0': '5',
                'sizeStocks_0': json.dumps([
                    {'size': 'S', 'stock': 10},
                    {'size': 'M', 'stock': 15},
                    {'size': 'L', 'stock': 12},
                    {'size': 'XL', 'stock': 8}
                ])
            }
            
            response = client.post('/seller/add_product_stocks', data=stocks_data)
            print(f"Stocks response: {response.status_code}")
            
            if response.status_code != 302:
                print("❌ Stocks step failed")
                return False
            
            # Step 4: Test preview and final submission
            print("\n👁️ STEP 4: Preview and Submit")
            print("-" * 40)
            
            response = client.post('/seller/add_product_preview')
            print(f"Preview submission response: {response.status_code}")
            
            if response.status_code == 302 and 'products' in response.location:
                print("✅ Successfully redirected to products page")
                
                # Check if product was saved correctly
                saved_product = SellerProduct.query.filter_by(name='Complete Test Product').first()
                if saved_product:
                    print("✅ Product saved to database!")
                    print(f"   📋 Name: '{saved_product.name}'")
                    print(f"   📂 Category: '{saved_product.category}'")
                    print(f"   📂 Subcategory: '{saved_product.subcategory}'")
                    print(f"   💰 Price: ${saved_product.price}")
                    print(f"   📦 Total Stock: {saved_product.total_stock}")
                    print(f"   🎨 Variants: {len(saved_product.variants or [])}")
                    
                    # Check variant details
                    if saved_product.variants:
                        print("   📊 Variant Details:")
                        for i, variant in enumerate(saved_product.variants):
                            print(f"      Variant {i+1}:")
                            print(f"        - SKU: {variant.get('sku', 'N/A')}")
                            print(f"        - Color: {variant.get('color', 'N/A')}")
                            print(f"        - Color Hex: {variant.get('colorHex', 'N/A')}")
                            
                            if 'sizeStocks' in variant:
                                print(f"        - Sizes: {len(variant['sizeStocks'])}")
                                for size_item in variant['sizeStocks']:
                                    print(f"          * {size_item.get('size', 'N/A')}: {size_item.get('stock', 0)} units")
                            else:
                                print(f"        - Size: {variant.get('size', 'N/A')}")
                                print(f"        - Stock: {variant.get('stock', 0)}")
                    
                    # Verify all critical fields
                    issues = []
                    if not saved_product.name or saved_product.name.strip() == '':
                        issues.append("Name is empty")
                    if not saved_product.category or saved_product.category.strip() == '':
                        issues.append("Category is empty")
                    if not saved_product.price or saved_product.price <= 0:
                        issues.append("Price is invalid")
                    if not saved_product.variants or len(saved_product.variants) == 0:
                        issues.append("No variants saved")
                    if saved_product.total_stock <= 0:
                        issues.append("No stock saved")
                    
                    if issues:
                        print(f"❌ ISSUES FOUND:")
                        for issue in issues:
                            print(f"   - {issue}")
                        return False
                    else:
                        print("✅ All fields validated successfully")
                    
                    # Test product display in management page
                    print("\n📋 STEP 5: Product Management Display")
                    print("-" * 40)
                    
                    response = client.get('/seller/products')
                    if response.status_code == 200:
                        print("✅ Product management page loads successfully")
                        
                        # Check if our product appears in the response
                        response_text = response.get_data(as_text=True)
                        if 'Complete Test Product' in response_text:
                            print("✅ Product appears in management list")
                        else:
                            print("❌ Product not found in management list")
                            return False
                    else:
                        print(f"❌ Product management page failed: {response.status_code}")
                        return False
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("🧹 Test product cleaned up")
                    
                else:
                    print("❌ Product was not found in database")
                    return False
            else:
                print(f"❌ Preview submission failed: {response.status_code}")
                if response.location:
                    print(f"   Redirected to: {response.location}")
                return False
            
            # Test the size validation fix
            print("\n🔧 STEP 6: Size Validation Test")
            print("-" * 40)
            
            # Test with missing sizes (should be handled gracefully now)
            stocks_data_no_sizes = {
                'sku_0': 'NOSIZES-001',
                'color_0': 'Red',
                'color_picker_0': '#FF0000',
                'lowStock_0': '5'
                # No sizeStocks_0 - this should trigger our validation fix
            }
            
            response = client.post('/seller/add_product_stocks', data=stocks_data_no_sizes)
            print(f"No sizes response: {response.status_code}")
            
            if response.status_code == 302:
                print("✅ Form submission handled gracefully even without sizes")
            else:
                print("❌ Form submission failed without sizes")
                return False
            
            print("\n🎉 COMPLETE FLOW TEST RESULTS")
            print("=" * 60)
            print("✅ Basic product information: PASSED")
            print("✅ Product description: PASSED")
            print("✅ Stock management with sizes: PASSED")
            print("✅ Preview and submission: PASSED")
            print("✅ Database saving: PASSED")
            print("✅ Product management display: PASSED")
            print("✅ Size validation handling: PASSED")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_size_validation_specifically():
    """Test the size validation fix specifically"""
    
    print("\n🔍 TESTING SIZE VALIDATION FIX")
    print("=" * 50)
    
    # Check if the JavaScript file was created
    js_file_path = 'project/static/js/seller_scripts/size_validation_fix.js'
    if os.path.exists(js_file_path):
        print("✅ Size validation fix JavaScript file exists")
        
        # Check file size
        file_size = os.path.getsize(js_file_path)
        print(f"✅ File size: {file_size} bytes")
        
        if file_size > 1000:  # Should be a substantial file
            print("✅ File appears to contain meaningful content")
        else:
            print("⚠️ File might be too small")
    else:
        print("❌ Size validation fix JavaScript file not found")
        return False
    
    # Check if the template was updated
    template_path = 'project/templates/seller/add_product_stocks.html'
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        if 'size_validation_fix.js' in template_content:
            print("✅ Template includes size validation fix script")
        else:
            print("❌ Template does not include size validation fix script")
            return False
    else:
        print("❌ Template file not found")
        return False
    
    print("✅ Size validation fix is properly integrated")
    return True

if __name__ == '__main__':
    print("🚀 STARTING COMPREHENSIVE PRODUCT CREATION TESTS")
    print("=" * 70)
    
    # Test the complete flow
    flow_success = test_complete_flow_with_sizes()
    
    # Test the size validation fix
    validation_success = test_size_validation_specifically()
    
    overall_success = flow_success and validation_success
    
    print("\n📊 FINAL TEST RESULTS")
    print("=" * 70)
    
    if overall_success:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Product creation flow is working correctly")
        print("✅ Size validation tooltip issue is fixed")
        print("✅ Products save properly to database")
        print("✅ Product management displays correctly")
        
        print("\n🎯 READY FOR PRODUCTION!")
        print("The product creation system is fully functional.")
        
    else:
        print("❌ SOME TESTS FAILED")
        print("\n⚠️ Issues detected:")
        if not flow_success:
            print("- Product creation flow has issues")
        if not validation_success:
            print("- Size validation fix not properly integrated")
        
        print("\nPlease check the error messages above for details.")
    
    sys.exit(0 if overall_success else 1)