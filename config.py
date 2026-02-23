import os

class Config:
    SECRET_KEY = 'plottwist_2026_devops'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///plottwist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False