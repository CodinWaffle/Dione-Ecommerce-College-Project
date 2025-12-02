#!/usr/bin/env python3
"""
Detailed cart functionality analysis
"""
from project import create_app, db
from project.models import SellerProduct, CartItem, User
import json

def analyze_cart_issues():
    """Analyze the current cart issues"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check existing cart items
            cart_items = db.session.query(CartItem).all()
            print(f"📊 Current cart items ({len(cart_items)}):")
            for item in cart_items:
                print(f"  - ID: {item.id}")
                print(f"    Product: {item.product_name} (Product ID: {item.product_id})")
                print(f"    Color: {item.color}, Size: {item.size}")
                print(f"    Quantity: {item.quantity}")
                print(f"    User ID: {item.user_id}, Session ID: {item.session_id}")
                print("    ---")
            
            # Check products
            products = db.session.query(SellerProduct).all()
            print(f"\n📦 Available products ({len(products)}):")
            for product in products:
                print(f"  - ID: {product.id}: {product.name}")
                print(f"    Price: ${product.price}")
                print(f"    Active: {product.is_active}")
                if hasattr(product, 'variants') and product.variants:
                    print(f"    Variants: {product.variants[:100]}...")
                print("    ---")
                
            return products[0] if products else None
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None

def test_cart_with_different_data():
    """Test cart with different data to isolate the issue"""
    app = create_app('development')
    
    with app.app_context():
        try:
            from project.routes.main_routes import add_to_cart
            import json
            
            # Test with a product that should exist
            product = db.session.query(SellerProduct).first()
            if not product:
                print("❌ No products found")
                return
            
            print(f"🧪 Testing with product: {product.name} (ID: {product.id})")
            
            # Try different color/size combinations
            test_cases = [
                {'product_id': product.id, 'color': 'Black', 'size': 'S', 'quantity': 1},
                {'product_id': product.id, 'color': 'White', 'size': 'M', 'quantity': 1},
                {'product_id': product.id, 'color': 'Blue', 'size': 'L', 'quantity': 1},
            ]
            
            for i, test_data in enumerate(test_cases, 1):
                print(f"\n🧪 Test case {i}: {test_data}")
                
                with app.test_request_context(
                    '/add-to-cart',
                    method='POST',
                    data=json.dumps(test_data),
                    content_type='application/json'
                ):
                    try:
                        response = add_to_cart()
                        
                        # Get response data
                        if hasattr(response, 'get_json'):
                            data = response.get_json()
                            print(f"  📋 Response data: {json.dumps(data, indent=4)}")
                        else:
                            print(f"  📋 Response: {response}")
                            
                        print(f"  📡 Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
                        
                    except Exception as e:
                        print(f"  ❌ Test case {i} failed: {e}")
                        import traceback
                        traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Testing failed: {e}")
            import traceback
            traceback.print_exc()

def clear_test_cart():
    """Clear any existing test cart items"""
    app = create_app('development')
    
    with app.app_context():
        try:
            count = db.session.query(CartItem).count()
            if count > 0:
                print(f"🗑️ Clearing {count} existing cart items...")
                db.session.query(CartItem).delete()
                db.session.commit()
                print("✅ Cart cleared")
            else:
                print("✅ Cart is already empty")
                
        except Exception as e:
            print(f"❌ Failed to clear cart: {e}")

if __name__ == '__main__':
    print("🔬 Detailed cart functionality analysis...\n")
    
    # Analyze current state
    product = analyze_cart_issues()
    
    if product:
        # Clear cart for clean testing
        clear_test_cart()
        print()
        
        # Test with different data
        test_cart_with_different_data()
        
        print("\n📋 Final cart state:")
        analyze_cart_issues()
    else:
        print("❌ No products available for testing")