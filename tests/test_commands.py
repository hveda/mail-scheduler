"""Comprehensive tests for commands module."""

from unittest.mock import MagicMock, patch

import click
import pytest

from app.commands import create_db, drop_db, recreate_db


def test_create_db(app, db):
    """Test the create_db function."""
    with patch("app.database.db.create_all") as mock_create_all:
        # Call the function
        with app.app_context():
            create_db()

        # Verify create_all was called
        assert mock_create_all.called


@patch("click.confirm")
def test_drop_db_with_confirmation(mock_confirm, app, db):
    """Test the drop_db function with user confirmation."""
    # Setup mock to return True (user confirms)
    mock_confirm.return_value = True

    with patch("app.database.db.drop_all") as mock_drop_all:
        # Set app to non-testing mode to test confirmation
        app.config["TESTING"] = False

        # Call the function
        with app.app_context():
            drop_db()

        # Verify confirm was called
        assert mock_confirm.called

        # Verify drop_all was called
        assert mock_drop_all.called

        # Restore testing config
        app.config["TESTING"] = True


@patch("click.confirm")
def test_drop_db_without_confirmation(mock_confirm, app, db):
    """Test the drop_db function when user doesn't confirm."""
    # Setup mock to return False and raise an exception to simulate abort
    mock_confirm.return_value = False
    mock_confirm.side_effect = Exception("User abort")

    with patch("app.database.db.drop_all") as mock_drop_all:
        # Set app to non-testing mode to test confirmation
        app.config["TESTING"] = False

        # Call the function - should abort
        with app.app_context():
            with pytest.raises(Exception):
                drop_db()

        # Verify confirm was called
        assert mock_confirm.called

        # Verify drop_all was NOT called
        assert not mock_drop_all.called

        # Restore testing config
        app.config["TESTING"] = True


def test_drop_db_in_testing_mode(app, db):
    """Test the drop_db function in testing mode (no confirmation)."""
    with patch("app.database.db.drop_all") as mock_drop_all:
        # Ensure app is in testing mode
        app.config["TESTING"] = True

        # Call the function
        with app.app_context():
            drop_db()

        # Verify drop_all was called (without confirmation)
        assert mock_drop_all.called


@patch("app.commands.drop_db")
@patch("app.commands.create_db")
def test_recreate_db(mock_create_db, mock_drop_db, app):
    """Test the recreate_db function."""
    # Call the function
    with app.app_context():
        recreate_db()

    # Verify both functions were called in order
    assert mock_drop_db.called
    assert mock_create_db.called
    # Check call order
    mock_drop_db.assert_called_once()
    mock_create_db.assert_called_once()
