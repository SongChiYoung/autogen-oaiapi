from typing import Dict, Optional
from autogen_oaiapi.session_manager.base import BaseSessionStore
from ..base.types import SessionContext


class InMemorySessionStore(BaseSessionStore):
    """
    In-memory implementation of the session store.

    Stores session contexts in a local dictionary for fast access.
    """
    def __init__(self) -> None:
        self._cache: Dict[str, SessionContext] = {}

    def get(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve the session context for a given session ID from memory.

        Args:
            session_id (str): The session identifier.

        Returns:
            Optional[SessionContext]: The session context object, or None if not found.
        """
        return self._cache.get(session_id)

    def set(self, session_id: str, session_context: SessionContext) -> None:
        """
        Store or update the session context for a given session ID in memory.

        Args:
            session_id (str): The session identifier.
            session_context (SessionContext): The session context to store.
        """
        self._cache[session_id] = session_context

    def delete(self, session_id: str) -> None:
        """
        Delete the session context for a given session ID from memory.

        Args:
            session_id (str): The session identifier.
        """
        self._cache.pop(session_id, None)