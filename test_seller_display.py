#!/usr/bin/env python3
"""
Test seller information display in header and product dropdown
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def test_seller_info():
    """Test seller information display"""
    try:
        from project import create_app, db
        from project.models import User, Seller
        
        app = create_app()
        with app.app_context():
            print("🧪 Testing Seller Information Display")
            print("=" * 50)
            
            # Check existing sellers
            sellers = Seller.query.all()
            print(f"Found {len(sellers)} sellers in database")
            
            for seller in sellers:
                user = User.query.get(seller.user_id)
                print(f"\n🏪 Seller: {seller.business_name}")
                print(f"   City: {seller.business_city or 'Not set'}")
                print(f"   Country: {seller.business_country or 'Not set'}")
                
                # Format location
                location_parts = []
                if seller.business_city:
                    location_parts.append(seller.business_city)
                if seller.business_country and seller.business_country != seller.business_city:
                    location_parts.append(seller.business_country)
                formatted_location = ', '.join(location_parts) if location_parts else 'Location Not Available'
                print(f"   Formatted Location: {formatted_location}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_seller_info()