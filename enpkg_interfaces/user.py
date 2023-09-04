"""Abstract interface for user objects."""
from typing import Type

from enpkg_interfaces.sample import Sample


class User:
    """Abstract class to represent a user."""

    def __init__(self, user_id: int) -> None:
        """Initialize user object.
        
        Parameters
        ----------
        user_id : int
            User ID.

        Raises
        ------
        ValueError
            If the user ID does not exist.
        """
        if not self.is_valid_user_id(user_id):
            raise ValueError(
                f"User ID #{user_id} does not exist."
            )
        
        self._user_id = user_id

    def get_user_id(self) -> int:
        """Return user ID."""
        return self._user_id

    def is_administrator(self) -> bool:
        """Return True if the user is an administrator."""
        raise NotImplementedError(
            "Abstract method 'is_administrator' must be implemented in subclass. "
            f"It was not implemented in {self.__class__.__name__}."
        )
    
    def is_moderator(self) -> bool:
        """Return True if the user is a moderator."""
        raise NotImplementedError(
            "Abstract method 'is_moderator' must be implemented in subclass. "
            f"It was not implemented in {self.__class__.__name__}."
        )
    
    def is_author_of_sample(self, sample: Type[Sample]) -> bool:
        """Return True if the user is the author of the sample."""
        return self.get_user_id() == sample.get_author_user_id()
    
    @classmethod
    def is_valid_user_id(cls, user_id: int) -> bool:
        """Return True if the user ID is valid.
        
        Parameters
        ----------
        user_id : int
            User ID.
        """
        raise NotImplementedError(
            "Abstract method 'is_valid_user_id' must be implemented in subclass. "
            f"It was not implemented in {cls.__class__.__name__}."
        )