import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'plottwist_2026_devops_secret_key_xyz')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///plottwist.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400