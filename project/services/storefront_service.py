"""
Services powering storefront, cart/checkout, store customization, and product reviews.
"""
import json
import os
import uuid
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import and_, func

from project import db
from project.models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    OrderTrackingEvent,
    Product,
    ProductVariant,
    Review,
    ReviewMedia,
    ReviewResponse,
    StoreProfile,
    User,
)
from werkzeug.utils import secure_filename


class StorefrontError(ValueError):
    """Raised when shopper or store operations fail validation."""


def _slugify(value: str) -> str:
    return (
        (value or "")
        .strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
    )


def ensure_store_profile(seller: User) -> StoreProfile:
    """Guarantee that a seller has an associated store profile."""
    store = StoreProfile.query.filter_by(seller_id=seller.id).first()
    if store:
        return store
    slug_base = _slugify(seller.username or f"store-{seller.id}")
    slug = slug_base
    counter = 1
    while StoreProfile.query.filter_by(slug=slug).first():
        counter += 1
        slug = f"{slug_base}-{counter}"
    store = StoreProfile(
        seller_id=seller.id,
        name=(seller.username or "Storefront").title(),
        slug=slug,
        tagline="New seller on Dione",
    )
    db.session.add(store)
    db.session.commit()
    return store


def update_store_profile(store: StoreProfile, form_data, files, config) -> StoreProfile:
    store.name = (form_data.get("name") or store.name or "").strip() or store.name
    store.slug = _slugify(form_data.get("slug") or store.slug or store.name)
    store.tagline = (form_data.get("tagline") or "").strip()
    store.description = (form_data.get("description") or "").strip()
    store.contact_email = (form_data.get("contact_email") or "").strip()
    store.contact_phone = (form_data.get("contact_phone") or "").strip()
    store.theme_color = (form_data.get("theme_color") or store.theme_color or "#111827").strip()
    store.shipping_policy = (form_data.get("shipping_policy") or "").strip()
    store.return_policy = (form_data.get("return_policy") or "").strip()

    social_links = {
        "facebook": (form_data.get("social_facebook") or "").strip(),
        "instagram": (form_data.get("social_instagram") or "").strip(),
        "tiktok": (form_data.get("social_tiktok") or "").strip(),
        "website": (form_data.get("social_website") or "").strip(),
    }
    store.social_links = json.dumps({k: v for k, v in social_links.items() if v})

    upload_folder = config["UPLOAD_FOLDER"]
    for field in ("logo_image", "banner_image"):
        file = files.get(field)
        if not file or not getattr(file, "filename", None):
            continue
        filename = secure_filename(file.filename)
        unique_name = f"store_{store.id}_{field}_{uuid.uuid4().hex}_{filename}"
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, unique_name)
        file.save(path)
        setattr(store, field, f"uploads/{unique_name}")

    db.session.commit()
    return store


def store_analytics(store: StoreProfile) -> Dict[str, float]:
    """Return aggregated analytics for a store."""
    total_products = Product.query.filter_by(seller_id=store.seller_id).count()
    order_query = Order.query.filter_by(seller_id=store.seller_id)
    total_orders = order_query.count()
    revenue = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.seller_id == store.seller_id)
        .scalar()
        or 0
    )
    rating_stats = (
        db.session.query(
            func.coalesce(func.avg(Review.rating), 0),
            func.count(Review.id),
        )
        .filter(Review.store_id == store.id, Review.is_published.is_(True))
        .one()
    )
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": float(revenue),
        "average_rating": float(rating_stats[0]),
        "review_count": rating_stats[1],
    }


def list_store_catalog(store: StoreProfile) -> List[Product]:
    return (
        Product.query.filter_by(seller_id=store.seller_id, is_active=True)
        .order_by(Product.created_at.desc())
        .all()
    )


def search_products(form) -> Tuple[List[Product], Dict[str, Optional[str]]]:
    """Return filtered products for storefront catalog."""
    query = Product.query.filter(Product.is_active.is_(True))
    filters = {
        "q": form.get("q", "").strip(),
        "category": form.get("category"),
        "min_price": form.get("min_price"),
        "max_price": form.get("max_price"),
        "featured": form.get("featured"),
        "stock": form.get("stock"),
    }
    if filters["q"]:
        like = f"%{filters['q']}%"
        query = query.filter(
            (Product.name.ilike(like)) | (Product.description.ilike(like))
        )
    if filters["category"]:
        try:
            category_id = int(filters["category"])
        except ValueError:
            raise StorefrontError("Invalid category filter.")
        query = query.filter(Product.category_id == category_id)
    if filters["featured"]:
        query = query.filter(Product.is_featured.is_(True))
    if filters["stock"] == "in":
        query = query.filter(Product.stock > 0)
    if filters["min_price"]:
        query = query.filter(Product.price >= _decimal(filters["min_price"]))
    if filters["max_price"]:
        query = query.filter(Product.price <= _decimal(filters["max_price"]))

    products = query.order_by(Product.updated_at.desc()).limit(50).all()
    return products, filters


def _decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        raise StorefrontError("Invalid numeric value.")


def get_or_create_cart(user: User) -> Cart:
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if cart:
        return cart
    cart = Cart(user_id=user.id, status="active")
    db.session.add(cart)
    db.session.commit()
    return cart


def add_item_to_cart(user: User, product_id: int, variant_id: Optional[int], quantity: int):
    if quantity <= 0:
        raise StorefrontError("Quantity must be at least 1.")
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        raise StorefrontError("Product not available.")
    variant = None
    base_price = product.price
    if variant_id:
        variant = ProductVariant.query.filter_by(id=variant_id, product_id=product.id).first()
        if not variant:
            raise StorefrontError("Variant not available.")
        if variant.stock < quantity:
            raise StorefrontError("Variant out of stock.")
        base_price = (Decimal(base_price) + Decimal(variant.price_delta)).quantize(Decimal("0.01"))
    else:
        if product.stock < quantity:
            raise StorefrontError("Not enough stock for this product.")

    cart = get_or_create_cart(user)
    item = next(
        (i for i in cart.items if i.product_id == product.id and (i.variant_id or None) == (variant.id if variant else None)),
        None,
    )
    if item:
        item.quantity += quantity
        item.unit_price = base_price
    else:
        item = CartItem(
            cart=cart,
            product_id=product.id,
            variant_id=variant.id if variant else None,
            quantity=quantity,
            unit_price=base_price,
        )
        db.session.add(item)
    db.session.commit()
    return cart


def list_cart_items(user: User) -> List[CartItem]:
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart:
        return []
    return list(cart.items)


def checkout_cart(user: User) -> List[Order]:
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart or not cart.items:
        raise StorefrontError("Your cart is empty.")

    grouped: Dict[int, List[CartItem]] = defaultdict(list)
    for item in cart.items:
        grouped[item.product.seller_id].append(item)

    orders: List[Order] = []
    for seller_id, items in grouped.items():
        order = Order(seller_id=seller_id, buyer_id=user.id, status="processing")
        db.session.add(order)
        db.session.flush()
        for item in items:
            product = item.product
            variant = item.variant
            qty = item.quantity
            if variant:
                if variant.stock < qty:
                    raise StorefrontError(f"{product.name} variant '{variant.value}' no longer available.")
                variant.stock -= qty
                line_price = Decimal(item.unit_price)
            else:
                if product.stock < qty:
                    raise StorefrontError(f"{product.name} is out of stock.")
                product.stock -= qty
                line_price = Decimal(item.unit_price)
            order_item = OrderItem(
                order=order,
                product_id=product.id,
                variant_id=variant.id if variant else None,
                quantity=qty,
                unit_price=line_price,
            )
            db.session.add(order_item)
        order.recompute_total()
        db.session.add(OrderTrackingEvent(order=order, status="pending", message="Order received"))
        orders.append(order)

    cart.status = "checked_out"
    cart.items.clear()
    db.session.commit()
    return orders


def create_review(user: User, product_id: int, rating: int, title: str, body: str, files, config) -> Review:
    if rating < 1 or rating > 5:
        raise StorefrontError("Rating must be between 1 and 5.")
    product = Product.query.get(product_id)
    if not product or not product.is_active:
        raise StorefrontError("Product not found.")
    store = ensure_store_profile(product.seller)

    review = Review(
        product_id=product.id,
        store_id=store.id,
        user_id=user.id,
        rating=rating,
        title=(title or "").strip() or None,
        body=(body or "").strip(),
        is_published=True,
    )
    db.session.add(review)
    db.session.flush()

    uploads = files.getlist("media") if hasattr(files, "getlist") else []
    upload_folder = config["UPLOAD_FOLDER"]
    allowed = {ext.lower() for ext in config.get("ALLOWED_IMAGE_EXTENSIONS", [])}
    count = 0
    for upload in uploads[:5]:
        if not upload or not getattr(upload, "filename", None):
            continue
        ext = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
        if ext not in allowed:
            continue
        filename = secure_filename(upload.filename)
        unique_name = f"review_{review.id}_{uuid.uuid4().hex}_{filename}"
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, unique_name)
        upload.save(path)
        db.session.add(ReviewMedia(review=review, path=f"uploads/{unique_name}", media_type="image"))
        count += 1
    review.media_count = count
    db.session.commit()
    return review


def get_rating_breakdown(product_id: int) -> Dict[str, float]:
    rows = (
        db.session.query(Review.rating, func.count(Review.id))
        .filter(Review.product_id == product_id, Review.is_published.is_(True))
        .group_by(Review.rating)
        .all()
    )
    total = sum(count for _, count in rows) or 0
    average = 0
    if total:
        total_score = sum(rating * count for rating, count in rows)
        average = total_score / total
    distribution = {str(rating): 0 for rating in range(1, 6)}
    for rating, count in rows:
        distribution[str(rating)] = count
    return {"average": average, "total": total, "distribution": distribution}


def respond_to_review(seller: User, review_id: int, message: str) -> ReviewResponse:
    review = Review.query.get(review_id)
    if not review:
        raise StorefrontError("Review not found.")
    if review.store.seller_id != seller.id:
        raise StorefrontError("You cannot respond to this review.")
    message = (message or "").strip()
    if not message:
        raise StorefrontError("Response message is required.")
    if review.response:
        review.response.message = message
        response = review.response
    else:
        response = ReviewResponse(review_id=review.id, seller_id=seller.id, message=message)
        db.session.add(response)
    db.session.commit()
    return response


def moderate_review(review_id: int, publish: bool) -> Review:
    review = Review.query.get(review_id)
    if not review:
        raise StorefrontError("Review not found.")
    review.is_published = bool(publish)
    db.session.commit()
    return review
