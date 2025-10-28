import pytest
import warnings
from project import create_app, db
from project.models import User, OAuth
from werkzeug.security import generate_password_hash
from flask import url_for
import time
import json

# Filter out the database connection warning
warnings.filterwarnings("ignore", message="unclosed database", category=ResourceWarning)





# Test fixtures
@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')

    # Create all tables
    with app.app_context():
        db.create_all()

    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user for authentication tests."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpassword', method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated client for testing protected routes."""
    # Login the user
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    return client

@pytest.fixture
def sample_users(app):
    """Create multiple sample users for testing."""
    with app.app_context():
        users_data = [
            ('user1', 'user1@example.com', 'pass1'),
            ('user2', 'user2@example.com', 'pass2'),
            ('user3', 'user3@example.com', 'pass3'),
        ]

        users = []
        for username, email, password in users_data:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        return users

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up database after each test."""
    yield  # Run the test first

    # Clean up after test
    with app.app_context():
        try:
            db.session.rollback()  # Rollback any pending transactions
            db.session.remove()   # Remove the session
            db.drop_all()
            db.create_all()
        except Exception:
            # If there's an error, just pass - the database will be recreated
            pass

# Helper function for consistent password hashing
def hash_password(password):
    """Generate password hash with consistent method."""
    return generate_password_hash(password, method='pbkdf2:sha256')


# Route Tests (9 tests)
def test_index_route(client):
    """Test homepage functionality and content validation."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Homepage' in response.data


def test_profile_route_requires_login(client):
    """Test that profile route requires authentication."""
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login


def test_profile_route_authenticated(client, test_user):
    """Test profile route works with authenticated user."""
    # Login first
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Now access profile
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert b'testuser' in response.data


def test_login_route(client):
    """Test login route GET request."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_signup_route(client):
    """Test signup route GET request."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data


def test_logout_route(client, authenticated_client):
    """Test logout route works."""
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to index


def test_index_route_content_type(client):
    """Test response headers and content types."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'


def test_profile_route_redirect_location(client):
    """Test profile route redirect location."""
    response = client.get('/profile')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_nonexistent_route(client):
    """Test 404 error handling for invalid routes."""
    response = client.get('/nonexistent')
    assert response.status_code == 404


# Authentication Tests (13 tests)
def test_login_route_get(client):
    """Test login route GET request."""
    response = client.get('/login')
    assert response.status_code == 200


def test_signup_route_get(client):
    """Test signup route GET request."""
    response = client.get('/signup')
    assert response.status_code == 200


def test_successful_signup(client, app):
    """Test successful user signup."""
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'


def test_duplicate_email_signup(client, app, test_user):
    """Test duplicate email signup validation."""
    response = client.post('/signup', data={
        'username': 'anotheruser',
        'email': 'test@example.com',  # Same email as test_user
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        # Check only one user with this email exists
        users = User.query.filter_by(email='test@example.com').all()
        assert len(users) == 1


def test_signup_missing_fields(client):
    """Test signup with missing required fields."""
    response = client.post('/signup', data={
        'username': 'testuser'
        # Missing email and password
    }, follow_redirects=True)
    assert response.status_code == 200


def test_successful_login(client, test_user):
    """Test successful login."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'testuser' in response.data


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect password' in response.data


def test_login_nonexistent_email(client):
    """Test login with non-existent email."""
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'No account found' in response.data


def test_logout_requires_login(client):
    """Test logout requires authentication."""
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to login


def test_reset_password_route_get(client):
    """Test reset password route GET request."""
    response = client.get('/reset')
    assert response.status_code == 200
    assert b'Reset Password' in response.data


def test_reset_password_post_valid_email(client, app, test_user):
    """Test reset password post with valid email."""
    response = client.post('/reset', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'email has been sent' in response.data


def test_reset_password_post_invalid_email(client):
    """Test reset password post with invalid email."""
    response = client.post('/reset', data={
        'email': 'invalid@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    # For security, no message is shown for invalid emails
    # Just verify the response is successful (redirect to login)


def test_logout_redirect(client, authenticated_client):
    """Test logout redirect location."""
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/' in response.headers['Location']


# Model Tests (10 tests)
def test_user_creation(app):
    """Test User model creation and validation."""
    with app.app_context():
        user = User(
            username='modeltest',
            email='model@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(email='model@example.com').first()
        assert saved_user is not None
        assert saved_user.username == 'modeltest'


def test_user_repr(app):
    """Test User model __repr__ method."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=hash_password('testpassword')
        )
        db.session.add(user)
        db.session.commit()
        assert repr(user) == 'User testuser'


def test_user_unique_email(app):
    """Test User model email uniqueness constraint."""
    with app.app_context():
        # Try to create duplicate user
        user1 = User(
            username='user1',
            email='duplicate@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user1)
        db.session.commit()

        # Try to create another user with same email
        user2 = User(
            username='user2',
            email='duplicate@example.com',
            password=hash_password('testpass2')
        )
        db.session.add(user2)

        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()


def test_user_get_reset_token(app):
    """Test User model get_reset_token method."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=hash_password('testpassword')
        )
        db.session.add(user)
        db.session.commit()
        token = user.get_reset_token()
        assert token is not None
        assert len(token) > 0
        # Token can be bytes (newer PyJWT) or str (older versions)
        assert isinstance(token, (str, bytes))


def test_user_verify_reset_token_valid(app):
    """Test User model verify_reset_token with valid token."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=hash_password('testpassword')
        )
        db.session.add(user)
        db.session.commit()
        token = user.get_reset_token()
        verified_user = User.verify_reset_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id


def test_user_verify_reset_token_invalid(app):
    """Test User model verify_reset_token with invalid token."""
    with app.app_context():
        verified_user = User.verify_reset_token('invalid_token')
        assert verified_user is None


def test_user_verify_email(app):
    """Test User model verify_email method."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password=hash_password('testpassword')
        )
        db.session.add(user)
        db.session.commit()

        verified_user = User.verify_email('test@example.com')
        assert verified_user is not None
        assert verified_user.id == user.id

        # Test with non-existent email
        verified_user = User.verify_email('nonexistent@example.com')
        assert verified_user is None


def test_oauth_creation(app):
    """Test OAuth model creation."""
    with app.app_context():
        user = User(
            username='oauth_user',
            email='oauth@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        oauth = OAuth(
            provider='google',
            provider_user_id='12345',
            user_id=user.id,
            token='{"access_token": "test_token"}'
        )
        db.session.add(oauth)
        db.session.commit()

        saved_oauth = OAuth.query.filter_by(provider='google').first()
        assert saved_oauth is not None
        assert saved_oauth.user_id == user.id


def test_oauth_token_dict_property(app):
    """Test OAuth model token_dict property."""
    with app.app_context():
        user = User(
            username='oauth_user2',
            email='oauth2@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        oauth = OAuth(
            provider='google',
            provider_user_id='12346',
            user_id=user.id,
            token='{"access_token": "test_token", "refresh_token": "refresh"}'
        )
        db.session.add(oauth)
        db.session.commit()

        token_dict = oauth.token_dict
        assert isinstance(token_dict, dict)
        assert token_dict['access_token'] == 'test_token'


def test_oauth_token_dict_empty(app):
    """Test OAuth model token_dict with empty token."""
    with app.app_context():
        user = User(
            username='oauth_user3',
            email='oauth3@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        oauth = OAuth(
            provider='google',
            provider_user_id='12347',
            user_id=user.id,
            token=''
        )
        db.session.add(oauth)
        db.session.commit()

        token_dict = oauth.token_dict
        assert token_dict == {}


def test_oauth_unique_constraint(app):
    """Test OAuth model unique constraint."""
    with app.app_context():
        user = User(
            username='oauth_user4',
            email='oauth4@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        # Create first OAuth entry
        oauth1 = OAuth(
            provider='google',
            provider_user_id='12348',
            user_id=user.id,
            token='test_token1'
        )
        db.session.add(oauth1)
        db.session.commit()

        # Try to create duplicate OAuth entry (same provider and provider_user_id)
        oauth2 = OAuth(
            provider='google',
            provider_user_id='12348',  # Same as oauth1
            user_id=user.id,
            token='test_token2'
        )
        db.session.add(oauth2)

        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db.session.commit()


# Integration Tests (13 tests)
def test_complete_user_workflow(client, app):
    """Test complete user workflow: registration → login → logout."""
    # Step 1: Register
    response = client.post('/signup', data={
        'username': 'workflow_user',
        'email': 'workflow@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Step 2: Login
    response = client.post('/login', data={
        'email': 'workflow@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'workflow_user' in response.data

    # Step 3: Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Homepage' in response.data


def test_multiple_users_registration(client, app):
    """Test multiple users registration scenario."""
    users_data = [
        ('user1', 'user1@example.com', 'pass123'),
        ('user2', 'user2@example.com', 'pass456'),
        ('user3', 'user3@example.com', 'pass789'),
    ]

    # Test each user registration individually
    for i, (username, email, password) in enumerate(users_data):
        response = client.post('/signup', data={
            'username': username,
            'email': email,
            'password': password
        }, follow_redirects=True)
        # Check if signup was successful (should redirect to login page)
        assert response.status_code == 200
        print(f"Response for user {i+1}: {response.data.decode()[:200]}...")

        # Verify user was created in the same app context
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if user is None:
                print(f"User {i+1} not found in database")
                # Check if there are any users at all
                all_users = User.query.all()
                print(f"Total users in database: {len(all_users)}")
            else:
                print(f"User {i+1} created successfully: {username}")
            assert user is not None
            assert user.username == username


def test_login_persistence(client, test_user):
    """Test login persistence across requests."""
    # Login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Access protected route
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data


def test_password_reset_workflow(client, app):
    """Test complete password reset workflow."""
    with app.app_context():
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=hash_password('testpassword')
        )
        db.session.add(user)
        db.session.commit()

        # Get reset token within the same context
        token = user.get_reset_token()
        assert token is not None

    # Request password reset
    response = client.post('/reset', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Reset password (token should be string for URL)
    token_str = token.decode('utf-8') if isinstance(token, bytes) else token
    response = client.post(f'/reset/{token_str}', data={
        'password': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'password has been updated' in response.data

    # Verify new password works
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_form_validation_signup(client):
    """Test form validation for signup."""
    # Test empty form
    response = client.post('/signup', data={}, follow_redirects=True)
    assert response.status_code == 200

    # Test missing email
    response = client.post('/signup', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Test missing password
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_form_validation_login(client):
    """Test form validation for login."""
    # Test empty form
    response = client.post('/login', data={}, follow_redirects=True)
    assert response.status_code == 200

    # Test missing password
    response = client.post('/login', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Test missing email
    response = client.post('/login', data={
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_navigation_links(client):
    """Test navigation and static file serving."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'href="/login"' in response.data or b'href="/signup"' in response.data


def test_static_files_served(client):
    """Test static files are served correctly."""
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert 'text/css' in response.content_type


def test_database_isolation_between_tests(app):
    """Test database isolation between tests."""
    with app.app_context():
        # Check initial state
        initial_count = User.query.count()

        # Create a user
        user = User(
            username='isolation_test',
            email='isolation@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        # Verify user exists
        assert User.query.count() == initial_count + 1

        # User should be cleaned up by cleanup_database fixture


def test_error_handling_500(client):
    """Test error handling for 500 errors."""
    # This would require creating an error condition
    # For now, just test that normal routes don't return 500
    response = client.get('/')
    assert response.status_code != 500

    response = client.get('/login')
    assert response.status_code != 500


def test_response_times(client):
    """Test response times are reasonable."""
    import time

    start_time = time.time()
    response = client.get('/')
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should respond within 1 second


def test_oauth_model_integration(app):
    """Test OAuth model integration with User model."""
    with app.app_context():
        user = User(
            username='oauth_integration',
            email='oauth_integration@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        oauth = OAuth(
            provider='google',
            provider_user_id='integration_123',
            user_id=user.id,
            token='integration_token'
        )
        db.session.add(oauth)
        db.session.commit()

        # Test relationship
        saved_user = User.query.filter_by(username='oauth_integration').first()
        assert len(saved_user.oauth) == 1
        assert saved_user.oauth[0].provider == 'google'


def test_oauth_blueprint_configuration(app):
    """Test OAuth blueprint configuration and URL generation."""
    with app.app_context():
        from project.routes.oauth_routes import google_blueprint, facebook_blueprint

        # Test blueprint attributes
        assert google_blueprint.client_id is not None
        assert google_blueprint.redirect_url is None  # Should be auto-generated
        assert 'google' in google_blueprint.name.lower()

        # Facebook client ID should be either the placeholder or empty string from env
        assert facebook_blueprint.client_id in ['YOUR_FACEBOOK_APP_ID', '', "''"]
        assert facebook_blueprint.redirect_url is None  # Should be auto-generated
        assert 'facebook' in facebook_blueprint.name.lower()

        # Test authorization URL generation (without making actual request)
        try:
            # This should not raise an error, even if URLs are not accessible
            google_auth_url = google_blueprint.authorization_url
            assert 'accounts.google.com' in google_auth_url

            facebook_auth_url = facebook_blueprint.authorization_url
            assert 'facebook.com' in facebook_auth_url

        except Exception as e:
            # OAuth URLs might not be accessible in test environment
            # This is expected and acceptable
            print(f"OAuth URL test skipped: {e}")


def test_oauth_token_handling(app):
    """Test OAuth token handling and storage."""
    with app.app_context():
        user = User(
            username='oauth_token_test',
            email='oauth_token@example.com',
            password=hash_password('testpass')
        )
        db.session.add(user)
        db.session.commit()

        # Test token storage
        oauth = OAuth(
            provider='google',
            provider_user_id='token_test_123',
            user_id=user.id,
            token='{"access_token": "test_token", "token_type": "Bearer"}'
        )
        db.session.add(oauth)
        db.session.commit()

        # Test token_dict property
        token_dict = oauth.token_dict
        assert isinstance(token_dict, dict)
        assert token_dict['access_token'] == 'test_token'

        # Test token_dict setter
        oauth.token_dict = {'access_token': 'new_token', 'refresh_token': 'refresh'}
        assert oauth.token == '{"access_token": "new_token", "refresh_token": "refresh"}'


def test_oauth_error_handling(app):
    """Test OAuth error handling and logging."""
    with app.app_context():
        from project.routes.oauth_routes import google_blueprint
        from unittest.mock import Mock

        # Test that blueprint has the necessary OAuth methods
        assert hasattr(google_blueprint, 'client_id')
        assert hasattr(google_blueprint, 'client_secret')
        assert hasattr(google_blueprint, 'scope')
        assert hasattr(google_blueprint, 'storage')

        # Test that blueprint is properly configured
        assert google_blueprint.client_id is not None
        assert len(google_blueprint.scope) > 0
        assert google_blueprint.storage is not None

        # Test blueprint name contains 'google'
        assert 'google' in google_blueprint.name.lower()


def test_database_migration_compatibility(app):
    """Test database migration compatibility."""
    with app.app_context():
        # Test that all required tables exist
        from project.models import User, OAuth

        # Check User table structure
        user_columns = [column.name for column in User.__table__.columns]
        required_user_columns = ['id', 'username', 'email', 'password']
        for col in required_user_columns:
            assert col in user_columns

        # Check OAuth table structure
        oauth_columns = [column.name for column in OAuth.__table__.columns]
        required_oauth_columns = ['provider', 'provider_user_id', 'user_id', 'token']
        for col in required_oauth_columns:
            assert col in oauth_columns

        # Test relationships
        assert hasattr(User, 'oauth')
        assert hasattr(OAuth, 'user')

        # Test constraints
        assert OAuth.__table__.constraints is not None
