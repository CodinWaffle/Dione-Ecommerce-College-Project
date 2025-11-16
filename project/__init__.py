from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='default'):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    from .config import config
    app.config.from_object(config[config_name])
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import models
    from .models import User, OAuth

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from .routes.auth_routes import auth
    from .routes.main_routes import main
    from .routes.oauth_routes import google_blueprint, facebook_blueprint, debug_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(google_blueprint, url_prefix="/login")
    app.register_blueprint(facebook_blueprint, url_prefix="/login")
    app.register_blueprint(debug_bp)
    app.register_blueprint(admin_bp)

    return app
