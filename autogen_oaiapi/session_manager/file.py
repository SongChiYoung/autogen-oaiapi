import os
import json
from autogen_oaiapi.session_manager.base import BaseSessionStore

class FileSessionStore(BaseSessionStore):
    def __init__(self, dir_path="sessions"):
        os.makedirs(dir_path, exist_ok=True)
        self.dir_path = dir_path

    def _file_path(self, session_id):
        return os.path.join(self.dir_path, f"{session_id}.json")

    def get(self, session_id: str):
        try:
            with open(self._file_path(session_id), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def set(self, session_id: str, team):
        with open(self._file_path(session_id), "w") as f:
            json.dump(team.dump_component(), f)