"""
TTTI ERMS - Main entry point
Gunicorn command: gunicorn main:application
"""
import os
import traceback

# Must set env before importing app
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app, db

application = create_app('production')


@application.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Initialize database on startup ──────────────────────────────────────────
with application.app_context():
    try:
        db_url = os.environ.get('DATABASE_URL', 'NOT SET')
        print(f"[startup] DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}")
        print(f"[startup] URL starts with: {db_url[:50]}")
        db.create_all()
        print("[startup] db.create_all() completed")
        from app.models import User
        count = User.query.count()
        print(f"[startup] User count: {count}")
        if count == 0:
            print("[startup] No users found — seeding...")
            from init_db import init_database
            init_database()
            print("[startup] Seed complete")
        else:
            print(f"[startup] DB already has {count} user(s) — skipping seed")
    except Exception as e:
        print(f"[startup] CRITICAL ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        # Don't exit — let gunicorn start so /health route works


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
