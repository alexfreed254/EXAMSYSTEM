"""
Supabase client singleton — used for authentication only.
All app data (results, transcripts, etc.) uses SQLAlchemy.
"""
import os
from supabase import create_client, Client

_client: Client = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.environ.get('SUPABASE_URL', '')
        key = os.environ.get('SUPABASE_ANON_KEY', '')
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )
        _client = create_client(url, key)
    return _client


def get_supabase_admin() -> Client:
    """
    Admin client using service_role key — bypasses RLS.
    Used for creating users server-side (admin creating trainers/trainees).
    """
    url = os.environ.get('SUPABASE_URL', '')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not service_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for admin operations"
        )
    return create_client(url, service_key)
