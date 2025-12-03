import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project import create_app, db
from project.models import User, CartItem
from sqlalchemy import func

app = create_app('development')

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for u in users[:5]:
        print(u.id, u.email)
    cart_counts = db.session.query(CartItem.user_id, func.count()).group_by(CartItem.user_id).all()
    print('Cart counts:', cart_counts)
