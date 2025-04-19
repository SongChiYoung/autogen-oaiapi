import os
import json
from ..base.types import SessionContext
from autogen_oaiapi.session_manager.base import BaseSessionStore

class FileSessionStore(BaseSessionStore):
    """
    File-based implementation of the session store.

    Stores each session context as a JSON file in the specified directory.
    """
    def __init__(self, dir_path="sessions"):
        raise NotImplementedError("FileSessionStore is not implemented yet.")
        os.makedirs(dir_path, exist_ok=True)
        self.dir_path = dir_path

    def _file_path(self, session_id):
        """
        Get the file path for a given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            str: The file path for the session JSON file.
        """
        return os.path.join(self.dir_path, f"{session_id}.json")

    def get(self, session_id: str) -> SessionContext:
        """
        Retrieve the session context for a given session ID from file.

        Args:
            session_id (str): The session identifier.

        Returns:
            SessionContext: The session context object, or None if not found.
        """
        try:
            with open(self._file_path(session_id), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def set(self, session_id: str, team):
        """
        Store or update the session context for a given session ID in a file.

        Args:
            session_id (str): The session identifier.
            team: The team object to serialize and store.
        """
        with open(self._file_path(session_id), "w") as f:
            json.dump(team.dump_component(), f)