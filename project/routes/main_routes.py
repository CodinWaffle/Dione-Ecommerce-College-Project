"""
Main routes for Dione Ecommerce
"""
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from project import db
from project.models import Category, Product, User

main = Blueprint('main', __name__)

@main.before_request
def check_suspension():
    """Check if authenticated user is suspended and log them out if needed"""
    if current_user.is_authenticated and getattr(current_user, 'is_suspended', False):
        logout_user()
        flash('Your account has been suspended. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

@main.route('/')
def index():
    # If a pending seller/rider logs in, force pending page until approved
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
            return redirect(url_for('main.pending'))
        role = (getattr(current_user, 'role', '') or '').lower()
        if role == 'seller':
            return redirect(url_for('seller.dashboard'))
        if role == 'rider':
            return redirect(url_for('main.rider_dashboard'))
    featured_products = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.is_featured.desc(), Product.updated_at.desc())
        .limit(8)
        .all()
    )
    new_arrivals = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .limit(6)
        .all()
    )
    categories = (
        Category.query.filter_by(is_active=True)
        .order_by(Category.name.asc())
        .limit(10)
        .all()
    )
    return render_template(
        'main/index.html',
        featured_products=featured_products,
        new_arrivals=new_arrivals,
        categories=categories,
    )

@main.route('/profile')
@login_required
def profile():
    role = (getattr(current_user, 'role', '') or 'buyer').lower()
    if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
        return redirect(url_for('main.pending'))
    if role == 'seller':
        return redirect(url_for('seller.dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return render_template('main/profile.html', username=current_user.username)

@main.route('/rider/dashboard')
@login_required
def rider_dashboard():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider' or not getattr(current_user, 'is_approved', False):
        flash("You don't have access to the rider dashboard.", 'warning')
        return redirect(url_for('main.profile'))
    return render_template('rider/dashboard.html', username=current_user.username)

@main.route('/rider/deliveries')
@login_required
def rider_deliveries():
    if (getattr(current_user, 'role', '') or '').lower() != 'rider':
        flash("You don't have access to rider tools.", 'warning')
        return redirect(url_for('main.profile'))
    # Placeholder deliveries page - replace with real delivery management later
    return render_template('rider/deliveries.html', username=current_user.username)

@main.route('/pending')
@login_required
def pending():
    """Show pending approval page for users awaiting role upgrade."""
    if getattr(current_user, 'role_requested', None) and not getattr(current_user, 'is_approved', True):
        return render_template('main/pending.html', username=current_user.username, requested=current_user.role_requested)
    # If not pending anymore, route to appropriate place
    role = (getattr(current_user, 'role', '') or 'buyer').lower()
    if role == 'seller':
        return redirect(url_for('main.seller_dashboard'))
    if role == 'rider':
        return redirect(url_for('main.rider_dashboard'))
    return redirect(url_for('main.index'))



@main.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        user_count = User.query.count()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        user_count = 0

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "oauth": "configured",
        "users": user_count
    })

@main.route('/test-db')
def test_db():
    """Test database connectivity"""
    try:
        user_count = User.query.count()
        return jsonify({
            "database_status": "connected",
            "user_count": user_count,
            "message": "Database connection successful"
        })
    except Exception as e:
        return jsonify({
            "database_status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }), 500
