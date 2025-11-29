#!/usr/bin/env python3
"""
Check seller table structure
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def check_seller_table():
    """Check seller table structure"""
    try:
        from project import create_app, db
        
        app = create_app()
        with app.app_context():
            print("🔍 Checking Seller Table Structure")
            print("=" * 50)
            
            from sqlalchemy import text
            
            # Check table names
            result = db.session.execute(text("SHOW TABLES LIKE '%seller%'"))
            tables = [row[0] for row in result]
            print(f"Seller-related tables: {tables}")
            
            # Check seller table structure
            if 'seller' in tables:
                result = db.session.execute(text("DESCRIBE seller"))
                print(f"\n📋 Seller table columns:")
                for row in result:
                    print(f"   {row[0]} - {row[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_seller_table()