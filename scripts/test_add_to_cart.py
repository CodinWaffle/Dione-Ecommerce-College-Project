"""Quick test runner to POST to /add-to-cart using the Flask test client.
It inspects the DB for a sample product/variant and posts a payload, printing
response JSON and cart item counts before/after.
"""
from project import create_app, db
import json

app = create_app('development')

with app.app_context():
    from project.models import SellerProduct, ProductVariant, VariantSize, CartItem

    def find_sample_payload():
        # Try normalized variant tables first
        try:
            variant = ProductVariant.query.first()
            if variant:
                size = VariantSize.query.filter_by(variant_id=variant.id).first()
                prod_id = variant.product_id or (variant.product.id if variant.product else None)
                if prod_id and size:
                    return {
                        'product_id': prod_id,
                        'variant_id': variant.id,
                        'size_id': size.id,
                        'quantity': 1
                    }
        except Exception as e:
            print('Variant table lookup failed:', e)

        # Fallback to SellerProduct with JSON variants
        prod = SellerProduct.query.filter_by(is_draft=False).first() or SellerProduct.query.first()
        if not prod:
            return None
        variants = prod.variants
        if isinstance(variants, str):
            try:
                variants = json.loads(variants)
            except Exception:
                variants = None
        if isinstance(variants, dict):
            # pick first key
            for k,v in variants.items():
                # try sizes
                size_list = v.get('sizeStocks') or v.get('sizes') or v.get('sizes_list') or []
                if isinstance(size_list, list) and size_list:
                    first_size = size_list[0]
                    size_label = first_size.get('size') or first_size.get('label') or first_size.get('name')
                    return {
                        'product_id': prod.id,
                        'color': k,
                        'size': size_label,
                        'quantity': 1
                    }
        elif isinstance(variants, list) and variants:
            v = variants[0]
            color = v.get('color') or v.get('name') or v.get('variant_name')
            size_list = v.get('sizeStocks') or v.get('sizes') or []
            if size_list and isinstance(size_list, list):
                first_size = size_list[0]
                size_label = first_size.get('size') or first_size.get('label') or first_size.get('name')
                return {
                    'product_id': prod.id,
                    'color': color,
                    'size': size_label,
                    'quantity': 1
                }
        # As a last resort, just send product_id + dummy color/size
        return {'product_id': prod.id, 'color': 'Default', 'size': 'M', 'quantity': 1}

    payload = find_sample_payload()
    if not payload:
        print('No product found in DB to test add-to-cart')
        raise SystemExit(1)

    print('Test payload:', payload)

    client = app.test_client()
    before_count = CartItem.query.count()
    resp = client.post('/add-to-cart', json=payload)
    after_count = CartItem.query.count()

    print('Status code:', resp.status_code)
    try:
        print('Response JSON:', resp.get_json())
    except Exception:
        print('Response text:', resp.get_data(as_text=True))

    print('Cart count before:', before_count, 'after:', after_count)
