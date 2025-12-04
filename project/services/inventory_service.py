"""Shared helpers for adjusting catalog inventory when orders progress."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from flask import current_app
from sqlalchemy.orm import joinedload

from project import db
from project.models import Order, OrderItem, ProductVariant, SellerProduct, VariantSize

INVENTORY_FLAG_KEY = "_inventory_deducted"
INVENTORY_FLAG_TS_KEY = "_inventory_deducted_at"


def _get_shipping_meta(order: Order) -> dict:
    source = order.shipping_address if isinstance(order.shipping_address, dict) else {}
    return dict(source)


def _has_inventory_flag(order: Order) -> bool:
    if not isinstance(order.shipping_address, dict):
        return False
    return bool(order.shipping_address.get(INVENTORY_FLAG_KEY))


def _set_inventory_flag(order: Order) -> None:
    metadata = _get_shipping_meta(order)
    metadata[INVENTORY_FLAG_KEY] = True
    metadata[INVENTORY_FLAG_TS_KEY] = datetime.utcnow().isoformat()
    order.shipping_address = metadata


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _deduct_variant_stock(item: OrderItem) -> bool:
    color_label = (item.color or "").strip()
    size_label = (item.size or "").strip()
    if not color_label or not size_label:
        return False

    pv = ProductVariant.query.filter_by(product_id=item.product_id, variant_name=color_label).first()
    if not pv:
        return False

    vs = VariantSize.query.filter_by(variant_id=pv.id, size_label=size_label).first()
    if not vs:
        return False

    quantity = _safe_int(item.quantity, 0)
    if quantity <= 0:
        return False

    new_stock = max(0, (vs.stock_quantity or 0) - quantity)
    if new_stock == vs.stock_quantity:
        return False

    vs.stock_quantity = new_stock
    db.session.add(vs)
    return True


def _deduct_product_stock(item: OrderItem) -> bool:
    product = SellerProduct.query.get(item.product_id)
    if not product:
        return False

    quantity = _safe_int(item.quantity, 0)
    if quantity <= 0:
        return False

    current_stock = product.total_stock or 0
    new_stock = max(0, current_stock - quantity)
    if new_stock == current_stock:
        return False

    product.total_stock = new_stock
    try:
        product.sync_status()
    except Exception:
        current_app.logger.exception("Failed to sync product status for %s", product.id)
    db.session.add(product)
    return True


def ensure_order_inventory_deducted(order: Order, logger=None) -> bool:
    """Deduct catalog inventory for the provided order if it has not been processed yet."""
    if not order:
        return False

    if _has_inventory_flag(order):
        return False

    db.session.flush()
    order_items: Iterable[OrderItem] = list(getattr(order, "order_items", []) or [])
    if not order_items:
        order_items = (
            OrderItem.query.options(joinedload(OrderItem.product))
            .filter_by(order_id=order.id)
            .all()
        )

    if not order_items:
        return False

    any_changes = False
    for item in order_items:
        try:
            variant_changed = _deduct_variant_stock(item)
        except Exception:
            (logger or current_app.logger).exception(
                "Failed to decrease VariantSize for order %s item %s",
                order.id,
                item.id,
            )
            variant_changed = False

        try:
            product_changed = _deduct_product_stock(item)
        except Exception:
            (logger or current_app.logger).exception(
                "Failed to decrease SellerProduct stock for order %s item %s",
                order.id,
                item.id,
            )
            product_changed = False

        if variant_changed or product_changed:
            any_changes = True

    if any_changes:
        _set_inventory_flag(order)
        order.updated_at = datetime.utcnow()
        db.session.add(order)

    return any_changes
