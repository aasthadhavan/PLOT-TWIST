import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-777-plottwist'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/plottwist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False