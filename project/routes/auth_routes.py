"""
Authentication routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from project.services.auth_service import AuthService
from project.utils.validators import Validators

auth = Blueprint('auth', __name__)

ROLE_DETAIL_FIELDS = {
    'buyer': [
        ('buyer_contact', 'Primary contact number', False),
        ('buyer_address', 'Preferred delivery address', False),
    ],
    'seller': [
        ('seller_store_name', 'Store name', True),
        ('seller_business_id', 'Business registration / permit', True),
        ('seller_contact', 'Business contact number', True),
        ('seller_address', 'Pickup / warehouse address', True),
        ('seller_description', 'What you plan to sell', False),
    ],
    'rider': [
        ('rider_vehicle_type', 'Vehicle type', True),
        ('rider_plate_number', 'Plate number', True),
        ('rider_license_number', 'Driver license number', True),
        ('rider_contact', 'Contact number', True),
        ('rider_service_area', 'Primary delivery areas', False),
    ],
}


def _collect_role_details(form_data, role):
    """Extract structured details for the given role from the signup form."""
    config = ROLE_DETAIL_FIELDS.get(role, [])
    entries = []
    missing_required = []
    for field_name, label, required in config:
        value = (form_data.get(field_name) or '').strip()
        if not value:
            if required:
                missing_required.append(label)
            continue
        entries.append({'label': label, 'value': value})
    return entries, missing_required

@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Validate form
    is_valid, errors = Validators.validate_login_form(email, password)
    if not is_valid:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.login'))

    # Authenticate user
    user, error = AuthService.authenticate_user(email, password)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    # Block suspended users
    if getattr(user, 'is_suspended', False):
        flash('Your account is suspended. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    # If pending approval, inform and keep on public area
    if getattr(user, 'role_requested', None) and not getattr(user, 'is_approved', True):
        flash(f"Your request to become a {user.role_requested} is pending admin approval.", 'info')
        return redirect(url_for('main.pending'))

    # Redirect by active role
    role = (getattr(user, 'role', '') or 'buyer').lower()
    if role == 'seller':
        return redirect(url_for('seller.dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    if role == 'admin':
        return redirect(url_for('admin.overview'))
    return redirect(url_for('main.index'))

@auth.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == "GET":
        return render_template('auth/reset.html')

    if request.method == "POST":
        email = request.form.get('email')
        user = AuthService.get_user_by_email(email)

        if user:
            success, error = AuthService.send_password_reset_email(user)
            if success:
                flash('An email has been sent with instructions to reset your password.', 'info')
            else:
                flash(f'Error sending email: {error}', 'danger')
        else:
            flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))

@auth.route('/reset/<token>', methods = ['GET', 'POST'])
def reset_verified(token):
    if request.method == "GET":
        return render_template('auth/reset_password.html')

    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('auth.reset_verified', token=token))

    success, error = AuthService.reset_password(token, password)

    if success:
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(error, 'danger')
        return redirect(url_for('auth.reset'))

@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = (request.form.get('role') or 'buyer').lower()
    role_details, missing_required = _collect_role_details(request.form, role)

    # Validate form
    is_valid, errors = Validators.validate_signup_form(username, email, password)
    # Validate role
    role_valid, role_error = Validators.validate_role(role)
    if not role_valid:
        errors.append(role_error)
    if role in {'seller', 'rider'} and missing_required:
        errors.append(
            f"Please complete the following fields for {role} applications: {', '.join(missing_required)}"
        )
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    # Create user
    details_payload = role_details if role in {'seller', 'rider'} else None
    user, error = AuthService.create_user(username, email, password, role=role, role_details=details_payload)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    if user.role_requested and not user.is_approved:
        flash(f"Account created! Your request to become a {role} is pending admin approval.", 'info')
    else:
        flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
