from abc import ABC, abstractmethod
from ..base.types import SessionContext

class BaseSessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> SessionContext:
        pass

    @abstractmethod
    def set(self, session_id: str, session_context: SessionContext) -> None:
        pass