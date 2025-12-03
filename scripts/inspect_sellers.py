import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from project import create_app
from project.models import Seller

app = create_app('development')

with app.app_context():
    sellers = Seller.query.all()
    print(f"Total sellers: {len(sellers)}")
    for s in sellers:
        print(f"Seller record {s.id} -> user_id {s.user_id} business {s.business_name}")
