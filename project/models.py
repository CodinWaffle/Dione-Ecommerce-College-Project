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
      'primaryImage': self.image or '/static/image/banner.png',
      'secondaryImage': self.secondary_image or self.image or '/static/image/banner.png',
      'material': (self.materials or 'Premium Fabric').split('\n')[0],
      'price': price,
      'originalPrice': compare_price if compare_price > price else None,
      'category': self.category,
      'subcategory': self.subcategory,
    }

  def __repr__(self):
    return f'<Product {self.id} - {self.name}>'


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
  is_from_admin = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  user = db.relationship('User', foreign_keys=[user_id], backref='chat_messages')
  admin = db.relationship('User', foreign_keys=[admin_id])

  def __repr__(self):
    return f'<ChatMessage {self.id} user={self.user_id} admin={self.admin_id}>'


