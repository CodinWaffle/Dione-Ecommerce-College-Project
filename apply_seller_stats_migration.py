#!/usr/bin/env python3
"""
Apply seller statistics migration
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def apply_seller_stats_migration():
    """Apply the seller statistics migration"""
    try:
        from project import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        with app.app_context():
            print("🔧 Applying Seller Statistics Migration")
            print("=" * 50)
            
            # Read migration file
            with open('migrations/002_add_seller_statistics_fixed.sql', 'r') as f:
                migration_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                try:
                    if statement:
                        db.session.execute(text(statement))
                        print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    if "Duplicate column name" in str(e) or "already exists" in str(e).lower():
                        print(f"ℹ️ Skipped existing: {statement[:50]}...")
                    else:
                        print(f"⚠️ Warning: {e}")
            
            db.session.commit()
            print("\n✅ Seller statistics migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_seller_stats_migration()