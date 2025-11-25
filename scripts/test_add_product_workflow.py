"""
Test script: simulate add-product 3-step workflow using testing config (SQLite in-memory).
Run: python scripts/test_add_product_workflow.py
"""
from project import create_app, db
from project.models import User, SellerProduct

app = create_app('testing')

with app.app_context():
    # ensure schema exists in the in-memory DB
    db.create_all()

    # create seller user
    seller = User(email='test_seller@example.com', username='test_seller', role='seller')
    db.session.add(seller)
    db.session.commit()

    client = app.test_client()

    # simulate logged-in seller
    with client.session_transaction() as sess:
        sess['_user_id'] = str(seller.id)
        sess['_fresh'] = True

    # Step 1
    r1 = client.post('/seller/add_product', data={
        'productName': 'Scripted Test Product',
        'price': '250.00',
        'discountPercentage': '20',
        'discountType': 'percentage',
        'voucherType': 'none',
        'category': 'accessories',
        'subcategory': 'Bags',
        'subitem': ['Handbags'],
        'primaryImage': '/static/image/test_main.jpg',
        'secondaryImage': '/static/image/test_secondary.jpg'
    }, follow_redirects=True)
    print('Step1:', r1.status_code)

    # Step 2
    r2 = client.post('/seller/add_product_description', data={
        'description': 'Scripted description',
        'materials': 'Faux leather',
        'detailsFit': 'One size',
        'sizeGuide[]': ['/static/image/size-guide.png'],
        'certifications[]': ['/static/image/cert.png']
    }, follow_redirects=True)
    print('Step2:', r2.status_code)

    # Step 3
    r3 = client.post('/seller/add_product_stocks', data={
        'sku_1': 'BAG-TEST-001',
        'color_1': 'Black',
        'color_picker_1': '#000000',
        'size_1': 'OneSize',
        'stock_1': '5',
        'lowStock_1': '1',
    }, follow_redirects=True)
    print('Step3:', r3.status_code)

    # Preview GET
    rp_get = client.get('/seller/add_product_preview')
    print('Preview GET:', rp_get.status_code)

    # Preview POST -> save
    rp_post = client.post('/seller/add_product_preview', data={'lowStockThreshold': '1'}, follow_redirects=True)
    print('Preview POST:', rp_post.status_code)

    # verify insertion
    products = SellerProduct.query.filter_by(seller_id=seller.id).all()
    print('Inserted count:', len(products))
    if products:
        p = products[0]
        print('Name:', p.name)
        print('Category:', p.category)
        print('Price:', float(p.price))
        print('Total stock:', p.total_stock)
        print('Variants:', p.variants)
        print('Attributes:', p.attributes)

    # Test details endpoint
    if products:
        pid = products[0].id
        rdet = client.get(f'/seller/product/{pid}/details')
        print('Details endpoint status:', rdet.status_code)
        print('Details JSON:', rdet.get_json())
