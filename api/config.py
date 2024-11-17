import os
from pathlib import Path

class Config:
    # Use an absolute path for SQLite database in the /tmp directory for serverless environment
    BASE_DIR = Path('/tmp')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/licenses.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
