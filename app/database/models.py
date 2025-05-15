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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Define relationship with Recipient model
    recipients = db.relationship('Recipient', backref='event', lazy='dynamic')

    def __init__(self,
                 email_subject: str,
                 email_content: str,
                 timestamp: datetime,
                 created_at: Optional[datetime] = None,
                 is_done: Optional[bool] = False,
                 done_at: Optional[datetime] = None,
                 user_id: Optional[int] = None) -> None:
        """
        Initialize an Event instance.

        Args:
            email_subject: Subject line of the email
            email_content: Body content of the email
            timestamp: When to send the email
            created_at: When the event was created (defaults to now)
            is_done: Whether the email has been sent
            done_at: When the email was sent
            user_id: ID of the user who created this event
        """
        self.email_subject = email_subject
        self.email_content = email_content
        self.timestamp = timestamp
        self.created_at = created_at or datetime.now(UTC)
        self.is_done = is_done
        self.done_at = done_at
        self.user_id = user_id

    @property
    def email_subject(self) -> str:
        """Get the email subject."""
        return self._email_subject

    @email_subject.setter
    def email_subject(self, value: str) -> None:
        """
        Set the email subject.

        Args:
            value: The new subject value

        Raises:
            ValueError: If value is empty
        """
        if not value:
            raise ValueError("Email subject cannot be empty")
        self._email_subject = value

    @property
    def email_content(self) -> str:
        """Get the email content."""
        return self._email_content

    @email_content.setter
    def email_content(self, value: str) -> None:
        """
        Set the email content.

        Args:
            value: The new content value
        """
        self._email_content = value or ""

    @property
    def is_done(self) -> bool:
        """Get the is_done status."""
        return self._is_done

    @is_done.setter
    def is_done(self, value: bool) -> None:
        """
        Set the is_done status.

        Args:
            value: The new status value

        Note:
            When setting to True, done_at is automatically set to current time
        """
        self._is_done = value
        # Update done_at when marking as done
        if value and not self.done_at:
            self.done_at = datetime.now(UTC)

    def __repr__(self) -> str:
        """String representation of the Event."""
        return f'<Event ID: {self.id}>'


class Recipient(db.Model):
    """Recipient model for email addresses."""

    __tablename__ = 'recipients'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=True)  # Optional recipient name
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    is_sent = db.Column(db.Boolean, nullable=False, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)

    def __init__(self,
                 email_address: str,
                 event_id: int,
                 name: Optional[str] = None,
                 is_sent: Optional[bool] = False,
                 sent_at: Optional[datetime] = None) -> None:
        """
        Initialize a Recipient instance.

        Args:
            email_address: Email address of the recipient
            event_id: ID of the associated event
            name: Name of the recipient (optional)
            is_sent: Whether the email has been sent to this recipient
            sent_at: When the email was sent to this recipient
        """
        self.email_address = email_address
        self.event_id = event_id
        self.name = name
        self.is_sent = is_sent
        self.sent_at = sent_at

    def __repr__(self) -> str:
        """String representation of the Recipient."""
        return f'<ID: {self.id} Email: {self.email_address}>'
