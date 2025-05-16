"""Module for initializing the Flask application in Vercel environment."""
import os
import sys
from flask import Flask

# Flag for Vercel environment
is_vercel = os.environ.get('VERCEL', '0') == '1'

def create_app(conf):
    """Returns an initialized Flask application."""
    from app import config
    from app.database import db
    
    app = Flask(__name__)
    app.config.from_object(conf)
    
    # Use the appropriate extensions based on environment
    if is_vercel:
        from app.vercel_extensions import mail, migrate, rq, login
    else:
        from app.extensions import mail, migrate, rq, login
    
    # Register extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)
    login.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register commands
    if not is_vercel:
        from app.commands import create_db, drop_db, recreate_db
        app.cli.add_command(create_db)
        app.cli.add_command(drop_db)
        app.cli.add_command(recreate_db)
    
    # Configure login
    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'
    
    return app

def register_blueprints(app):
    """Register blueprints with the Flask application."""
    from app.api import blueprint as api
    app.register_blueprint(api, url_prefix='/api')
    
    # Register the event blueprint
    from app.event.views import blueprint as event_blueprint
    app.register_blueprint(event_blueprint, url_prefix='/items')
    
    # Register the auth blueprint
    from app.auth import blueprint as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return None
