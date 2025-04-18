import itertools
from typing import Optional
from fastapi import FastAPI
from autogen_oaiapi.app.router import register_routes
from autogen_oaiapi.app.middleware import RequestContextMiddleware
from autogen_oaiapi.app.exception_handlers import register_exception_handlers
from autogen_oaiapi.session_manager.memory import InMemorySessionStore
from autogen_oaiapi.session_manager.base import BaseSessionStore
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
    def __init__(self, team, output_idx:int|None = None, source_select:str|None = None, session_store: Optional[BaseSessionStore] = None):
        self.session_store = session_store or InMemorySessionStore()
        self.team_type = type(team)
        self.team_dump = team.dump_component()
        self.output_idx = output_idx
        self.source_select = source_select
        self.app = FastAPI()
        self.terminate_messages = []

        # Register routers, middlewares, and exception handlers
        register_routes(self.app, self)
        self.app.add_middleware(RequestContextMiddleware)
        register_exception_handlers(self.app)

    async def get_team(self, session_id: str):
        """
        Retrieve or initialize the team for a given session.

        Args:
            session_id (str): The session identifier.

        Returns:
            team: The loaded team instance for the session.
        """
        session = self.session_store.get(session_id)
        # if team := session.get("team", None) is not None:
        #     while True:
        #         try:
        #             await team.reset()  # Reset the team state instead of reloading
        #             return team
        #         except:
        #             pass

        team = self.team_type.load_component(self.team_dump)
        # self.session_store.set(session_id, team)

        def get_termination_conditions(termination_condition):
            if isinstance(termination_condition, str):
                return [termination_condition]

            if isinstance(termination_condition, TextMentionTermination):
                return [termination_condition._termination_text]
            
            if isinstance(termination_condition, OrTerminationCondition) or isinstance(termination_condition, AndTerminationCondition):
                _termination_conditions = [get_termination_conditions(condition) for condition in termination_condition._conditions]
                return list(itertools.chain.from_iterable(_termination_conditions))
            
            return []

        self.terminate_messages = get_termination_conditions(team._termination_condition)

        return team

    async def cleanup_team(self, session_id: str, team):
        """
        Cleanup logic for the team after a session ends.

        Args:
            session_id (str): The session identifier.
            team: The team instance to clean up.
        """
        # Cleanup logic for the team
        pass


    def run(self, host="0.0.0.0", port=8000):
        """
        Start the FastAPI server using Uvicorn.

        Args:
            host (str): Host address to bind. Defaults to "0.0.0.0".
            port (int): Port number. Defaults to 8000.
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)