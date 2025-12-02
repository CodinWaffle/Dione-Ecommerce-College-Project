@main.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """Create orders from the current user's cart items."""
    from project.models import CartItem, Order, OrderItem, SellerProduct, ProductVariant, VariantSize
    from project import db

    try:
        user = current_user
        if not user or not user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        # Get form data (shipping and payment information)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"DEBUG: Received order data: {data}")  # Debug log
        
        # Extract shipping information
        shipping_info = {
            'first_name': data.get('firstName', ''),
            'last_name': data.get('lastName', ''),
            'email': data.get('email', ''),
            'address': data.get('address', ''),
            'apartment': data.get('apartment', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'zip_code': data.get('zipCode', ''),
            'phone': data.get('phone', ''),
            'country': data.get('country', '')
        }
        
        # Extract payment information
        payment_info = {
            'method': data.get('paymentMethod', ''),
            'card_number': data.get('cardNumber', ''),
            'expiry': data.get('expiry', ''),
            'cvc': data.get('cvc', ''),
            'cardholder_name': data.get('cardholderName', ''),
            'gcash_number': data.get('gcashNumber', '')
        }

        # Fetch cart items for the user
        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        if not cart_items:
            return jsonify({'error': 'No items in cart'}), 400
        
        print(f"DEBUG: Found {len(cart_items)} cart items for user {user.id}")  # Debug log

        # Group by seller_id
        groups = {}
        for it in cart_items:
            groups.setdefault(it.seller_id, []).append(it)

        created_orders = []
        for seller_id, items in groups.items():
            try:
                print(f"DEBUG: Processing order for seller {seller_id} with {len(items)} items")
                order_number = f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{seller_id}"
                subtotal = 0
                for it in items:
                    subtotal += float(it.product_price or 0) * int(it.quantity or 1)

                delivery_fee = 0 if subtotal >= 1500 or subtotal == 0 else 150
                total_amount = subtotal + delivery_fee

                order = Order(
                    order_number=order_number,
                    buyer_id=user.id,
                    seller_id=seller_id,
                    total_amount=total_amount,
                    shipping_fee=delivery_fee,
                    tax_amount=0,
                    discount_amount=0,
                    status='pending',
                    payment_status='pending' if payment_info['method'] == 'cod' else 'paid',
                    shipping_address={
                        'first_name': shipping_info['first_name'],
                        'last_name': shipping_info['last_name'],
                        'email': shipping_info['email'],
                        'address': shipping_info['address'],
                        'apartment': shipping_info['apartment'],
                        'city': shipping_info['city'],
                        'state': shipping_info['state'],
                        'zip_code': shipping_info['zip_code'],
                        'phone': shipping_info['phone'],
                        'country': shipping_info['country']
                    },
                    billing_address={
                        'payment_method': payment_info['method'],
                        'card_number_last4': payment_info['card_number'][-4:] if payment_info['card_number'] else '',
                        'cardholder_name': payment_info['cardholder_name'],
                        'gcash_number': payment_info['gcash_number'],
                        'payment_status': 'processed'
                    }
                )
                db.session.add(order)
                db.session.flush()

                # Create OrderItems and adjust stock
                for it in items:
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=it.product_id,
                        product_name=it.product_name,
                        product_image=it.variant_image,
                        variant_name=f"{it.color} · {it.size}",
                        size=it.size,
                        color=it.color,
                        quantity=it.quantity,
                        unit_price=it.product_price,
                        total_price=(float(it.product_price or 0) * int(it.quantity or 1))
                    )
                    db.session.add(oi)

                    # Try to decrement VariantSize if it exists
                    try:
                        pv = ProductVariant.query.filter_by(product_id=it.product_id, variant_name=it.color).first()
                        if pv:
                            vs = VariantSize.query.filter_by(variant_id=pv.id, size_label=it.size).first()
                            if vs:
                                vs.stock_quantity = max(0, (vs.stock_quantity or 0) - int(it.quantity or 0))
                                db.session.add(vs)
                    except Exception:
                        pass

                    # Update seller product total_stock if present
                    try:
                        sp = SellerProduct.query.get(it.product_id)
                        if sp and sp.total_stock is not None:
                            sp.total_stock = max(0, (sp.total_stock or 0) - int(it.quantity or 0))
                            db.session.add(sp)
                    except Exception:
                        pass

                # Commit order and remove cart items
                db.session.commit()
                created_orders.append(order_number)
                print(f"DEBUG: Successfully created order {order_number}")
                
                # Remove cart items for this seller
                for it in items:
                    try:
                        db.session.delete(it)
                    except Exception:
                        pass
                db.session.commit()
            
            except Exception as e:
                print(f"ERROR: Failed to create order for seller {seller_id}: {str(e)}")
                db.session.rollback()
                continue

        # Clear session cart cache
        session.pop('cart_items', None)
        latest_order_number = created_orders[0] if created_orders else f"DIO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        session['latest_order_number'] = latest_order_number
        session['latest_order_eta'] = '3-5 business days'

        return jsonify({'success': True, 'order_numbers': created_orders, 'order_number': latest_order_number})

    except Exception as e:
        print('Error placing order:', e)
        db.session.rollback()
        return jsonify({'error': 'Failed to place order'}), 500