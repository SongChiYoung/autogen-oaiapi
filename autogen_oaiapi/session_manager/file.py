import os
import json
from typing import Optional
from autogen_core.serialization import dump_component, load_component
from autogen_oaiapi.session_manager.base import BaseSessionStore
from autogen_oaiapi.base.types import SessionContext


class FileSessionStore(BaseSessionStore):
    """
    File-based implementation of the session store.

    Stores each session context as a JSON file in the specified directory.
    """
    def __init__(self, dir_path: str = "sessions") -> None:
        """
        Initialize FileSessionStore.

        Args:
            dir_path (str): The directory path to store session files.
        """
        os.makedirs(dir_path, exist_ok=True)
        self.dir_path = dir_path

    def _file_path(self, session_id: str) -> str:
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
            Optional[SessionContext]: The session context object, or None if not found.
        """
        file_path = self._file_path(session_id)
        if os.path.exists(file_path):
            try:
                loaded_data = load_component(file_path=file_path)
                if isinstance(loaded_data, SessionContext):
                    return loaded_data
                elif isinstance(loaded_data, dict):
                    try:
                        return SessionContext(**loaded_data)
                    except Exception:
                        print(f"Warning: Could not reconstruct SessionContext from dict for {session_id}")
                        return None
                else:
                    print(f"Warning: Loaded unexpected data type {type(loaded_data)} for {session_id}")
                    return None
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
                return None
        return None

    def set(self, session_id: str, session_context: SessionContext) -> None:
        """
        Store or update the session context for a given session ID in a file.

        Args:
            session_id (str): The session identifier.
            session_context (SessionContext): The session context object to serialize and store.
        """
        file_path = self._file_path(session_id)
        try:
            dump_component(session_context, file_path=file_path)
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")

    def delete(self, session_id: str) -> None:
        """
        Delete the session context for a given session ID.

        Args:
            session_id (str): The session identifier.
        """
        file_path = self._file_path(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)