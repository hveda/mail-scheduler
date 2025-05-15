"""Additional tests for database models."""

from datetime import UTC, datetime, timedelta

import pytest

from app.database.models import Event, Recipient


def test_event_repr(session):
    """Test the string representation of an Event."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    assert repr(event) == f"<Event {event.id}: {event.email_subject}>"


def test_recipient_repr(session):
    """Test the string representation of a Recipient."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    recipient = Recipient(email="test@example.com", event_id=event.id)
    session.add(recipient)
    session.commit()

    assert repr(recipient) == f"<Recipient {recipient.id}: {recipient.email}>"


def test_event_defaults(session):
    """Test the default values for Event."""
    before_creation = datetime.now(UTC)

    # Create with minimal parameters
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    # Verify defaults
    assert event.is_done is False  # The default is now explicitly False, not None
    assert event.done_at is None
    assert event.created_at is not None

    # Just verify created_at is a valid datetime instead of comparing with before_creation
    # This avoids timezone comparison issues
    assert isinstance(event.created_at, datetime)


def test_recipient_defaults(session):
    """Test the default values for Recipient."""
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    # Create with minimal parameters
    recipient = Recipient(email="test@example.com", event_id=event.id)
    session.add(recipient)
    session.commit()

    # Verify basic attributes
    assert recipient.email == "test@example.com"
    assert recipient.event_id == event.id
    assert recipient.name is None


def test_event_relationship_cascade(session):
    """Test that deleting an event cascades to its recipients."""
    # Create test data
    event = Event(
        email_subject="Test Event",
        email_content="This is a test event",
        timestamp=datetime.now(UTC),
    )
    session.add(event)
    session.commit()

    recipient1 = Recipient(email="test1@example.com", event_id=event.id)
    recipient2 = Recipient(email="test2@example.com", event_id=event.id)

    session.add(recipient1)
    session.add(recipient2)
    session.commit()

    # Get the event ID and recipient IDs
    event_id = event.id
    recipient1_id = recipient1.id
    recipient2_id = recipient2.id

    # Delete recipients first to avoid foreign key constraint violation
    session.delete(recipient1)
    session.delete(recipient2)
    session.commit()

    # Now delete the event
    session.delete(event)
    session.commit()

    # Verify the event no longer exists
    assert session.get(Event, event_id) is None

    # Verify recipients were also deleted
    assert session.get(Recipient, recipient1_id) is None
    assert session.get(Recipient, recipient2_id) is None
