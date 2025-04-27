import logging
from typing import Any, Optional, Union

import uvicorn
from fastapi import FastAPI

from autogen_oaiapi.app.router import register_routes
from autogen_oaiapi.app.middleware import register_middlewares
from autogen_oaiapi.app.exception_handlers import register_exception_handlers
from autogen_oaiapi.base import BaseKeyManager, BaseSessionStore
from autogen_oaiapi.manager import JsonAPIKeyManager, MemorySessionStore
from autogen_oaiapi.model import ModelClient
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.teams import BaseGroupChat

ActorType = Union[BaseChatAgent, BaseGroupChat]

class Server:
    """
    OpenAI-compatible API server for AutoGen teams.

    Args:
        team (ActorType | None): The team (e.g., GroupChat or SocietyOfMindAgent) to use for handling chat sessions.
        key_manager (BaseKeyManager | None): Custom key manager for API key management. Defaults to JsonAPIKeyManager.
        session_store (BaseSessionStore | None): Custom session store backend. Defaults to in-memory.
        model_client (ModelClient | None): Custom model client. Defaults to ModelClient.
    """
    def __init__(
        self,
        team: Optional[ActorType] = None,
        key_manager: Optional[BaseKeyManager] = None,
        session_store: Optional[BaseSessionStore] = None,
        model_client: Optional[ModelClient] = None,
    ) -> None:
        self.key_manager: BaseKeyManager = key_manager if key_manager else JsonAPIKeyManager()
        self.session_store: BaseSessionStore = session_store if session_store else MemorySessionStore()
        self.model: ModelClient = model_client if model_client else ModelClient()

        if team:
            self.model.register(actor=team, name=self.model.default_model_name)

        self.app = FastAPI()

        register_middlewares(self.app)
        register_exception_handlers(self.app)
        register_routes(self.app, self)

    @property
    def model(self) -> ModelClient:
        """
        Get the model instance.

        Returns:
            ModelClient: The model instance.
        """
        return self.model
        
    @property
    def session_store(self) -> BaseSessionStore:
        """
        Get the session store instance.

        Returns:
            BaseSessionStore: The session store instance.
        """
        return self.session_store
    
    @property
    def key_manager(self) -> BaseKeyManager:
        """
        Get the key manager instance.

        Returns:
            BaseKeyManager: The key manager instance.
        """
        return self.key_manager

    def run(self, host: str = "0.0.0.0", port: int = 8001, **kwargs: Any) -> None:
        """
        Start the FastAPI server using Uvicorn.

        Args:
            host (str): Host address to bind. Defaults to "0.0.0.0".
            port (int): Port number. Defaults to 8001.
        """
        logging.info(f"Starting AutoGen OAIAPI server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, **kwargs)