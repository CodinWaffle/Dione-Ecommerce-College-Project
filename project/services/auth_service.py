"""
Authentication service for Dione Ecommerce
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from flask import render_template
from project.models import User
from project import db, mail

class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def create_user(username, email, password):
        """Create a new user"""
        # Validate required fields
        if not username or not email or not password:
            return None, "All fields are required"

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email address already exists"

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating user: {str(e)}"

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate a user with email and password"""
        user = User.query.filter_by(email=email).first()

        if not user:
            return None, "No account found with that email address"

        # Check if this is an OAuth user (no password set)
        if not user.password:
            return None, "This account uses social login (Google/Facebook). Please use the 'Sign in with Google' button"

        # Verify password
        if not check_password_hash(user.password, password):
            return None, "Incorrect password. Please try again"

        return user, None

    @staticmethod
    def send_password_reset_email(user):
        """Send password reset email to user"""
        try:
            token = user.get_reset_token()

            msg = Message()
            msg.subject = "Login System: Password Reset Request"
            msg.sender = 'dnxncpcx@gmail.com'
            msg.recipients = [user.email]
            msg.html = render_template('reset_pwd.html', user=user, token=token)

            mail.send(msg)
            return True, None
        except Exception as e:
            return False, f"Error sending email: {str(e)}"

    @staticmethod
    def reset_password(token, new_password):
        """Reset user password using token"""
        user = User.verify_reset_token(token)

        if not user:
            return False, "User not found or token has expired"

        if not new_password:
            return False, "Password is required"

        try:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.password = hashed_password
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating password: {str(e)}"

    @staticmethod
    def get_user_by_email(email):
        """Get user by email address"""
        return User.verify_email(email)
