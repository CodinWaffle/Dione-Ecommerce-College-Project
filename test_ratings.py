#!/usr/bin/env python3
"""
Test the star rating display functionality
"""
from project import create_app, db
from project.models import SellerProduct
import requests

def test_rating_display():
    """Test that ratings are displayed correctly on product pages"""
    try:
        print("🌟 Testing product rating display functionality...")
        
        # Test product page with ratings
        response = requests.get('http://localhost:5000/product/1', timeout=10)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for rating-related content
            if 'star' in content and 'rating' in content:
                print("✅ Star rating elements found in product page")
            else:
                print("❌ Star rating elements not found")
                
            # Check for FontAwesome stars
            if 'fas fa-star' in content or 'far fa-star' in content:
                print("✅ FontAwesome star icons found")
            else:
                print("❌ FontAwesome star icons not found")
                
            # Check for review count
            if 'review' in content:
                print("✅ Review count display found")
            else:
                print("❌ Review count display not found")
                
            print(f"📄 Product page loaded successfully (status: {response.status_code})")
            
        else:
            print(f"❌ Failed to load product page (status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error testing rating display: {e}")

def check_backend_rating_calculation():
    """Test the backend rating calculation"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Get a sample product
            product = SellerProduct.query.first()
            if product:
                print(f"📦 Testing with product: {product.name} (ID: {product.id})")
                
                # Test the rating calculation logic
                from project.models import ProductReview
                from sqlalchemy import func
                
                rating_data = db.session.query(
                    func.avg(ProductReview.rating).label('avg_rating'),
                    func.count(ProductReview.id).label('count')
                ).filter_by(product_id=product.id).first()
                
                if rating_data and rating_data.avg_rating:
                    print(f"✅ Real ratings found - Avg: {rating_data.avg_rating}, Count: {rating_data.count}")
                else:
                    print("ℹ️  No real ratings found, will use fallback data")
                    
            else:
                print("❌ No products found in database")
                
        except Exception as e:
            print(f"❌ Backend test error: {e}")

if __name__ == '__main__':
    print("🧪 Testing Product Rating Display...\n")
    
    # Test backend calculation
    check_backend_rating_calculation()
    print()
    
    # Test frontend display
    test_rating_display()
    
    print("\n✨ Rating display testing completed!")
    print("\n🎯 To manually test:")
    print("1. Open http://localhost:5000 in browser")
    print("2. Click on any product")
    print("3. Look for star ratings next to the 'sold' count")
    print("4. Verify stars and review count are displayed")