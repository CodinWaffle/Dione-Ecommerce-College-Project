#!/usr/bin/env python3
"""
Update seller locations with realistic Philippine locations
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def update_seller_locations():
    """Update seller locations with realistic data"""
    try:
        from project import create_app, db
        from project.models import Seller
        
        app = create_app()
        with app.app_context():
            print("🔧 Updating Seller Locations")
            print("=" * 40)
            
            # Realistic Philippine locations
            locations = [
                {'city': 'Quezon City', 'province': 'Metro Manila'},
                {'city': 'Manila', 'province': 'Metro Manila'},
                {'city': 'Cebu City', 'province': 'Cebu'},
                {'city': 'Davao City', 'province': 'Davao del Sur'},
                {'city': 'Makati', 'province': 'Metro Manila'},
                {'city': 'Taguig', 'province': 'Metro Manila'},
            ]
            
            sellers = Seller.query.all()
            updated_count = 0
            
            for i, seller in enumerate(sellers):
                if i < len(locations):
                    location = locations[i]
                    seller.business_city = location['city']
                    seller.business_country = location['province']
                    updated_count += 1
                    print(f"✅ Updated {seller.business_name}: {location['city']}, {location['province']}")
            
            db.session.commit()
            print(f"\n🎉 Updated {updated_count} seller locations")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    update_seller_locations()