from project import create_app
from project.models import User
from project.routes.main_routes import place_order
from flask_login import login_user

sample_payload = {
    "email": "tester@example.com",
    "firstName": "Test",
    "lastName": "User",
    "address": "123 Test St",
    "apartment": "Unit 5",
    "city": "Test City",
    "state": "Metro",
    "zipCode": "1000",
    "phone": "09123456789",
    "country": "Philippines",
    "region": "NCR",
    "barangay": "Barangay 1",
    "paymentMethod": "cod"
}

app = create_app('development')

with app.app_context():
    user = User.query.get(3)
    assert user, "User with id=3 not found"
    with app.test_request_context('/place-order', method='POST', json=sample_payload):
        login_user(user)
        response = place_order()
        print(response)
