"""
Buyer Routes - My Purchases and Order Management
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import uuid

from project import db
from project.models import Order, OrderItem, ProductReview, SellerProduct, User

buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')

@buyer_bp.before_request
@login_required
def restrict_to_buyers():
    """Ensure only buyers can access buyer routes"""
    if not current_user.is_authenticated:
        flash("Please log in to access your purchases.", 'warning')
        return redirect(url_for('auth.login'))


@buyer_bp.route('/my-purchases')
def my_purchases():
    """My Purchases page with all order statuses"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Base query for user's orders
    orders_query = Order.query.filter_by(buyer_id=current_user.id)
    
    # Apply status filter
    if status_filter != 'all':
        orders_query = orders_query.filter_by(status=status_filter)
    
    # Order by most recent first
    orders_query = orders_query.order_by(desc(Order.created_at))
    
    # Paginate results
    pagination = orders_query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    # Get order counts for each status
    status_counts = {
        'all': Order.query.filter_by(buyer_id=current_user.id).count(),
        'pending': Order.query.filter_by(buyer_id=current_user.id, status='pending').count(),
        'confirmed': Order.query.filter_by(buyer_id=current_user.id, status='confirmed').count(),
        'shipping': Order.query.filter_by(buyer_id=current_user.id, status='shipping').count(),
        'in_transit': Order.query.filter_by(buyer_id=current_user.id, status='in_transit').count(),
        'delivered': Order.query.filter_by(buyer_id=current_user.id, status='delivered').count(),
        'to_review': Order.query.join(OrderItem).filter(
            Order.buyer_id == current_user.id,
            Order.status == 'delivered',
            OrderItem.is_reviewed == False
        ).count()
    }
    
    return render_template(
        'buyer/my_purchases.html',
        orders=orders,
        pagination=pagination,
        status_filter=status_filter,
        status_counts=status_counts
    )


@buyer_bp.route('/order/<int:order_id>')
def order_details(order_id):
    """Order details page"""
    order = Order.query.filter_by(
        id=order_id,
        buyer_id=current_user.id
    ).first_or_404()
    
    return render_template('buyer/order_details.html', order=order)


@buyer_bp.route('/order/<int:order_id>/track')
def track_order(order_id):
    """Order tracking page"""
    order = Order.query.filter_by(
        id=order_id,
        buyer_id=current_user.id
    ).first_or_404()
    
    # Create tracking timeline
    timeline = []
    
    # Order placed
    timeline.append({
        'status': 'Order Placed',
        'date': order.created_at,
        'completed': True,
        'icon': 'ri-shopping-cart-line'
    })
    
    # Order confirmed
    if order.status in ['confirmed', 'shipping', 'in_transit', 'delivered']:
        timeline.append({
            'status': 'Order Confirmed',
            'date': order.created_at + timedelta(hours=1),  # Mock data
            'completed': True,
            'icon': 'ri-check-line'
        })
    
    # Shipping
    if order.status in ['shipping', 'in_transit', 'delivered']:
        timeline.append({
            'status': 'Shipped',
            'date': order.shipped_at or (order.created_at + timedelta(days=1)),
            'completed': True,
            'icon': 'ri-truck-line'
        })
    
    # In transit
    if order.status in ['in_transit', 'delivered']:
        timeline.append({
            'status': 'In Transit',
            'date': order.shipped_at + timedelta(days=1) if order.shipped_at else (order.created_at + timedelta(days=2)),
            'completed': True,
            'icon': 'ri-map-pin-line'
        })
    
    # Delivered
    if order.status == 'delivered':
        timeline.append({
            'status': 'Delivered',
            'date': order.delivered_at or (order.created_at + timedelta(days=3)),
            'completed': True,
            'icon': 'ri-home-line'
        })
    
    return render_template('buyer/order_tracking.html', order=order, timeline=timeline)


@buyer_bp.route('/review/write/<int:order_item_id>', methods=['GET', 'POST'])
def write_review(order_item_id):
    """Write a product review"""
    order_item = OrderItem.query.join(Order).filter(
        OrderItem.id == order_item_id,
        Order.buyer_id == current_user.id,
        Order.status == 'delivered'
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create review
            review = ProductReview(
                order_item_id=order_item_id,
                product_id=order_item.product_id,
                buyer_id=current_user.id,
                rating=data.get('rating'),
                title=data.get('title', ''),
                comment=data.get('comment', ''),
                images=data.get('images', [])
            )
            
            # Mark order item as reviewed
            order_item.is_reviewed = True
            
            db.session.add(review)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Review submitted successfully!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('buyer/write_review.html', order_item=order_item)


@buyer_bp.route('/reviews')
def my_reviews():
    """My reviews page"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews_query = ProductReview.query.filter_by(buyer_id=current_user.id).order_by(desc(ProductReview.created_at))
    pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
    reviews = pagination.items
    
    return render_template('buyer/my_reviews.html', reviews=reviews, pagination=pagination)


# Sample data creation route (for testing)
@buyer_bp.route('/create-sample-orders')
def create_sample_orders():
    """Create sample orders for testing (remove in production)"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:
        # Create sample orders with different statuses
        statuses = ['pending', 'confirmed', 'shipping', 'in_transit', 'delivered']
        
        for i, status in enumerate(statuses):
            order = Order(
                order_number=f'ORD-{uuid.uuid4().hex[:8].upper()}',
                buyer_id=current_user.id,
                seller_id=1,  # Assuming seller with ID 1 exists
                total_amount=99.99 + (i * 25),
                shipping_fee=15.00,
                status=status,
                payment_status='paid' if status != 'pending' else 'pending',
                tracking_number=f'TRK{uuid.uuid4().hex[:10].upper()}' if status in ['shipping', 'in_transit', 'delivered'] else None,
                shipping_address={
                    'name': current_user.username,
                    'address': '123 Sample Street',
                    'city': 'Sample City',
                    'zip': '12345',
                    'country': 'Philippines'
                },
                created_at=datetime.utcnow() - timedelta(days=i),
                shipped_at=datetime.utcnow() - timedelta(days=max(0, i-1)) if status in ['shipping', 'in_transit', 'delivered'] else None,
                delivered_at=datetime.utcnow() - timedelta(days=max(0, i-3)) if status == 'delivered' else None
            )
            
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Add sample order items
            for j in range(1, 3):  # 2 items per order
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=1,  # Assuming product with ID 1 exists
                    product_name=f'Sample Product {j}',
                    product_image='/static/image/banner.png',
                    variant_name=f'Color {j} - Size M',
                    size='M',
                    color=f'Color {j}',
                    quantity=1,
                    unit_price=49.99 + (j * 10),
                    total_price=49.99 + (j * 10),
                    is_reviewed=False
                )
                db.session.add(order_item)
        
        db.session.commit()
        flash('Sample orders created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating sample orders: {str(e)}', 'error')
    
    return redirect(url_for('buyer.my_purchases'))