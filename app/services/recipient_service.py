"""Recipient service class implementation."""
from typing import List, Dict, Any, Optional, Union

from markupsafe import Markup

from app.database import db
from app.database.models import Recipient, Event
from app.services.base import BaseService


class RecipientService(BaseService[Recipient]):
    """Service class for managing recipients."""
    
    @classmethod
    def get_all(cls) -> List[Recipient]:
        """
        Get all recipients from the database.
        
        Returns:
            List of Recipient objects
        """
        return Recipient.query.all()
        
    @classmethod
    def get_by_id(cls, item_id: int) -> Optional[Recipient]:
        """
        Get a recipient by its ID.
        
        Args:
            item_id: The ID of the recipient to retrieve
            
        Returns:
            Recipient object if found, None otherwise
        """
        return Recipient.query.get(item_id)
        
    @classmethod
    def get_by_event_id(cls, event_id: int) -> List[Recipient]:
        """
        Get all recipients for a specific event.
        
        Args:
            event_id: The ID of the event
            
        Returns:
            List of Recipient objects for the event
        """
        return Recipient.query.filter_by(event_id=event_id).all()
        
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Union[int, Markup]:
        """
        Create a new recipient from form data.
        
        Args:
            data: Dictionary containing recipient data
            
        Returns:
            Recipient ID if successful, error message if not
        """
        try:
            # Create a new recipient object
            new_recipient = Recipient(
                name=data.get('name', ''),
                email=data.get('email', ''),
                event_id=data.get('event_id')
            )
            
            # Save to database
            db.session.add(new_recipient)
            db.session.commit()
            
            return new_recipient.id
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to add recipient: {str(e)}")
    
    @classmethod
    def update(cls, item_id: int, data: Dict[str, Any]) -> Union[bool, Markup]:
        """
        Update an existing recipient.
        
        Args:
            item_id: ID of the recipient to update
            data: Dictionary containing updated recipient data
            
        Returns:
            True if successful, error message if not
        """
        try:
            recipient = Recipient.query.get(item_id)
            if not recipient:
                return Markup("<strong>Error!</strong> Recipient does not exist.")
                
            # Update recipient attributes
            if 'name' in data:
                recipient.name = data['name']
            if 'email' in data:
                recipient.email = data['email']
            if 'event_id' in data:
                recipient.event_id = data['event_id']
            
            # Save changes
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to update recipient: {str(e)}")
    
    @classmethod
    def delete(cls, item_id: int) -> Union[bool, Markup]:
        """
        Delete a recipient.
        
        Args:
            item_id: ID of the recipient to delete
            
        Returns:
            True if successful, error message if not
        """
        try:
            recipient = Recipient.query.get(item_id)
            if not recipient:
                return Markup("<strong>Error!</strong> Recipient does not exist.")
                
            # Delete the recipient
            db.session.delete(recipient)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return Markup(f"<strong>Error!</strong> Unable to delete recipient: {str(e)}")
            
    @classmethod
    def bulk_create(cls, recipients: List[Dict[str, Any]], event_id: int) -> Union[int, Markup]:
        """
        Create multiple recipients for an event.
        
        Args:
            recipients: List of dictionaries containing recipient data
            event_id: The ID of the event to associate recipients with
            
        Returns:
            Number of recipients created if successful, error message if not
        """
        try:
            count = 0
            for recipient_data in recipients:
                # Add event_id to each recipient
                recipient_data['event_id'] = event_id
                result = cls.create(recipient_data)
                if isinstance(result, int):
                    count += 1
                    
            return count
        except Exception as e:
            return Markup(f"<strong>Error!</strong> Unable to add recipients: {str(e)}")
