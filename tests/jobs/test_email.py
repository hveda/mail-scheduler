"""Tests for email sending functionality."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.database.models import Event, Recipient
from app.event.jobs import send_mail


@patch("app.event.jobs.BeautifulSoup")
@patch("app.extensions.mail.connect")
@patch("app.database.db.session.add")
@patch("app.database.db.session.commit")
def test_send_mail_plain_text(mock_commit, mock_add, mock_mail_connect, mock_bs, db):
    """Test sending a plain text email."""
    # Mock Event query
    mock_event = MagicMock()
    mock_event.email_subject = "Test Subject"
    mock_event.email_content = "This is a plain text email"

    # Create a mock query result
    with patch("app.event.jobs.Event.query") as mock_query:
        mock_query_obj = MagicMock()
        mock_query_obj.get.return_value = mock_event
        mock_query.return_value = mock_query_obj

        # Mock BeautifulSoup to indicate no HTML
        mock_soup = MagicMock()
        mock_soup.find.return_value = None
        mock_bs.return_value = mock_soup

        # Mock mail connection
        mock_conn = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_mail_connect.return_value = mock_context

        # Call the function
        result = send_mail(1, ["test@example.com"])

        # Assertions
        assert "Success" in result
        assert mock_conn.send.called
        assert mock_add.called
        assert mock_commit.called


@patch("app.event.jobs.BeautifulSoup")
@patch("app.extensions.mail.connect")
@patch("app.database.db.session.add")
@patch("app.database.db.session.commit")
def test_send_mail_html(mock_commit, mock_add, mock_mail_connect, mock_bs, db):
    """Test sending an HTML email."""
    # Mock Event query
    mock_event = MagicMock()
    mock_event.email_subject = "Test Subject"
    mock_event.email_content = "<p>This is an HTML email</p>"

    # Create a mock query result
    with patch("app.event.jobs.Event.query") as mock_query:
        mock_query_obj = MagicMock()
        mock_query_obj.get.return_value = mock_event
        mock_query.return_value = mock_query_obj

        # Mock BeautifulSoup to indicate HTML content
        mock_soup = MagicMock()
        mock_soup.find.return_value = True  # Indicate HTML content
        mock_bs.return_value = mock_soup

        # Mock mail connection
        mock_conn = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_mail_connect.return_value = mock_context

        # Call the function
        result = send_mail(1, ["test@example.com"])

        # Assertions
        assert "Success" in result
        assert mock_conn.send.called
        assert mock_add.called
        assert mock_commit.called


@patch("app.event.jobs.Event.query")
@patch("app.extensions.mail.connect")
@patch("app.database.db.session.add")
@patch("app.database.db.session.commit")
def test_send_mail_multiple_recipients(
    mock_commit, mock_add, mock_mail_connect, mock_event_query, db
):
    """Test sending email to multiple recipients."""
    # Setup mock event with actual string content
    mock_event = MagicMock()
    mock_event.email_subject = "Test Subject"
    mock_event.email_content = "Test Content"

    # Mock Event.query.get to return our mock event
    mock_event_query.get.return_value = mock_event

    # Create a mock Message class
    mock_message = MagicMock()

    with patch("app.event.jobs.Message", return_value=mock_message):
        # Mock mail connection
        mock_conn = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_conn
        mock_mail_connect.return_value = mock_context

        # Call the function with multiple recipients
        recipients = [
            "test1@example.com",
            "test2@example.com",
            "test3@example.com",
        ]
        result = send_mail(1, recipients)

        # Assertions
        assert "Success" in result
        assert mock_add.called
        assert mock_commit.called

        # Verify recipients were added
        assert mock_message.add_recipient.call_count == 3
