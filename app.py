"""
Top-level app.py — Render auto-detects this as the entry point.
Also works with: gunicorn app:application
"""
import os
import traceback
from app import create_app, db

application = create_app(os.environ.get('FLASK_ENV', 'production'))
app = application  # gunicorn can use either name


@application.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Auto-initialize database on startup ─────────────────────────────────────
with application.app_context():
    try:
        print(f"[startup] DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}")
        print(f"[startup] URL prefix: {os.environ.get('DATABASE_URL', 'NOT SET')[:50]}")
        db.create_all()
        print("[startup] Tables OK")
        from app.models import User
        count = User.query.count()
        print(f"[startup] Users in DB: {count}")
        if count == 0:
            print("[startup] Seeding database...")
            from init_db import init_database
            init_database()
            print("[startup] Seed complete")
    except Exception as e:
        print(f"[startup] DB ERROR: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=5000)
