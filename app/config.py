import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))

if IS_VERCEL:
    INSTANCE_DIR = '/tmp/instance'
    UPLOAD_FOLDER = '/tmp/uploads'
    
    # Copy pre-seeded database to /tmp if it exists
    default_db_src = os.path.join(BASE_DIR, 'instance', 'civicpulse.db')
    target_db_dest = '/tmp/civicpulse.db'
    if os.path.exists(default_db_src) and not os.path.exists(target_db_dest):
        try:
            shutil.copy2(default_db_src, target_db_dest)
        except Exception:
            pass
            
    # Copy seed upload images to /tmp/uploads if available
    seed_uploads = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    if os.path.exists(seed_uploads) and not os.path.exists(UPLOAD_FOLDER):
        try:
            shutil.copytree(seed_uploads, UPLOAD_FOLDER)
        except Exception:
            pass
else:
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

try:
    os.makedirs(INSTANCE_DIR, exist_ok=True)
except OSError:
    pass

try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except OSError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'civicpulse-smartcity-secret-key-2026-sdg11')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IS_VERCEL = IS_VERCEL
    
    # Upload directories
    UPLOAD_FOLDER = UPLOAD_FOLDER
    ISSUES_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'issues')
    RESOLUTIONS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'resolutions')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # SDG 11 city default coordinates (e.g. Metro City Center)
    DEFAULT_MAP_CENTER = [12.9716, 77.5946] # Bangalore / Metro Tech hub as default sample
    DEFAULT_MAP_ZOOM = 13

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'civicpulse.db')}" if not IS_VERCEL else 'sqlite:////tmp/civicpulse.db'
    )

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'civicpulse.db')}" if not IS_VERCEL else 'sqlite:////tmp/civicpulse.db'
    )

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
