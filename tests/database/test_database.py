"""Tests for database module."""

from unittest.mock import patch

import pytest


def test_db_object():
    """Test database object initialization."""
    from app.database import db

    assert db is not None
    assert hasattr(db, "Model")
    assert hasattr(db, "session")


@patch("app.database.db.drop_all")
@patch("app.database.db.create_all")
def test_reset_database(mock_create_all, mock_drop_all):
    """Test reset_database function."""
    from app.database import reset_database

    # Call the function
    reset_database()

    # Verify both drop_all and create_all were called
    assert mock_drop_all.called
    assert mock_create_all.called
    assert mock_drop_all.call_count == 1
    assert mock_create_all.call_count == 1
