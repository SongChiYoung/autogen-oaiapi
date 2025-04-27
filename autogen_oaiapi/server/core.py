from typing import Optional
from fastapi import FastAPI
from autogen_oaiapi.app.router import register_routes
from autogen_oaiapi.app.middleware import RequestContextMiddleware, APIKeyModelMiddleware
from autogen_oaiapi.app.exception_handlers import register_exception_handlers
from autogen_oaiapi.session_manager.memory import InMemorySessionStore
from autogen_oaiapi.session_manager.base import BaseSessionStore
from autogen_oaiapi.model import Model
from autogen_oaiapi.base import BaseKeyManager
from autogen_oaiapi.manager.api_key._non_key_manager import NonKeyManager
from autogen_agentchat.teams import BaseGroupChat
from autogen_agentchat.agents import BaseChatAgent

class Server:
    """
    OpenAI-compatible API server for AutoGen teams.

    Args:
        team: The team (e.g., GroupChat or SocietyOfMindAgent) to use for handling chat sessions.
        output_idx (int | None): Index of the output message to select (if applicable).
        source_select (str | None): Name of the agent whose output should be selected.
        key_manager (BaseKeyManager): Custom key manager for API key management. Defaults to NonKeyManager. NonKeyManager is used for no key management.
        session_store (BaseSessionStore | None): Custom session store backend. Defaults to in-memory.
    """
    def __init__(
            self,
            team: BaseGroupChat | BaseChatAgent | None=None,
            output_idx:int|None = None,
            source_select:str|None = None,
            key_manager:BaseKeyManager|None = None,
            session_store: Optional[BaseSessionStore] = None
        ):
        self._session_store = session_store or InMemorySessionStore()
        self._key_manager = key_manager or NonKeyManager()
        self._model = Model()
        self.app = FastAPI()

        # Register the team with the model
        if team is not None:
            self._model.register(
                name="autogen-baseteam",
                actor=team,
                source_select=source_select,
                output_idx=output_idx,
            )

        # Register routers, middlewares, and exception handlers
        register_routes(self.app)
        # server is passed to the app state for access in routes
        self.app.state.server = self

        self.app.add_middleware(APIKeyModelMiddleware)
        self.app.add_middleware(RequestContextMiddleware)
        register_exception_handlers(self.app)

    @property
    def model(self) -> Model:
        """
        Get the model instance.

        Returns:
            Model: The model instance.
        """
        return self._model
        
    @property
    def session_store(self) -> BaseSessionStore:
        """
        Get the session store instance.

        Returns:
            BaseSessionStore: The session store instance.
        """
        return self._session_store
    
    @property
    def key_manager(self) -> BaseKeyManager:
        """
        Get the key manager instance.

        Returns:
            BaseKeyManager: The key manager instance.
        """
        return self._key_manager

    def run(self, host:str="0.0.0.0", port:int=8000) -> None:
        """
        Start the FastAPI server using Uvicorn.

        Args:
            host (str): Host address to bind. Defaults to "0.0.0.0".
            port (int): Port number. Defaults to 8000.
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)