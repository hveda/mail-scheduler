"""Database module for SQLAlchemy initialization."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    # Import all models to ensure they're registered with SQLAlchemy
    # Import using direct imports to avoid circular references
    from app.database.models.user import User
    from app.database.models_core import Event, Recipient

    # Ensure models are registered (silence flake8 warnings)
    models = [User, Event, Recipient]
    assert models  # Models imported for registration  # nosec B101

    db.drop_all()
    db.create_all()
