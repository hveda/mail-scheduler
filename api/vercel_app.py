"""
A simplified version of the mail-scheduler app for Vercel deployment.
This version removes all Redis/RQ dependencies.
"""
import os
from flask import Flask, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize database
db = SQLAlchemy()

# Initialize extensions
login = LoginManager()
mail = Mail()
migrate = Migrate()

class Config:
    """Base configuration for the Vercel app."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-vercel')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vercel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'mail-scheduler@example.com')
    
    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

def create_app(config_class=Config):
    """Create the Flask application for Vercel."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Set up login view
    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Simple routes for Vercel deployment
        @app.route('/')
        def index():
            return redirect(url_for('vercel_home'))
        
        @app.route('/vercel')
        def vercel_home():
            """Home page for Vercel deployment."""
            return jsonify({
                'app': 'Mail Scheduler',
                'environment': 'Vercel Serverless',
                'note': 'This is a simplified version of the app for Vercel.'
            })
        
        @app.route('/health')
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'ok'})
        
        @app.errorhandler(404)
        def page_not_found(e):
            return jsonify({'error': 'Not found', 'message': str(e)}), 404
        
        @app.errorhandler(500)
        def server_error(e):
            return jsonify({'error': 'Server error', 'message': str(e)}), 500
    
    return app

# Create the application
app = create_app()
