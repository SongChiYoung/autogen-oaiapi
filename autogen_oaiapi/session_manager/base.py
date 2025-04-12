from abc import ABC, abstractmethod

class BaseSessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str):
        pass

    @abstractmethod
    def set(self, session_id: str, team):
        pass