"""
Run this script to generate correct password hashes for Supabase SQL.
Then copy the hashes into supabase_schema.sql
"""
from werkzeug.security import generate_password_hash

passwords = {
    'admin':    'Admin@2025',
    'trainer1': 'Trainer@2025',
    'trainee1': 'Trainee@2025',
}

print("Copy these hashes into supabase_schema.sql:\n")
for user, pwd in passwords.items():
    h = generate_password_hash(pwd)
    print(f"{user}: '{h}'")
