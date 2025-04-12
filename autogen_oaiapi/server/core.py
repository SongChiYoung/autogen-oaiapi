import asyncio
from typing import Optional
from fastapi import FastAPI
from autogen_oaiapi.app.router import register_routes
from autogen_oaiapi.app.middleware import RequestContextMiddleware
from autogen_oaiapi.app.exception_handlers import register_exception_handlers
from autogen_oaiapi.session_manager.memory import InMemorySessionStore
from autogen_oaiapi.session_manager.base import BaseSessionStore

class Server:
    def __init__(self, team, output_idx:int|None = None, source_select:str|None = None, session_store: Optional[BaseSessionStore] = None):
        self.session_store = session_store or InMemorySessionStore()
        self.team_type = type(team)
        self.team_dump = team.dump_component()
        self.session_store = InMemorySessionStore()
        self.output_idx = output_idx
        self.app = FastAPI()

        # Register routers, middlewares, and exception handlers
        register_routes(self.app, self)
        self.app.add_middleware(RequestContextMiddleware)
        register_exception_handlers(self.app)

    def get_team(self, session_id: str):
        team = self.session_store.get(session_id)
        if team is not None:
            asyncio.run(team.reset())  # 상태 초기화만 수행 (message history, cache 등)
            return team

        team = self.team_type.load_component(self.team_dump)
        self.session_store.set(session_id, team)
        return team

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)