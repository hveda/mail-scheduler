"""The app module, containing the app factory function."""
from flask import Flask

from app import config
from app.api import blueprint as api
from app.commands import create_db, drop_db, recreate_db
from app.database import db
from app.extensions import mail, migrate, rq


def create_app(conf=config.Config):
    """Returns an initialized Flask application."""
    app = Flask(__name__)
    app.config.from_object(conf)

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def register_blueprints(app):
    """Register blueprints with the Flask application."""
    app.register_blueprint(api, url_prefix='/api')
    return None


def register_extensions(app):
    """Register extensions with the Flask application."""
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)


def register_commands(app):
    """Register custom commands for the Flask CLI."""
    for command in [create_db, drop_db, recreate_db]:
        app.cli.command()(command)
