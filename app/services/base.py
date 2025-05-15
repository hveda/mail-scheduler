"""Base service classes for the application."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Union

from markupsafe import Markup

# Define a generic type variable for our models
T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """Abstract base service class for all service classes."""

    @classmethod
    @abstractmethod
    def get_all(cls) -> List[T]:
        """
        Get all items of a specific type.

        Returns:
            List of items
        """
        pass

    @classmethod
    @abstractmethod
    def get_by_id(cls, item_id: int) -> Optional[T]:
        """
        Get an item by its ID.

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            The item if found, None otherwise
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, data: dict) -> Union[int, Markup]:
        """
        Create a new item.

        Args:
            data: Dictionary containing item data

        Returns:
            ID of the created item if successful, error message otherwise
        """
        pass

    @classmethod
    @abstractmethod
    def update(cls, item_id: int, data: dict) -> Union[bool, Markup]:
        """
        Update an existing item.

        Args:
            item_id: ID of the item to update
            data: Dictionary containing updated item data

        Returns:
            True if successful, error message otherwise
        """
        pass

    @classmethod
    @abstractmethod
    def delete(cls, item_id: int) -> Union[bool, Markup]:
        """
        Delete an item.

        Args:
            item_id: ID of the item to delete

        Returns:
            True if successful, error message otherwise
        """
        pass
