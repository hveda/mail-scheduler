#!/usr/bin/env python
"""
Reset and initialize the database for mail-scheduler.
This script is an alternative to running flask db migrate/upgrade
when you encounter compatibility issues with SQLAlchemy in Python 3.13.
"""

from app import create_app
from app.database import db
from app.database.init_db import (
    create_default_admin, create_test_user,
    create_standard_users, create_sample_events
)

# Create a Flask app instance
app = create_app()


def reset_database():
    """Drop all tables and recreate them."""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database tables have been reset!")

        # Initialize the database with default data
        print("Initializing database with default data...")
        print("Creating admin user...")
        create_default_admin()
        print("Creating test user...")
        create_test_user()
        print("Creating standard users...")
        create_standard_users()
        print("Creating sample events...")
        create_sample_events()
        print("Database initialization completed!")


if __name__ == "__main__":
    # Run with app context
    with app.app_context():
        reset_database()
