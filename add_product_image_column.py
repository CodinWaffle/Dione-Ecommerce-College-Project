from project import create_app, db
from project.models import OrderItem

# Create app context
app = create_app('development')

with app.app_context():
    # Check if product_image column exists
    try:
        # Try to access the column to see if it exists
        result = db.session.execute(db.text("SHOW COLUMNS FROM order_items LIKE 'product_image'"))
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            print("Adding product_image column to order_items table...")
            db.session.execute(db.text("ALTER TABLE order_items ADD COLUMN product_image VARCHAR(500) AFTER product_name"))
            db.session.commit()
            print("✅ Successfully added product_image column!")
        else:
            print("✅ product_image column already exists!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()