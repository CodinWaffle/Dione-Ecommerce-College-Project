import sys
import os
sys.path.insert(0, os.getcwd())

from project import create_app, db
from project.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("All users in database:")
    for user in users:
        print(f"  ID: {user.id}, Username: {user.username}, Role: {user.role}")
    
    sellers = User.query.filter_by(role='seller').all()
    print(f"\nSellers found: {len(sellers)}")