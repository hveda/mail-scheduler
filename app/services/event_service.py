"""Event service class implementation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Union, cast

from markupsafe import Markup

from app.database import db
from app.database.models import Event
from app.services.base import BaseService
from app.utils.security import safe_error_message


class EventService(BaseService[Event]):
    """Service class for managing events."""

    @classmethod
    def get_all(cls) -> List[Event]:
        """
        Get all events from the database.

        Returns:
            List of Event objects
        """
        # Check if the Event model has a user relationship before trying to
        # load it
        # This makes the method more robust and backwards compatible
        if hasattr(Event, "user"):
            return cast(
                List[Event], Event.query.options(db.joinedload(Event.user)).all()
            )
        return cast(List[Event], Event.query.all())

    # Legacy adapter for backward compatibility
    @classmethod
    def get_all_events(cls) -> List[Event]:
        """Legacy adapter method for get_all()."""
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
        return cast(Optional[Event], Event.query.get(item_id))

    # Legacy adapter for backward compatibility
    @classmethod
    def get_event_by_id(cls, event_id: int) -> Optional[Event]:
        """Legacy adapter method for get_by_id()."""
        return cls.get_by_id(event_id)

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Union[int, Markup]:
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
                email_subject=data.get("name", ""),
                email_content=data.get("notes", ""),
                # This should be adjusted based on your needs
                timestamp=datetime.now(UTC),
                created_at=datetime.now(UTC),
                is_done=False,
                done_at=None,
            )

            # Save to database
            db.session.add(new_event)
            db.session.commit()

            return cast(int, new_event.id)
        except Exception as e:
            db.session.rollback()
            return safe_error_message(e)

    # Legacy adapter for backward compatibility
    @classmethod
    def create_event(cls, data: Dict[str, Any]) -> Union[int, Markup]:
        """Legacy adapter method for create()."""
        return cls.create(data)

    @classmethod
    def update(cls, item_id: int, data: Dict[str, Any]) -> Union[bool, Markup]:
        """
        Update an existing event.

        Args:
            item_id: ID of the event to update
            data: Dictionary containing updated event data

        Returns:
            True if successful, error message if not
        """
        try:
            event = Event.query.get(item_id)
            if not event:
                return Markup("<strong>Error!</strong> Event does not exist.")

            # Update event attributes
            event.email_subject = data.get("name", event.email_subject)
            event.email_content = data.get("notes", event.email_content)

            # Save changes
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return safe_error_message(e)

    # Legacy adapter for backward compatibility
    @classmethod
    def update_event(cls, event_id: int, data: Dict[str, Any]) -> Union[bool, Markup]:
        """Legacy adapter method for update()."""
        return cls.update(event_id, data)

    @classmethod
    def delete(cls, item_id: int) -> Union[bool, Markup]:
        """
        Delete an event.

        Args:
            item_id: ID of the event to delete

        Returns:
            True if successful, error message if not
        """
        try:
            event = Event.query.get(item_id)
            if not event:
                return Markup("<strong>Error!</strong> Event does not exist.")

            # Delete the event
            db.session.delete(event)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return safe_error_message(e)

    # Legacy adapter for backward compatibility
    @classmethod
    def delete_event(cls, event_id: int) -> Union[bool, Markup]:
        """Legacy adapter method for delete()."""
        return cls.delete(event_id)
