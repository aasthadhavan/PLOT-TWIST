import os
from datetime import timedelta

class Config:
    # --- CORE ---
    SECRET_KEY = os.environ.get('FLASK_SECRET', 'plottwist_2026_devops_secret_key_xyz')
    # --- DATABASE ---
    _db_path = 'plottwist.db'
    if os.environ.get('VERCEL') == '1':
        _db_path = '/tmp/plottwist.db'
        DEBUG = False
        SESSION_COOKIE_SECURE = True
    else:
        DEBUG = True
        SESSION_COOKIE_SECURE = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{_db_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- SECURITY ---
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    
    # --- GIT ENGINE CONFIG ---
    GIT_STORY_NAMESPACE = "story/"