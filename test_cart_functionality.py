#!/usr/bin/env python3
"""
Test the add to cart functionality completely
"""
from project import create_app, db
from project.models import SellerProduct, CartItem, User, ProductVariant, VariantSize, Seller
import requests
import json

def create_test_data():
    """Create some test data for testing cart functionality"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create test user
            test_user = User(
                email='testuser@example.com',
                username='testuser',
                role='buyer',
                is_approved=True
            )
            test_user.set_password('testpass123')
            db.session.add(test_user)
            
            # Create test seller
            seller_user = User(
                email='seller@example.com', 
                username='testseller',
                role='seller',
                is_approved=True
            )
            seller_user.set_password('testpass123')
            db.session.add(seller_user)
            db.session.flush()  # Get IDs
            
            seller = Seller(
                user_id=seller_user.id,
                business_name='Test Store',
                is_verified=True
            )
            db.session.add(seller)
            db.session.flush()
            
            # Create test product
            test_product = SellerProduct(
                name='Test T-Shirt',
                price=29.99,
                description='A comfortable test t-shirt',
                seller_id=seller_user.id,
                category='clothing',
                is_active=True,
                variants='[{"variant_name": "Red", "stock": {"S": 10, "M": 15, "L": 8}}, {"variant_name": "Blue", "stock": {"S": 5, "M": 12, "L": 20}}]'
            )
            db.session.add(test_product)
            db.session.flush()  # Get product ID
            
            # Create product variants
            red_variant = ProductVariant(
                product_id=test_product.id,
                variant_name='Red',
                variant_value='#FF0000'
            )
            db.session.add(red_variant)
            db.session.flush()
            
            blue_variant = ProductVariant(
                product_id=test_product.id,
                variant_name='Blue',
                variant_value='#0000FF'
            )
            db.session.add(blue_variant)
            db.session.flush()
            
            # Create variant sizes
            sizes_data = [
                {'variant_id': red_variant.id, 'size_label': 'S', 'stock_quantity': 10},
                {'variant_id': red_variant.id, 'size_label': 'M', 'stock_quantity': 15},
                {'variant_id': red_variant.id, 'size_label': 'L', 'stock_quantity': 8},
                {'variant_id': blue_variant.id, 'size_label': 'S', 'stock_quantity': 5},
                {'variant_id': blue_variant.id, 'size_label': 'M', 'stock_quantity': 12},
                {'variant_id': blue_variant.id, 'size_label': 'L', 'stock_quantity': 20},
            ]
            
            for size_data in sizes_data:
                variant_size = VariantSize(**size_data)
                db.session.add(variant_size)
            
            db.session.commit()
            print("✅ Test data created successfully")
            print(f"   User ID: {test_user.id}")
            print(f"   Seller ID: {seller_user.id}")
            print(f"   Product ID: {test_product.id}")
            print(f"   Red Variant ID: {red_variant.id}")
            print(f"   Blue Variant ID: {blue_variant.id}")
            
            return test_product.id, red_variant.id, blue_variant.id
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            return None, None, None

def test_add_to_cart_api():
    """Test the add to cart API endpoint"""
    try:
        # Test data
        test_payload = {
            'product_id': 1,  # Assuming first product
            'color': 'Red',
            'size': 'M',
            'quantity': 2
        }
        
        print(f"\n🧪 Testing add to cart API with payload: {test_payload}")
        
        response = requests.post(
            'http://localhost:5000/add-to-cart',
            headers={'Content-Type': 'application/json'},
            json=test_payload
        )
        
        print(f"📡 Response status: {response.status_code}")
        if response.headers.get('Content-Type', '').startswith('application/json'):
            result = response.json()
            print(f"📋 Response data: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ Item successfully added to cart")
            else:
                print(f"❌ Failed to add to cart: {result.get('error', 'Unknown error')}")
        else:
            print(f"📄 Response text: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def check_cart_items():
    """Check current cart items in database"""
    app = create_app('development')
    
    with app.app_context():
        try:
            cart_items = db.session.query(CartItem).all()
            print(f"\n🛒 Cart items in database: {len(cart_items)}")
            
            for item in cart_items:
                print(f"  - ID: {item.id}")
                print(f"    Product: {item.product_name}")
                print(f"    Color: {item.color}")
                print(f"    Size: {item.size}")
                print(f"    Quantity: {item.quantity}")
                print(f"    Price: ${item.product_price}")
                print(f"    User ID: {item.user_id}")
                print(f"    Session ID: {item.session_id}")
                print("    ---")
                
        except Exception as e:
            print(f"❌ Error checking cart items: {e}")

if __name__ == '__main__':
    print("🧪 Starting comprehensive cart functionality test...")
    
    # Create test data
    product_id, red_variant_id, blue_variant_id = create_test_data()
    
    if product_id:
        # Check current cart items
        check_cart_items()
        
        # Test add to cart API
        test_add_to_cart_api()
        
        # Check cart items after API call
        check_cart_items()
    else:
        print("❌ Failed to create test data. Cannot proceed with tests.")