"""Tests for database models."""

from datetime import UTC, datetime

import pytest

from app.database.models import Event, Recipient


def test_event_creation(session):
    """Test creating an Event object."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    assert event.id is not None
    assert event.email_subject == "Test Event"
    assert event.email_content == "This is a test event"
    assert isinstance(event.timestamp, datetime)


def test_recipient_creation(session):
    """Test creating a Recipient object."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    recipient = Recipient(
        email="test@example.com",
        event_id=event.id,
    )
    session.add(recipient)
    session.commit()

    assert recipient.id is not None
    assert recipient.email == "test@example.com"
    assert recipient.event_id == event.id


def test_event_recipient_relationship(session):
    """Test the relationship between Event and Recipient."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    recipient1 = Recipient(
        email="test1@example.com",
        event_id=event.id,
    )
    recipient2 = Recipient(
        email="test2@example.com",
        event_id=event.id,
    )

    session.add(recipient1)
    session.add(recipient2)
    session.commit()

    # Refresh the event
    session.refresh(event)

    # Convert the query to a list
    recipients_list = list(event.recipients)
    assert len(recipients_list) == 2
    assert recipient1 in recipients_list
    assert recipient2 in recipients_list
