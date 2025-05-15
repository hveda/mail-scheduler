"""Core data models for the application.

This module contains the Event and Recipient models.
"""
from app.database import db
from datetime import datetime, UTC
from typing import Optional, List


class Event(db.Model):
    """Event model for scheduled emails."""

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    _email_subject = db.Column('email_subject', db.String, nullable=False)
    _email_content = db.Column('email_content', db.String)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(UTC))
    _is_done = db.Column('is_done', db.Boolean, nullable=False, default=False)
    done_at = db.Column(db.DateTime, nullable=True)
    recipients = db.relationship('Recipient', backref='event', lazy='dynamic')

    def __init__(self,
                 email_subject: str,
                 email_content: str,
                 timestamp: datetime,
                 created_at: Optional[datetime] = None,
                 is_done: Optional[bool] = False,
                 done_at: Optional[datetime] = None) -> None:
        """
        Initialize an Event instance.

        Args:
            email_subject: Subject line of the email
            email_content: Body content of the email
            timestamp: When to send the email
            created_at: When the event was created (defaults to now)
            is_done: Whether the email has been sent
            done_at: When the email was sent
        """
        self.email_subject = email_subject
        self.email_content = email_content
        self.timestamp = timestamp
        if created_at:
            self.created_at = created_at
        self.is_done = is_done
        self.done_at = done_at

    @property
    def email_subject(self) -> str:
        """Get the email subject."""
        return self._email_subject

    @email_subject.setter
    def email_subject(self, value: str) -> None:
        """Set the email subject."""
        self._email_subject = value

    @property
    def email_content(self) -> str:
        """Get the email content."""
        return self._email_content

    @email_content.setter
    def email_content(self, value: str) -> None:
        """Set the email content."""
        self._email_content = value

    @property
    def is_done(self) -> bool:
        """Check if the event is done."""
        return self._is_done

    @is_done.setter
    def is_done(self, value: bool) -> None:
        """Set the event as done or not."""
        self._is_done = value
        if value and not self.done_at:
            self.done_at = datetime.now(UTC)

    def __repr__(self) -> str:
        """String representation of the event."""
        return f"<Event {self.id}: {self.email_subject}>"


class Recipient(db.Model):
    """Recipient model for event recipients."""

    __tablename__ = 'recipients'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'events.id'), nullable=False)

    def __init__(self, email: str, name: Optional[str] = None, event_id: Optional[int] = None) -> None:
        """
        Initialize a Recipient instance.

        Args:
            email: Email address of the recipient
            name: Name of the recipient (optional)
            event_id: ID of the associated event
        """
        self.email = email
        self.name = name
        if event_id:
            self.event_id = event_id

    def __repr__(self) -> str:
        """String representation of the recipient."""
        if self.name:
            return f"<Recipient {self.id}: {self.name} ({self.email})>"
        return f"<Recipient {self.id}: {self.email}>"
