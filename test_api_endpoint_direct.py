#!/usr/bin/env python3
"""
Test the API endpoint directly without server
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_api_endpoint_direct():
    """Test the API endpoint directly"""
    try:
        from project import create_app
        from project.routes.main_routes import get_product_sizes_for_color
        
        app = create_app()
        with app.app_context():
            print("🧪 Testing API Endpoint Directly")
            print("=" * 50)
            
            # Test with known product and color
            product_id = 37
            color = "Black"
            
            print(f"Testing product {product_id}, color {color}")
            
            try:
                # Call the function directly
                response = get_product_sizes_for_color(product_id, color)
                print(f"Response type: {type(response)}")
                print(f"Response: {response}")
                
                # If it's a Flask response, get the data
                if hasattr(response, 'get_json'):
                    data = response.get_json()
                    print(f"JSON data: {data}")
                elif hasattr(response, 'data'):
                    print(f"Response data: {response.data}")
                
            except Exception as e:
                print(f"Error calling function: {e}")
                import traceback
                traceback.print_exc()
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_endpoint_direct()