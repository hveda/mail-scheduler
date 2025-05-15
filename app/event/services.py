"""Service classes for event-related business logic."""
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional, Union

from flask import Markup

from app.database import db
from app.database.models import Event, Recipient
from app.event.jobs import add_recipients, schedule_mail
from app.services.base import BaseService


class EventService(BaseService[Event]):
    """Service class for managing events."""

    @classmethod
    def get_all(cls) -> List[Event]:
        """
        Get all events from the database.

        Returns:
            List of Event objects
        """
        return Event.query.all()

    # Legacy method for backwards compatibility
    @classmethod
    def get_all_events(cls) -> List[Event]:
        """Legacy method, use get_all() instead."""
        return cls.get_all()

    @classmethod
    def get_by_id(cls, item_id: int) -> Optional[Event]:
        """
        Get an event by its ID.

        Args:
            item_id: The ID of the event to retrieve

        Returns:
            Event object if found, None otherwise
        """
        return Event.query.get(item_id)

    # Legacy method for backwards compatibility
    @classmethod
    def get_event_by_id(cls, event_id: int) -> Optional[Event]:
        """Legacy method, use get_by_id() instead."""
        return cls.get_by_id(event_id)

    @staticmethod
    def create_event(data: Dict[str, Any]) -> Union[int, Markup]:
        """
        Create a new event from form data.

        Args:
            data: Dictionary containing event data

        Returns:
            Event ID if successful, error message if not
        """
        try:
            # Create a new event object
            new_event = Event(
                email_subject=data.get('name', ''),
                email_content=data.get('notes', ''),
                # This should be adjusted based on your needs
                timestamp=datetime.now(UTC),
                created_at=datetime.now(UTC),
                is_done=False,
                done_at=None
            )

            # Save to database
            db.session.add(new_event)
            db.session.commit()

            return new_event.id
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to add event: {str(e)}")

    @staticmethod
    def update_event(event_id: int, data: Dict[str, Any]) -> Union[bool, Markup]:
        """
        Update an existing event.

        Args:
            event_id: ID of the event to update
            data: Dictionary containing updated event data

        Returns:
            True if successful, error message if not
        """
        try:
            event = Event.query.get(event_id)
            if not event:
                return Markup("<strong>Error!</strong> Event does not exist.")

            # Update event attributes
            event.email_subject = data.get('name', event.email_subject)
            event.email_content = data.get('notes', event.email_content)

            # Save changes
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to update event: {str(e)}")

    @staticmethod
    def delete_event(event_id: int) -> Union[bool, Markup]:
        """
        Delete an event.

        Args:
            event_id: ID of the event to delete

        Returns:
            True if successful, error message if not
        """
        try:
            event = Event.query.get(event_id)
            if not event:
                return Markup("<strong>Error!</strong> Event does not exist.")

            # Delete the event
            db.session.delete(event)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to delete event: {str(e)}")
