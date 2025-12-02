import os
import json
from datetime import datetime
from . import db
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask import current_app
import jwt
from time import time

def _normalize_image_path(path):
    """Normalize stored image path into a usable URL for the frontend.

    If `path` is an absolute URL or already starts with `/`, return as-is.
    Otherwise prefix with `/static/` so static files under `static/` are reachable.
    """
    if not path:
        return None
    s = str(path)
    if s.startswith('/') or s.startswith('http'):
        return s
    return '/static/' + s.lstrip('/')

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=False)  # Primary identifier for login
  password = db.Column(db.String(255))
  username = db.Column(db.String(150))

  role = db.Column(db.String(20), nullable=False, default='buyer')

  role_requested = db.Column(db.String(20))
  is_approved = db.Column(db.Boolean, nullable=False, default=True)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  is_suspended = db.Column(db.Boolean, nullable=False, default=False)


  oauth = db.relationship('OAuth', back_populates='user')

  def __repr__(self):
      return 'User {}'.format(self.email)

  def get_reset_token(self, expires=300):
    """Generate password reset token that expires in 5 minutes (300 seconds) by default."""
    return jwt.encode(
      {'reset_password': self.email, 'exp': time() + expires},
      current_app.config.get('SECRET_KEY', 'random_key'), algorithm='HS256')

  @staticmethod
  def verify_reset_token(token):
    try:

      if isinstance(token, bytes):
        token = token.decode('utf-8')
      email = jwt.decode(token, current_app.config.get('SECRET_KEY', 'random_key'),
                              algorithms=['HS256'])['reset_password']
    except:
      return
    return User.query.filter_by(email = email).first()

  @staticmethod
  def verify_email(email):
    user = User.query.filter_by(email = email).first()
    return user


class OAuth(OAuthConsumerMixin, db.Model):
  __tablename__ = 'oauth'
  __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
  provider = db.Column(db.String(50), nullable=False)
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  token = db.Column(db.Text)
  provider_user_id = db.Column(db.String(256), nullable=False)
  provider_user_login = db.Column(db.String(256))
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  user = db.relationship('User', back_populates='oauth')

  @property
  def token_dict(self):
    """Get token as dictionary"""
    if self.token:
      try:
        return json.loads(self.token)
      except (json.JSONDecodeError, TypeError):
        return {"access_token": self.token}
    return {}

  @token_dict.setter
  def token_dict(self, value):
    """Set token from dictionary"""
    if isinstance(value, dict):
      self.token = json.dumps(value)
    elif isinstance(value, str):
      self.token = value
    else:
      self.token = str(value)


class Buyer(db.Model):
  """Buyer profile data"""
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, unique=True)
  phone = db.Column(db.String(20))
  address = db.Column(db.Text)
  city = db.Column(db.String(100))
  zip_code = db.Column(db.String(20))
  country = db.Column(db.String(100))
  preferred_language = db.Column(db.String(50), default='English')
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  user = db.relationship('User', backref='buyer_profile')

  def __repr__(self):
    return f'<Buyer {self.user_id}>'


class Seller(db.Model):
  """Seller profile data"""
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, unique=True)
  business_name = db.Column(db.String(255), nullable=False)
  business_type = db.Column(db.String(100))
  business_address = db.Column(db.Text)
  business_city = db.Column(db.String(100))
  business_zip = db.Column(db.String(20))
  business_country = db.Column(db.String(100))
  bank_type = db.Column(db.String(50))
  bank_name = db.Column(db.String(255))
  bank_account = db.Column(db.String(100))
  bank_holder_name = db.Column(db.String(255))
  tax_id = db.Column(db.String(50))
  store_description = db.Column(db.Text)
  is_verified = db.Column(db.Boolean, nullable=False, default=False)
  
  # Statistics fields
  rating_count = db.Column(db.Integer, default=0)
  products_count = db.Column(db.Integer, default=0)
  followers_count = db.Column(db.Integer, default=0)
  total_sales = db.Column(db.Integer, default=0)
  last_active = db.Column(db.DateTime, default=datetime.utcnow)
  
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  user = db.relationship('User', backref='seller_profile')

  def __repr__(self):
    return f'<Seller {self.user_id}>'


class Rider(db.Model):
  """Rider profile data"""
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, unique=True)
  phone = db.Column(db.String(20), nullable=False)
  license_number = db.Column(db.String(50))
  vehicle_type = db.Column(db.String(50))
  vehicle_number = db.Column(db.String(50))
  availability_status = db.Column(db.String(20), default='available')
  current_location = db.Column(db.String(255))
  delivery_zones = db.Column(db.Text)
  is_verified = db.Column(db.Boolean, nullable=False, default=False)
  verification_date = db.Column(db.DateTime)
  rating = db.Column(db.Float, default=0.0)
  total_deliveries = db.Column(db.Integer, default=0)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  user = db.relationship('User', backref='rider_profile')

  def __repr__(self):
    return f'<Rider {self.user_id}>'


class SiteSetting(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.String(64), unique=True, nullable=False)
  value = db.Column(db.Text, nullable=False, default='')
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  def __repr__(self):
    return f"<SiteSetting {self.key}={self.value}>"


class Product(db.Model):
  """Product listings created by sellers"""
  id = db.Column(db.Integer, primary_key=True)
  seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  name = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text, default='')
  category = db.Column(db.String(50), nullable=False)
  subcategory = db.Column(db.String(50))
  price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
  compare_at_price = db.Column(db.Numeric(10, 2))
  stock = db.Column(db.Integer, nullable=False, default=0)
  sku = db.Column(db.String(100))
  barcode = db.Column(db.String(100))
  status = db.Column(db.String(20), nullable=False, default='draft')
  discount_type = db.Column(db.String(20))
  discount_value = db.Column(db.Numeric(6, 2))
  voucher_type = db.Column(db.String(50))
  materials = db.Column(db.Text)
  details_fit = db.Column(db.Text)
  model_height = db.Column(db.String(50))
  wearing_size = db.Column(db.String(50))
  allow_backorder = db.Column(db.Boolean, default=False)
  track_inventory = db.Column(db.Boolean, default=True)
  low_stock_threshold = db.Column(db.Integer, default=0)
  attributes = db.Column(db.JSON, default=dict)
  image = db.Column(db.String(512))
  secondary_image = db.Column(db.String(512))
  tags = db.Column(db.Text)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  seller = db.relationship('User', backref=db.backref('products', lazy=True))

  def sync_status(self):
    """Update status to reflect current inventory."""
    current_status = (self.status or 'draft').lower()
    if self.stock <= 0:
      self.status = 'out-of-stock'
    elif current_status in ('out-of-stock', 'draft'):
      self.status = 'active'
    elif current_status not in ('active', 'inactive'):
      self.status = 'active'

  def to_dashboard_dict(self):
    """Return lightweight dictionary for seller dashboard tables."""
    compare = float(self.compare_at_price or 0)
    price = float(self.price or 0)
    return {
      'id': self.id,
      'name': self.name,
      'category': self.category,
      'subcategory': self.subcategory,
      'price': price,
      'compare_at_price': compare if compare > 0 else None,
      'stock': self.stock,
      'status': self.status,
      'sku': self.sku,
      'image': self.image,
    }

  def to_public_dict(self):
    """Return product data for buyer-facing pages."""
    price = float(self.price or 0)
    compare_price = float(self.compare_at_price or 0)
    return {
      'id': self.id,
      'name': self.name,
      'primaryImage': _normalize_image_path(self.image) or '/static/image/banner.png',
      'secondaryImage': _normalize_image_path(self.secondary_image) or _normalize_image_path(self.image) or '/static/image/banner.png',
      'material': (self.materials or 'Premium Fabric').split('\n')[0],
      'price': price,
      'originalPrice': compare_price if compare_price > price else None,
      'category': self.category,
      'subcategory': self.subcategory,
      'colors': [],
      'variants': [],
    }

  def __repr__(self):
    return f'<Product {self.id} - {self.name}>'


class SellerProduct(db.Model):
  """Model for storing seller products with complete details"""
  __tablename__ = 'seller_product_management'

  id = db.Column(db.Integer, primary_key=True)

  # reference to user table (seller)
  seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, index=True)

  # Basic Information
  name = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text)
  category = db.Column(db.String(100), nullable=False, index=True)
  subcategory = db.Column(db.String(100))

  # Pricing
  price = db.Column(db.Numeric(10, 2), nullable=False)
  compare_at_price = db.Column(db.Numeric(10, 2))
  discount_type = db.Column(db.String(50))
  discount_value = db.Column(db.Numeric(10, 2))
  voucher_type = db.Column(db.String(50))

  # Product Details
  materials = db.Column(db.Text)
  details_fit = db.Column(db.Text)

  # Images
  primary_image = db.Column(db.String(500))
  secondary_image = db.Column(db.String(500))

  # Inventory
  total_stock = db.Column(db.Integer, default=0)
  low_stock_threshold = db.Column(db.Integer, default=5)
  base_sku = db.Column(db.String(255))

  # JSON fields for complex data
  variants = db.Column(db.JSON)
  attributes = db.Column(db.JSON)
  draft_data = db.Column(db.JSON)

  # Status & Timestamps
  status = db.Column(db.String(20), default='draft')
  is_draft = db.Column(db.Boolean, default=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  # Relationships
  product_variants = db.relationship('ProductVariant', backref='product', cascade='all, delete-orphan')
  product_description = db.relationship('ProductDescription', backref='product', uselist=False, cascade='all, delete-orphan')

  def __repr__(self):
    return f'<SellerProduct {self.name}>'

  def to_dict(self):
    """Convert to dictionary for API responses"""
    return {
      'id': self.id,
      'name': self.name,
      'subcategory': self.subcategory,
      'category': self.category,
      'price': float(self.price) if self.price else 0,
      'total_stock': self.total_stock,
      'primary_image': (self.primary_image if (self.primary_image and (str(self.primary_image).startswith('/') or str(self.primary_image).startswith('http'))) else (('/static/' + str(self.primary_image).lstrip('/')) if self.primary_image else None)),
      'secondary_image': (self.secondary_image if (self.secondary_image and (str(self.secondary_image).startswith('/') or str(self.secondary_image).startswith('http'))) else (('/static/' + str(self.secondary_image).lstrip('/')) if self.secondary_image else None)),
      'status': self.status,
      'is_draft': self.is_draft,
      'base_sku': self.base_sku,
      'variants': self.variants if self.variants is not None else [],
      'attributes': self.attributes if self.attributes is not None else {},
      'description': self.description,
      'materials': self.materials,
      'details_fit': self.details_fit,
      'discount_type': self.discount_type,
      'discount_value': float(self.discount_value) if self.discount_value else None,
      'voucher_type': self.voucher_type,
      'compare_at_price': float(self.compare_at_price) if self.compare_at_price else None,
      'low_stock_threshold': self.low_stock_threshold,
      'created_at': self.created_at.isoformat() if self.created_at else None,
    }

  def commit_draft(self):
    """Convert draft product to active product"""
    self.is_draft = False
    self.status = 'active'
    return self


class CartItem(db.Model):
  """Persistent cart item storage for both authenticated and guest buyers."""
  __tablename__ = 'cart_items'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
  session_id = db.Column(db.String(255), index=True)
  product_id = db.Column(db.Integer, nullable=False, index=True)
  product_name = db.Column(db.String(255), nullable=False)
  product_price = db.Column(db.Numeric(10, 2), nullable=False)
  color = db.Column(db.String(100))
  size = db.Column(db.String(50))
  quantity = db.Column(db.Integer, nullable=False, default=1)
  variant_image = db.Column(db.String(500))
  seller_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  user = db.relationship('User', foreign_keys=[user_id], backref='cart_items')
  seller = db.relationship('User', foreign_keys=[seller_id])

  __table_args__ = (
    db.CheckConstraint('quantity > 0', name='cart_items_quantity_positive'),
    db.CheckConstraint('product_price >= 0', name='cart_items_price_positive'),
    db.UniqueConstraint('user_id', 'session_id', 'product_id', 'color', 'size', name='uniq_cart_item'),
  )

  def __repr__(self):
    return f'<CartItem {self.product_name} x{self.quantity}>'

  def to_dict(self):
    return {
      'id': self.id,
      'product_id': self.product_id,
      'product_name': self.product_name,
      'product_price': float(self.product_price or 0),
      'color': self.color,
      'size': self.size,
      'quantity': self.quantity,
      'variant_image': self.variant_image,
      'seller_id': self.seller_id,
      'user_id': self.user_id,
      'session_id': self.session_id,
      'created_at': self.created_at.isoformat() if self.created_at else None,
      'updated_at': self.updated_at.isoformat() if self.updated_at else None,
    }


class Warning(db.Model):
  """Records warning emails sent to users by admins."""
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  admin_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
  template_key = db.Column(db.String(100))
  subject = db.Column(db.String(255))
  body = db.Column(db.Text)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  user = db.relationship('User', foreign_keys=[user_id], backref='warnings')
  admin = db.relationship('User', foreign_keys=[admin_id])

  def __repr__(self):
    return f'<Warning {self.id} to {self.user_id}>'


class ChatMessage(db.Model):
  """Simple chat messages between users and admin."""
  __tablename__ = 'chat_messages'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  admin_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
  sender_name = db.Column(db.String(255))
  sender_role = db.Column(db.String(50))
  body = db.Column(db.Text, nullable=False)
  # Optional filename/path for an uploaded attachment (images, files)
  attachment = db.Column(db.String(512), nullable=True)
  is_from_admin = db.Column(db.Boolean, default=False)
  is_read = db.Column(db.Boolean, nullable=False, default=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  user = db.relationship('User', foreign_keys=[user_id], backref='chat_messages')
  admin = db.relationship('User', foreign_keys=[admin_id])

  def __repr__(self):
    return f'<ChatMessage {self.id} user={self.user_id} admin={self.admin_id}>'


class ProductVariant(db.Model):
  """Product variants with multiple sizes support"""
  __tablename__ = 'product_variants'
  
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(
    db.Integer,
    db.ForeignKey('seller_product_management.id', ondelete='CASCADE'),
    nullable=False
  )
  variant_name = db.Column(db.String(255), nullable=False)  # e.g., "Black", "Red"
  variant_sku = db.Column(db.String(255))
  images_json = db.Column(db.JSON)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  # Relationship to sizes
  sizes = db.relationship('VariantSize', backref='variant', cascade='all, delete-orphan')
  
  def __repr__(self):
    return f'<ProductVariant {self.variant_name}>'


class VariantSize(db.Model):
  """Individual size entries for each variant"""
  __tablename__ = 'variant_sizes'
  
  id = db.Column(db.Integer, primary_key=True)
  variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
  size_label = db.Column(db.String(50), nullable=False)  # e.g., "S", "M", "L"
  stock_quantity = db.Column(db.Integer, default=0)
  sku = db.Column(db.String(255))  # Optional individual SKU
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  def __repr__(self):
    return f'<VariantSize {self.size_label}: {self.stock_quantity}>'


class ProductDescription(db.Model):
  """Extended product description and metadata"""
  __tablename__ = 'product_descriptions'
  
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(
    db.Integer,
    db.ForeignKey('seller_product_management.id', ondelete='CASCADE'),
    nullable=False
  )
  description_text = db.Column(db.Text)
  materials = db.Column(db.Text)
  care_instructions = db.Column(db.Text)
  details_fit = db.Column(db.Text)
  meta_json = db.Column(db.JSON)  # For certifications, size guides, etc.
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  def __repr__(self):
    return f'<ProductDescription {self.product_id}>'


class Order(db.Model):
  """Customer orders"""
  __tablename__ = 'orders'
  
  id = db.Column(db.Integer, primary_key=True)
  order_number = db.Column(db.String(50), unique=True, nullable=False)
  buyer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  
  # Order details
  total_amount = db.Column(db.Numeric(10, 2), nullable=False)
  shipping_fee = db.Column(db.Numeric(10, 2), default=0)
  tax_amount = db.Column(db.Numeric(10, 2), default=0)
  discount_amount = db.Column(db.Numeric(10, 2), default=0)
  
  # Status and tracking
  status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipping, in_transit, delivered, cancelled
  payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
  tracking_number = db.Column(db.String(100))
  
  # Addresses
  shipping_address = db.Column(db.JSON)
  billing_address = db.Column(db.JSON)
  
  # Timestamps
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  shipped_at = db.Column(db.DateTime)
  delivered_at = db.Column(db.DateTime)
  
  # Relationships
  buyer = db.relationship('User', foreign_keys=[buyer_id], backref='orders_as_buyer')
  seller = db.relationship('User', foreign_keys=[seller_id], backref='orders_as_seller')
  order_items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
  
  def __repr__(self):
    return f'<Order {self.order_number}>'
  
  def to_dict(self):
    return {
      'id': self.id,
      'order_number': self.order_number,
      'total_amount': float(self.total_amount),
      'status': self.status,
      'payment_status': self.payment_status,
      'tracking_number': self.tracking_number,
      'created_at': self.created_at.isoformat() if self.created_at else None,
      'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
      'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
    }


class OrderItem(db.Model):
  """Individual items in an order"""
  __tablename__ = 'order_items'
  
  id = db.Column(db.Integer, primary_key=True)
  order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
  product_id = db.Column(
    db.Integer,
    db.ForeignKey('seller_product_management.id', ondelete='CASCADE'),
    nullable=False
  )
  
  # Item details
  product_name = db.Column(db.String(255), nullable=False)
  product_image = db.Column(db.String(500))
  variant_name = db.Column(db.String(100))  # e.g., "Black - Size M"
  size = db.Column(db.String(50))
  color = db.Column(db.String(50))
  
  # Pricing and quantity
  quantity = db.Column(db.Integer, nullable=False)
  unit_price = db.Column(db.Numeric(10, 2), nullable=False)
  total_price = db.Column(db.Numeric(10, 2), nullable=False)
  
  # Review status
  is_reviewed = db.Column(db.Boolean, default=False)
  
  # Relationships
  product = db.relationship('SellerProduct', backref='order_items')
  reviews = db.relationship('ProductReview', backref='order_item', cascade='all, delete-orphan')
  
  def __repr__(self):
    return f'<OrderItem {self.product_name} x{self.quantity}>'


class ProductReview(db.Model):
  """Product reviews by customers"""
  __tablename__ = 'product_reviews'
  
  id = db.Column(db.Integer, primary_key=True)
  order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('seller_product_management.id'), nullable=False)
  buyer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  
  # Review content
  rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
  title = db.Column(db.String(200))
  comment = db.Column(db.Text)
  
  # Review images
  images = db.Column(db.JSON)  # Array of image URLs
  
  # Timestamps
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  # Relationships
  buyer = db.relationship('User', backref='reviews')
  product = db.relationship('SellerProduct', backref='reviews')
  
  def __repr__(self):
    return f'<ProductReview {self.rating} stars>'


class ProductReport(db.Model):
  """Product reports/flags submitted by users or anonymous visitors."""
  __tablename__ = 'product_reports'
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(db.Integer, nullable=False, index=True)
  reporter_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
  reason = db.Column(db.String(100), nullable=False)
  details = db.Column(db.Text)
  resolved = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  reporter = db.relationship('User', foreign_keys=[reporter_id])

  def __repr__(self):
    return f'<ProductReport {self.id} product={self.product_id} reason={self.reason}>'


class StoreFollower(db.Model):
  """Store followers tracking"""
  __tablename__ = 'store_followers'
  id = db.Column(db.Integer, primary_key=True)
  follower_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  store_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
  followed_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  # Relationships
  follower = db.relationship('User', foreign_keys=[follower_id], backref='following_stores')
  store = db.relationship('User', foreign_keys=[store_id], backref='followers')
  
  # Unique constraint
  __table_args__ = (db.UniqueConstraint('follower_id', 'store_id', name='unique_follower_store'),)
  
  def __repr__(self):
    return f'<StoreFollower follower={self.follower_id} store={self.store_id}>'


