"""
A simplified and enhanced version of the mail-scheduler app for Vercel deployment.
This version is designed to work with Vercel's PostgreSQL database.
"""
import os
import logging
from flask import Flask, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database with connection pooling settings
db = SQLAlchemy(engine_options={
    'pool_pre_ping': True,
    'pool_recycle': 280,
    'connect_args': {'connect_timeout': 10}
})

# Initialize extensions
login = LoginManager()
mail = Mail()
migrate = Migrate()

class Config:
    """Base configuration for the Vercel app."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-vercel')
    
    # Use Vercel Postgres if available
    if os.environ.get('mail_scheduler_DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('mail_scheduler_DATABASE_URL')
        logger.info("Using PostgreSQL database")
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///vercel.db'
        logger.info("Using SQLite database")
        
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

# Simple User model for login
class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

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
        try:
            # Initialize database
            db.create_all()
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
        
        # Simple routes for Vercel deployment
        @app.route('/')
        def index():
            return redirect(url_for('vercel_home'))
        
        @app.route('/vercel')
        def vercel_home():
            """Home page for Vercel deployment."""
            db_type = "PostgreSQL" if "postgres" in str(app.config.get('SQLALCHEMY_DATABASE_URI', '')) else "SQLite"
            return jsonify({
                'app': 'Mail Scheduler',
                'environment': 'Vercel Serverless',
                'database': db_type,
                'status': 'active',
                'note': 'This is a simplified version of the app for Vercel.'
            })
        
        @app.route('/api/health')
        def health():
            """Health check endpoint."""
            try:
                # Try a simple database query to check connection
                db.session.execute("SELECT 1").scalar()
                return jsonify({'status': 'ok', 'database': 'connected'})
            except SQLAlchemyError as e:
                return jsonify({'status': 'error', 'database': 'disconnected', 'error': str(e)}), 500
        
        @app.errorhandler(404)
        def page_not_found(e):
            return jsonify({'error': 'Not found', 'message': str(e)}), 404
        
        @app.errorhandler(500)
        def server_error(e):
            return jsonify({'error': 'Server error', 'message': str(e)}), 500
    
    return app

# Create the application
app = create_app()

# For Vercel serverless deployment
handler = app
