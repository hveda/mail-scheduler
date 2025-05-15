"""Integration tests for email sending jobs."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC, timedelta

from app.event.jobs import add_recipients, dt_utc, add_event
from app.database.models import Event, Recipient


def test_add_recipients(session):
    """Test adding recipients to database."""
    # Create a test event
    event = Event(
        email_subject='Test Event',
        email_content='This is a test event',
        timestamp=datetime.now(UTC)
    )
    session.add(event)
    session.commit()

    # Add recipients
    recipients_str = "test1@example.com, test2@example.com, test3@example.com"
    result = add_recipients(recipients_str, event.id)

    # Verify recipients were added to database
    db_recipients = session.query(Recipient).filter_by(event_id=event.id).all()

    # Check results
    assert len(result) == 3
    assert len(db_recipients) == 3

    # Check email addresses
    email_addresses = [r.email_address for r in db_recipients]
    assert "test1@example.com" in email_addresses
    assert "test2@example.com" in email_addresses
    assert "test3@example.com" in email_addresses


def test_dt_utc_with_timezone():
    """Test datetime conversion to UTC with timezone info."""
    # Test with timezone info
    dt_str = "2025-05-10 12:00:00+08:00"  # UTC+8
    result = dt_utc(dt_str)

    # Expected: 2025-05-10 04:00:00 UTC (12:00 UTC+8 is 04:00 UTC)
    # But we get a naive datetime, so check the hour
    assert result.year == 2025
    assert result.month == 5
    assert result.day == 10
    assert result.hour == 4
    assert result.minute == 0
    assert result.second == 0
    assert result.tzinfo is None  # Should be converted to naive UTC


def test_dt_utc_without_timezone():
    """Test datetime conversion to UTC without timezone info."""
    # Test without timezone info (assumes local timezone)
    dt_str = "2025-05-10 12:00:00"
    result = dt_utc(dt_str)

    # Since this depends on local timezone, we just check it's a valid datetime
    assert isinstance(result, datetime)
    assert result.tzinfo is None  # Should be naive UTC


@patch('app.event.jobs.schedule_mail')
def test_add_event(mock_schedule, session):
    """Test adding a new event."""
    # Test data
    data = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': '2025-05-10 12:00:00',
        'recipients': 'test1@example.com, test2@example.com'
    }

    # Call function
    event_id = add_event(data)

    # Verify event was created
    event = session.query(Event).get(event_id)
    assert event is not None
    assert event.email_subject == 'Test Subject'
    assert event.email_content == 'Test Content'

    # Verify recipients were added
    recipients = session.query(Recipient).filter_by(event_id=event_id).all()
    assert len(recipients) == 2

    # Verify schedule_mail was called
    assert mock_schedule.called
