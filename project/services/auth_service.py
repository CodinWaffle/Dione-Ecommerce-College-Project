"""
Authentication service for Dione Ecommerce
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from flask import render_template
from project.models import User, Buyer, Seller, Rider
from project import db, mail

class AuthService:
    """Service class for authentication operations"""

    @staticmethod
    def create_user(email, password, role='buyer'):
        """Create a new user"""
        # Validate required fields
        if not email or not password:
            return None, "Email and password are required"

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email address already exists"

        desired_role = (role or 'buyer').lower()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # If user applies for seller/rider, create a pending request, otherwise normal creation
        if desired_role in {'seller', 'rider'}:
            new_user = User(
                email=email,
                password=hashed_password,
                role='buyer',
                role_requested=desired_role,
                is_approved=False
            )
        else:
            # For buyer/admin: set active role immediately (admin creation should be restricted in production)
            new_user = User(
                email=email,
                password=hashed_password,
                role=desired_role if desired_role in {'buyer', 'admin'} else 'buyer',
                role_requested=None,
                is_approved=True
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
            msg.html = render_template('auth/reset_pwd.html', user=user, token=token)

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

    @staticmethod
    def create_buyer_profile(user_id, buyer_data):
        """Create buyer profile with additional data"""
        try:
            buyer = Buyer(
                user_id=user_id,
                phone=buyer_data.get('phone'),
                address=buyer_data.get('address'),
                city=buyer_data.get('city'),
                zip_code=buyer_data.get('zip_code'),
                country=buyer_data.get('country'),
                preferred_language=buyer_data.get('preferred_language', 'English')
            )
            db.session.add(buyer)
            db.session.commit()
            return buyer, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating buyer profile: {str(e)}"

    @staticmethod
    def create_seller_profile(user_id, seller_data):
        """Create seller profile with additional data"""
        try:
            seller = Seller(
                user_id=user_id,
                business_name=seller_data.get('business_name'),
                business_type=seller_data.get('business_type'),
                business_address=seller_data.get('business_address'),
                business_city=seller_data.get('business_city'),
                business_zip=seller_data.get('business_zip'),
                business_country=seller_data.get('business_country'),
                bank_name=seller_data.get('bank_name'),
                bank_account=seller_data.get('bank_account'),
                bank_holder_name=seller_data.get('bank_holder_name'),
                tax_id=seller_data.get('tax_id'),
                store_description=seller_data.get('store_description'),
                is_verified=False
            )
            db.session.add(seller)
            db.session.commit()
            return seller, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating seller profile: {str(e)}"

    @staticmethod
    def create_rider_profile(user_id, rider_data):
        """Create rider profile with additional data"""
        try:
            rider = Rider(
                user_id=user_id,
                phone=rider_data.get('phone'),
                license_number=rider_data.get('license_number'),
                vehicle_type=rider_data.get('vehicle_type'),
                vehicle_number=rider_data.get('vehicle_number'),
                availability_status=rider_data.get('availability_status', 'available'),
                current_location=rider_data.get('current_location'),
                delivery_zones=rider_data.get('delivery_zones'),
                is_verified=False
            )
            db.session.add(rider)
            db.session.commit()
            return rider, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating rider profile: {str(e)}"
