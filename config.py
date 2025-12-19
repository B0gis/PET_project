import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'в'

    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'federation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    IMAGE_TARGET_SIZE = (1920, 1080)
    IMAGE_QUALITY = 85
    THUMBNAIL_SIZE = (400, 300)
    THUMBNAIL_QUALITY = 75

    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'