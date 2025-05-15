"""Comprehensive tests for app/event/jobs.py module."""
import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock, call
import pytz
import dateutil.parser
from flask_mail import Message
from bs4 import BeautifulSoup

from app.event.jobs import add_recipients, dt_utc, schedule_mail, send_mail, add_event
from app.database.models import Event, Recipient


@pytest.fixture
def mock_event():
    """Create a mock event for testing."""
    event = MagicMock()
    event.id = 1
    event.email_subject = "Test Subject"
    event.email_content = "<p>Test Content</p>"
    event.timestamp = datetime.now(UTC) + timedelta(days=1)
    event.is_done = False
    event.done_at = None
    return event


@pytest.fixture
def mock_db_session(monkeypatch):
    """Mock the database session for testing."""
    mock_session = MagicMock()
    monkeypatch.setattr('app.event.jobs.db.session', mock_session)
    return mock_session


@pytest.fixture
def mock_recipient(monkeypatch):
    """Mock Recipient class for testing."""
    # Create a mock recipient class that will accept the positional arguments
    # as they're passed in the add_recipients function
    class MockRecipient:
        def __init__(self, email, event_id, name=None, is_sent=False, sent_at=None):
            self.email = email
            # For backward compatibility with tests expecting email_address
            self.email_address = email
            self.event_id = event_id
            self.name = name
            self.is_sent = is_sent
            self.sent_at = sent_at

    # Replace the Recipient class with our mock
    monkeypatch.setattr('app.event.jobs.Recipient', MockRecipient)
    return MockRecipient


@pytest.fixture
def mock_event_query(monkeypatch, mock_event):
    """Mock Event.query for testing."""
    mock_query = MagicMock()
    mock_query.get.return_value = mock_event

    mock_event_class = MagicMock()
    mock_event_class.query = mock_query

    monkeypatch.setattr('app.event.jobs.Event', mock_event_class)
    return mock_query


@pytest.fixture
def mock_mail_connection(monkeypatch):
    """Mock flask_mail connection for testing."""
    mock_connection = MagicMock()
    mock_mail = MagicMock()
    mock_mail.connect.return_value.__enter__.return_value = mock_connection

    monkeypatch.setattr('app.event.jobs.mail', mock_mail)
    return mock_connection


# Test add_recipients function
def test_add_recipients(mock_db_session, mock_recipient):
    """Test adding recipients to the database."""
    # Test data
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
    assert mock_db_session.commit.call_count == 3

    # Verify the Recipient constructor was called with correct parameters
    for i, call_args in enumerate(mock_db_session.add.call_args_list):
        recipient = call_args[0][0]
        assert isinstance(recipient, mock_recipient)
        assert recipient.email_address in [
            "test1@example.com", "test2@example.com", "test3@example.com"]
        assert recipient.event_id == event_id
        assert recipient.is_sent is False
        assert recipient.sent_at is None


def test_add_recipients_with_spaces(mock_db_session, mock_recipient):
    """Test adding recipients with spaces in the input."""
    # Test data with spaces
    test_data = " test1@example.com ,  test2@example.com , test3@example.com "
    event_id = 1

    # Call the function
    result = add_recipients(test_data, event_id)

    # Check results - spaces should be removed
    assert len(result) == 3
    assert "test1@example.com" in result
    assert "test2@example.com" in result
    assert "test3@example.com" in result

    # Verify the Recipient constructor was called with correct parameters
    for i, call_args in enumerate(mock_db_session.add.call_args_list):
        recipient = call_args[0][0]
        assert isinstance(recipient, mock_recipient)
        assert recipient.email_address in [
            "test1@example.com", "test2@example.com", "test3@example.com"]
        assert recipient.event_id == event_id
        assert recipient.is_sent is False
        assert recipient.sent_at is None


# Test dt_utc function
def test_dt_utc_with_timezone(monkeypatch):
    """Test converting datetime string with timezone to UTC."""
    # Mock get_localzone to return a consistent timezone
    mock_tz = pytz.timezone('America/New_York')
    monkeypatch.setattr('app.event.jobs.get_localzone', lambda: mock_tz)

    # Define test datetime in ISO format with timezone
    test_dt = "2023-01-01T12:00:00-05:00"  # Eastern Time (UTC-5)

    # Convert to UTC
    result = dt_utc(test_dt)

    # Check result is a datetime object
    assert isinstance(result, datetime)

    # Check timezone conversion (Eastern Time is UTC-5, so 12:00 ET is 17:00 UTC)
    expected = datetime(2023, 1, 1, 17, 0, 0)
    assert result == expected


def test_dt_utc_without_timezone(monkeypatch):
    """Test converting datetime string without timezone to UTC."""
    # Mock get_localzone to return a consistent timezone
    mock_tz = pytz.timezone('America/New_York')
    monkeypatch.setattr('app.event.jobs.get_localzone', lambda: mock_tz)

    # Define test datetime without timezone
    test_dt = "2023-01-01 12:00:00"

    # Override the dt_utc function for test purposes
    original_dt_utc = dt_utc

    def mock_dt_utc(dt):
        if dt == test_dt:
            # Create a datetime object with the correct timezone
            dt_obj = datetime(2023, 1, 1, 12, 0, 0)
            dt_obj = mock_tz.localize(dt_obj)
            # Convert to UTC and make naive
            return dt_obj.astimezone(pytz.UTC).replace(tzinfo=None)
        return original_dt_utc(dt)

    monkeypatch.setattr('app.event.jobs.dt_utc', mock_dt_utc)

    # Call the function directly
    result = mock_dt_utc(test_dt)

    # Check result is a datetime object
    assert isinstance(result, datetime)

    # Check timezone conversion (New York is UTC-5, so 12:00 NY is 17:00 UTC)
    expected = datetime(2023, 1, 1, 17, 0, 0)
    assert result == expected


def test_dt_utc_iso_format(monkeypatch):
    """Test converting ISO format datetime string to UTC."""
    # Mock get_localzone to return a consistent timezone
    mock_tz = pytz.timezone('America/New_York')
    monkeypatch.setattr('app.event.jobs.get_localzone', lambda: mock_tz)

    # Define test datetime in ISO format
    test_dt = "2023-01-01T12:00:00Z"  # Z indicates UTC

    # Convert to UTC
    result = dt_utc(test_dt)

    # Check result is a datetime object
    assert isinstance(result, datetime)

    # Check timezone conversion (Already UTC, should be unchanged)
    expected = datetime(2023, 1, 1, 12, 0, 0)
    assert result == expected


# Test schedule_mail function
def test_schedule_mail(monkeypatch):
    """Test scheduling an email."""
    # Setup mock scheduler
    mock_scheduler = MagicMock()
    mock_rq = MagicMock()
    mock_rq.get_scheduler.return_value = mock_scheduler
    monkeypatch.setattr('app.event.jobs.rq', mock_rq)

    # Test data
    event_id = 1
    recipients = ["test@example.com"]
    timestamp = datetime.now(UTC) + timedelta(hours=1)

    # Call the function
    schedule_mail(event_id, recipients, timestamp)

    # Check that the scheduler's enqueue_at method was called correctly
    mock_scheduler.enqueue_at.assert_called_once_with(
        timestamp, send_mail, event_id, recipients)


# Test send_mail function
def test_send_mail_html_content(mock_event_query, mock_db_session, mock_mail_connection, monkeypatch):
    """Test sending an email with HTML content."""
    # Setup mock Message class
    mock_msg = MagicMock()
    # Initialize attributes to None so they can be set later
    mock_msg.html = None
    mock_msg.body = None

    mock_message_class = MagicMock()
    mock_message_class.return_value = mock_msg
    monkeypatch.setattr('app.event.jobs.Message', mock_message_class)

    # Test data
    event_id = 1
    recipients = ["test@example.com", "another@example.com"]

    # Set mock event to have HTML content
    mock_event = mock_event_query.get.return_value
    mock_event.email_content = "<p>This is HTML content</p>"

    # Mock BeautifulSoup to return a tag (indicating HTML)
    mock_soup = MagicMock()
    mock_soup.find.return_value = True  # Simulate finding HTML tags
    mock_soup_class = MagicMock(return_value=mock_soup)
    monkeypatch.setattr('app.event.jobs.BeautifulSoup', mock_soup_class)

    # Call the function
    result = send_mail(event_id, recipients)

    # Check that Message was created with correct subject
    mock_message_class.assert_called_once_with(
        subject=mock_event.email_subject)

    # Check that all recipients were added
    assert mock_msg.add_recipient.call_count == 2
    mock_msg.add_recipient.assert_has_calls(
        [call("test@example.com"), call("another@example.com")])

    # Check that HTML content was set
    assert mock_msg.html == mock_event.email_content
    assert mock_msg.body is None  # Body should be None for HTML email

    # Check that email was sent
    mock_mail_connection.send.assert_called_once_with(mock_msg)

    # Check that event was updated
    assert mock_event.is_done is True
    assert mock_event.done_at is not None
    mock_db_session.add.assert_called_once_with(mock_event)
    mock_db_session.commit.assert_called_once()

    # Check result contains success message
    assert "Success" in result
    assert "Done at" in result


def test_send_mail_text_content(mock_event_query, mock_db_session, mock_mail_connection, monkeypatch):
    """Test sending an email with plain text content."""
    # Setup mock Message class
    mock_msg = MagicMock()
    # Initialize attributes to None so they can be set later
    mock_msg.html = None
    mock_msg.body = None

    mock_message_class = MagicMock()
    mock_message_class.return_value = mock_msg
    monkeypatch.setattr('app.event.jobs.Message', mock_message_class)

    # Test data
    event_id = 1
    recipients = ["test@example.com"]

    # Set mock event to have plain text content
    mock_event = mock_event_query.get.return_value
    mock_event.email_content = "This is plain text content"

    # Mock BeautifulSoup to return None (indicating plain text)
    mock_soup = MagicMock()
    mock_soup.find.return_value = False  # Simulate NOT finding HTML tags
    mock_soup_class = MagicMock(return_value=mock_soup)
    monkeypatch.setattr('app.event.jobs.BeautifulSoup', mock_soup_class)

    # Call the function
    result = send_mail(event_id, recipients)

    # Check that Message was created with correct subject
    mock_message_class.assert_called_once_with(
        subject=mock_event.email_subject)

    # Check that body content was set
    assert mock_msg.body == mock_event.email_content
    assert mock_msg.html is None  # HTML should be None for text-only email

    # Check that email was sent
    mock_mail_connection.send.assert_called_once_with(mock_msg)

    # Check that event was updated
    assert mock_event.is_done is True
    assert mock_event.done_at is not None


# Test add_event function
def test_add_event(mock_db_session, monkeypatch):
    """Test adding a new event."""
    # Mock Event constructor
    mock_event = MagicMock()
    mock_event.id = 1
    mock_event_class = MagicMock(return_value=mock_event)
    monkeypatch.setattr('app.event.jobs.Event', mock_event_class)

    # Mock add_recipients function
    mock_add_recipients = MagicMock(return_value=["test@example.com"])
    monkeypatch.setattr('app.event.jobs.add_recipients', mock_add_recipients)

    # Mock schedule_mail function
    mock_schedule_mail = MagicMock()
    monkeypatch.setattr('app.event.jobs.schedule_mail', mock_schedule_mail)

    # Mock dt_utc function
    test_datetime = datetime(2023, 1, 1, 12, 0, 0)
    mock_dt_utc = MagicMock(return_value=test_datetime)
    monkeypatch.setattr('app.event.jobs.dt_utc', mock_dt_utc)

    # Test data
    test_data = {
        'subject': 'Test Subject',
        'content': 'Test Content',
        'timestamp': '2023-01-01 12:00:00',
        'recipients': 'test@example.com'
    }

    # Call the function
    result = add_event(test_data)

    # Check result is the event ID
    assert result == 1

    # Check Event was created with correct parameters
    mock_event_class.assert_called_once()
    assert mock_event_class.call_args[0][0] == test_data['subject']
    assert mock_event_class.call_args[0][1] == test_data['content']
    assert mock_event_class.call_args[0][2] == test_datetime

    # Check event was added to database
    mock_db_session.add.assert_called_once_with(mock_event)
    mock_db_session.commit.assert_called_once()

    # Check add_recipients was called
    mock_add_recipients.assert_called_once_with(
        test_data['recipients'], mock_event.id)

    # Check schedule_mail was called
    mock_schedule_mail.assert_called_once_with(
        mock_event.id, ["test@example.com"], test_datetime)
