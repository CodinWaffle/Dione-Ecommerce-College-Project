#!/usr/bin/env python3
"""
Debug the color-size issue to see what's actually happening
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def debug_product_data():
    """Debug what data is actually being passed to the frontend"""
    try:
        from project import create_app, db
        from project.models import SellerProduct, ProductVariant, VariantSize
        
        app = create_app()
        with app.app_context():
            print("🔍 Debugging Product Data Structure")
            print("=" * 60)
            
            # Check all products and their variant data
            products = SellerProduct.query.all()
            
            for product in products:
                print(f"\n📦 Product: {product.name} (ID: {product.id})")
                
                # Check ProductVariant table data
                variants = ProductVariant.query.filter_by(product_id=product.id).all()
                print(f"   🎨 ProductVariant table: {len(variants)} variants")
                
                for variant in variants:
                    sizes = VariantSize.query.filter_by(variant_id=variant.id).all()
                    print(f"      • {variant.variant_name}: {len(sizes)} sizes")
                    for size in sizes:
                        print(f"        - {size.size_label}: {size.stock_quantity} stock")
                
                # Check variants JSON field
                print(f"   📄 Variants JSON field:")
                if product.variants:
                    try:
                        import json
                        variants_data = product.variants
                        if isinstance(variants_data, str):
                            variants_data = json.loads(variants_data)
                        
                        print(f"      Type: {type(variants_data)}")
                        if isinstance(variants_data, dict):
                            for key, value in variants_data.items():
                                print(f"      • {key}: {type(value)}")
                        elif isinstance(variants_data, list):
                            print(f"      List with {len(variants_data)} items")
                            for i, item in enumerate(variants_data[:3]):
                                print(f"        [{i}]: {type(item)} - {item}")
                    except Exception as e:
                        print(f"      Error parsing: {e}")
                else:
                    print(f"      No variants JSON data")
            
            return True
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_product_api():
    """Test API for a specific product"""
    try:
        from project import create_app
        from project.routes.main_routes import get_product_sizes_for_color
        
        app = create_app()
        with app.app_context():
            print(f"\n🧪 Testing Specific Product API")
            print(f"=" * 50)
            
            # Test with different products
            test_cases = [
                (37, "Black"),
                (38, "Black"),  # Different product
                (37, "White"),  # Same product, different color
                (37, "Red"),
            ]
            
            for product_id, color in test_cases:
                print(f"\n   Testing Product {product_id}, Color {color}")
                try:
                    response = get_product_sizes_for_color(product_id, color)
                    if hasattr(response, 'get_json'):
                        data = response.get_json()
                        if data and data.get('success'):
                            sizes = data.get('sizes', {})
                            print(f"   ✅ Found {len(sizes)} sizes: {list(sizes.keys())}")
                            for size, info in sizes.items():
                                print(f"      {size}: {info['stock']} stock")
                        else:
                            print(f"   ❌ API Error: {data.get('error') if data else 'No data'}")
                    else:
                        print(f"   ❌ Invalid response type: {type(response)}")
                except Exception as e:
                    print(f"   ❌ Exception: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Color-Size Debug Session")
    print("=" * 70)
    
    # Debug product data structure
    debug_success = debug_product_data()
    
    # Test API functionality
    api_success = test_specific_product_api()
    
    print(f"\n🏁 Debug Results")
    print(f"=" * 70)
    print(f"Data Structure Debug: {'✅ SUCCESS' if debug_success else '❌ FAILED'}")
    print(f"API Functionality Test: {'✅ SUCCESS' if api_success else '❌ FAILED'}")