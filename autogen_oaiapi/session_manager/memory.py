from autogen_oaiapi.session_manager.base import BaseSessionStore
from ..base.types import SessionContext


class InMemorySessionStore(BaseSessionStore):
    def __init__(self):
        self._cache = {}

    def get(self, session_id: str)->SessionContext:
        return self._cache.get(session_id)

    def set(self, session_id: str, session_context: SessionContext) -> None:
        self._cache[session_id] = session_context