import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'production'))


@app.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Auto-initialize on startup ───────────────────────────────────────────────
with app.app_context():
    try:
        db.create_all()
        from app.models import User
        if not User.query.first():
            from init_db import init_database
            init_database()
    except Exception as e:
        print(f"[startup] DB init: {e}")


if __name__ == '__main__':
    app.run()
