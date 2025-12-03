"""Update order_items foreign keys to match current product and seller tables."""
import os
import sys
from sqlalchemy import text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app, db

app = create_app('development')

commands = [
    "ALTER TABLE order_items DROP FOREIGN KEY order_items_ibfk_2",
    "ALTER TABLE order_items DROP FOREIGN KEY order_items_ibfk_4",
    "ALTER TABLE order_items ADD CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES seller_product_management (id) ON DELETE SET NULL",
    "ALTER TABLE order_items ADD CONSTRAINT fk_order_items_seller FOREIGN KEY (seller_id) REFERENCES user (id) ON DELETE SET NULL"
]

with app.app_context():
    for cmd in commands:
        try:
            db.session.execute(text(cmd))
            db.session.commit()
            print(f"Executed: {cmd}")
        except Exception as exc:
            db.session.rollback()
            print(f"Skipping '{cmd}': {exc}")
