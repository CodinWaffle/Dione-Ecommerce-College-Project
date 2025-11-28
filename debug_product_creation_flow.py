#!/usr/bin/env python3
"""
Debug script to test product creation flow and identify database saving issues
"""

import sys
import os
import json
from datetime import datetime
from decimal import Decimal

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_product_creation():
    """Test the product creation flow to identify database issues"""
    
    try:
        # Import Flask app and models
        from project import create_app, db
        from project.models import SellerProduct, User
        from flask import current_app
        
        app = create_app()
        
        with app.app_context():
            print("=== Product Creation Debug Test ===")
            
            # Check database connection
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text('SELECT 1'))
                print("✓ Database connection successful")
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                return False
            
            # Check if seller_product_management table exists
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(db.text("""
                        SELECT TABLE_NAME FROM information_schema.tables 
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'seller_product_management'
                    """)).fetchone()
                
                if result:
                    print("✓ seller_product_management table exists")
                else:
                    print("✗ seller_product_management table does not exist")
                    print("Creating table...")
                    db.create_all()
                    print("✓ Tables created")
            except Exception as e:
                print(f"✗ Table check failed: {e}")
                return False
            
            # Check if we have a test user (seller)
            test_user = User.query.filter_by(email='test@seller.com').first()
            if not test_user:
                print("Creating test seller user...")
                test_user = User(
                    username='testseller',
                    email='test@seller.com',
                    password='dummy_hash',
                    role='seller',
                    is_approved=True
                )
                db.session.add(test_user)
                db.session.commit()
                print("✓ Test seller created")
            else:
                print("✓ Test seller exists")
            
            # Test product creation with sample data
            print("\n=== Testing Product Creation ===")
            
            sample_product_data = {
                'step1': {
                    'productName': 'Test Product Debug',
                    'category': 'Electronics',
                    'subcategory': 'Phones',
                    'price': '299.99',
                    'discountType': 'percentage',
                    'discountPercentage': '10',
                    'voucherType': 'standard',
                    'primaryImage': '/static/images/test.jpg',
                    'secondaryImage': '/static/images/test2.jpg',
                    'subitem': ['Feature1', 'Feature2']
                },
                'step2': {
                    'description': 'Test product description',
                    'materials': 'Test materials',
                    'detailsFit': 'Test fit details',
                    'sizeGuide': ['/static/images/size1.jpg'],
                    'certifications': ['/static/images/cert1.jpg']
                },
                'step3': {
                    'variants': [
                        {
                            'sku': 'TEST-001',
                            'color': 'Red',
                            'colorHex': '#FF0000',
                            'size': 'M',
                            'stock': 10,
                            'lowStock': 2
                        }
                    ],
                    'totalStock': 10
                }
            }
            
            step1 = sample_product_data['step1']
            step2 = sample_product_data['step2']
            step3 = sample_product_data['step3']
            
            # Helper function to convert to decimal
            def _to_decimal(value, default=0):
                if value is None or value == '':
                    return Decimal(str(default))
                try:
                    return Decimal(str(value))
                except:
                    return Decimal(str(default))
            
            # Helper function to convert to int
            def _to_int(value, default=0):
                if value is None or value == '':
                    return default
                try:
                    return int(value)
                except:
                    return default
            
            # Calculate pricing
            base_price = _to_decimal(step1.get('price'))
            discount_type = (step1.get('discountType') or '').lower() or None
            discount_value = _to_decimal(step1.get('discountPercentage', 0))
            
            sale_price = base_price
            compare_price = None
            
            if discount_type == 'percentage' and discount_value > 0:
                compare_price = base_price
                percentage_left = max(Decimal('0'), Decimal('100') - discount_value)
                sale_price = (base_price * percentage_left) / Decimal('100')
            elif discount_type == 'fixed' and discount_value > 0:
                compare_price = base_price
                sale_price = max(base_price - discount_value, Decimal('0.00'))
            
            print(f"Base price: {base_price}")
            print(f"Sale price: {sale_price}")
            print(f"Compare price: {compare_price}")
            
            # Create product instance
            try:
                product = SellerProduct(
                    seller_id=test_user.id,
                    name=step1.get('productName', ''),
                    description=step2.get('description', ''),
                    category=step1.get('category', ''),
                    subcategory=step1.get('subcategory'),
                    price=float(sale_price),
                    compare_at_price=float(compare_price) if compare_price else None,
                    discount_type=discount_type,
                    discount_value=float(discount_value) if discount_value > 0 else None,
                    voucher_type=step1.get('voucherType'),
                    materials=step2.get('materials', ''),
                    details_fit=step2.get('detailsFit', ''),
                    primary_image=step1.get('primaryImage', '/static/image/banner.png'),
                    secondary_image=step1.get('secondaryImage'),
                    total_stock=step3.get('totalStock', 0),
                    low_stock_threshold=5,
                    variants=step3.get('variants', []),
                    attributes={
                        'subitems': step1.get('subitem', []),
                        'size_guides': step2.get('sizeGuide', []),
                        'certifications': step2.get('certifications', []),
                    },
                    created_at=datetime.utcnow(),
                )
                
                print("✓ Product instance created successfully")
                print(f"Product name: {product.name}")
                print(f"Product category: {product.category}")
                print(f"Product price: {product.price}")
                print(f"Product variants: {product.variants}")
                
            except Exception as e:
                print(f"✗ Failed to create product instance: {e}")
                return False
            
            # Try to save to database
            try:
                db.session.add(product)
                db.session.commit()
                print("✓ Product saved to database successfully!")
                
                # Verify the product was saved
                saved_product = SellerProduct.query.filter_by(name='Test Product Debug').first()
                if saved_product:
                    print(f"✓ Product verified in database with ID: {saved_product.id}")
                    
                    # Clean up test product
                    db.session.delete(saved_product)
                    db.session.commit()
                    print("✓ Test product cleaned up")
                else:
                    print("✗ Product not found in database after save")
                    return False
                    
            except Exception as e:
                print(f"✗ Failed to save product to database: {e}")
                db.session.rollback()
                return False
            
            print("\n=== All tests passed! ===")
            return True
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_product_creation()
    if not success:
        print("\n=== Debug suggestions ===")
        print("1. Check if the database file exists and is writable")
        print("2. Verify Flask app configuration")
        print("3. Check if all required tables exist")
        print("4. Verify user authentication and session data")
        sys.exit(1)
    else:
        print("\nProduct creation flow is working correctly!")