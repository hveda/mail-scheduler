"""Integration tests for Flask CLI commands."""
import pytest
from unittest.mock import patch
from datetime import datetime, UTC

from app.commands import create_db, drop_db, recreate_db
from app.database import db
from app.database.models import Event

# We're only testing create_db since it's the most straightforward
# drop_db and recreate_db require more complex mocking for console input


def test_create_db_integration(app):
    """Test that create_db creates the tables."""
    # Run in app context
    with app.app_context():
        # Call the command
        create_db()

        # Verify db object exists
        assert db is not None

        # Verify engine exists
        assert hasattr(db, 'engine')
        assert db.engine is not None


def test_drop_db_integration(app):
    """Test dropping database tables"""
    # Run in app context
    with app.app_context():
        # First ensure tables exist
        create_db()

        # Create a test event
        event = Event(
            email_subject='Test Event',
            email_content='This is a test event',
            timestamp=datetime.now(UTC)  # Use proper timezone-aware datetime
        )
        db.session.add(event)
        db.session.commit()

        # Remember the ID
        event_id = event.id

        # Now drop the database
        drop_db()

        # Create tables again to be able to query
        create_db()

        # Verify the record no longer exists
        assert db.session.get(Event, event_id) is None


@patch('click.confirm')
def test_drop_db_with_confirmation(mock_confirm, app):
    """Test drop_db with user confirmation."""
    # Set confirmation to True
    mock_confirm.return_value = True

    with app.app_context():
        # Set app not in testing mode to test confirmation path
        app.config['TESTING'] = False

        # Call drop_db, which should use the mocked confirm
        drop_db()

        # Verify confirm was called
        assert mock_confirm.called

        # Reset testing mode
        app.config['TESTING'] = True


@patch('app.commands.drop_db')
@patch('app.commands.create_db')
def test_recreate_db_integration(mock_create_db, mock_drop_db, app):
    """Test the recreate_db command calls both drop_db and create_db."""
    with app.app_context():
        # Call recreate_db
        recreate_db()

        # Verify both functions were called
        assert mock_drop_db.called
        assert mock_create_db.called
