"""
Public storefront, cart, checkout, and review routes.
"""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from project.models import Category, Order, Product, Review, StoreProfile
from project.services.storefront_service import (
    StorefrontError,
    add_item_to_cart,
    checkout_cart,
    create_review,
    get_rating_breakdown,
    list_cart_items,
    search_products,
)

shop_bp = Blueprint("shop", __name__, url_prefix="/shop")


@shop_bp.route("/")
def catalog():
    try:
        products, filters = search_products(request.args)
    except StorefrontError as exc:
        flash(str(exc), "danger")
        products, filters = [], {}
    categories = Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()
    return render_template(
        "shop/catalog.html",
        products=products,
        categories=categories,
        filters=filters,
    )


@shop_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    rating = get_rating_breakdown(product.id)
    reviews = (
        Review.query.filter_by(product_id=product.id, is_published=True)
        .order_by(Review.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "shop/product_detail.html",
        product=product,
        rating=rating,
        reviews=reviews,
    )


@shop_bp.post("/product/<int:product_id>/reviews")
@login_required
def product_review(product_id):
    try:
        create_review(
            current_user,
            product_id,
            int(request.form.get("rating", 0)),
            request.form.get("title"),
            request.form.get("body"),
            request.files,
            current_app.config,
        )
        flash("Review submitted!", "success")
    except (ValueError, StorefrontError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("shop.product_detail", product_id=product_id))


@shop_bp.post("/cart/items")
@login_required
def cart_add_item():
    try:
        product_id = int(request.form.get("product_id"))
        variant_id = request.form.get("variant_id")
        variant_id = int(variant_id) if variant_id else None
        quantity = int(request.form.get("quantity", 1))
        add_item_to_cart(current_user, product_id, variant_id, quantity)
        flash("Product added to cart.", "success")
    except (ValueError, StorefrontError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart")
@login_required
def cart():
    items = list_cart_items(current_user)
    total = sum(float(item.unit_price) * item.quantity for item in items)
    return render_template("shop/cart.html", items=items, total=total)


@shop_bp.post("/cart/checkout")
@login_required
def cart_checkout():
    try:
        orders = checkout_cart(current_user)
        flash(f"Checkout complete! {len(orders)} order(s) placed.", "success")
        order = orders[0]
        return redirect(url_for("shop.order_tracking", order_id=order.id))
    except StorefrontError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/orders/<int:order_id>/track")
@login_required
def order_tracking(order_id):
    order = Order.query.filter_by(id=order_id, buyer_id=current_user.id).first_or_404()
    return render_template("shop/order_tracking.html", order=order)


@shop_bp.route("/store/<slug>")
def store_profile(slug):
    store = StoreProfile.query.filter_by(slug=slug).first_or_404()
    products = store.seller.products.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    rating = get_rating_breakdown_for_store(store.id)
    return render_template(
        "shop/store_profile.html",
        store=store,
        products=products,
        rating=rating,
    )


def get_rating_breakdown_for_store(store_id: int):
    rows = (
        Review.query.with_entities(Review.rating, func.count(Review.id))
        .filter_by(store_id=store_id, is_published=True)
        .group_by(Review.rating)
        .all()
    )
    total = sum(count for _, count in rows) or 0
    average = 0
    if total:
        average = sum(rating * count for rating, count in rows) / total
    return {"average": average, "total": total}
