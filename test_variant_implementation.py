#!/usr/bin/env python3
"""
Test script to verify the variant implementation works correctly.
This script creates sample products with variants and tests the API endpoints.
"""

import sys
import os
import json
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project import create_app, db
from project.models import SellerProduct, User

def create_test_data():
    """Create test products with variant data."""
    
    # Create a test seller user if not exists
    seller = User.query.filter_by(email='test_seller@example.com').first()
    if not seller:
        seller = User(
            email='test_seller@example.com',
            role='seller',
            is_approved=True
        )
        db.session.add(seller)
        db.session.commit()
    
    # Sample variant data structure
    variants = [
        {
            'sku': 'TSHIRT-BLK-XS',
            'color': 'Black',
            'colorHex': '#000000',
            'size': 'XS',
            'stock': 5,
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-BLK-S',
            'color': 'Black',
            'colorHex': '#000000',
            'size': 'S',
            'stock': 8,
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-BLK-M',
            'color': 'Black',
            'colorHex': '#000000',
            'size': 'M',
            'stock': 0,  # Out of stock
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-RED-XS',
            'color': 'Red',
            'colorHex': '#dc143c',
            'size': 'XS',
            'stock': 3,
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-RED-S',
            'color': 'Red',
            'colorHex': '#dc143c',
            'size': 'S',
            'stock': 0,  # Out of stock
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-BLUE-XS',
            'color': 'Blue',
            'colorHex': '#0066cc',
            'size': 'XS',
            'stock': 0,  # Out of stock
            'lowStock': 2
        },
        {
            'sku': 'TSHIRT-BLUE-S',
            'color': 'Blue',
            'colorHex': '#0066cc',
            'size': 'S',
            'stock': 0,  # Out of stock - entire color out of stock
            'lowStock': 2
        }
    ]
    
    # Create test product
    test_product = SellerProduct.query.filter_by(name='Test Variant T-Shirt').first()
    if test_product:
        # Update existing
        test_product.variants = variants
        test_product.total_stock = sum(v['stock'] for v in variants)
    else:
        # Create new
        test_product = SellerProduct(
            seller_id=seller.id,
            name='Test Variant T-Shirt',
            description='A test t-shirt with multiple color and size variants',
            category='clothing',
            subcategory='tops',
            price=Decimal('29.99'),
            compare_at_price=Decimal('39.99'),
            primary_image='/static/image/banner.png',
            secondary_image='/static/image/banner.png',
            variants=variants,
            total_stock=sum(v['stock'] for v in variants),
            status='active'
        )
        db.session.add(test_product)
    
    db.session.commit()
    print(f"Created/updated test product with ID: {test_product.id}")
    return test_product

def test_api_endpoints(product_id):
    """Test the API endpoints."""
    from flask import url_for
    
    with app.test_client() as client:
        # Test main product API
        response = client.get(f'/api/product/{product_id}')
        print(f"\nAPI Product Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            product = data.get('product', {})
            print(f"Product Name: {product.get('name')}")
            print(f"Variant Photos: {product.get('variant_photos')}")
            print(f"Stock Data: {product.get('stock_data')}")
        else:
            print(f"API Error: {response.get_json()}")
        
        # Test product detail page
        response = client.get(f'/product/{product_id}')
        print(f"\nProduct Detail Page Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Product detail page loaded successfully")
        else:
            print("Product detail page failed to load")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Create test data
        print("Creating test data...")
        test_product = create_test_data()
        
        # Test API endpoints
        print("\nTesting API endpoints...")
        test_api_endpoints(test_product.id)
        
        print(f"\nTest complete! Visit http://localhost:5000/product/{test_product.id} to see the variant UI in action.")
        print("\nExpected behavior:")
        print("- Black color should have XS (5 stock), S (8 stock), M (0 stock - disabled)")
        print("- Red color should have XS (3 stock), S (0 stock - disabled)")
        print("- Blue color should be completely out of stock (disabled with OOS label)")
        print("- Selecting different colors should update available sizes")
        print("- Selecting different sizes should update stock count")
        print("- Out of stock combinations should disable the Add to Bag button")