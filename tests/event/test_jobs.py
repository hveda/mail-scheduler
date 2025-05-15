"""Comprehensive tests for app/event/jobs.py."""
import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock
import pytz

from app.event.jobs import add_recipients, dt_utc, schedule_mail, send_mail
from app.database.models import Event, Recipient


@pytest.fixture
def mock_event(app):
    """Create a mock event for testing."""
    with app.app_context():
        event = Event(dict(
            email_subject="Test Subject",
            email_content="<p>Test Content</p>",
            timestamp=datetime.now(UTC) + timedelta(days=1)
        ))
        return event


@pytest.fixture
def mock_db_session(monkeypatch):
    """Mock the database session for testing."""
    mock_session = MagicMock()
    monkeypatch.setattr('app.event.jobs.db.session', mock_session)
    return mock_session


# Test add_recipients function
def test_add_recipients(app, mock_db_session):
    """Test adding recipients to the database."""
    with app.app_context():
        test_data = "test1@example.com, test2@example.com, test3@example.com"
        event_id = 1

        # Call the function
        result = add_recipients(test_data, event_id)

        # Check results
        assert len(result) == 3
        assert "test1@example.com" in result
        assert "test2@example.com" in result
        assert "test3@example.com" in result

        # Check that recipients were added to the database
        assert mock_db_session.add.call_count == 3
        assert mock_db_session.commit.call_count == 1


# Test dt_utc function
def test_dt_utc_with_timezone(monkeypatch):
    """Test converting datetime string with timezone to UTC."""
    # Mock get_localzone to return a consistent timezone
    mock_tz = pytz.timezone('America/New_York')
    monkeypatch.setattr('app.event.jobs.get_localzone', lambda: mock_tz)

    # Define test datetime in a specific timezone
    test_dt = "2023-01-01 12:00:00 US/Pacific"

    # Convert to UTC
    result = dt_utc(test_dt)

    # Check result is a datetime object
    assert isinstance(result, datetime)

    # Check timezone conversion (Pacific is UTC-8, so 12:00 Pacific is 20:00 UTC)
    expected = datetime(2023, 1, 1, 20, 0, 0)
    assert result == expected


def test_dt_utc_without_timezone(monkeypatch):
    """Test converting datetime string without timezone to UTC."""
    # Mock get_localzone to return a consistent timezone
    mock_tz = pytz.timezone('America/New_York')
    monkeypatch.setattr('app.event.jobs.get_localzone', lambda: mock_tz)

    # Define test datetime without timezone
    test_dt = "2023-01-01 12:00:00"

    # Convert to UTC (assumes local timezone is New York, UTC-5)
    result = dt_utc(test_dt)

    # Check result is a datetime object
    assert isinstance(result, datetime)

    # Check timezone conversion (New York is UTC-5, so 12:00 NY is 17:00 UTC)
    expected = datetime(2023, 1, 1, 17, 0, 0)
    assert result == expected


# Test schedule_mail function
def test_schedule_mail(mock_redis):
    """Test scheduling an email."""
    event_id = 1
    recipients = ["test@example.com"]
    timestamp = datetime.now(UTC) + timedelta(hours=1)

    # Call the function
    schedule_mail(event_id, recipients, timestamp)

    # Check that the scheduler's enqueue_at method was called
    assert mock_redis.enqueue_at.called
    mock_redis.enqueue_at.assert_called_with(
        timestamp, send_mail, event_id, recipients)


# Test send_mail function
@patch('app.event.jobs.Message')
def test_send_mail(mock_message_class, app, mock_event, monkeypatch):
    """Test sending an email."""
    # Setup
    mock_msg = MagicMock()
    mock_message_class.return_value = mock_msg

    # Mock Event.query.get to return our mock event
    mock_query = MagicMock()
    mock_query.get.return_value = mock_event
    mock_event_class = MagicMock()
    mock_event_class.query = mock_query
    monkeypatch.setattr('app.event.jobs.Event', mock_event_class)

    # Mock mail.send
    mock_mail = MagicMock()
    monkeypatch.setattr('app.event.jobs.mail', mock_mail)

    # Mock recipient query and update
    mock_recipient = MagicMock()
    mock_recipient_query = MagicMock()
    mock_recipient_query.filter_by.return_value.first.return_value = mock_recipient
    mock_recipient_class = MagicMock()
    mock_recipient_class.query = mock_recipient_query
    monkeypatch.setattr('app.event.jobs.Recipient', mock_recipient_class)

    # Mock db session
    mock_db_session = MagicMock()
    monkeypatch.setattr('app.event.jobs.db.session', mock_db_session)

    # Call the function
    with app.app_context():
        result = send_mail(1, ["test@example.com"])

    # Check that email was created with correct subject
    mock_message_class.assert_called_once_with(
        subject=mock_event.email_subject)

    # Check that email recipients were added
    assert mock_msg.add_recipient.called

    # Check that email was sent
    assert mock_mail.send.called

    # Check that recipient was updated in the database
    assert mock_db_session.commit.called

    # Check result contains success message
    assert "Email sent" in result
    assert "to test@example.com" in result
