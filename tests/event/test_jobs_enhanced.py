"""Comprehensive tests for app/event/jobs.py."""
import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timedelta, UTC
import pytz
from bs4 import BeautifulSoup

from app.event.jobs import add_recipients, dt_utc, schedule_mail, send_mail, add_event
from app.database.models import Event, Recipient


class TestAddRecipients:
    """Tests for the add_recipients function."""

    def test_add_recipients_single(self, session):
        """Test adding a single recipient."""
        # Setup
        recipient_data = "test@example.com"
        event_id = 1

        # Execute
        result = add_recipients(recipient_data, event_id)

        # Verify
        assert result == ["test@example.com"]
        recipients = Recipient.query.filter_by(event_id=event_id).all()
        assert len(recipients) == 1
        assert recipients[0].email == "test@example.com"
        assert recipients[0].event_id == event_id
        assert recipients[0].is_sent is False
        assert recipients[0].sent_at is None

    def test_add_recipients_multiple(self, session):
        """Test adding multiple recipients."""
        # Setup
        recipient_data = "test1@example.com, test2@example.com,test3@example.com"
        event_id = 2

        # Execute
        result = add_recipients(recipient_data, event_id)

        # Verify
        assert result == ["test1@example.com",
                          "test2@example.com", "test3@example.com"]
        recipients = Recipient.query.filter_by(event_id=event_id).all()
        assert len(recipients) == 3
        emails = [r.email for r in recipients]
        assert "test1@example.com" in emails
        assert "test2@example.com" in emails
        assert "test3@example.com" in emails

    def test_add_recipients_with_spaces(self, session):
        """Test adding recipients with spaces in the input string."""
        # Setup
        recipient_data = " test1@example.com,  test2@example.com , test3@example.com"
        event_id = 3

        # Execute
        result = add_recipients(recipient_data, event_id)

        # Verify
        assert result == ["test1@example.com",
                          "test2@example.com", "test3@example.com"]
        recipients = Recipient.query.filter_by(event_id=event_id).all()
        assert len(recipients) == 3


class TestDtUtc:
    """Tests for the dt_utc function."""

    def test_dt_utc_with_timezone(self):
        """Test conversion of datetime with timezone to UTC."""
        # Setup - Create a timezone-aware datetime
        local_tz = pytz.timezone('America/New_York')
        dt_str = "2023-05-10T15:30:00-04:00"  # New York time with offset

        # Execute
        result = dt_utc(dt_str)

        # Verify - Result should be UTC equivalent (19:30 UTC)
        expected = datetime(2023, 5, 10, 19, 30, 0)
        assert result == expected

    def test_dt_utc_without_timezone(self, monkeypatch):
        """Test conversion of datetime without timezone to UTC."""
        # Setup - Mock local timezone to ensure consistent test
        mock_local_tz = pytz.timezone('Europe/London')
        monkeypatch.setattr('app.event.jobs.get_localzone',
                            lambda: mock_local_tz)

        # Test with a datetime without timezone
        dt_str = "2023-05-10 15:30:00"

        # Execute
        result = dt_utc(dt_str)

        # Verify - If local is London (UTC+1 in summer), should convert to 14:30 UTC
        # Note: This is timezone-dependent, so mocking is necessary
        expected_dt = datetime(2023, 5, 10, 14, 30, 0)
        assert result == expected_dt

    def test_dt_utc_different_formats(self):
        """Test dt_utc with different datetime formats."""
        # ISO format
        dt_str1 = "2023-05-10T15:30:00Z"  # UTC
        result1 = dt_utc(dt_str1)
        assert result1 == datetime(2023, 5, 10, 15, 30, 0)

        # RFC 2822 format
        dt_str2 = "Wed, 10 May 2023 15:30:00 +0000"  # UTC
        result2 = dt_utc(dt_str2)
        assert result2 == datetime(2023, 5, 10, 15, 30, 0)


class TestScheduleMail:
    """Tests for the schedule_mail function."""

    def test_schedule_mail(self, mock_redis):
        """Test scheduling an email."""
        # Setup
        event_id = 1
        recipients = ["test@example.com"]
        timestamp = datetime.now(UTC) + timedelta(hours=1)

        # Execute
        schedule_mail(event_id, recipients, timestamp)

        # Verify
        # Assert that scheduler.enqueue_at was called with correct args
        # This depends on the mock_redis fixture in conftest.py
        assert mock_redis.enqueue_at.assert_called_once_with(
            timestamp, send_mail, event_id, recipients)


class TestSendMail:
    """Tests for the send_mail function."""

    @patch('app.event.jobs.Event')
    @patch('app.event.jobs.Message')
    @patch('app.event.jobs.mail')
    @patch('app.event.jobs.db')
    def test_send_mail_text_content(self, mock_db, mock_mail, mock_message, mock_event):
        """Test sending an email with text content."""
        # Setup
        event_id = 1
        recipients = ["test@example.com"]

        # Mock event
        mock_event_obj = MagicMock()
        mock_event_obj.email_subject = "Test Subject"
        mock_event_obj.email_content = "Test content with no HTML"
        mock_event.query.get.return_value = mock_event_obj

        # Mock message
        mock_msg = MagicMock()
        mock_message.return_value = mock_msg

        # Mock mail connection
        mock_conn = MagicMock()
        mock_mail.connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = send_mail(event_id, recipients)

        # Verify
        mock_message.assert_called_once_with(subject="Test Subject")
        mock_msg.add_recipient.assert_called_once_with("test@example.com")
        # For text content, only set body not html
        assert hasattr(mock_msg, 'body')
        assert mock_msg.body == "Test content with no HTML"
        mock_conn.send.assert_called_once_with(mock_msg)
        assert mock_event_obj.is_done is True
        assert mock_event_obj.done_at is not None
        mock_db.session.add.assert_called_once_with(mock_event_obj)
        mock_db.session.commit.assert_called_once()
        assert "Success" in result

    @patch('app.event.jobs.Event')
    @patch('app.event.jobs.Message')
    @patch('app.event.jobs.mail')
    @patch('app.event.jobs.db')
    def test_send_mail_html_content(self, mock_db, mock_mail, mock_message, mock_event):
        """Test sending an email with HTML content."""
        # Setup
        event_id = 1
        recipients = ["test@example.com"]

        # Mock event
        mock_event_obj = MagicMock()
        mock_event_obj.email_subject = "Test Subject"
        mock_event_obj.email_content = "<html><body><p>Test HTML content</p></body></html>"
        mock_event.query.get.return_value = mock_event_obj

        # Mock message
        mock_msg = MagicMock()
        mock_message.return_value = mock_msg

        # Mock mail connection
        mock_conn = MagicMock()
        mock_mail.connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = send_mail(event_id, recipients)

        # Verify
        mock_message.assert_called_once_with(subject="Test Subject")
        mock_msg.add_recipient.assert_called_once_with("test@example.com")
        # For HTML content, only set html not body
        assert hasattr(mock_msg, 'html')
        assert mock_msg.html == "<html><body><p>Test HTML content</p></body></html>"
        mock_conn.send.assert_called_once_with(mock_msg)
        assert mock_event_obj.is_done is True
        assert mock_event_obj.done_at is not None
        mock_db.session.add.assert_called_once_with(mock_event_obj)
        mock_db.session.commit.assert_called_once()
        assert "Success" in result

    @patch('app.event.jobs.Event')
    @patch('app.event.jobs.Message')
    @patch('app.event.jobs.mail')
    @patch('app.event.jobs.db')
    def test_send_mail_multiple_recipients(self, mock_db, mock_mail, mock_message, mock_event):
        """Test sending an email to multiple recipients."""
        # Setup
        event_id = 1
        recipients = ["test1@example.com",
                      "test2@example.com", "test3@example.com"]

        # Mock event
        mock_event_obj = MagicMock()
        mock_event_obj.email_subject = "Test Subject"
        mock_event_obj.email_content = "Test content"
        mock_event.query.get.return_value = mock_event_obj

        # Mock message
        mock_msg = MagicMock()
        mock_message.return_value = mock_msg

        # Mock mail connection
        mock_conn = MagicMock()
        mock_mail.connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = send_mail(event_id, recipients)

        # Verify
        mock_message.assert_called_once_with(subject="Test Subject")
        assert mock_msg.add_recipient.call_count == 3
        mock_conn.send.assert_called_once_with(mock_msg)
        assert "Success" in result


class TestAddEvent:
    """Tests for the add_event function."""

    @patch('app.event.jobs.dt_utc')
    @patch('app.event.jobs.Event')
    @patch('app.event.jobs.db')
    @patch('app.event.jobs.add_recipients')
    @patch('app.event.jobs.schedule_mail')
    def test_add_event(self, mock_schedule, mock_add_recipients, mock_db, mock_event, mock_dt_utc):
        """Test adding a new event."""
        # Setup
        event_data = {
            'subject': 'Test Subject',
            'content': 'Test Content',
            'timestamp': '2023-05-10T15:30:00Z',
            'recipients': 'test@example.com'
        }

        # Mock dt_utc to return a consistent datetime
        timestamp = datetime(2023, 5, 10, 15, 30, 0)
        mock_dt_utc.return_value = timestamp

        # Mock Event constructor
        mock_event_obj = MagicMock()
        mock_event_obj.id = 1
        mock_event.return_value = mock_event_obj

        # Mock add_recipients
        mock_add_recipients.return_value = ['test@example.com']

        # Execute
        result = add_event(event_data)

        # Verify
        mock_dt_utc.assert_called_once_with('2023-05-10T15:30:00Z')
        mock_event.assert_called_once_with(
            'Test Subject', 'Test Content', timestamp, ANY, False, None, None
        )
        mock_db.session.add.assert_called_once_with(mock_event_obj)
        mock_db.session.commit.assert_called_once()
        mock_add_recipients.assert_called_once_with('test@example.com', 1)
        mock_schedule.assert_called_once_with(
            1, ['test@example.com'], timestamp)
        assert result == 1
