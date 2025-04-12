from fastapi import APIRouter
from autogen_oaiapi.app.routes.v1.chat import router as chat_router

def register_routes(app, server):
    api_router = APIRouter()
    api_router.include_router(chat_router, prefix="/v1")
    app.include_router(api_router)

    # server 객체를 app에 주입
    app.state.server = server