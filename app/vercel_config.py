"""Vercel specific configuration."""
import os
from app.config import Config, ProductionConfig

class VercelConfig(ProductionConfig):
    """Configuration for Vercel deployment."""
    # Use SQLite for Vercel deployment
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vercel.db'
    
    # Disable Redis Queue for Vercel
    RQ_ASYNC = False
    
    # Security configurations
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Mail configuration (update with your SMTP details)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'mail-scheduler@example.com')
