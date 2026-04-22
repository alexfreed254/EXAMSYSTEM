"""
TTTI ERMS — Gunicorn entry point
Start: gunicorn main:application --workers 1 --bind 0.0.0.0:$PORT --timeout 120
"""
import os
import traceback

os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app, db

application = create_app('production')


@application.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Startup: connect DB and seed ─────────────────────────────────────────────
with application.app_context():
    try:
        db_url = application.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
        print(f"[startup] DB URL: {db_url[:60]}...")

        # Test connection first
        db.session.execute(db.text('SELECT 1'))
        print("[startup] DB connection OK")

        db.create_all()
        print("[startup] Tables verified")

        from app.models import User
        count = User.query.count()
        print(f"[startup] Users: {count}")

        if count == 0:
            from init_db import init_database
            init_database()

    except Exception as e:
        print(f"[startup] ERROR — {type(e).__name__}: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
