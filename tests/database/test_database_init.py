"""Tests for database module."""
import pytest
from unittest.mock import patch, MagicMock

from app.database import db, reset_database


def test_db_exists():
    """Test that the db object exists."""
    assert db is not None
    assert hasattr(db, 'session')
    assert hasattr(db, 'Model')


@patch('app.database.db')
def test_reset_database(mock_db):
    """Test the reset_database function."""
    # Call the function
    reset_database()

    # Verify db operations were called
    assert mock_db.drop_all.called
    assert mock_db.create_all.called
