#!/usr/bin/env python3
"""
Test script to verify that color variants are properly fetched from database
and displayed in product cards.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from project.models import SellerProduct, db
import json

def test_color_variants_extraction():
    """Test that color variants are properly extracted from database products"""
    app = create_app()
    
    with app.app_context():
        print("🎨 Testing Color Variants Extraction from Database")
        print("=" * 60)
        
        # Get all active seller products
        products = SellerProduct.query.filter_by(status='active').limit(10).all()
        
        if not products:
            print("❌ No active products found in database")
            return
        
        print(f"📦 Found {len(products)} active products")
        print()
        
        for product in products:
            print(f"🏷️  Product: {product.name} (ID: {product.id})")
            
            # Check if product has variants
            if product.variants:
                try:
                    # Parse variants JSON
                    variants_data = product.variants
                    if isinstance(variants_data, str):
                        variants_data = json.loads(variants_data)
                    
                    print(f"   📝 Raw variants type: {type(variants_data)}")
                    
                    # Extract colors
                    colors = []
                    if isinstance(variants_data, list):
                        print(f"   📋 Variants list with {len(variants_data)} items:")
                        for i, variant in enumerate(variants_data):
                            if isinstance(variant, dict):
                                color = variant.get('color')
                                size = variant.get('size', 'N/A')
                                stock = variant.get('stock', 0)
                                print(f"      {i+1}. Color: {color}, Size: {size}, Stock: {stock}")
                                if color and color not in colors:
                                    colors.append(color)
                    
                    elif isinstance(variants_data, dict):
                        print(f"   📋 Variants dict with {len(variants_data)} colors:")
                        for color_name, variant_info in variants_data.items():
                            print(f"      - {color_name}: {type(variant_info)}")
                            if color_name not in colors:
                                colors.append(color_name)
                    
                    print(f"   🎨 Extracted colors: {colors}")
                    
                except Exception as e:
                    print(f"   ❌ Error parsing variants: {e}")
                    print(f"   📝 Raw variants: {product.variants}")
            else:
                print("   ⚪ No variants found")
            
            print()

def test_api_response():
    """Test the API response format"""
    app = create_app()
    
    with app.test_client() as client:
        print("🌐 Testing API Response Format")
        print("=" * 60)
        
        # Test the products API
        response = client.get('/api/products?limit=5')
        
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            
            print(f"📦 API returned {len(products)} products")
            
            for product in products[:3]:  # Test first 3 products
                print(f"\n🏷️  Product: {product.get('name')} (ID: {product.get('id')})")
                print(f"   🎨 Colors: {product.get('colors', [])}")
                print(f"   📋 Variants: {len(product.get('variants', []))} items")
                
                for variant in product.get('variants', [])[:3]:  # Show first 3 variants
                    print(f"      - {variant.get('color')}: {variant.get('image', 'No image')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")

if __name__ == '__main__':
    print("🧪 Testing Color Variants Display System")
    print("=" * 60)
    
    test_color_variants_extraction()
    print()
    test_api_response()
    
    print("\n✅ Test completed!")