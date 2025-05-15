"""Test configuration for the Mail-Scheduler application."""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app import config, create_app
from app.database import db as _db

# Mock scheduler for testing


class MockScheduler:
    def enqueue_at(self, timestamp, func, *args, **kwargs):
        # Just return a success value for testing
        return "mocked_job_id"


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(config.TestingConfig)

    # Create a temporary database for tests
    with app.app_context():
        _db.create_all()

    # Ensure the Flask-SQLAlchemy session has a remove method for teardown
    original_session = _db.session
    if not hasattr(original_session, "remove"):

        def session_remove():
            pass

        original_session.remove = session_remove

    yield app

    # Clean up after the tests
    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope="session")
def db(app):
    """Create a database interface for testing."""
    with app.app_context():
        yield _db


@pytest.fixture(scope="function")
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Create a session directly rather than using create_scoped_session
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=connection)
    session = Session()

    # Add a remove method to make it compatible with Flask-SQLAlchemy teardown
    def remove():
        session.close()

    session.remove = remove

    # Make this session available to the database object
    original_session = db.session
    db.session = session

    yield session

    # Clean up
    db.session = original_session
    transaction.rollback()
    connection.close()
    session.close()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    # Patch Redis-related functions for testing
    with patch("app.event.jobs.rq.get_scheduler", return_value=MockScheduler()):
        with patch("app.event.jobs.schedule_mail", return_value=None):
            yield app.test_client()


# Mock redis for the scheduler tests


@pytest.fixture(scope="function")
def mock_redis(monkeypatch):
    """Mock Redis connections for tests."""
    from unittest.mock import Mock

    mock_scheduler = Mock()
    monkeypatch.setattr("app.event.jobs.rq.get_scheduler", lambda: mock_scheduler)
    return mock_scheduler
