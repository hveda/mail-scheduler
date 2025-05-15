"""The app module, containing the app factory function."""
from flask import Flask

from app import config
from app.api import blueprint as api
from app.commands import create_db, drop_db, recreate_db
from app.database import db
from app.extensions import mail, migrate, rq, login


def create_app(conf=config.Config):
    """Returns an initialized Flask application."""
    app = Flask(__name__)
    app.config.from_object(conf)

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    configure_login(app)

    return app


def register_blueprints(app):
    """Register blueprints with the Flask application."""
    app.register_blueprint(api, url_prefix='/api')

    # Register the event blueprint
    from app.event.views import blueprint as event_blueprint
    app.register_blueprint(event_blueprint, url_prefix='/items')

    # Register the auth blueprint
    from app.auth import blueprint as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return None


def register_extensions(app):
    """Register extensions with the Flask application."""
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)
    login.init_app(app)

    return None


def configure_login(app):
    """Configure Flask-Login."""
    from app.database.models.user import User

    @login.user_loader
    def load_user(user_id):
        """Load a user from the database given their ID."""
        return User.query.get(int(user_id))

    return None


def register_commands(app):
    """Register custom commands for the Flask CLI."""
    for command in [create_db, drop_db, recreate_db]:
        app.cli.command()(command)

    # Register init_db command
    from app.database.init_db import register_commands as register_db_commands
    register_db_commands(app)
