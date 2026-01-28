"""
Configuration settings for Flask backend
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'brain_mri_db')
    
    # Model
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/resnet50_best.pth')
    IMG_SIZE = int(os.getenv('IMG_SIZE', 224))
    
    # Storage
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    GRADCAM_FOLDER = os.getenv('GRADCAM_FOLDER', 'gradcam_outputs')
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False  # Disabled to avoid bytes/string issue
    SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-origin in production
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'  # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # CORS - Add Azure frontend URL
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
