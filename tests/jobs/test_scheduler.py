"""Tests for email scheduling jobs."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.event.jobs import add_event, add_recipients, dt_utc


@patch("app.event.jobs.add_recipients")
@patch("app.event.jobs.dt_utc")
@patch("app.database.db.session.add")
@patch("app.database.db.session.commit")
@patch("app.event.jobs.Event")
def test_add_event(
    mock_event_class,
    mock_commit,
    mock_add,
    mock_dt_utc,
    mock_add_recipients,
    mock_redis,
):
    """Test adding an event to the scheduler."""
    # Setup mocks
    mock_dt_utc.return_value = datetime(2025, 5, 10, 12, 0, 0)
    mock_add_recipients.return_value = ["test@example.com"]

    # Mock Event instance
    mock_event = MagicMock()
    mock_event.id = 12345  # Set a dummy event ID
    mock_event_class.return_value = mock_event

    # Test data
    event_data = {
        "subject": "Test Email",
        "content": "This is a test",
        "timestamp": "10 May 2025 12:00 +08",
        "recipients": "test@example.com",
    }

    # Call function
    print("Before add_event call")
    result = add_event(event_data)
    print(f"Result from add_event: {result}")

    # Assertions
    print(f"mock_add called: {mock_add.called}")
    print(f"mock_commit called: {mock_commit.called}")
    print(f"mock_add_recipients called: {mock_add_recipients.called}")
    assert mock_add.called
    assert mock_commit.called
    assert mock_add_recipients.called
    assert result == 12345  # Should match the mocked event ID


def test_dt_utc_with_timezone():
    """Test dt_utc function with timezone info."""
    dt_str = "10 May 2025 12:00 +08"
    result = dt_utc(dt_str)

    # Expected: 10 May 2025 04:00 UTC (8 hours behind +08)
    assert result.hour == 4
    assert result.day == 10
    assert result.month == 5
    assert result.year == 2025
    assert result.tzinfo is None  # UTC time is stored without tzinfo


def test_dt_utc_without_timezone():
    """Test dt_utc function without timezone info."""
    dt_str = "10 May 2025 12:00"
    result = dt_utc(dt_str)

    # Time should be converted from local to UTC
    assert result is not None
    assert result.tzinfo is None


def test_add_recipients():
    """Test adding recipients to the database."""
    with patch("app.database.db.session.add") as mock_add:
        with patch("app.database.db.session.commit") as mock_commit:
            recipients = "test1@example.com, test2@example.com"
            event_id = 1

            result = add_recipients(recipients, event_id)

            assert len(result) == 2
            assert "test1@example.com" in result
            assert "test2@example.com" in result
            assert mock_add.call_count == 2
            assert mock_commit.call_count == 1
