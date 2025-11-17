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


