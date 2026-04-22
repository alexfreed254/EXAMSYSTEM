"""
Gunicorn entry point — named 'server.py' to avoid conflict with the 'app/' package.
Render start command: gunicorn server:application
"""
import os
from app import create_app, db

# Create the Flask application instance
application = create_app(os.environ.get('FLASK_ENV', 'production'))

# Also expose as 'app' for compatibility
app = application


@application.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Auto-initialize database on startup ─────────────────────────────────────
with application.app_context():
    try:
        db.create_all()
        from app.models import User
        if not User.query.first():
            from init_db import init_database
            init_database()
    except Exception as e:
        print(f"[startup] DB init warning: {e}")


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=5000)
