import os
from typing import Optional
from ..base.types import SessionContext
from autogen_oaiapi.session_manager.base import BaseSessionStore

class FileSessionStore(BaseSessionStore):
    """
    File-based implementation of the session store.

    Stores each session context as a JSON file in the specified directory.
    """
    def __init__(self, dir_path:str="sessions") -> None:
        os.makedirs(dir_path, exist_ok=True)
        self.dir_path = dir_path
        raise NotImplementedError("FileSessionStore is not implemented yet.")

    def _file_path(self, session_id:str) -> str:
        """
        Get the file path for a given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            str: The file path for the session JSON file.
        """
        return os.path.join(self.dir_path, f"{session_id}.json")

    def get(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve the session context for a given session ID from file.

        Args:
            session_id (str): The session identifier.

        Returns:
            SessionContext: The session context object, or None if not found.
        """
        raise NotImplementedError("FileSessionStore is not implemented yet.")


    def set(self, session_id: str, session_context: SessionContext) -> None:
        """
        Store or update the session context for a given session ID in a file.

        Args:
            session_id (str): The session identifier.
            team: The team object to serialize and store.
        """
        raise NotImplementedError("FileSessionStore is not implemented yet.")