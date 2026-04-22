"""
Gunicorn entry point — named 'server.py' to avoid conflict with the 'app/' package.
Render start command: gunicorn server:application
"""
import os
import traceback
from app import create_app, db

# Create the Flask application instance
application = create_app(os.environ.get('FLASK_ENV', 'production'))
app = application  # alias


@application.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Health check + DB diagnostic route ──────────────────────────────────────
@application.route('/health')
def health():
    from flask import jsonify
    status = {
        'app': 'ok',
        'db': 'unknown',
        'db_url_set': bool(os.environ.get('DATABASE_URL')),
        'db_url_prefix': os.environ.get('DATABASE_URL', '')[:40] + '...' if os.environ.get('DATABASE_URL') else 'NOT SET',
        'flask_env': os.environ.get('FLASK_ENV', 'not set'),
        'secret_key_set': bool(os.environ.get('SECRET_KEY')),
        'tables': [],
        'error': None,
    }
    try:
        result = db.session.execute(db.text('SELECT 1')).fetchone()
        status['db'] = 'connected' if result else 'no result'
        # List tables
        tables = db.session.execute(
            db.text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        ).fetchall()
        status['tables'] = [t[0] for t in tables]
        # Check user count
        from app.models import User
        status['user_count'] = User.query.count()
    except Exception as e:
        status['db'] = 'error'
        status['error'] = str(e)
        status['traceback'] = traceback.format_exc()
    return jsonify(status), 200 if status['db'] == 'connected' else 500


# ── Auto-initialize database on startup ─────────────────────────────────────
with application.app_context():
    try:
        print(f"[startup] DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}")
        print(f"[startup] DB URL prefix: {os.environ.get('DATABASE_URL','NOT SET')[:50]}")
        db.create_all()
        print("[startup] db.create_all() OK")
        from app.models import User
        count = User.query.count()
        print(f"[startup] User count: {count}")
        if count == 0:
            from init_db import init_database
            init_database()
            print("[startup] Seed complete")
    except Exception as e:
        print(f"[startup] ERROR: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=5000)
