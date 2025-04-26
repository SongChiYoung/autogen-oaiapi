import itertools
from typing import Optional
from fastapi import FastAPI
from autogen_oaiapi.app.router import register_routes
from autogen_oaiapi.app.middleware import RequestContextMiddleware
from autogen_oaiapi.app.exception_handlers import register_exception_handlers
from autogen_oaiapi.session_manager.memory import InMemorySessionStore
from autogen_oaiapi.session_manager.base import BaseSessionStore
from autogen_oaiapi.model import Model
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.base import AndTerminationCondition, OrTerminationCondition

class Server:
    """
    OpenAI-compatible API server for AutoGen teams.

    Args:
        team: The team (e.g., GroupChat or SocietyOfMindAgent) to use for handling chat sessions.
        output_idx (int | None): Index of the output message to select (if applicable).
        source_select (str | None): Name of the agent whose output should be selected.
        session_store (BaseSessionStore | None): Custom session store backend. Defaults to in-memory.
    """
    def __init__(self, team=None, output_idx:int|None = None, source_select:str|None = None, session_store: Optional[BaseSessionStore] = None):
        self.session_store = session_store or InMemorySessionStore()
        # self.team_type = type(team)
        # self.team_dump = team.dump_component()
        # self.output_idx = output_idx
        # self.source_select = source_select
        self._model = Model()
        self.app = FastAPI()
        self.terminate_messages = []

        # Register the team with the model
        if team is not None:
            self._model.register(
                name="autogen-baseteam",
                actor=team,
                source_select=source_select,
                output_idx=output_idx,
            )
        else:
            raise ValueError("Team must be provided")

        # Register routers, middlewares, and exception handlers
        register_routes(self.app, self)
        self.app.add_middleware(RequestContextMiddleware)
        register_exception_handlers(self.app)

    @property
    def model(self):
        """
        Get the model instance.

        Returns:
            Model: The model instance.
        """
        return self._model
        

    def run(self, host="0.0.0.0", port=8000):
        """
        Start the FastAPI server using Uvicorn.

        Args:
            host (str): Host address to bind. Defaults to "0.0.0.0".
            port (int): Port number. Defaults to 8000.
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)