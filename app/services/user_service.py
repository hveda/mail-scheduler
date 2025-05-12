"""User service class implementation."""

from typing import List, Dict, Any, Optional, Union

from app.database import db
from app.database.models.user import User
from app.services.base import BaseService


class UserService(BaseService[User]):
    """Service class for managing users."""
    
    @classmethod
    def get_all(cls) -> List[User]:
        """
        Get all users from the database.
        
        Returns:
            List of User objects
        """
        return User.query.all()
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.get(user_id)
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional[User]:
        """
        Get a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[User]:
        """
        Get a user by their email.
        
        Args:
            email: The email to search for
            
        Returns:
            User object if found, None otherwise
        """
        return User.query.filter_by(email=email).first()
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Union[int, str]:
        """
        Create a new user.
        
        Args:
            data: Dictionary containing user information
            
        Returns:
            ID of the created user
            
        Raises:
            ValueError: If the user cannot be created
        """
        if cls.get_by_username(data.get('username')):
            raise ValueError(f"Username '{data.get('username')}' is already taken")
        
        if cls.get_by_email(data.get('email')):
            raise ValueError(f"Email '{data.get('email')}' is already taken")
        
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'user')
        )
        
        # Set password if provided
        if 'password' in data:
            user.password = data['password']
        
        db.session.add(user)
        db.session.commit()
        
        return user.id
    
    @classmethod
    def update(cls, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing user.
        
        Args:
            user_id: ID of the user to update
            data: Dictionary containing updated user information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the user cannot be updated
        """
        user = cls.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check username uniqueness if changed
        if 'username' in data and data['username'] != user.username:
            existing_user = cls.get_by_username(data['username'])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"Username '{data['username']}' is already taken")
        
        # Check email uniqueness if changed
        if 'email' in data and data['email'] != user.email:
            existing_user = cls.get_by_email(data['email'])
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"Email '{data['email']}' is already taken")
        
        # Update fields
        for key, value in data.items():
            if key == 'password':
                user.password = value
            elif hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return True
    
    @classmethod
    def delete(cls, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if successful, False otherwise
        """
        user = cls.get_by_id(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
