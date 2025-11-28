#!/usr/bin/env python3
"""
Approve pending seller requests
"""

from project import create_app, db
from project.models import User, Seller

def approve_pending_sellers():
    """Approve all pending seller requests"""
    
    app = create_app('development')
    
    with app.app_context():
        print("=== Approving Pending Seller Requests ===")
        
        # Find pending sellers
        pending_sellers = User.query.filter(
            User.role_requested == 'seller',
            User.is_approved == False
        ).all()
        
        if not pending_sellers:
            print("✅ No pending seller requests to approve")
            return
        
        print(f"📋 Found {len(pending_sellers)} pending seller request(s)")
        
        for user in pending_sellers:
            print(f"\nApproving seller: {user.email}")
            
            # Update user role and approval status
            user.role = 'seller'  # Change from buyer to seller
            user.is_approved = True
            user.role_requested = None  # Clear the request
            
            try:
                db.session.commit()
                print(f"✅ Successfully approved {user.email} as seller")
                
                # Check if seller profile exists
                seller_profile = Seller.query.filter_by(user_id=user.id).first()
                if seller_profile:
                    print(f"   Business: {seller_profile.business_name}")
                    print(f"   Type: {seller_profile.business_type}")
                    print(f"   City: {seller_profile.business_city}")
                else:
                    print("   ⚠️  No seller profile found")
                    
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error approving {user.email}: {e}")
        
        print(f"\n=== Approval Complete ===")
        
        # Show updated status
        approved_sellers = User.query.filter(User.role == 'seller').all()
        print(f"✅ Total approved sellers: {len(approved_sellers)}")
        
        for seller in approved_sellers:
            print(f"   - {seller.email} (approved)")

if __name__ == "__main__":
    approve_pending_sellers()