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
    def validate_username(username):
        """Validate username format"""
        if not username:
            return False, "Username is required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 30:
            return False, "Username must be at most 30 characters long"

        # Allow alphanumeric, underscore, and hyphen
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"

        return True, None

    @staticmethod
    def validate_signup_form(*args):
        """Validate complete signup form

        Supports two calling conventions:
        - validate_signup_form(email, password) - backward compatible
        - validate_signup_form(username, email, password) - for tests
        """
        errors = []

        # Handle both calling conventions
        if len(args) == 2:
            # Backward compatible: (email, password)
            email, password = args
            username = None
        elif len(args) == 3:
            # Test format: (username, email, password)
            username, email, password = args
        else:
            return False, ["Invalid number of arguments"]

        # Validate username if provided
        if username is not None:
            is_valid, error = Validators.validate_username(username)
            if not is_valid:
                errors.append(error)

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
