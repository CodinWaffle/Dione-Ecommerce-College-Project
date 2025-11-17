"""
Validation utilities for Dione Ecommerce
"""
import re
from flask import flash

class Validators:
    """Validation utility class"""

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False, "Email is required"

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"

        return True, None

    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters long"

        return True, None

    @staticmethod
    def validate_signup_form(email, password):
        """Validate complete signup form"""
        errors = []

        # Validate email
        is_valid, error = Validators.validate_email(email)
        if not is_valid:
            errors.append(error)

        # Validate password
        is_valid, error = Validators.validate_password(password)
        if not is_valid:
            errors.append(error)

        return len(errors) == 0, errors

    @staticmethod
    def validate_role(role):
        """Validate user role value"""
        allowed = {'buyer', 'seller', 'rider'}
        if not role:
            return False, "Role is required"
        if role.lower() not in allowed:
            return False, "Invalid role selected"
        return True, None

    @staticmethod
    def validate_login_form(email, password):
        """Validate login form"""
        errors = []

        # Validate email
        is_valid, error = Validators.validate_email(email)
        if not is_valid:
            errors.append(error)

        # Validate password
        if not password:
            errors.append("Password is required")

        return len(errors) == 0, errors
