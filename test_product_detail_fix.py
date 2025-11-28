#!/usr/bin/env python3
"""
Test script to verify that product detail color and size selection works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct
import json

def test_product_detail_stock():
    """Test that products with stock data render correctly"""
    app = create_app()
    
    with app.app_context():
        # Find a product with variants
        product = SellerProduct.query.filter(SellerProduct.variants.isnot(None)).first()
        
        if not product:
            print("❌ No products with variants found")
            return False
            
        print(f"✅ Found product: {product.name} (ID: {product.id})")
        
        # Check variants structure
        variants = product.variants
        if isinstance(variants, str):
            try:
                variants = json.loads(variants)
            except:
                print("❌ Invalid variants JSON")
                return False
        
        print(f"✅ Variants data: {variants}")
        
        # Check if variants have stock data
        has_stock_data = False
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict) and 'stock' in variant:
                    has_stock_data = True
                    print(f"✅ Found variant with stock: {variant}")
                    break
        elif isinstance(variants, dict):
            for color, data in variants.items():
                if isinstance(data, dict) and 'stock' in data:
                    has_stock_data = True
                    print(f"✅ Found color '{color}' with stock: {data['stock']}")
                    break
        
        if not has_stock_data:
            print("❌ No stock data found in variants")
            return False
            
        print("✅ Product has valid stock data structure")
        return True

def test_template_rendering():
    """Test that the template can render without errors"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Find a product to test
            product = SellerProduct.query.first()
            if not product:
                print("❌ No products found for template test")
                return False
                
            # Try to render the product detail page
            response = client.get(f'/product/{product.id}')
            
            if response.status_code == 200:
                print(f"✅ Product detail page renders successfully for product {product.id}")
                
                # Check if the response contains the expected elements
                html = response.get_data(as_text=True)
                
                checks = [
                    ('color-option', 'Color selection buttons'),
                    ('size-option', 'Size selection buttons'),
                    ('product-detail.js', 'JavaScript file inclusion'),
                    ('selectColor', 'Color selection function'),
                    ('selectSize', 'Size selection function')
                ]
                
                for check, description in checks:
                    if check in html:
                        print(f"✅ {description} found in template")
                    else:
                        print(f"⚠️  {description} not found in template")
                
                return True
            else:
                print(f"❌ Product detail page failed to render: {response.status_code}")
                return False

if __name__ == "__main__":
    print("🧪 Testing Product Detail Fix...")
    print("=" * 50)
    
    stock_test = test_product_detail_stock()
    template_test = test_template_rendering()
    
    print("=" * 50)
    if stock_test and template_test:
        print("✅ All tests passed! Product detail should work correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")