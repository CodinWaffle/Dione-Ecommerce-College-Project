"""
OAuth service for social login integration
"""
from project.models import User, OAuth
from project import db

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

        # Create new user
        user = User(username=name, email=email)
        db.session.add(user)
        db.session.flush()  # Get the user.id

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
            return user, True  # New user created
        except Exception as e:
            db.session.rollback()
            raise e

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
