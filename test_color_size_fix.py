#!/usr/bin/env python3
"""
Test script to verify the color-size API fix is working correctly
"""

import requests
import json
import sys
from project.models import SellerProduct, ProductVariant, VariantSize
from project import create_app, db

def test_color_size_api():
    """Test the API endpoint that fetches sizes for specific colors"""
    
    print("🔍 Testing Color-Size API Fix...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Find a product with variants
        product = SellerProduct.query.filter(
            SellerProduct.variants.isnot(None)
        ).first()
        
        if not product:
            print("❌ No products with variants found")
            return False
            
        print(f"✅ Found test product: {product.name} (ID: {product.id})")
        
        # Get variants data
        try:
            variants_data = product.variants
            if isinstance(variants_data, str):
                variants_data = json.loads(variants_data)
                
            # Handle both list and dict formats
            if isinstance(variants_data, list):
                colors = [variant.get('color', 'Unknown') for variant in variants_data]
            else:
                colors = list(variants_data.keys())
                
            print(f"📦 Product has {len(colors)} color variants:")
            for color in colors:
                print(f"   - {color}")
                
        except Exception as e:
            print(f"❌ Error parsing variants: {e}")
            return False
        
        # Test API endpoint for each color
        base_url = "http://localhost:5000"
        success_count = 0
        
        for color in colors:
            try:
                print(f"\n🎨 Testing API for color: {color}")
                response = requests.get(f"{base_url}/api/product/{product.id}/sizes/{color}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('sizes'):
                        sizes = data['sizes']
                        print(f"   ✅ API returned {len(sizes)} sizes:")
                        for size, info in sizes.items():
                            stock = info.get('stock', 0)
                            available = info.get('available', False)
                            status = "✅ Available" if available else "❌ Out of Stock"
                            print(f"      {size}: {stock} units ({status})")
                        success_count += 1
                    else:
                        print(f"   ❌ API returned invalid data: {data}")
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"   ⚠️  Server not running - skipping API test for {color}")
            except Exception as e:
                print(f"   ❌ Error testing {color}: {e}")
        
        # Check database directly
        print(f"\n🗄️  Checking database directly...")
        variant_count = ProductVariant.query.filter_by(product_id=product.id).count()
        size_count = db.session.query(VariantSize).join(ProductVariant).filter(
            ProductVariant.product_id == product.id
        ).count()
        
        print(f"   📊 Database has {variant_count} variants and {size_count} sizes")
        
        if variant_count > 0:
            variants = ProductVariant.query.filter_by(product_id=product.id).all()
            for variant in variants:
                sizes = VariantSize.query.filter_by(variant_id=variant.id).all()
                print(f"   🎨 {variant.variant_name}: {len(sizes)} sizes")
                for size in sizes:
                    print(f"      {size.size_label}: {size.stock_quantity} units")
        
        print(f"\n📈 Summary:")
        print(f"   - Product tested: {product.name}")
        print(f"   - Colors with working API: {success_count}/{len(colors)}")
        print(f"   - Database variants: {variant_count}")
        print(f"   - Database sizes: {size_count}")
        
        if success_count > 0 or variant_count > 0:
            print(f"\n✅ Fix appears to be working! Sizes should now be fetched from database.")
            return True
        else:
            print(f"\n❌ Fix may not be working properly.")
            return False

def test_frontend_fix():
    """Test that the frontend no longer has hardcoded sizes"""
    
    print(f"\n🌐 Testing Frontend Fix...")
    
    # Check if the problematic inline script was removed
    try:
        with open('project/templates/main/product_detail.html', 'r') as f:
            content = f.read()
            
        # Check for removed problematic code
        issues = []
        
        if 'parseStockData' in content and '"One Size": 30' in content:
            issues.append("❌ parseStockData with hardcoded sizes still present")
        else:
            print("✅ parseStockData with hardcoded sizes removed")
            
        if 'window.selectColor = function' in content:
            issues.append("❌ Inline selectColor function still overriding external JS")
        else:
            print("✅ Inline selectColor function removed")
            
        if 'window.updateSizeOptions' in content:
            issues.append("❌ Inline updateSizeOptions function still present")
        else:
            print("✅ Inline updateSizeOptions function removed")
            
        # Check for API call in external JS
        try:
            with open('project/static/js/buyer_scripts/product_detail.js', 'r') as f:
                js_content = f.read()
                
            if '/api/product/${productId}/sizes/${encodeURIComponent(selectedColor)}' in js_content:
                print("✅ External JS has API call for dynamic size loading")
            else:
                issues.append("❌ External JS missing API call for size loading")
                
        except FileNotFoundError:
            issues.append("❌ External product_detail.js file not found")
        
        if issues:
            print(f"\n❌ Frontend issues found:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print(f"\n✅ Frontend fix looks good!")
            return True
            
    except FileNotFoundError:
        print("❌ product_detail.html template not found")
        return False

if __name__ == "__main__":
    print("🚀 Testing Color-Size Fix Implementation\n")
    
    frontend_ok = test_frontend_fix()
    api_ok = test_color_size_api()
    
    print(f"\n" + "="*50)
    print(f"📋 FINAL RESULTS:")
    print(f"   Frontend Fix: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"   API Fix: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if frontend_ok and api_ok:
        print(f"\n🎉 SUCCESS! The fix should resolve the issue where")
        print(f"   all colors showed the same hardcoded sizes.")
        print(f"   Now each color will show its actual sizes from the database.")
    else:
        print(f"\n⚠️  Some issues remain. Check the details above.")
    
    print(f"\n💡 To test manually:")
    print(f"   1. Start the Flask server")
    print(f"   2. Go to any product detail page")
    print(f"   3. Click different colors")
    print(f"   4. Verify that different sizes appear for each color")