"""
Authentication routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from project.services.auth_service import AuthService
from project.utils.validators import Validators

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

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

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/reset', methods=['GET','POST'])
def reset():
    if request.method == "GET":
        return render_template('reset.html')

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
        return render_template('reset_password.html')

    password = request.form.get('password')
    success, error = AuthService.reset_password(token, password)

    if success:
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(error, 'danger')
        return redirect(url_for('auth.reset'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate form
    is_valid, errors = Validators.validate_signup_form(username, email, password)
    if not is_valid:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    # Create user
    user, error = AuthService.create_user(username, email, password)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.signup'))

    flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
