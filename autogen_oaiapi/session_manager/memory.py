from autogen_oaiapi.session_manager.base import BaseSessionStore

class InMemorySessionStore(BaseSessionStore):
    def __init__(self):
        self._cache = {}

    def get(self, session_id: str):
        return self._cache.get(session_id)

    def set(self, session_id: str, team):
        self._cache[session_id] = team