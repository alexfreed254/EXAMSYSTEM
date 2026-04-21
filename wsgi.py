import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'production'))


@app.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow()}


# ── Auto-initialize database on first startup (Render) ──────────────────────
with app.app_context():
    try:
        db.create_all()
        # Seed admin account if database is empty
        from app.models import User
        if not User.query.first():
            admin = User(
                username='admin',
                email='admin@ttti.ac.ke',
                full_name='System Administrator',
                role='admin'
            )
            admin.set_password('Admin@2025')
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(f"DB init warning: {e}")


if __name__ == '__main__':
    app.run()
