#!/usr/bin/env python3
"""
Debug script to identify why sizes aren't loading when colors are selected
"""

import requests
import json
from project.models import SellerProduct, ProductVariant, VariantSize
from project import create_app, db

def debug_size_loading():
    """Debug the size loading issue"""
    
    print("🔍 Debugging Size Loading Issue...")
    
    app = create_app()
    
    with app.app_context():
        # Find products with variants
        products = SellerProduct.query.filter(
            SellerProduct.variants.isnot(None)
        ).limit(3).all()
        
        if not products:
            print("❌ No products with variants found")
            return
            
        for product in products:
            print(f"\n📦 Product: {product.name} (ID: {product.id})")
            
            # Check variants data structure
            try:
                variants_data = product.variants
                if isinstance(variants_data, str):
                    variants_data = json.loads(variants_data)
                    
                print(f"   📊 Variants type: {type(variants_data)}")
                print(f"   📊 Variants content: {variants_data}")
                
                # Extract colors from variants
                if isinstance(variants_data, list):
                    colors = []
                    for variant in variants_data:
                        if isinstance(variant, dict) and 'color' in variant:
                            colors.append(variant['color'])
                    print(f"   🎨 Colors from list format: {colors}")
                elif isinstance(variants_data, dict):
                    colors = list(variants_data.keys())
                    print(f"   🎨 Colors from dict format: {colors}")
                else:
                    print(f"   ❌ Unknown variants format: {type(variants_data)}")
                    continue
                    
            except Exception as e:
                print(f"   ❌ Error parsing variants: {e}")
                continue
            
            # Check database variants
            db_variants = ProductVariant.query.filter_by(product_id=product.id).all()
            db_colors = [v.variant_name for v in db_variants]
            print(f"   🗄️  Database colors: {db_colors}")
            
            # Test API for each color from variants data
            for color in colors:
                print(f"\n   🎨 Testing color: '{color}'")
                try:
                    response = requests.get(f"http://localhost:5000/api/product/{product.id}/sizes/{color}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"      ✅ API Response: {data}")
                        if data.get('success') and data.get('sizes'):
                            sizes = data['sizes']
                            print(f"      📏 Found {len(sizes)} sizes:")
                            for size, info in sizes.items():
                                print(f"         {size}: {info}")
                        else:
                            print(f"      ⚠️  No sizes returned for '{color}'")
                    else:
                        print(f"      ❌ API error: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    print(f"      ⚠️  Server not running")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            
            # Test API for database colors
            for db_color in db_colors:
                if db_color not in colors:
                    print(f"\n   🗄️  Testing DB color not in variants: '{db_color}'")
                    try:
                        response = requests.get(f"http://localhost:5000/api/product/{product.id}/sizes/{db_color}")
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success') and data.get('sizes'):
                                sizes = data['sizes']
                                print(f"      📏 DB color has {len(sizes)} sizes:")
                                for size, info in sizes.items():
                                    print(f"         {size}: {info}")
                    except:
                        pass

def check_frontend_javascript():
    """Check if the frontend JavaScript is correctly calling the API"""
    
    print(f"\n🌐 Checking Frontend JavaScript...")
    
    try:
        with open('project/static/js/buyer_scripts/product_detail.js', 'r') as f:
            js_content = f.read()
            
        # Check for API call
        if '/api/product/${productId}/sizes/${encodeURIComponent(selectedColor)}' in js_content:
            print("✅ API call found in JavaScript")
        else:
            print("❌ API call NOT found in JavaScript")
            
        # Check for updateSizeAvailability function
        if 'function updateSizeAvailability()' in js_content:
            print("✅ updateSizeAvailability function found")
        else:
            print("❌ updateSizeAvailability function NOT found")
            
        # Check for selectColor function
        if 'function selectColor(' in js_content:
            print("✅ selectColor function found")
        else:
            print("❌ selectColor function NOT found")
            
        # Check if selectColor calls updateSizeAvailability
        if 'updateSizeAvailability()' in js_content:
            print("✅ updateSizeAvailability is called")
        else:
            print("❌ updateSizeAvailability is NOT called")
            
    except FileNotFoundError:
        print("❌ product_detail.js file not found")

def check_template_issues():
    """Check the template for potential issues"""
    
    print(f"\n📄 Checking Template...")
    
    try:
        with open('project/templates/main/product_detail.html', 'r') as f:
            template_content = f.read()
            
        # Check for sizeOptions container
        if 'id="sizeOptions"' in template_content:
            print("✅ sizeOptions container found in template")
        else:
            print("❌ sizeOptions container NOT found in template")
            
        # Check for conflicting inline scripts
        if 'window.selectColor = function' in template_content:
            print("❌ Conflicting inline selectColor function still present")
        else:
            print("✅ No conflicting inline selectColor function")
            
        # Check for parseStockData
        if 'parseStockData' in template_content:
            print("❌ parseStockData function still present")
        else:
            print("✅ parseStockData function removed")
            
        # Check for hardcoded sizes
        if '"One Size": 30' in template_content or '"XS": 10' in template_content:
            print("❌ Hardcoded sizes still present")
        else:
            print("✅ No hardcoded sizes found")
            
    except FileNotFoundError:
        print("❌ product_detail.html template not found")

if __name__ == "__main__":
    print("🚀 Debugging Size Loading Issue\n")
    
    check_template_issues()
    check_frontend_javascript()
    debug_size_loading()
    
    print(f"\n" + "="*60)
    print(f"💡 DEBUGGING CHECKLIST:")
    print(f"1. Check browser console for JavaScript errors")
    print(f"2. Check network tab to see if API calls are being made")
    print(f"3. Verify color names match between frontend and database")
    print(f"4. Ensure Flask server is running on localhost:5000")
    print(f"5. Check if selectColor function is being called when clicking colors")