#!/usr/bin/env python3
"""
Fix orders table by adding missing columns
"""

from project import create_app, db
import pymysql

def fix_orders_table():
    app = create_app('development')
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Check if shipping_fee column exists
            cursor.execute("SHOW COLUMNS FROM orders LIKE 'shipping_fee'")
            result = cursor.fetchone()
            
            if not result:
                print("Adding shipping_fee column...")
                cursor.execute("ALTER TABLE orders ADD COLUMN shipping_fee DECIMAL(10,2) DEFAULT 0")
                print("✅ shipping_fee column added successfully")
            else:
                print("✅ shipping_fee column already exists")
            
            # Check if tax_amount column exists
            cursor.execute("SHOW COLUMNS FROM orders LIKE 'tax_amount'")
            result = cursor.fetchone()
            
            if not result:
                print("Adding tax_amount column...")
                cursor.execute("ALTER TABLE orders ADD COLUMN tax_amount DECIMAL(10,2) DEFAULT 0")
                print("✅ tax_amount column added successfully")
            else:
                print("✅ tax_amount column already exists")
            
            # Check if discount_amount column exists
            cursor.execute("SHOW COLUMNS FROM orders LIKE 'discount_amount'")
            result = cursor.fetchone()
            
            if not result:
                print("Adding discount_amount column...")
                cursor.execute("ALTER TABLE orders ADD COLUMN discount_amount DECIMAL(10,2) DEFAULT 0")
                print("✅ discount_amount column added successfully")
            else:
                print("✅ discount_amount column already exists")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            connection.rollback()

if __name__ == "__main__":
    fix_orders_table()