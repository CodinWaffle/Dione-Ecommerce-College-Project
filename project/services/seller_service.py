"""
Utility functions backing the seller dashboard and product management flows.
"""
import os
import uuid
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Optional

from sqlalchemy import func, desc

from project import db
from project.models import (
    Category,
    InventoryTransaction,
    Order,
    OrderItem,
    Product,
    ProductImage,
    User,
)
from werkzeug.utils import secure_filename


class ProductValidationError(ValueError):
    """Raised when seller input fails validation."""


def _slugify(value: str) -> str:
    return (
        value.lower()
        .strip()
        .replace(" ", "-")
        .replace("_", "-")
    )


def list_categories() -> List[Category]:
    return Category.query.filter_by(is_active=True).order_by(Category.name.asc()).all()


def upsert_category(name: str) -> Optional[Category]:
    cleaned = (name or "").strip()
    if not cleaned:
        return None
    slug = _slugify(cleaned)
    category = Category.query.filter(
        func.lower(Category.slug) == slug.lower()
    ).first()
    if not category:
        category = Category(name=cleaned, slug=slug, is_active=True)
        db.session.add(category)
        db.session.flush()
    return category


def _parse_decimal(value: str, field: str) -> Decimal:
    try:
        numeric = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ProductValidationError(f"Invalid {field}.")
    if numeric < 0:
        raise ProductValidationError(f"{field.title()} cannot be negative.")
    return numeric.quantize(Decimal("0.01"))


def _parse_int(value: str, field: str) -> int:
    try:
        integer = int(value)
    except (ValueError, TypeError):
        raise ProductValidationError(f"Invalid {field}.")
    if integer < 0:
        raise ProductValidationError(f"{field.title()} cannot be negative.")
    return integer


def _validate_images(files: Iterable, existing_count: int, allowed_extensions: Iterable[str], max_images: int = 5) -> List:
    sanitized = []
    for upload in files:
        if not upload or not getattr(upload, "filename", None):
            continue
        filename = upload.filename
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in allowed_extensions:
            raise ProductValidationError(f"Unsupported file extension: {ext}")
        sanitized.append(upload)
    if existing_count + len(sanitized) > max_images:
        raise ProductValidationError(f"You can only store up to {max_images} images.")
    return sanitized


def _reset_images(product: Product, upload_folder: str):
    for image in list(product.images):
        path = os.path.join(upload_folder, os.path.basename(image.path))
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
        db.session.delete(image)
    db.session.flush()


def _persist_images(product: Product, uploads: Iterable, upload_folder: str):
    for idx, upload in enumerate(uploads, start=len(product.images)):
        filename = secure_filename(upload.filename)
        unique_name = f"{product.id}_{uuid.uuid4().hex}_{filename}"
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, unique_name)
        upload.save(filepath)
        image = ProductImage(product=product, path=f'uploads/{unique_name}', position=idx)
        db.session.add(image)


def save_product_from_form(
    seller: User,
    form_data,
    files,
    config,
    product: Optional[Product] = None,
) -> Product:
    if not seller or (seller.role or "").lower() != "seller":
        raise ProductValidationError("Only sellers can manage products.")

    name = (form_data.get("name") or "").strip()
    description = (form_data.get("description") or "").strip()
    price = _parse_decimal(form_data.get("price", "0"), "price")
    stock = _parse_int(form_data.get("stock", "0"), "inventory")

    if not name:
        raise ProductValidationError("Product name is required.")
    if price == Decimal("0.00"):
        raise ProductValidationError("Price must be greater than zero.")

    category_id = form_data.get("category_id")
    new_category = form_data.get("new_category")
    category = None
    if category_id:
        category = Category.query.get(int(category_id))
    if not category and new_category:
        category = upsert_category(new_category)

    is_featured = bool(form_data.get("is_featured"))

    if product is None:
        product = Product(
            seller_id=seller.id,
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            is_featured=is_featured,
        )
        db.session.add(product)
        db.session.flush()
        if stock:
            txn = InventoryTransaction(product=product, change=stock, source="initial", note="Initial stock")
            db.session.add(txn)
    else:
        previous_stock = product.stock
        product.name = name
        product.description = description
        product.price = price
        product.category = category
        product.is_featured = is_featured
        product.is_active = bool(form_data.get("is_active"))
        if stock != previous_stock:
            delta = stock - previous_stock
            product.stock = stock
            txn = InventoryTransaction(product=product, change=delta, source="manual", note="Inventory adjustment")
            db.session.add(txn)
        else:
            product.stock = stock

    uploads = files.getlist("images") if hasattr(files, "getlist") else []
    upload_folder = config["UPLOAD_FOLDER"]
    allowed_ext = {ext.lower() for ext in config.get("ALLOWED_IMAGE_EXTENSIONS", [])}
    replace_images = form_data.get("replace_images")
    if replace_images and product.images:
        _reset_images(product, upload_folder)
    validated = _validate_images(uploads, len(product.images), allowed_ext)
    _persist_images(product, validated, upload_folder)
    db.session.commit()
    return product


def toggle_featured(product: Product) -> Product:
    product.is_featured = not product.is_featured
    db.session.commit()
    return product


def gather_dashboard_metrics(seller_id: int) -> dict:
    total_products = Product.query.filter_by(seller_id=seller_id).count()
    featured_products = Product.query.filter_by(seller_id=seller_id, is_featured=True).count()
    total_stock = db.session.query(func.coalesce(func.sum(Product.stock), 0)).filter(Product.seller_id == seller_id).scalar() or 0

    orders_query = Order.query.filter(Order.seller_id == seller_id)
    total_orders = orders_query.count()
    revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(Order.seller_id == seller_id, Order.status.in_(("processing", "shipped", "completed"))).scalar() or 0
    open_orders = orders_query.filter(Order.status.in_(("pending", "processing"))).count()

    product_performance = (
        db.session.query(
            Product.id,
            Product.name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .outerjoin(OrderItem, OrderItem.product_id == Product.id)
        .outerjoin(Order, OrderItem.order_id == Order.id)
        .filter(Product.seller_id == seller_id)
        .group_by(Product.id)
        .order_by(desc("revenue"))
        .limit(5)
        .all()
    )

    low_inventory = (
        Product.query.filter(Product.seller_id == seller_id, Product.stock <= 5)
        .order_by(Product.stock.asc())
        .limit(5)
        .all()
    )

    return {
        "total_products": total_products,
        "featured_products": featured_products,
        "total_stock": int(total_stock),
        "total_orders": total_orders,
        "total_revenue": float(revenue),
        "open_orders": open_orders,
        "product_performance": product_performance,
        "low_inventory": low_inventory,
    }


def log_manual_order(
    seller: User,
    product_id: int,
    quantity: int,
    buyer_email: Optional[str] = None,
) -> Order:
    product = Product.query.filter_by(id=product_id, seller_id=seller.id).first()
    if not product:
        raise ProductValidationError("Invalid product selection.")
    if quantity <= 0:
        raise ProductValidationError("Quantity must be at least 1.")
    if product.stock < quantity:
        raise ProductValidationError("Insufficient stock for this order.")

    buyer = None
    if buyer_email:
        buyer = User.query.filter(func.lower(User.email) == buyer_email.lower()).first()

    order = Order(
        seller_id=seller.id,
        buyer_id=buyer.id if buyer else None,
        status="processing",
    )
    item = OrderItem(order=order, product_id=product.id, quantity=quantity, unit_price=product.price)
    db.session.add(order)
    db.session.add(item)
    db.session.flush()
    order.recompute_total()

    product.stock -= quantity
    txn = InventoryTransaction(product=product, change=-quantity, source="order", note=f"Manual order #{order.id}")
    db.session.add(txn)
    db.session.commit()
    return order


def update_order_status(order: Order, status: str):
    if status not in Order.STATUS_CHOICES:
        raise ProductValidationError("Invalid status.")
    order.status = status
    db.session.commit()


def recent_inventory_transactions(product_ids: Iterable[int]) -> List[InventoryTransaction]:
    if not product_ids:
        return []
    return (
        InventoryTransaction.query.filter(InventoryTransaction.product_id.in_(product_ids))
        .order_by(InventoryTransaction.created_at.desc())
        .limit(20)
        .all()
    )
