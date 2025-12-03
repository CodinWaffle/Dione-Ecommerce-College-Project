import os
import sys
from sqlalchemy import text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app, db

table_name = sys.argv[1] if len(sys.argv) > 1 else 'order_items'

app = create_app('development')

with app.app_context():
    result = db.session.execute(text(f'SHOW CREATE TABLE {table_name}')).fetchone()
    if result:
        print(result[1])
    else:
        print(f'{table_name} table not found')
