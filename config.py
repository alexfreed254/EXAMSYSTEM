import os
from dotenv import load_dotenv

load_dotenv()


def _build_db_url():
    """
    Build the database URL from environment.
    Supports both full DATABASE_URL and individual Supabase components.
    """
    url = os.environ.get('DATABASE_URL', '')

    # Fix legacy postgres:// prefix
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)

    if url:
        return url

    # Build from Supabase components if DATABASE_URL not set
    # Direct connection: db.[ref].supabase.co:5432
    ref = 'igphwverobcvslmgpxdo'
    pwd = os.environ.get('DB_PASSWORD', '')
    if pwd:
        return f'postgresql://postgres.{ref}:{pwd}@aws-0-us-east-1.pooler.supabase.com:5432/postgres'

    return 'sqlite:///local_dev.db'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ttti-dev-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = _build_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase client credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://igphwverobcvslmgpxdo.supabase.co')
    SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')

    # SQLAlchemy engine options — tuned for Supabase
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 3,
        'max_overflow': 1,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 15,
            'application_name': 'ttti-erms',
        }
    }

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def init_app(app):
        # Re-evaluate URL at runtime in case env vars loaded late
        url = _build_db_url()
        app.config['SQLALCHEMY_DATABASE_URI'] = url
        print(f"[config] DB URL prefix: {url[:60]}")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'sslmode': 'require', 'connect_timeout': 15}
    }


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig,
}
