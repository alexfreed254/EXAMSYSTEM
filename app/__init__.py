from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()


def create_app(config_name=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Load config
    from config import config
    cfg = config.get(config_name or os.environ.get('FLASK_ENV', 'default'), config['default'])
    app.config.from_object(cfg)
    cfg.init_app(app)

    # Fix Render postgres URL
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_url.startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql://', 1)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # Register blueprints
    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.trainer import trainer as trainer_bp
    app.register_blueprint(trainer_bp, url_prefix='/trainer')

    from app.trainee import trainee as trainee_bp
    app.register_blueprint(trainee_bp, url_prefix='/trainee')

    from app.main import main as main_bp
    app.register_blueprint(main_bp)

    # ── Global error handlers ────────────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        from flask import render_template_string
        tb = traceback.format_exc()
        print(f"[500 ERROR] {tb}")
        # Show detailed error in production temporarily for debugging
        return render_template_string("""
        <!DOCTYPE html><html><body style="font-family:monospace;padding:20px;background:#1a1a2e;color:#e94560">
        <h2>500 Internal Server Error</h2>
        <pre style="background:#16213e;padding:15px;color:#0f3460;color:#a8dadc;border-radius:8px;overflow:auto">{{ tb }}</pre>
        <p><a href="/" style="color:#e94560">Go Home</a></p>
        </body></html>
        """, tb=tb), 500

    return app
