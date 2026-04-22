import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ttti-secret-key-2025-change-in-production'
    # Supabase PostgreSQL — project: igphwverobcvslmgpxdo
    # DATABASE_URL must be set in Render environment variables
    # Format: postgresql://postgres.[ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres.igphwverobcvslmgpxdo:your-db-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres'

    SUPABASE_URL = 'https://igphwverobcvslmgpxdo.supabase.co'
    SUPABASE_ANON_KEY = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        '.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlncGh3dmVyb2JjdnNsbWdweGRvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4NDM2MTUsImV4cCI6MjA5MjQxOTYxNX0'
        '.bBjFLktHZ-hCX1Hunw5-Z05qerEwBq-6CQ24IHciIxQ'
    )

    # SQLAlchemy pool settings for Supabase Pooler (port 6543 = transaction mode)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 2,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10,
        }
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Fix postgres:// -> postgresql:// (some providers use old format)
    @staticmethod
    def init_app(app):
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
            os.environ['DATABASE_URL'] = db_url
            app.config['SQLALCHEMY_DATABASE_URI'] = db_url


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
