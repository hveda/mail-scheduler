"""Tests for error handling in jobs."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.event.jobs import add_event, dt_utc


@patch("app.event.jobs.dt_utc")
def test_add_event_exception_handling(mock_dt_utc):
    """Test that exceptions in add_event are properly raised."""
    # Make dt_utc raise an exception
    mock_dt_utc.side_effect = ValueError("Invalid timestamp format")

    # Test data with valid format but will trigger exception due to mock
    event_data = {
        "subject": "Test Email",
        "content": "This is a test",
        "timestamp": "10 May 2025 12:00 +08",
        "recipients": "test@example.com",
    }

    # Call function, should raise the exception
    with pytest.raises(ValueError) as excinfo:
        add_event(event_data)

    assert "Invalid timestamp format" in str(excinfo.value)


@patch("app.event.jobs.Event")
@patch("app.database.db.session.add")
@patch("app.database.db.session.commit")
def test_add_event_database_error(mock_commit, mock_add, mock_event):
    """Test database error handling in add_event."""
    # Setup mock to raise exception when accessing property
    mock_event_instance = MagicMock()
    mock_event.return_value = mock_event_instance
    mock_commit.side_effect = Exception("Database error")

    # Test data
    event_data = {
        "subject": "Test Email",
        "content": "This is a test",
        "timestamp": "10 May 2025 12:00 +08",
        "recipients": "test@example.com",
    }

    # Call function, should raise the exception
    with pytest.raises(Exception) as excinfo:
        add_event(event_data)

    assert "Database error" in str(excinfo.value)
    assert mock_add.called


def test_dt_utc_invalid_format():
    """Test dt_utc with invalid timestamp format."""
    with pytest.raises(Exception):
        dt_utc("not a valid timestamp")


def test_dt_utc_extreme_values():
    """Test dt_utc with extreme values."""
    # Test very old date
    result = dt_utc("01 Jan 1970 00:00:00 UTC")
    assert result.year == 1970
    assert result.month == 1
    assert result.day == 1

    # Test far future date
    result = dt_utc("31 Dec 2099 23:59:59 UTC")
    assert result.year == 2099
    assert result.month == 12
    assert result.day == 31
