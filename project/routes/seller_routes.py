"""
Seller focused routes for product management, analytics, and order operations.
"""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from project.models import Order, Product, Review
from project.services.seller_service import (
    ProductValidationError,
    gather_dashboard_metrics,
    list_categories,
    log_manual_order,
    save_product_from_form,
    toggle_featured,
    update_order_status,
)
from project.services.storefront_service import (
    StorefrontError,
    ensure_store_profile,
    list_store_catalog,
    respond_to_review,
    store_analytics,
    update_store_profile,
)

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")


@seller_bp.before_request
def ensure_seller():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if current_user.is_suspended:
        flash("Your seller account is suspended.", "danger")
        return redirect(url_for("main.profile"))
    if (current_user.role or "").lower() != "seller" or not current_user.is_approved:
        flash("Seller access required.", "warning")
        return redirect(url_for("main.profile"))
    ensure_store_profile(current_user)


@seller_bp.route("/dashboard")
@login_required
def dashboard():
    metrics = gather_dashboard_metrics(current_user.id)
    recent_orders = (
        Order.query.filter_by(seller_id=current_user.id)
        .order_by(Order.placed_at.desc())
        .limit(5)
        .all()
    )
    featured = (
        Product.query.filter_by(seller_id=current_user.id, is_featured=True)
        .order_by(Product.updated_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "seller/dashboard.html",
        username=current_user.username,
        metrics=metrics,
        recent_orders=recent_orders,
        featured_products=featured,
    )


@seller_bp.route("/products")
@login_required
def products():
    items = (
        Product.query.filter_by(seller_id=current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    categories = list_categories()
    return render_template(
        "seller/products.html",
        username=current_user.username,
        products=items,
        categories=categories,
    )


@seller_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def product_create():
    categories = list_categories()
    if request.method == "POST":
        try:
            save_product_from_form(current_user, request.form, request.files, current_app.config)
            flash("Product created successfully.", "success")
            return redirect(url_for("seller.products"))
        except ProductValidationError as exc:
            flash(str(exc), "danger")
    return render_template(
        "seller/product_form.html",
        categories=categories,
        product=None,
        form_action=url_for("seller.product_create"),
    )


@seller_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def product_edit(product_id):
    product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first_or_404()
    categories = list_categories()
    if request.method == "POST":
        try:
            save_product_from_form(current_user, request.form, request.files, current_app.config, product=product)
            flash("Product updated.", "success")
            return redirect(url_for("seller.products"))
        except ProductValidationError as exc:
            flash(str(exc), "danger")
    return render_template(
        "seller/product_form.html",
        categories=categories,
        product=product,
        form_action=url_for("seller.product_edit", product_id=product.id),
    )


@seller_bp.post("/products/<int:product_id>/feature")
@login_required
def product_toggle_featured(product_id):
    product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first_or_404()
    toggle_featured(product)
    message = "added to" if product.is_featured else "removed from"
    flash(f"{product.name} {message} featured products.", "info")
    return redirect(url_for("seller.products"))


@seller_bp.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id"))
            quantity = int(request.form.get("quantity"))
            buyer_email = request.form.get("buyer_email") or None
            log_manual_order(current_user, product_id, quantity, buyer_email=buyer_email)
            flash("Manual order recorded.", "success")
            return redirect(url_for("seller.orders"))
        except (ValueError, ProductValidationError) as exc:
            flash(str(exc), "danger")

    order_rows = (
        Order.query.filter_by(seller_id=current_user.id)
        .order_by(Order.placed_at.desc())
        .all()
    )
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.name.asc()).all()
    return render_template(
        "seller/orders.html",
        orders=order_rows,
        products=products,
        status_choices=Order.STATUS_CHOICES,
    )


@seller_bp.post("/orders/<int:order_id>/status")
@login_required
def order_status(order_id):
    order = Order.query.filter_by(id=order_id, seller_id=current_user.id).first_or_404()
    status = request.form.get("status")
    try:
        update_order_status(order, status)
        flash("Order status updated.", "success")
    except ProductValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("seller.orders"))


@seller_bp.route("/store/profile", methods=["GET", "POST"])
@login_required
def store_profile():
    store = ensure_store_profile(current_user)
    if request.method == "POST":
        try:
            update_store_profile(store, request.form, request.files, current_app.config)
            flash("Store profile updated.", "success")
            return redirect(url_for("seller.store_profile"))
        except StorefrontError as exc:
            flash(str(exc), "danger")
    return render_template("seller/store_profile.html", store=store)


@seller_bp.route("/store/analytics")
@login_required
def store_insights():
    store = ensure_store_profile(current_user)
    metrics = store_analytics(store)
    catalog = list_store_catalog(store)
    return render_template(
        "seller/store_analytics.html",
        store=store,
        metrics=metrics,
        catalog=catalog,
    )


@seller_bp.route("/store/reviews")
@login_required
def store_reviews():
    store = ensure_store_profile(current_user)
    reviews = (
        Review.query.filter_by(store_id=store.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return render_template("seller/store_reviews.html", store=store, reviews=reviews)


@seller_bp.post("/store/reviews/<int:review_id>/respond")
@login_required
def store_review_response(review_id):
    try:
        respond_to_review(current_user, review_id, request.form.get("message"))
        flash("Response saved.", "success")
    except StorefrontError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("seller.store_reviews"))
