#!/usr/bin/env python3
"""
Simple diagnostic: list ProductVariant and VariantSize table contents
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from project import create_app, db
from project.models import ProductVariant, VariantSize, SellerProduct

app = create_app()
with app.app_context():
    try:
        print("ProductVariant count:", ProductVariant.query.count())
        print("VariantSize count:", VariantSize.query.count())

        variants = ProductVariant.query.order_by(ProductVariant.id).limit(10).all()
        for v in variants:
            print(f"Variant {v.id}: product_id={v.product_id} name={v.variant_name} images={v.images_json}")
            sizes = VariantSize.query.filter_by(variant_id=v.id).all()
            for s in sizes:
                print(f"  Size {s.id}: label={s.size_label} stock={s.stock_quantity} sku={s.sku}")
    except Exception as e:
        print("ORM query failed:", e)
        print("Falling back to raw SQL to inspect table columns")
        from sqlalchemy import text
        try:
            res = db.session.execute(text("SHOW COLUMNS FROM product_variants")).all()
            print("product_variants columns:")
            for r in res:
                print(" ", r)
        except Exception as e2:
            print("Failed to show product_variants columns:", e2)

        try:
            res2 = db.session.execute(text("SHOW COLUMNS FROM variant_sizes")).all()
            print("variant_sizes columns:")
            for r in res2:
                print(" ", r)
        except Exception as e3:
            print("Failed to show variant_sizes columns:", e3)

    # Also show any products that have variants JSON
    sp = SellerProduct.query.limit(5).all()
    for p in sp:
        print(f"SellerProduct {p.id} name={p.name} total_stock={p.total_stock} variants_type={type(p.variants)} variants_summary={(p.variants and len(p.variants)) if p.variants else 0}")

print('Done')
