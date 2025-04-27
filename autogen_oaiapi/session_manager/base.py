from abc import ABC, abstractmethod
from typing import Optional
from ..base.types import SessionContext

class BaseSessionStore(ABC):
    """
    Abstract base class for session storage backends.

    Subclasses must implement get and set methods for session management.
    """
    @abstractmethod
    def get(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve the session context for a given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            SessionContext: The session context object, or None if not found.
        """
        pass

    @abstractmethod
    def set(self, session_id: str, session_context: SessionContext) -> None:
        """
        Store or update the session context for a given session ID.

        Args:
            session_id (str): The session identifier.
            session_context (SessionContext): The session context to store.
        """
        pass