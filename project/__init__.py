from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from jinja2 import Undefined
try:
    from flask.json.provider import DefaultJSONProvider
except Exception:
    DefaultJSONProvider = None
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
    from .models import User, OAuth, Product

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from .routes.auth_routes import auth
    from .routes.main_routes import main, get_nav_items
    from .routes.oauth_routes import google_blueprint, facebook_blueprint, debug_bp
    from .routes.admin_routes import admin_bp
    from .routes.seller_routes import seller_bp
    from .routes.chat_routes import chat_bp
    from .routes.rider_routes import rider_bp

    # Context processor to make current_user available in all templates
    @app.context_processor
    def inject_current_user():
        """Make current_user available in all Jinja2 templates"""
        return {'current_user': current_user}

    # Prefer Flask's JSON provider API (Flask>=2.2). If available,
    # subclass the provider to convert Jinja2 Undefined -> None.
    if DefaultJSONProvider is not None:
        class _CustomJSONProvider(DefaultJSONProvider):
            def default(self, obj):
                try:
                    if isinstance(obj, Undefined):
                        return None
                except Exception:
                    pass
                return super().default(obj)

        app.json_provider_class = _CustomJSONProvider
    else:
        # Fallback: older Flask versions use app.json_encoder
        try:
            from json import JSONEncoder as _PyJSONEncoder

            class _CustomJSONEncoder(_PyJSONEncoder):
                def default(self, obj):
                    try:
                        if isinstance(obj, Undefined):
                            return None
                    except Exception:
                        pass
                    return super().default(obj)

            app.json_encoder = _CustomJSONEncoder
        except Exception:
            # If all else fails, leave defaults and rely on per-endpoint sanitizers
            pass

    @app.context_processor
    def inject_nav_items():
        """Provide navigation data for buyer headers on all public pages"""
        try:
            return {'nav_items': get_nav_items()}
        except Exception:
            return {'nav_items': []}

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(google_blueprint, url_prefix="/login")
    app.register_blueprint(facebook_blueprint, url_prefix="/login")
    app.register_blueprint(debug_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(rider_bp)

    return app
