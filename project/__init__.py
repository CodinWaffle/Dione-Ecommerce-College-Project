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
    from .routes.buyer_routes import buyer_bp

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
    # Register buyer routes (my purchases, reviews, order tracking)
    app.register_blueprint(buyer_bp)
    # Ensure DB has chat_messages.attachment column for file uploads.
    try:
        with app.app_context():
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'chat_messages' in inspector.get_table_names():
                cols = [c.get('name') for c in inspector.get_columns('chat_messages')]
                if 'attachment' not in cols:
                    # Add nullable attachment column if missing. Use raw SQL to be safe
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE chat_messages ADD COLUMN attachment VARCHAR(512) NULL'))
                        conn.commit()
                    app.logger.info('Added missing chat_messages.attachment column')
    except Exception:
        # If automatic migration fails, log and continue; developer can run alembic
        app.logger.exception('Automatic check/create for chat_messages.attachment failed')

    # Ensure DB has chat_messages.is_read column for read receipts (boolean)
    try:
        with app.app_context():
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'chat_messages' in inspector.get_table_names():
                cols = [c.get('name') for c in inspector.get_columns('chat_messages')]
                if 'is_read' not in cols:
                    # Add nullable/boolean is_read column if missing. Use raw SQL to be safe
                    # MySQL uses TINYINT(1) for booleans
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE chat_messages ADD COLUMN is_read TINYINT(1) NOT NULL DEFAULT 0"))
                        conn.commit()
                    app.logger.info('Added missing chat_messages.is_read column')
    except Exception:
        # If automatic migration fails, log and continue; developer can run alembic
        app.logger.exception('Automatic check/create for chat_messages.is_read failed')

    # Ensure orders table has buyer_id and seller_id columns compatible with models
    try:
        with app.app_context():
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'orders' in inspector.get_table_names():
                cols = [c.get('name') for c in inspector.get_columns('orders')]
                to_run = []
                if 'buyer_id' not in cols:
                    to_run.append("ALTER TABLE orders ADD COLUMN buyer_id INT NULL")
                if 'seller_id' not in cols:
                    to_run.append("ALTER TABLE orders ADD COLUMN seller_id INT NULL")

                if to_run:
                    with db.engine.connect() as conn:
                        for stmt in to_run:
                            try:
                                conn.execute(text(stmt))
                                conn.commit()
                                app.logger.info(f'Added column to orders: {stmt}')
                            except Exception:
                                app.logger.exception(f'Failed to run: {stmt}')

                        # Backfill buyer_id from legacy user_id if present and buyer_id is NULL
                        if 'user_id' in cols:
                            try:
                                conn.execute(text('UPDATE orders SET buyer_id = user_id WHERE buyer_id IS NULL'))
                                conn.commit()
                                app.logger.info('Backfilled orders.buyer_id from orders.user_id')
                            except Exception:
                                app.logger.exception('Failed to backfill orders.buyer_id from user_id')
                        # Ensure shipping_fee exists (models use shipping_fee, legacy schema may use shipping_amount)
                        if 'shipping_fee' not in cols:
                            try:
                                conn.execute(text('ALTER TABLE orders ADD COLUMN shipping_fee DECIMAL(10,2) NULL'))
                                conn.commit()
                                app.logger.info('Added orders.shipping_fee column')
                            except Exception:
                                app.logger.exception('Failed to add orders.shipping_fee')

                        if 'shipping_amount' in cols and 'shipping_fee' in [c.get('name') for c in inspector.get_columns('orders')]:
                            try:
                                conn.execute(text('UPDATE orders SET shipping_fee = shipping_amount WHERE shipping_fee IS NULL'))
                                conn.commit()
                                app.logger.info('Backfilled orders.shipping_fee from shipping_amount')
                            except Exception:
                                app.logger.exception('Failed to backfill orders.shipping_fee from shipping_amount')
    except Exception:
        app.logger.exception('Automatic check/create for orders.buyer_id/seller_id failed')
    return app
