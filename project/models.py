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
  password = db.Column(db.String(255))  # Increased to 255 for pbkdf2:sha256 hashes
  username = db.Column(db.String(150))

  # OAuth relationship
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
      # Handle both bytes and string tokens
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


class OAuth(OAuthConsumerMixin, db.Model):
  __tablename__ = 'oauth'  # Explicitly set table name
  __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
  provider = db.Column(db.String(50), nullable=False)
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  token = db.Column(db.Text)  # Store as JSON string
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


