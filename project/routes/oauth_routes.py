"""
OAuth routes for social login (Google, Facebook)
"""
import json
from flask import redirect, url_for, flash, request, Blueprint
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from project import db
from project.models import User, OAuth
from project.config import config
from project.services.oauth_service import OAuthService

# Get current configuration
current_config = config['default']

# OAuth Blueprints with proper configuration
google_blueprint = make_google_blueprint(
    client_id=current_config.GOOGLE_CLIENT_ID,
    client_secret=current_config.GOOGLE_CLIENT_SECRET,
    # Use None here to let Flask-Dance generate the redirect URI automatically
    # This avoids hardcoded URL mismatches
    redirect_url=None,
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    storage=SQLAlchemyStorage(OAuth, db.session),
    # Note: Flask-Dance will use default OAuth URLs for Google
)

facebook_blueprint = make_facebook_blueprint(
    client_id=current_config.FACEBOOK_CLIENT_ID,
    client_secret=current_config.FACEBOOK_CLIENT_SECRET,
    # Use None to let Flask-Dance generate the redirect URI automatically
    redirect_url=None,
    scope=["email"],
    storage=SQLAlchemyStorage(OAuth, db.session)
)

# OAuth blueprints configured successfully

# Create a blueprint for debug routes
debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/oauth-debug')
def oauth_debug():
    """Debug route to show OAuth configuration"""
    # Generate the actual authorization URLs to see what Flask-Dance is using
    try:
        google_auth_url = google_blueprint.authorization_url
    except Exception as e:
        google_auth_url = f"Error generating URL: {e}"

    try:
        facebook_auth_url = facebook_blueprint.authorization_url
    except Exception as e:
        facebook_auth_url = f"Error generating URL: {e}"

    debug_info = f"""
    Google OAuth Configuration:
    - Client ID: {google_blueprint.client_id[:20]}...
    - Configured Redirect URL: {google_blueprint.redirect_url}
    - Authorization URL: {google_blueprint.authorization_url}
    - Token URL: {google_blueprint.token_url}
    - Generated Auth URL: {google_auth_url}

    Facebook OAuth Configuration:
    - Client ID: {facebook_blueprint.client_id}
    - Configured Redirect URL: {facebook_blueprint.redirect_url}
    - Authorization URL: {facebook_blueprint.authorization_url}
    - Token URL: {facebook_blueprint.token_url}
    - Generated Auth URL: {facebook_auth_url}

    Current Request:
    - URL: {request.url}
    - Base URL: {request.base_url}
    - URL Root: {request.url_root}
    - Host: {request.host}
    - Port: {request.environ.get('SERVER_PORT', 'unknown')}

    Expected Google Redirect URI: {request.url_root}login/google/authorized
    Expected Facebook Redirect URI: {request.url_root}login/facebook/authorized
    """
    return f"<pre>{debug_info}</pre>"

# OAuth success handlers
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = f"Failed to fetch user info from Google. Status: {resp.status_code}"
        flash(msg, category="error")
        return

    google_info = resp.json()
    google_name = google_info["name"]
    google_user_id = str(google_info["id"])
    google_email = google_info.get("email", f"{google_user_id}@oauth.local")

    # Handle user login/creation
    if current_user.is_anonymous:
        try:
            user, is_new = OAuthService.create_or_get_oauth_user(
                provider=blueprint.name,
                provider_user_id=google_user_id,
                provider_user_login=google_name,
                email=google_email,
                name=google_name
            )

            # Update token
            oauth = OAuthService.get_oauth_by_provider_and_id(blueprint.name, google_user_id)
            if oauth:
                OAuthService.update_oauth_token(oauth, token)

            login_user(user)
        except Exception as e:
            from project import db
            db.session.rollback()
            flash(f"Error during Google login: {str(e)}", category="error")
            return

    # Role-aware redirect
    try:
        role = (getattr(current_user, 'role', '') or 'buyer').lower()
        if role == 'seller':
            return redirect(url_for('seller.dashboard'))
        if role == 'rider':
            return redirect(url_for('main.rider_dashboard'))
        return redirect(url_for('main.index'))
    except Exception:
        return redirect(url_for("main.index"))

@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return

    resp = blueprint.session.get("/me")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return

    facebook_info = resp.json()
    facebook_name = facebook_info["name"]
    facebook_user_id = str(facebook_info["id"])
    facebook_email = facebook_info.get("email", f"{facebook_user_id}@oauth.local")

    # Handle user login/creation
    if current_user.is_anonymous:
        try:
            user, is_new = OAuthService.create_or_get_oauth_user(
                provider=blueprint.name,
                provider_user_id=facebook_user_id,
                provider_user_login=facebook_name,
                email=facebook_email,
                name=facebook_name
            )

            # Update token
            oauth = OAuthService.get_oauth_by_provider_and_id(blueprint.name, facebook_user_id)
            if oauth:
                OAuthService.update_oauth_token(oauth, token)

            login_user(user)
        except Exception as e:
            flash(f"Error during Facebook login: {str(e)}", category="error")
            return

    try:
        role = (getattr(current_user, 'role', '') or 'buyer').lower()
        if role == 'seller':
            return redirect(url_for('seller.dashboard'))
        if role == 'rider':
            return redirect(url_for('main.rider_dashboard'))
        return redirect(url_for('main.index'))
    except Exception:
        return redirect(url_for("main.index"))

# OAuth error handlers
@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, message, response):
    error_msg = f"OAuth error from {blueprint.name}! Error: {message}"
    if response:
        error_msg += f" | Response: {response.text}"
    flash(error_msg, category="error")

@oauth_error.connect_via(facebook_blueprint)
def facebook_error(blueprint, message, response):
    error_msg = f"OAuth error from {blueprint.name}! Error: {message}"
    if response:
        error_msg += f" | Response: {response.text}"
    flash(error_msg, category="error")
