"""
Authentication routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from project.services.auth_service import AuthService
from project.utils.validators import Validators
from project import db

auth = Blueprint('auth', __name__)

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

    role = (getattr(user, 'role', '') or '').lower()
    if role == 'admin':
        flash('Admin accounts must sign in on the Admin Login page.', 'warning')
        return render_template('auth/login.html'), 403

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

@auth.route('/seller-signup')
def seller_signup():
    return render_template('auth/seller_signup.html')

@auth.route('/buyer-signup')
def buyer_signup():
    return render_template('auth/buyer_signup.html')

@auth.route('/rider-signup')
def rider_signup():
    return render_template('auth/rider_signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    username = (request.form.get('username') or '').strip()
    role = (request.form.get('role') or 'buyer').lower()

    # Validate form
    if username:
        is_valid, errors = Validators.validate_signup_form(username, email, password)
    else:
        is_valid, errors = Validators.validate_signup_form(email, password)
    # Validate role
    role_valid, role_error = Validators.validate_role(role)
    if not role_valid:
        errors.append(role_error)
    if not is_valid:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    # Create user
    user, error = AuthService.create_user(email, password, role=role, username=username)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    # Create role-specific profile based on selected role
    if role == 'buyer':
        buyer_data = {
            'phone': request.form.get('phone'),
            'address': request.form.get('streetAddress') or request.form.get('address') or '',
            'city': request.form.get('city') or '',
            'zip_code': request.form.get('zipCode') or request.form.get('zip_code') or '',
            'country': request.form.get('country') or 'Philippines',
            'preferred_language': request.form.get('preferred_language', 'English')
        }
        profile, profile_error = AuthService.create_buyer_profile(user.id, buyer_data)
        if profile_error:
            flash(profile_error, 'warning')

    elif role == 'seller':
        seller_data = {
            'business_name': request.form.get('business_name'),
            'business_type': request.form.get('business_type'),
            'business_address': request.form.get('streetAddress') or request.form.get('business_address') or '',
            'business_city': request.form.get('city') or request.form.get('business_city') or '',
            'business_zip': request.form.get('business_zip') or '',
            'business_country': request.form.get('country') or 'Philippines',
            'bank_name': request.form.get('bank_name'),
            'bank_account': request.form.get('bank_account'),
            'bank_holder_name': request.form.get('bank_holder_name'),
            'tax_id': request.form.get('tax_id') or '',
            'store_description': request.form.get('store_description')
        }
        # Set seller to pending approval
        user.is_approved = False
        user.role_requested = 'seller'
        db.session.commit()
        
        profile, profile_error = AuthService.create_seller_profile(user.id, seller_data)
        if profile_error:
            flash(profile_error, 'warning')

    elif role == 'rider':
        rider_data = {
            'phone': request.form.get('phone'),
            'license_number': request.form.get('license_number'),
            'vehicle_type': request.form.get('vehicle_type'),
            'vehicle_number': request.form.get('vehicle_number'),
            'availability_status': request.form.get('availability_status', 'available'),
            'current_location': request.form.get('current_location') or '',
            'delivery_zones': request.form.get('delivery_zones') or ''
        }
        profile, profile_error = AuthService.create_rider_profile(user.id, rider_data)
        if profile_error:
            flash(profile_error, 'warning')

    # Auto-login the user after successful account creation
    login_user(user)
    
    # Check if user needs approval
    if user.role_requested and not user.is_approved:
        flash(f"Account created! Your request to become a {role} is pending admin approval.", 'info')
        return redirect(url_for('main.pending'))
    
    # Redirect to appropriate dashboard based on role
    if role == 'buyer':
        flash('Account created successfully! Welcome to DIONE.', 'success')
        return redirect(url_for('main.index'))
    elif role == 'seller':
        flash('Account created successfully! Welcome to your seller dashboard.', 'success')
        return redirect(url_for('seller.dashboard'))
    elif role == 'rider':
        flash('Account created successfully! Welcome to your rider dashboard.', 'success')
        return redirect(url_for('main.rider_dashboard'))
    
    # Fallback to index
    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
