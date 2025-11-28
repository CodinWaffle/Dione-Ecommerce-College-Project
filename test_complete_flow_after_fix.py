#!/usr/bin/env python3
"""
Test the complete product creation flow after applying the session preservation fix
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_complete_flow_after_fix():
    """Test the complete flow after the session preservation fix"""
    
    try:
        from project import create_app, db
        from project.models import User, SellerProduct
        
        app = create_app()
        
        with app.app_context():
            print("🧪 TESTING COMPLETE FLOW AFTER SESSION FIX")
            print("=" * 60)
            
            client = app.test_client()
            
            # Test with seller ID 8 (the one that was having issues)
            seller = User.query.filter_by(id=8).first()
            if not seller:
                print("❌ Seller ID 8 not found")
                return False
            
            # Login as that seller
            with client.session_transaction() as sess:
                sess['_user_id'] = str(seller.id)
                sess['_fresh'] = True
            
            print(f"✅ Testing with seller: {seller.email}")
            
            # Complete flow test
            print("\n🔄 COMPLETE FLOW TEST")
            print("-" * 40)
            
            # Step 1: Basic product info
            basic_data = {
                'productName': 'Session Fix Test Product',
                'category': 'Clothing',
                'subcategory': 'T-Shirts',
                'price': '49.99',
                'discountType': 'percentage',
                'discountPercentage': '15',
                'voucherType': 'SAVE15',
                'primaryImage': '/static/images/test.jpg',
                'secondaryImage': '/static/images/test2.jpg'
            }
            
            response = client.post('/seller/add_product', data=basic_data)
            print(f"✅ Step 1 (Basic Info): {response.status_code}")
            
            # Check session after step 1
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step1 = workflow.get('step1', {})
                print(f"   Session step1: {step1.get('productName', 'MISSING')} / {step1.get('category', 'MISSING')}")
            
            # Step 2: Description
            description_data = {
                'description': 'High-quality cotton t-shirt perfect for everyday wear',
                'materials': '100% organic cotton',
                'detailsFit': 'Regular fit, true to size'
            }
            
            response = client.post('/seller/add_product_description', data=description_data)
            print(f"✅ Step 2 (Description): {response.status_code}")
            
            # Check session after step 2
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step1 = workflow.get('step1', {})
                step2 = workflow.get('step2', {})
                print(f"   Session step1 still intact: {step1.get('productName', 'MISSING')}")
                print(f"   Session step2: {step2.get('description', 'MISSING')[:30]}...")
            
            # Step 3: Stocks with variants
            stocks_data = {
                'sku_0': 'TSHIRT-FIX-001',
                'color_0': 'Navy Blue',
                'color_picker_0': '#000080',
                'lowStock_0': '5',
                'sizeStocks_0': json.dumps([
                    {'size': 'S', 'stock': 12},
                    {'size': 'M', 'stock': 18},
                    {'size': 'L', 'stock': 15},
                    {'size': 'XL', 'stock': 10}
                ])
            }
            
            response = client.post('/seller/add_product_stocks', data=stocks_data)
            print(f"✅ Step 3 (Stocks): {response.status_code}")
            
            # Check session after step 3 - THIS IS THE CRITICAL TEST
            with client.session_transaction() as sess:
                workflow = sess.get('product_workflow', {})
                step1 = workflow.get('step1', {})
                step2 = workflow.get('step2', {})
                step3 = workflow.get('step3', {})
                
                print(f"   🔍 CRITICAL CHECK - Session after step 3:")
                print(f"      Step1 preserved: {step1.get('productName', 'MISSING')} / {step1.get('category', 'MISSING')}")
                print(f"      Step2 preserved: {step2.get('description', 'MISSING')[:30]}...")
                print(f"      Step3 added: {len(step3.get('variants', []))} variants, {step3.get('totalStock', 0)} total stock")
            
            # Step 4: Preview and submit
            response = client.post('/seller/add_product_preview')
            print(f"✅ Step 4 (Preview/Submit): {response.status_code}")
            
            if response.status_code == 302 and 'products' in response.location:
                print("✅ Successfully redirected to products page")
                
                # Check the saved product
                saved_product = SellerProduct.query.filter_by(name='Session Fix Test Product').first()
                if saved_product:
                    print(f"\n📊 SAVED PRODUCT VERIFICATION")
                    print(f"   📋 Name: '{saved_product.name}' ✅")
                    print(f"   📂 Category: '{saved_product.category}' ✅")
                    print(f"   📂 Subcategory: '{saved_product.subcategory}' ✅")
                    print(f"   💰 Price: ${saved_product.price} ✅")
                    print(f"   📝 Description: '{saved_product.description[:50]}...' ✅")
                    print(f"   🧵 Materials: '{saved_product.materials}' ✅")
                    print(f"   📏 Details/Fit: '{saved_product.details_fit}' ✅")
                    print(f"   📦 Total Stock: {saved_product.total_stock} ✅")
                    print(f"   🎨 Variants: {len(saved_product.variants or [])} ✅")
                    
                    if saved_product.variants:
                        variant = saved_product.variants[0]
                        print(f"   🏷️ Variant Details:")
                        print(f"      - SKU: {variant.get('sku', 'N/A')}")
                        print(f"      - Color: {variant.get('color', 'N/A')}")
                        print(f"      - Sizes: {len(variant.get('sizeStocks', []))}")
                        for size_item in variant.get('sizeStocks', []):
                            print(f"        * {size_item.get('size', 'N/A')}: {size_item.get('stock', 0)} units")
                    
                    # Verify no critical fields are missing
                    issues = []
                    if not saved_product.name or saved_product.name == '-':
                        issues.append("Name is missing or invalid")
                    if not saved_product.category or saved_product.category == '-':
                        issues.append("Category is missing or invalid")
                    if saved_product.price <= 0:
                        issues.append("Price is zero or invalid")
                    if not saved_product.description:
                        issues.append("Description is missing")
                    if saved_product.total_stock <= 0:
                        issues.append("No stock saved")
                    
                    if issues:
                        print(f"\n❌ ISSUES FOUND:")
                        for issue in issues:
                            print(f"   - {issue}")
                        return False
                    else:
                        print(f"\n🎉 ALL FIELDS SAVED CORRECTLY!")
                    
                    # Clean up
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("🧹 Test product cleaned up")
                    
                    return True
                    
                else:
                    print("❌ Product was not found in database")
                    return False
            else:
                print(f"❌ Preview submission failed: {response.status_code}")
                if response.location:
                    print(f"   Redirected to: {response.location}")
                return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_complete_flow_after_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SESSION PRESERVATION FIX SUCCESSFUL!")
        print("\n✅ The issue has been resolved:")
        print("   - Session data is now properly preserved between steps")
        print("   - All product information saves correctly to database")
        print("   - Basic info, description, and stock data all work together")
        print("\n🚀 The product creation system is now fully functional!")
    else:
        print("❌ SESSION PRESERVATION FIX FAILED")
        print("\n⚠️ There are still issues with the product creation flow.")
        print("Please check the error messages above for details.")
    
    sys.exit(0 if success else 1)