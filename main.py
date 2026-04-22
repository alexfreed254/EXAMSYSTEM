"""
TTTI ERMS — Gunicorn entry point (Render hosting + Supabase database)
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


# ── Startup: verify Supabase connection and seed if needed ───────────────────
with application.app_context():
    try:
        print(f"[startup] DB_PASSWORD set: {bool(os.environ.get('DB_PASSWORD'))}")
        db.session.execute(db.text('SELECT 1'))
        print("[startup] Supabase connection OK")
        db.create_all()
        print("[startup] Tables verified")
        from app.models import User
        count = User.query.count()
        print(f"[startup] Users in DB: {count}")
        if count == 0:
            from init_db import init_database
            init_database()
            print("[startup] Seed complete")
    except Exception as e:
        print(f"[startup] ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
