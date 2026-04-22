import os
from dotenv import load_dotenv

load_dotenv()

# ── Supabase project constants ────────────────────────────────────────────────
SUPABASE_REF = 'igphwverobcvslmgpxdo'
SUPABASE_HOST = f'aws-0-us-east-1.pooler.supabase.com'
SUPABASE_PORT = '5432'
SUPABASE_DB   = 'postgres'


def get_database_url():
    """
    Always returns a valid Supabase Session Pooler URL.
    Username MUST be: postgres.igphwverobcvslmgpxdo  (not just 'postgres')
    """
    password = os.environ.get('DB_PASSWORD', '')

    if not password:
        print("[config] WARNING: DB_PASSWORD not set — using SQLite fallback")
        return 'sqlite:///local_dev.db'

    url = (
        f'postgresql://postgres.{SUPABASE_REF}:{password}'
        f'@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}'
    )
    print(f"[config] DB URL: postgresql://postgres.{SUPABASE_REF}:***@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}")
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ttti-dev-key-change-in-prod'

    SQLALCHEMY_DATABASE_URI    = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPABASE_URL = f'https://{SUPABASE_REF}.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle':  280,
        'pool_size':     3,
        'max_overflow':  1,
        'connect_args': {
            'sslmode':          'require',
            'connect_timeout':  15,
            'application_name': 'ttti-erms',
        }
    }

    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def init_app(app):
        # Re-build URL at runtime so env vars are definitely loaded
        url = get_database_url()
        app.config['SQLALCHEMY_DATABASE_URI'] = url


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     ProductionConfig,
}
