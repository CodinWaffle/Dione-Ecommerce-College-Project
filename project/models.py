import os
import json
from . import db
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask import current_app
import jwt
from time import time

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=True)  # Allow NULL for OAuth users
  password = db.Column(db.String(255))
  username = db.Column(db.String(150))
  role_request_details = db.Column(db.Text)  # Stores JSON details for pending role applications

  role = db.Column(db.String(20), nullable=False, default='buyer')

  role_requested = db.Column(db.String(20))
  is_approved = db.Column(db.Boolean, nullable=False, default=True)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  is_suspended = db.Column(db.Boolean, nullable=False, default=False)


  oauth = db.relationship('OAuth', back_populates='user')

  def __repr__(self):
      return 'User {}'.format(self.username)

  def get_reset_token(self, expires=300):
    """Generate password reset token that expires in 5 minutes (300 seconds) by default."""
    return jwt.encode(
      {'reset_password': self.username, 'exp': time() + expires},
      current_app.config.get('SECRET_KEY', 'random_key'), algorithm='HS256')

  @staticmethod
  def verify_reset_token(token):
    try:

      if isinstance(token, bytes):
        token = token.decode('utf-8')
      username = jwt.decode(token, current_app.config.get('SECRET_KEY', 'random_key'),
                              algorithms=['HS256'])['reset_password']
    except:
      return
    return User.query.filter_by(username = username).first()

  @staticmethod
  def verify_email(email):
    user = User.query.filter_by(email = email).first()
    return user

  @property
  def role_request_details_entries(self):
    """Return parsed role request details as list of label/value pairs."""
    if not self.role_request_details:
      return []
    try:
      parsed = json.loads(self.role_request_details)
    except (TypeError, json.JSONDecodeError):
      return []
    if isinstance(parsed, list):
      return parsed
    if isinstance(parsed, dict):
      return [{"label": key.replace('_', ' ').title(), "value": value} for key, value in parsed.items()]
    return []

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


class SiteSetting(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.String(64), unique=True, nullable=False)
  value = db.Column(db.Text, nullable=False, default='')
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  def __repr__(self):
    return f"<SiteSetting {self.key}={self.value}>"


class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False, unique=True)
  slug = db.Column(db.String(120), unique=True)
  description = db.Column(db.Text)
  is_active = db.Column(db.Boolean, default=True, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  products = db.relationship('Product', back_populates='category', lazy='dynamic')

  def __repr__(self):
    return f"<Category {self.name}>"


class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
  name = db.Column(db.String(150), nullable=False)
  description = db.Column(db.Text)
  price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
  sku = db.Column(db.String(64), unique=True)
  stock = db.Column(db.Integer, nullable=False, default=0)
  is_active = db.Column(db.Boolean, default=True, nullable=False)
  is_featured = db.Column(db.Boolean, default=False, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  seller = db.relationship('User', backref=db.backref('products', lazy='dynamic'))
  category = db.relationship('Category', back_populates='products')
  images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
  inventory_transactions = db.relationship('InventoryTransaction', back_populates='product', cascade='all, delete-orphan')
  order_items = db.relationship('OrderItem', back_populates='product')
  variants = db.relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')
  reviews = db.relationship('Review', back_populates='product', cascade='all, delete-orphan')

  def __repr__(self):
    return f"<Product {self.name} (Seller {self.seller_id})>"

  @property
  def inventory_level(self):
    return self.stock

  @property
  def primary_image(self):
    return self.images[0] if self.images else None

  def adjust_stock(self, delta: int, note: str = '', source: str = 'manual'):
    self.stock += delta
    txn = InventoryTransaction(product=self, change=delta, source=source, note=note)
    db.session.add(txn)
    return txn


class ProductImage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  path = db.Column(db.String(255), nullable=False)
  position = db.Column(db.Integer, nullable=False, default=0)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  product = db.relationship('Product', back_populates='images')

  def __repr__(self):
    return f"<ProductImage product={self.product_id} position={self.position}>"


class InventoryTransaction(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  change = db.Column(db.Integer, nullable=False)
  source = db.Column(db.String(50), nullable=False, default='manual')
  note = db.Column(db.String(255))
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  product = db.relationship('Product', back_populates='inventory_transactions')

  def __repr__(self):
    return f"<InventoryTransaction product={self.product_id} change={self.change}>"


class Order(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
  buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
  status = db.Column(db.String(20), nullable=False, default='pending')
  total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
  currency = db.Column(db.String(8), nullable=False, default='PHP')
  placed_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('orders', lazy='dynamic'))
  buyer = db.relationship('User', foreign_keys=[buyer_id])
  items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

  STATUS_CHOICES = ('pending', 'processing', 'shipped', 'completed', 'cancelled')

  def __repr__(self):
    return f"<Order {self.id} seller={self.seller_id} status={self.status}>"

  def recompute_total(self):
    self.total_amount = sum((item.quantity * item.unit_price) for item in self.items)


class OrderItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'))
  quantity = db.Column(db.Integer, nullable=False, default=1)
  unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)

  order = db.relationship('Order', back_populates='items')
  product = db.relationship('Product', back_populates='order_items')
  variant = db.relationship('ProductVariant', back_populates='order_items')

  def __repr__(self):
    return f"<OrderItem order={self.order_id} product={self.product_id} qty={self.quantity}>"


class StoreProfile(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
  name = db.Column(db.String(150), nullable=False)
  slug = db.Column(db.String(160), nullable=False, unique=True)
  tagline = db.Column(db.String(255))
  description = db.Column(db.Text)
  contact_email = db.Column(db.String(150))
  contact_phone = db.Column(db.String(50))
  theme_color = db.Column(db.String(20), default="#111827")
  logo_image = db.Column(db.String(255))
  banner_image = db.Column(db.String(255))
  social_links = db.Column(db.Text)
  shipping_policy = db.Column(db.Text)
  return_policy = db.Column(db.Text)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  seller = db.relationship('User', backref=db.backref('store_profile', uselist=False))

  def __repr__(self):
    return f"<StoreProfile seller={self.seller_id} name={self.name}>"

  @property
  def social_links_dict(self):
    if not self.social_links:
      return {}
    try:
      return json.loads(self.social_links)
    except (TypeError, json.JSONDecodeError):
      return {}


class ProductVariant(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  attribute = db.Column(db.String(80), nullable=False, default="Size")
  value = db.Column(db.String(80), nullable=False)
  price_delta = db.Column(db.Numeric(12, 2), nullable=False, default=0)
  stock = db.Column(db.Integer, nullable=False, default=0)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  product = db.relationship('Product', back_populates='variants')
  order_items = db.relationship('OrderItem', back_populates='variant')

  def __repr__(self):
    return f"<ProductVariant product={self.product_id} {self.attribute}={self.value}>"


class Cart(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  status = db.Column(db.String(20), nullable=False, default='active')
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

  user = db.relationship('User', backref=db.backref('carts', lazy='dynamic'))
  items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

  def __repr__(self):
    return f"<Cart {self.id} user={self.user_id} status={self.status}>"


class CartItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'))
  quantity = db.Column(db.Integer, nullable=False, default=1)
  unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)

  cart = db.relationship('Cart', back_populates='items')
  product = db.relationship('Product')
  variant = db.relationship('ProductVariant')

  def __repr__(self):
    return f"<CartItem cart={self.cart_id} product={self.product_id} qty={self.quantity}>"


class Review(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  store_id = db.Column(db.Integer, db.ForeignKey('store_profile.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  rating = db.Column(db.Integer, nullable=False)
  title = db.Column(db.String(150))
  body = db.Column(db.Text)
  media_count = db.Column(db.Integer, nullable=False, default=0)
  is_published = db.Column(db.Boolean, nullable=False, default=True)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  product = db.relationship('Product', back_populates='reviews')
  store = db.relationship('StoreProfile', backref=db.backref('reviews', lazy='dynamic'))
  user = db.relationship('User')
  media = db.relationship('ReviewMedia', back_populates='review', cascade='all, delete-orphan')
  response = db.relationship('ReviewResponse', back_populates='review', uselist=False, cascade='all, delete-orphan')

  def __repr__(self):
    return f"<Review product={self.product_id} rating={self.rating}>"


class ReviewMedia(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
  path = db.Column(db.String(255), nullable=False)
  media_type = db.Column(db.String(20), nullable=False, default='image')

  review = db.relationship('Review', back_populates='media')

  def __repr__(self):
    return f"<ReviewMedia review={self.review_id} type={self.media_type}>"


class ReviewResponse(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False, unique=True)
  seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  message = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  review = db.relationship('Review', back_populates='response')
  seller = db.relationship('User')

  def __repr__(self):
    return f"<ReviewResponse review={self.review_id} seller={self.seller_id}>"


class OrderTrackingEvent(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
  status = db.Column(db.String(50), nullable=False)
  message = db.Column(db.String(255), nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  order = db.relationship('Order', backref=db.backref('tracking_events', cascade='all, delete-orphan'))

  def __repr__(self):
    return f"<OrderTrackingEvent order={self.order_id} status={self.status}>"


