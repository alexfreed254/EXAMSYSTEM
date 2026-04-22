from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import os

db      = SQLAlchemy()
migrate = Migrate()
mail    = Mail()


def create_app(config_name=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    from config import config
    cfg = config.get(config_name or os.environ.get('FLASK_ENV', 'default'), config['default'])
    app.config.from_object(cfg)
    cfg.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # ── Load current user from session on every request ──────────────────────
    @app.before_request
    def load_current_user():
        g.current_user = None
        uid = session.get('user_id')
        if uid:
            from app.models import User
            g.current_user = User.query.get(uid)

    # ── Inject current_user into all templates ────────────────────────────────
    @app.context_processor
    def inject_user():
        from datetime import datetime
        return {
            'current_user': g.get('current_user'),
            'now': datetime.utcnow(),
        }

    # ── Register blueprints ───────────────────────────────────────────────────
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

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route('/health')
    def health_check():
        from flask import jsonify
        status = {'app': 'ok', 'db': 'unknown', 'tables': [], 'users': 0, 'error': None}
        try:
            db.session.execute(db.text('SELECT 1'))
            status['db'] = 'connected'
            rows = db.session.execute(
                db.text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            ).fetchall()
            status['tables'] = [r[0] for r in rows]
            from app.models import User
            status['users'] = User.query.count()
        except Exception as e:
            status['db'] = 'error'
            status['error'] = str(e)
        return jsonify(status), 200 if status['db'] == 'connected' else 500

    # ── 500 error handler ─────────────────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        from flask import render_template_string
        tb = traceback.format_exc()
        print(f"[500]\n{tb}")
        return render_template_string("""<!DOCTYPE html>
<html><head><title>500</title></head>
<body style="font-family:monospace;padding:20px;background:#0d1117;color:#f0f6fc">
<h2 style="color:#f85149">500 - Internal Server Error</h2>
<pre style="background:#161b22;padding:15px;border-radius:8px;overflow:auto;color:#79c0ff;font-size:13px">{{ tb }}</pre>
<a href="/" style="color:#58a6ff">← Home</a></body></html>""", tb=tb), 500

    return app
