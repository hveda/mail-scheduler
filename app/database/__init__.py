"""Database module for SQLAlchemy initialization."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    # Import all models to ensure they're registered with SQLAlchemy
    # Import using direct imports to avoid circular references
    from app.database.models.user import User
    from app.database.models_core import Event, Recipient

    db.drop_all()
    db.create_all()
