"""
OAuth service for social login integration
"""
import re
from project.models import User, OAuth
from project import db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

class OAuthService:
    """Service class for OAuth operations"""

    @staticmethod
    def create_or_get_oauth_user(provider, provider_user_id, provider_user_login, email, name):
        """Create or get user for OAuth login"""
        # Check if OAuth record exists
        oauth = OAuth.query.filter_by(
            provider=provider,
            provider_user_id=provider_user_id
        ).first()

        if oauth and oauth.user:
            return oauth.user, False  # User exists, not new

        # Normalize email (if provided) and try to find existing account
        email_normalized = (email or '').strip().lower() or None
        user = None
        if email_normalized:
            user = User.query.filter(
                func.lower(func.trim(User.email)) == email_normalized
            ).first()

        username_source = name or provider_user_login or (email_normalized.split('@')[0] if email_normalized else None) or provider_user_id
        username_value = OAuthService._sanitize_username(username_source, provider, provider_user_id)

        # Create new user if none exists
        created_new_user = False
        if not user:
            # Providers may not always share emails. Generate a deterministic placeholder when needed.
            placeholder_email = email_normalized or f"{provider_user_id}@{provider}.oauth.local"
            user = User(email=placeholder_email, username=username_value)
            db.session.add(user)
            created_new_user = True
            try:
                db.session.flush()  # Ensure user.id is available
            except IntegrityError:
                # Another process created this user first; fetch and reuse
                db.session.rollback()
                user = User.query.filter(
                    func.lower(func.trim(User.email)) == placeholder_email.strip().lower()
                ).first()
                created_new_user = False
                if not user:
                    raise

        # Backfill username for existing accounts without one
        if user and not getattr(user, 'username', None):
            user.username = username_value

        # Create or update OAuth record
        if not oauth:
            oauth = OAuth(
                provider=provider,
                provider_user_id=provider_user_id,
                provider_user_login=provider_user_login,
                user_id=user.id,
            )
            db.session.add(oauth)
        else:
            # Update existing OAuth record with user_id
            oauth.user_id = user.id

        try:
            db.session.commit()
            return user, created_new_user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _sanitize_username(raw_value, provider, provider_user_id):
        """Generate a fallback username that matches validation rules"""
        base = (raw_value or '').strip()
        if not base:
            base = f"{provider}_{provider_user_id}"
        cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', base)
        cleaned = cleaned.strip('_') or 'user'
        return cleaned[:30]

    @staticmethod
    def update_oauth_token(oauth, token):
        """Update OAuth token for user"""
        try:
            oauth.token_dict = token
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_oauth_by_provider_and_id(provider, provider_user_id):
        """Get OAuth record by provider and user ID"""
        return OAuth.query.filter_by(
            provider=provider,
            provider_user_id=provider_user_id
        ).first()
