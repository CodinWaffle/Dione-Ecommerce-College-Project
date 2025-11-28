import itertools
import io
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from project import create_app, db
from project.models import (
    Category,
    OAuth,
    Order,
    OrderTrackingEvent,
    Product,
    Review,
    SiteSetting,
    StoreProfile,
    User,
)
from project.utils.validators import Validators


pytestmark = [
    pytest.mark.filterwarnings("ignore::ResourceWarning"),
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]

DEFAULT_PASSWORD = "Passw0rd!"
ADMIN_PASSWORD = "AdminPass!23"

EMAIL_CASES: Iterable[Tuple[str, bool]] = [
    ("user@example.com", True),
    ("first.last@example.co", True),
    ("user+tag@sub.domain.org", True),
    ("simple@example.io", True),
    ("UPPER@EXAMPLE.COM", True),
    ("missingatsign", False),
    ("missingdomain@", False),
    ("@missinglocal.com", False),
    ("name@domain", False),
    ("", False),
    ("name@domain.c", False),
    ("name@domain,com", False),
    ("dash-domain@exa-mple.com", True),
    ("numbers123@domain123.com", True),
    ("under_score@domain.com", True),
    ("valid.mailbox@sample.org", True),
]

PASSWORD_CASES: Iterable[Tuple[str, bool]] = [
    ("secret1", True),
    ("123456", True),
    ("pass", False),
    ("", False),
    ("abcde", False),
    ("complexPASS123", True),
    ("sixsix", True),
    ("twelve_chars", True),
    ("tiny", False),
    ("plentyoflengthhere", True),
]

USERNAME_CASES: Iterable[Tuple[str, bool]] = [
    ("ab", False),
    ("abc", True),
    ("user_name", True),
    ("user-name", True),
    ("user name", False),
    ("", False),
    ("lo" * 30, False),
    ("validuser123", True),
    ("CAPSLOCK", True),
    ("with.dots", False),
    ("hyphenated-user", True),
    ("__underscore__", True),
]

ROLE_CASES: Iterable[Tuple[str, bool]] = [
    ("buyer", True),
    ("seller", True),
    ("rider", True),
    ("Seller", True),
    ("admin", False),
    ("", False),
]

LOGIN_FORM_CASES: Iterable[Tuple[str, str, bool]] = [
    ("login@example.com", DEFAULT_PASSWORD, True),
    ("", DEFAULT_PASSWORD, False),
    ("invalid-email", DEFAULT_PASSWORD, False),
    ("login@example.com", "", False),
    ("login_at_example.com", "secret", False),
    ("missing@example.com", DEFAULT_PASSWORD, True),
    ("user@example.com", "short", True),
    ("bad@", "bad", False),
]

SIGNUP_FORM_CASES: Iterable[Tuple[str, str, str, bool]] = [
    ("abc", "signup@example.com", DEFAULT_PASSWORD, True),
    ("", "signup@example.com", DEFAULT_PASSWORD, False),
    ("ab", "signup@example.com", DEFAULT_PASSWORD, False),
    ("username", "invalid-email", DEFAULT_PASSWORD, False),
    ("username", "signup@example.com", "123", False),
    ("valid-user", "valid@example.com", "longpassword", True),
    ("another", "", DEFAULT_PASSWORD, False),
    ("third", "third@example.co", DEFAULT_PASSWORD, True),
]


def _hash(password: str) -> str:
    """Return a pbkdf2 hash for deterministic password creation."""
    if not password:
        password = DEFAULT_PASSWORD
    if password.startswith("pbkdf2:"):
        return password
    return generate_password_hash(password, method="pbkdf2:sha256")


def _cleanup_product_uploads(app, product: Product):
    upload_root = Path(app.config["UPLOAD_FOLDER"])
    for image in product.images:
        file_path = upload_root / Path(image.path).name
        if file_path.exists():
            try:
                file_path.unlink()
            except PermissionError:
                pass


def login(client, email: str, password: str):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


@pytest.fixture()
def app():
    test_app = create_app("testing")
    test_app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False
    with test_app.app_context():
        db.create_all()
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()
        # Close all database connections to prevent ResourceWarnings
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_factory(app):
    counter = itertools.count(1)

    def _create_user(**overrides):
        idx = next(counter)
        data: Dict = {
            "username": f"user{idx}",
            "email": f"user{idx}@example.com",
            "password": DEFAULT_PASSWORD,
            "role": "buyer",
            "role_requested": None,
            "is_approved": True,
            "is_suspended": False,
        }
        data.update(overrides)
        password = _hash(data.pop("password"))
        with app.app_context():
            user = User(password=password, **data)
            db.session.add(user)
            db.session.commit()
            # Load all attributes to prevent DetachedInstanceError
            _ = user.id
            _ = user.email
            _ = user.username
            _ = user.role
            _ = user.role_requested
            _ = user.is_approved
            _ = user.is_suspended
            # Expunge to properly detach from session
            db.session.expunge(user)
            return user

    return _create_user


@pytest.fixture()
def admin_credentials():
    return {"email": "admin@example.com", "password": ADMIN_PASSWORD}


@pytest.fixture()
def admin_user(user_factory, admin_credentials):
    return user_factory(
        username="admin",
        email=admin_credentials["email"],
        password=admin_credentials["password"],
        role="admin",
    )


@pytest.fixture()
def admin_client(client, admin_credentials, admin_user):
    response = client.post("/admin/login", data=admin_credentials, follow_redirects=True)
    assert response.status_code == 200
    return client


@pytest.fixture()
def authenticated_client(client, user_factory):
    user = user_factory()
    response = login(client, user.email, DEFAULT_PASSWORD)
    assert response.status_code == 200
    return client


@pytest.mark.parametrize(
    "path,status_code",
    [
        ("/", 200),
        ("/shop/", 200),
        ("/login", 200),
        ("/signup", 200),
        ("/reset", 200),
        ("/reset/test-token", 200),
        ("/health", 200),
        ("/test-db", 200),
        ("/admin/login", 200),
        ("/oauth-debug", 200),
        ("/static/css/style.css", 200),
        ("/static/css/admin.css", 200),
        ("/logout", 302),
    ],
)
def test_public_routes_render(client, path, status_code):
    response = client.get(path)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "path,redirect_fragment",
    [
        ("/profile", "/login"),
        ("/seller/dashboard", "/login"),
        ("/seller/products", "/login"),
        ("/rider/dashboard", "/login"),
        ("/rider/deliveries", "/login"),
        ("/pending", "/login"),
        ("/shop/cart", "/login"),
        ("/admin/overview", "/admin/login"),
        ("/admin/users", "/admin/login"),
        ("/admin/pending", "/admin/login"),
        ("/admin/settings", "/admin/login"),
    ],
)
def test_protected_routes_require_login(client, path, redirect_fragment):
    response = client.get(path)
    assert response.status_code == 302
    assert redirect_fragment in response.headers["Location"]


def test_signup_creates_user(client, app):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
    }
    response = client.post("/signup", data=payload, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        saved = User.query.filter_by(email=payload["email"]).first()
        assert saved is not None
        assert saved.username == payload["username"]


def test_signup_prevents_duplicate_emails(client, app, user_factory):
    user = user_factory(email="dup@example.com")
    payload = {
        "username": "dup",
        "email": user.email,
        "password": DEFAULT_PASSWORD,
    }
    response = client.post("/signup", data=payload, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email=user.email).count() == 1


@pytest.mark.parametrize(
    "form_data",
    [
        {"username": "", "email": "bad@example.com", "password": DEFAULT_PASSWORD},
        {"username": "ab", "email": "bad@example.com", "password": DEFAULT_PASSWORD},
        {"username": "valid", "email": "invalid", "password": DEFAULT_PASSWORD},
        {"username": "valid", "email": "valid@example.com", "password": "123"},
        {"username": "valid", "email": "", "password": DEFAULT_PASSWORD},
    ],
)
def test_signup_validation_errors(client, app, form_data):
    response = client.post("/signup", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign Up" in response.data
    with app.app_context():
        assert User.query.count() == 0


def test_successful_login_redirects_to_home(client, user_factory):
    user = user_factory(email="login@example.com")
    response = login(client, user.email, DEFAULT_PASSWORD)
    assert response.status_code == 200
    assert b"Homepage" in response.data


@pytest.mark.parametrize(
    "form_data,expected_fragment",
    [
        ({"email": "", "password": DEFAULT_PASSWORD}, b"Email is required"),
        ({"email": "invalid-email", "password": DEFAULT_PASSWORD}, b"Invalid email format"),
        ({"email": "user@example.com", "password": ""}, b"Password is required"),
        ({"email": "user@example.com", "password": "wrong"}, b"Incorrect password"),
        ({"email": "missing@example.com", "password": DEFAULT_PASSWORD}, b"No account found"),
    ],
)
def test_login_invalid_inputs(client, user_factory, form_data, expected_fragment):
    user_factory(email="user@example.com")
    response = client.post("/login", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert expected_fragment in response.data


def test_logout_requires_login(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_flow(authenticated_client):
    response = authenticated_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Homepage" in response.data


def test_password_reset_flow(client, app, user_factory):
    user = user_factory(email="reset@example.com")
    response = client.post("/reset", data={"email": user.email}, follow_redirects=True)
    assert b"email has been sent" in response.data
    with app.app_context():
        token = user.get_reset_token()
    token_str = token.decode("utf-8") if isinstance(token, bytes) else token
    response = client.post(
        f"/reset/{token_str}",
        data={"password": "NewPass123", "confirm_password": "NewPass123"},
        follow_redirects=True,
    )
    assert b"password has been updated" in response.data
    response = client.post(
        "/login",
        data={"email": user.email, "password": "NewPass123"},
        follow_redirects=True,
    )
    assert b"Homepage" in response.data


def test_profile_displays_username(client, user_factory):
    user = user_factory(username="visible", email="visible@example.com")
    login(client, user.email, DEFAULT_PASSWORD)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"visible" in response.data


def test_pending_user_redirects_to_pending_page(client, user_factory):
    user = user_factory(
        email="pending@example.com",
        role="buyer",
        role_requested="seller",
        is_approved=False,
    )
    login(client, user.email, DEFAULT_PASSWORD)
    response = client.get("/")
    assert response.status_code == 302
    assert "/pending" in response.headers["Location"]
    response = client.get("/pending")
    assert b"Approval Pending" in response.data


def test_non_pending_user_skip_pending_page(client, user_factory):
    user = user_factory(email="buyer@example.com", role="buyer")
    login(client, user.email, DEFAULT_PASSWORD)
    response = client.get("/pending")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_seller_dashboard_access_control(client, user_factory):
    buyer = user_factory(email="buyer@example.com", role="buyer")
    login(client, buyer.email, DEFAULT_PASSWORD)
    response = client.get("/seller/dashboard", follow_redirects=True)
    assert b"Welcome" in response.data


def test_seller_dashboard_allowed_for_seller(client, user_factory):
    seller = user_factory(email="seller@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    response = client.get("/seller/dashboard")
    assert response.status_code == 200
    assert b"Seller Dashboard" in response.data


def test_seller_can_create_product_with_images(client, app, user_factory):
    seller = user_factory(email="maker@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    data = {
        "name": "Camera",
        "price": "199.99",
        "stock": "10",
        "description": "Mirrorless camera",
        "new_category": "Electronics",
        "is_featured": "on",
        "images": [
            (io.BytesIO(b"img-one"), "camera1.jpg"),
            (io.BytesIO(b"img-two"), "camera2.jpg"),
        ],
    }
    response = client.post(
        "/seller/products/new",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Product created successfully" in response.data
    with app.app_context():
        product = Product.query.filter_by(name="Camera").first()
        assert product is not None
        assert product.category is not None
        assert product.category.name == "Electronics"
        assert product.is_featured is True
        assert len(product.images) == 2
        _cleanup_product_uploads(app, product)


def test_product_image_limit_enforced(client, user_factory):
    seller = user_factory(email="limit@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    data = {
        "name": "Bulk Upload",
        "price": "50",
        "stock": "5",
        "description": "Too many images",
        "images": [(io.BytesIO(b"data"), f"img{i}.jpg") for i in range(6)],
    }
    response = client.post(
        "/seller/products/new",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"only store up to 5 images" in response.data


def test_manual_order_creation_updates_inventory(client, app, user_factory):
    seller = user_factory(email="orders@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    with app.app_context():
        product = Product(
            seller_id=seller.id,
            name="Widget",
            price=Decimal("100.00"),
            stock=5,
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    response = client.post(
        "/seller/orders",
        data={"product_id": product_id, "quantity": 2},
        follow_redirects=True,
    )
    assert b"Manual order recorded" in response.data
    with app.app_context():
        refreshed = db.session.get(Product, product_id)
        assert refreshed.stock == 3
        order = Order.query.filter_by(seller_id=seller.id).one()
        assert float(order.total_amount) == pytest.approx(200.0, rel=1e-3)


def test_seller_can_update_order_status(client, app, user_factory):
    seller = user_factory(email="status@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    with app.app_context():
        order = Order(seller_id=seller.id, status="pending", total_amount=100)
        db.session.add(order)
        db.session.commit()
        order_id = order.id
    response = client.post(
        f"/seller/orders/{order_id}/status",
        data={"status": "completed"},
        follow_redirects=True,
    )
    assert b"Order status updated" in response.data
    with app.app_context():
        refreshed = db.session.get(Order, order_id)
        assert refreshed.status == "completed"


def test_store_profile_auto_created_on_dashboard(client, app, user_factory):
    seller = user_factory(email="autostore@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    client.get("/seller/dashboard")
    with app.app_context():
        store = StoreProfile.query.filter_by(seller_id=seller.id).first()
        assert store is not None
        assert store.slug


def test_store_profile_update(client, app, user_factory):
    seller = user_factory(email="storeupdate@example.com", role="seller", is_approved=True)
    login(client, seller.email, DEFAULT_PASSWORD)
    payload = {
        "name": "Updated Store",
        "slug": "updated-store",
        "tagline": "Tagline",
        "contact_email": "store@example.com",
    }
    response = client.post("/seller/store/profile", data=payload, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        store = StoreProfile.query.filter_by(seller_id=seller.id).first()
        assert store.name == "Updated Store"
        assert store.contact_email == "store@example.com"


def test_rider_dashboard_allowed_for_rider(client, user_factory):
    rider = user_factory(email="rider@example.com", role="rider", is_approved=True)
    login(client, rider.email, DEFAULT_PASSWORD)
    response = client.get("/rider/dashboard")
    assert response.status_code == 200
    assert b"Rider Dashboard" in response.data


def test_rider_dashboard_rejects_buyers(client, user_factory):
    buyer = user_factory(email="buyer2@example.com", role="buyer")
    login(client, buyer.email, DEFAULT_PASSWORD)
    response = client.get("/rider/dashboard", follow_redirects=True)
    assert b"Welcome" in response.data


def test_health_endpoint_reports_user_count(client, user_factory, app):
    user_factory()
    user_factory()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["users"] == 2


def test_test_db_endpoint_reports_success(client, user_factory):
    user_factory()
    response = client.get("/test-db")
    assert response.status_code == 200
    data = response.get_json()
    assert data["database_status"] == "connected"
    assert "user_count" in data


def test_oauth_token_storage(app, user_factory):
    user = user_factory()
    with app.app_context():
        oauth = OAuth(
            provider="google",
            provider_user_id="test123",
            user_id=user.id,
            token='{"access_token": "abc"}',
        )
        db.session.add(oauth)
        db.session.commit()
        loaded = OAuth.query.filter_by(provider="google").first()
        assert loaded.token_dict["access_token"] == "abc"
        loaded.token_dict = {"access_token": "xyz"}
        db.session.commit()
        assert loaded.token_dict["access_token"] == "xyz"


def test_user_repr(app):
    with app.app_context():
        user = User(
            username="repruser",
            email="repr@example.com",
            password=_hash(DEFAULT_PASSWORD),
        )
        db.session.add(user)
        db.session.commit()
        assert repr(user) == "User repruser"


def test_user_unique_email_constraint(app):
    with app.app_context():
        user = User(
            username="unique",
            email="unique@example.com",
            password=_hash(DEFAULT_PASSWORD),
        )
        db.session.add(user)
        db.session.commit()
        dup = User(
            username="duplicate",
            email="unique@example.com",
            password=_hash(DEFAULT_PASSWORD),
        )
        db.session.add(dup)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_user_verify_reset_token_invalid(app):
    with app.app_context():
        assert User.verify_reset_token("badtoken") is None


def test_user_verify_email(app, user_factory):
    existing = user_factory(email="findme@example.com")
    with app.app_context():
        found = User.verify_email(existing.email)
        assert found.id == existing.id
        assert User.verify_email("missing@example.com") is None


def test_site_setting_repr(app):
    with app.app_context():
        setting = SiteSetting(key="support_email", value="help@example.com")
        db.session.add(setting)
        db.session.commit()
        assert "support_email" in repr(setting)


def test_admin_login_requires_admin_role(client, user_factory):
    user_factory(email="notadmin@example.com", role="buyer")
    response = client.post(
        "/admin/login",
        data={"email": "notadmin@example.com", "password": DEFAULT_PASSWORD},
        follow_redirects=True,
    )
    assert b"Invalid admin credentials" in response.data


def test_admin_overview_requires_admin_role(client, user_factory):
    user = user_factory(email="buyer@example.com", role="buyer")
    login(client, user.email, DEFAULT_PASSWORD)
    response = client.get("/admin/overview")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_admin_login_logout_flow(client, admin_credentials, admin_user):
    response = client.post("/admin/login", data=admin_credentials, follow_redirects=True)
    assert b"Dashboard" in response.data
    response = client.get("/admin/logout", follow_redirects=True)
    assert b"Logged out successfully" in response.data


@pytest.mark.parametrize(
    "endpoint",
    ["/admin/overview", "/admin/pending", "/admin/users", "/admin/settings", "/admin/profile", "/admin/monitoring", "/admin/content"],
)
def test_admin_pages_render(admin_client, endpoint):
    response = admin_client.get(endpoint)
    assert response.status_code == 200


def test_admin_pending_lists_requests(admin_client, user_factory):
    pending_user = user_factory(
        username="pendinguser",
        role="buyer",
        role_requested="seller",
        is_approved=False,
    )
    response = admin_client.get("/admin/pending")
    assert response.status_code == 200
    assert pending_user.username.encode() in response.data


def test_admin_users_lists_roles(admin_client, user_factory):
    user_factory(username="buyer", role="buyer")
    user_factory(username="seller", role="seller")
    user_factory(username="rider", role="rider")
    response = admin_client.get("/admin/users")
    assert b"buyer" in response.data
    assert b"seller" in response.data
    assert b"rider" in response.data


def test_admin_can_approve_request(admin_client, app, user_factory):
    pending_user = user_factory(
        username="promote",
        role="buyer",
        role_requested="seller",
        is_approved=False,
    )
    response = admin_client.post(
        f"/admin/approve-request/{pending_user.id}", follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        refreshed = db.session.get(User, pending_user.id)
        assert refreshed.role == "seller"
        assert refreshed.role_requested is None
        assert refreshed.is_approved is True


def test_admin_can_reject_request(admin_client, app, user_factory):
    pending_user = user_factory(
        username="reject",
        role="buyer",
        role_requested="rider",
        is_approved=False,
    )
    response = admin_client.post(
        f"/admin/reject-request/{pending_user.id}", follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        refreshed = db.session.get(User, pending_user.id)
        assert refreshed.role == "buyer"
        assert refreshed.role_requested is None
        assert refreshed.is_approved is False


def test_admin_suspend_reactivate_and_delete_user(admin_client, app, user_factory):
    target = user_factory(username="target", email="target@example.com")
    response = admin_client.post(f"/admin/users/{target.id}/suspend", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = db.session.get(User, target.id)
        assert user.is_suspended is True
    response = admin_client.post(
        f"/admin/users/{target.id}/reactivate", follow_redirects=True
    )
    with app.app_context():
        user = db.session.get(User, target.id)
        assert user.is_suspended is False
    response = admin_client.post(f"/admin/users/{target.id}/delete", follow_redirects=True)
    with app.app_context():
        assert db.session.get(User, target.id) is None


def test_admin_cannot_suspend_self(admin_client, app, admin_user):
    response = admin_client.post(f"/admin/users/{admin_user.id}/suspend", follow_redirects=True)
    assert b"cannot suspend your own admin account" in response.data
    with app.app_context():
        user = db.session.get(User, admin_user.id)
        assert user.is_suspended is False


def test_admin_settings_bootstrap_and_update(admin_client, app):
    response = admin_client.get("/admin/settings")
    assert response.status_code == 200
    with app.app_context():
        keys = {setting.key for setting in SiteSetting.query.all()}
        assert {"support_email", "support_phone", "auto_approve_sellers"}.issubset(keys)
    form_data = {
        "support_email": "support@example.com",
        "support_phone": "+63 900 111 2222",
        "auto_approve_sellers": "on",
        "maintenance_mode": "on",
    }
    response = admin_client.post("/admin/settings", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        setting = SiteSetting.query.filter_by(key="support_email").first()
        assert setting.value == "support@example.com"


def test_admin_dashboard_counts_include_pending(admin_client, user_factory):
    user_factory(role="buyer")
    user_factory(role="seller")
    user_factory(role="rider")
    user_factory(role="buyer", role_requested="seller", is_approved=False)
    response = admin_client.get("/admin/overview")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_oauth_blueprints_registered(app):
    assert "google" in app.blueprints
    assert "facebook" not in app.blueprints


def test_shop_search_filters_products(client, app, user_factory):
    seller = user_factory(email="catalogseller@example.com", role="seller", is_approved=True)
    with app.app_context():
        category = Category(name="Gadgets", slug="gadgets")
        db.session.add(category)
        db.session.commit()
        product = Product(
            seller_id=seller.id,
            name="Camera Pro",
            description="Mirrorless camera",
            price=Decimal("500.00"),
            category_id=category.id,
            stock=10,
            is_featured=True,
        )
        db.session.add(product)
        db.session.commit()
        category_id = category.id
    response = client.get(f"/shop/?q=Camera&category={category_id}&featured=1&stock=in")
    assert response.status_code == 200
    assert b"Camera Pro" in response.data


def test_cart_checkout_creates_orders_and_tracking(client, app, user_factory):
    seller = user_factory(email="sellercart@example.com", role="seller", is_approved=True)
    buyer = user_factory(email="buyercart@example.com", role="buyer")
    with app.app_context():
        product = Product(
            seller_id=seller.id,
            name="Sneakers",
            description="Running shoes",
            price=Decimal("120.00"),
            stock=5,
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    login(client, buyer.email, DEFAULT_PASSWORD)
    client.post("/shop/cart/items", data={"product_id": product_id, "quantity": 2}, follow_redirects=True)
    response = client.post("/shop/cart/checkout", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        orders = Order.query.filter_by(buyer_id=buyer.id).all()
        assert len(orders) == 1
        assert orders[0].items[0].quantity == 2
        assert OrderTrackingEvent.query.filter_by(order_id=orders[0].id).count() == 1


def test_review_creation_and_seller_response(client, app, user_factory):
    seller = user_factory(email="sellerreviews@example.com", role="seller", is_approved=True)
    buyer = user_factory(email="buyerreviews@example.com", role="buyer")
    with app.app_context():
        product = Product(
            seller_id=seller.id,
            name="Backpack",
            description="Travel backpack",
            price=Decimal("80.00"),
            stock=15,
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    login(client, buyer.email, DEFAULT_PASSWORD)
    client.post(
        f"/shop/product/{product_id}/reviews",
        data={"rating": "5", "title": "Great", "body": "Loved it"},
        follow_redirects=True,
    )
    client.get("/logout")
    login(client, seller.email, DEFAULT_PASSWORD)
    with app.app_context():
        review = Review.query.filter_by(product_id=product_id).first()
        assert review is not None
        review_id = review.id
    client.post(
        f"/seller/store/reviews/{review_id}/respond",
        data={"message": "Thank you!"},
        follow_redirects=True,
    )
    with app.app_context():
        refreshed = db.session.get(Review, review_id)
        assert refreshed.response is not None
        assert refreshed.response.message == "Thank you!"


def test_navigation_links_present(client):
    response = client.get("/")
    assert b'href="/login"' in response.data
    assert b'href="/signup"' in response.data
    assert b'href="/shop/' in response.data


def test_static_assets_served(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.content_type


def test_reset_route_handles_invalid_email(client):
    response = client.post("/reset", data={"email": "missing@example.com"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"email has been sent" in response.data


def test_reset_token_requires_matching_password(client, app, user_factory):
    user = user_factory(email="token@example.com")
    with app.app_context():
        token = user.get_reset_token()
    token_str = token.decode("utf-8") if isinstance(token, bytes) else token
    response = client.post(
        f"/reset/{token_str}",
        data={"password": "onepass", "confirm_password": "different"},
        follow_redirects=True,
    )
    assert b"Passwords do not match" in response.data


def test_database_schema_contains_expected_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert "user" in tables
        assert "oauth" in tables
        assert "site_setting" in tables
        assert "product" in tables
        assert "category" in tables
        assert "product_image" in tables
        assert "inventory_transaction" in tables
        assert "order" in tables
        assert "order_item" in tables
        assert "store_profile" in tables
        assert "product_variant" in tables
        assert "cart" in tables
        assert "cart_item" in tables
        assert "review" in tables
        assert "review_media" in tables
        assert "review_response" in tables
        assert "order_tracking_event" in tables


def test_site_setting_persistence(app):
    with app.app_context():
        setting = SiteSetting(key="maintenance_mode", value="false")
        db.session.add(setting)
        db.session.commit()
        setting.value = "true"
        db.session.commit()
        refreshed = SiteSetting.query.filter_by(key="maintenance_mode").first()
        assert refreshed.value == "true"


@pytest.mark.parametrize("email,expected", EMAIL_CASES)
def test_validate_email_cases(email, expected):
    is_valid, _ = Validators.validate_email(email)
    assert is_valid is expected


@pytest.mark.parametrize("password,expected", PASSWORD_CASES)
def test_validate_password_cases(password, expected):
    is_valid, _ = Validators.validate_password(password)
    assert is_valid is expected


@pytest.mark.parametrize("username,expected", USERNAME_CASES)
def test_validate_username_cases(username, expected):
    is_valid, _ = Validators.validate_username(username)
    assert is_valid is expected


@pytest.mark.parametrize("role,expected", ROLE_CASES)
def test_validate_role_cases(role, expected):
    is_valid, _ = Validators.validate_role(role)
    assert is_valid is expected


@pytest.mark.parametrize("email,password,expected", LOGIN_FORM_CASES)
def test_login_form_validation(email, password, expected):
    is_valid, errors = Validators.validate_login_form(email, password)
    assert is_valid is expected
    if expected:
        assert errors == []
    else:
        assert len(errors) >= 1


@pytest.mark.parametrize("username,email,password,expected", SIGNUP_FORM_CASES)
def test_signup_form_validation(username, email, password, expected):
    is_valid, errors = Validators.validate_signup_form(username, email, password)
    assert is_valid is expected
    if expected:
        assert errors == []
    else:
        assert len(errors) >= 1
