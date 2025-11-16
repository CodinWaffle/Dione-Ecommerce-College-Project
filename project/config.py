"""
Configuration settings for Dione Ecommerce application
"""
import os
from datetime import timedelta

def load_env_file():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or '60976a5747100e32f8206121d5aefa5f'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    SQLALCHEMY_DISABLE_DRIVER_HACKS = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'dnxncpcx@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'tfxt gycw tltd yikd'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_SECRET_KEY = SECRET_KEY

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or "570919329793-g8sl8nn0h03mbk32qbgop8gie34m5chq.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or "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"
    FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID') or "YOUR_FACEBOOK_APP_ID"
    FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET') or "YOUR_FACEBOOK_APP_SECRET"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/dione_data'
    MAIL_SUPPRESS_SEND = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SECRET_KEY = 'test-secret-key'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/dione_data'
    MAIL_SUPPRESS_SEND = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
