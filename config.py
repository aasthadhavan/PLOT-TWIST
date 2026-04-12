import os
from datetime import timedelta

class Config:
    # --- CORE ---
    SECRET_KEY = os.environ.get('FLASK_SECRET', 'plottwist_2026_devops_secret_key_xyz')
    DEBUG = False
    TESTING = False

    # --- DATABASE ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///plottwist.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- SECURITY ---
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    
    # --- GIT ENGINE CONFIG ---
    GIT_STORY_NAMESPACE = "story/"