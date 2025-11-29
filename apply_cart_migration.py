#!/usr/bin/env python3
"""
Apply cart system migration
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project'))

def apply_cart_migration():
    """Apply the cart system migration"""
    try:
        from project import create_app, db
        
        app = create_app()
        with app.app_context():
            print("🔧 Applying Cart System Migration")
            print("=" * 50)
            
            # Read migration file
            with open('migrations/003_add_cart_system.sql', 'r') as f:
                migration_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                try:
                    if statement:
                        db.session.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️ Warning: {e}")
                    else:
                        print(f"ℹ️ Skipped existing: {statement[:50]}...")
            
            db.session.commit()
            print("\n✅ Cart system migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_cart_migration()